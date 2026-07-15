using System.Collections.Concurrent;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Channels;
using Extend0.Lifecycle.CrossProcess;
using Microsoft.Extensions.Logging;

namespace Metastable.ControlPlane;

public sealed record OrchestrationResult(string Outcome, string? Payload);

public interface IRunOrchestrator : ICrossProcessService
{
    Task<OrchestrationResult> SubmitAsync(
        string idempotencyKey,
        string requestJson);

    Task<string?> GetRunAsync(string runId);

    Task<OrchestrationResult> CancelAsync(string runId);

    Task<string?> GetArtifactAsync(string runId, string artifactId);
}

internal sealed partial class Extend0RunOrchestrator
    : CrossProcessServiceBase<IRunOrchestrator>, IRunOrchestrator, IDisposable
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);
    private readonly ILogger<Extend0RunOrchestrator> _logger;
    private readonly ControlPlaneStore _store;
    private readonly ScientificWorkerClient _worker;
    private readonly Channel<Guid> _queue = Channel.CreateUnbounded<Guid>(
        new UnboundedChannelOptions
        {
            SingleReader = true,
            SingleWriter = false,
        });
    private readonly ConcurrentDictionary<Guid, CancellationTokenSource> _active = new();
    private readonly CancellationTokenSource _shutdown = new();
    private readonly Task _dispatchLoop;
    private bool _disposed;

    public override string ContractName =>
        "metastable.control-plane.run-orchestrator.v1";

    protected override string PipeName =>
        "Metastable.ControlPlane.RunOrchestrator.v1";

    public Extend0RunOrchestrator(
        string stateDirectory,
        string workerUrl,
        ILogger<Extend0RunOrchestrator> logger,
        bool start = true)
        : base(logger)
    {
        _logger = logger;
        _store = new ControlPlaneStore(stateDirectory);
        _worker = new ScientificWorkerClient(workerUrl);
        foreach (var queued in _store.RecoverInterruptedRuns())
        {
            _queue.Writer.TryWrite(queued);
        }

        _dispatchLoop = start
            ? Task.Run(() => DispatchLoopAsync(_shutdown.Token))
            : Task.CompletedTask;
    }

    public Task<OrchestrationResult> SubmitAsync(
        string idempotencyKey,
        string requestJson)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        var request = JsonSerializer.Deserialize<ExperimentRequest>(
            requestJson,
            JsonOptions);
        if (request is null || !request.IsValid())
        {
            return Task.FromResult(new OrchestrationResult("invalid", null));
        }

        var result = _store.CreateRun(idempotencyKey, request);
        if (result.Conflict)
        {
            return Task.FromResult(new OrchestrationResult("conflict", null));
        }

        if (result.Created && !_queue.Writer.TryWrite(result.Run.RunId))
        {
            _store.Fail(result.Run.RunId, "Extend0 orchestrator queue is unavailable");
            return Task.FromResult(new OrchestrationResult("unavailable", null));
        }

        var payload = JsonSerializer.Serialize(result.Run.ToResponse(), JsonOptions);
        return Task.FromResult(new OrchestrationResult(
            result.Created ? "created" : "existing",
            payload));
    }

    public Task<string?> GetRunAsync(string runId)
    {
        if (!Guid.TryParseExact(runId, "D", out var parsed))
        {
            return Task.FromResult<string?>(null);
        }

        var run = _store.GetRun(parsed);
        return Task.FromResult(run is null
            ? null
            : JsonSerializer.Serialize(run.ToResponse(), JsonOptions));
    }

    public Task<OrchestrationResult> CancelAsync(string runId)
    {
        if (!Guid.TryParseExact(runId, "D", out var parsed))
        {
            return Task.FromResult(new OrchestrationResult("missing", null));
        }

        if (_store.GetRun(parsed) is null)
        {
            return Task.FromResult(new OrchestrationResult("missing", null));
        }

        if (!_store.TryCancel(parsed, out var run) || run is null)
        {
            return Task.FromResult(new OrchestrationResult("terminal", null));
        }

        if (_active.TryGetValue(parsed, out var active))
        {
            active.Cancel();
        }

        return Task.FromResult(new OrchestrationResult(
            "cancelled",
            JsonSerializer.Serialize(run.ToResponse(), JsonOptions)));
    }

    public Task<string?> GetArtifactAsync(string runId, string artifactId)
    {
        if (!Guid.TryParseExact(runId, "D", out var parsed))
        {
            return Task.FromResult<string?>(null);
        }

        var artifact = _store.GetArtifact(parsed, artifactId);
        return Task.FromResult(artifact is null
            ? null
            : JsonSerializer.Serialize(artifact, JsonOptions));
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _shutdown.Cancel();
        _queue.Writer.TryComplete();
        try
        {
            _dispatchLoop.GetAwaiter().GetResult();
        }
        catch (OperationCanceledException)
        {
            // Expected during owner shutdown.
        }

        _shutdown.Dispose();
        _worker.Dispose();
        _store.Dispose();
    }

    private async Task DispatchLoopAsync(CancellationToken stoppingToken)
    {
        try
        {
            await foreach (var runId in _queue.Reader.ReadAllAsync(stoppingToken))
            {
                using var dispatch = CancellationTokenSource.CreateLinkedTokenSource(
                    stoppingToken);
                if (!_active.TryAdd(runId, dispatch))
                {
                    _store.Fail(runId, "duplicate active Extend0 dispatch");
                    continue;
                }

                try
                {
                    // Register cancellation before persisting `running`. CancelAsync
                    // can now either cancel a queued run or signal every running run,
                    // so physical work cannot start through the gap between the two.
                    if (!_store.TryBeginDispatch(runId, out var run) || run is null)
                    {
                        continue;
                    }

                    var result = await _worker.ExecuteAsync(run.Request, dispatch.Token);
                    _store.Complete(runId, result.ArtifactUri, result.ResponseBody);
                }
                catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
                {
                    _store.Interrupt(runId);
                }
                catch (OperationCanceledException) when (dispatch.IsCancellationRequested)
                {
                    // CancelAsync persisted the terminal transition before signalling.
                }
                catch (Exception exception)
                {
                    RecordDispatchFailure(runId, exception);
                }
                finally
                {
                    _active.TryRemove(runId, out _);
                }
            }
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
            // The Extend0 owner is shutting down.
        }
    }

    private void RecordDispatchFailure(Guid runId, Exception exception)
    {
        LogDispatchFailure(_logger, exception, runId);
        try
        {
            _store.Fail(runId, exception.Message);
        }
        catch (Exception persistenceException)
        {
            LogFailurePersistenceFailure(
                _logger,
                persistenceException,
                runId);
        }
    }

    [LoggerMessage(
        EventId = 3401,
        Level = LogLevel.Error,
        Message = "Extend0 orchestrator dispatch failed for run {RunId}")]
    private static partial void LogDispatchFailure(
        ILogger logger,
        Exception exception,
        Guid runId);

    [LoggerMessage(
        EventId = 3402,
        Level = LogLevel.Error,
        Message = "Could not persist dispatch failure for run {RunId}; continuing queue processing")]
    private static partial void LogFailurePersistenceFailure(
        ILogger logger,
        Exception exception,
        Guid runId);
}

internal sealed class ScientificWorkerClient : IDisposable
{
    private static readonly JsonSerializerOptions JsonOptions =
        new(JsonSerializerDefaults.Web);
    private readonly HttpClient _client;

    internal ScientificWorkerClient(string workerUrl)
    {
        _client = new HttpClient
        {
            BaseAddress = new Uri(workerUrl, UriKind.Absolute),
            Timeout = TimeSpan.FromMinutes(5),
        };
    }

    internal async Task<WorkerResult> ExecuteAsync(
        ExperimentRequest request,
        CancellationToken cancellationToken)
    {
        var payload = JsonSerializer.SerializeToUtf8Bytes(request, JsonOptions);
        using var content = new ByteArrayContent(payload);
        content.Headers.ContentType = new MediaTypeHeaderValue("application/json")
        {
            CharSet = "utf-8",
        };
        using var response = await _client.PostAsync(
            "/v1/experiments",
            content,
            cancellationToken);
        var body = await response.Content.ReadAsStringAsync(cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            throw new InvalidOperationException(
                $"Scientific worker returned HTTP {(int)response.StatusCode}: {body}");
        }

        using var document = JsonDocument.Parse(body);
        var root = document.RootElement;
        var requestId = root.GetProperty("request_id").GetString();
        var status = root.GetProperty("status").GetString();
        var artifact = root.GetProperty("artifact").GetString();
        if (!string.Equals(requestId, request.RequestId, StringComparison.OrdinalIgnoreCase)
            || status != "completed"
            || string.IsNullOrWhiteSpace(artifact))
        {
            throw new InvalidDataException(
                "Scientific worker response does not match the v1 execution contract.");
        }

        return new WorkerResult(artifact, body);
    }

    public void Dispose() => _client.Dispose();
}

internal sealed record WorkerResult(string ArtifactUri, string ResponseBody);

internal sealed class RunOrchestratorSingleton : CrossProcessSingleton<IRunOrchestrator>
{
    internal RunOrchestratorSingleton(
        string stateDirectory,
        string workerUrl,
        ILoggerFactory loggerFactory)
        : base(
            () => new Extend0RunOrchestrator(
                stateDirectory,
                workerUrl,
                loggerFactory.CreateLogger<Extend0RunOrchestrator>(),
                start: true),
            new CrossProcessSingletonOptions
            {
                Mode = SingletonMode.CrossProcess,
                TransportKind = OperatingSystem.IsWindows()
                    ? TransportKind.NamedPipe
                    : TransportKind.UnixDomainSocket,
                CrossProcessName = "Metastable.ControlPlane.RunOrchestrator.v1",
                CrossProcessConnectTimeoutMs = 5000,
                Overwrite = false,
                Logger = loggerFactory.CreateLogger<RunOrchestratorSingleton>(),
            },
            loggerFactory)
    {
    }
}
