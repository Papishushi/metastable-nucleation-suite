using System.Reflection;
using System.Text.Json;
using Metastable.ControlPlane;

if (args is ["--self-test"])
{
    return ControlPlaneSelfTest.Run();
}

if (args is ["--print-openapi"])
{
    Console.WriteLine(JsonSerializer.Serialize(ControlPlaneOpenApi.Create()));
    return 0;
}

if (args is ["--health-check", var healthUrl])
{
    using var healthClient = new HttpClient { Timeout = TimeSpan.FromSeconds(2) };
    using var response = await healthClient.GetAsync(healthUrl);
    return response.IsSuccessStatusCode ? 0 : 1;
}

var builder = WebApplication.CreateBuilder(args);
var stateDirectory = Environment.GetEnvironmentVariable("METASTABLE_CONTROL_PLANE_STATE")
    ?? Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "metastable-nucleation-suite",
        "control-plane");
var workerUrl = Environment.GetEnvironmentVariable("METASTABLE_SCIENTIFIC_WORKER_URL")
    ?? "http://127.0.0.1:8081";

builder.Services.AddSingleton(provider => new RunOrchestratorSingleton(
    stateDirectory,
    workerUrl,
    provider.GetRequiredService<ILoggerFactory>()));

var app = builder.Build();

app.MapGet("/healthz", async (RunOrchestratorSingleton _) =>
{
    var heartbeat = await RunOrchestratorSingleton.Service.PingAsync();
    return Results.Ok(new
    {
        status = "ok",
        orchestrator_owner = RunOrchestratorSingleton.IsOwner,
        observed_at_utc = heartbeat.UtcTime,
    });
});
app.MapGet("/openapi/v1.json", () => Results.Json(ControlPlaneOpenApi.Create()));
app.MapGet("/v1/capabilities", () => Results.Ok(new
{
    schema_version = "1.0.0",
    server_version = GetVersion(),
    generated_at_utc = DateTimeOffset.UtcNow,
    capabilities = new[]
    {
        Capability("server.capabilities.v1"),
        Capability("runs.submit.v1"),
        Capability("runs.read.v1"),
        Capability("runs.cancel.v1"),
        Capability("artifacts.read.v1"),
    },
}));

app.MapPost("/v1/runs", async (
    HttpRequest httpRequest,
    RunOrchestratorSingleton _,
    CancellationToken cancellationToken) =>
{
    var idempotencyKey = httpRequest.Headers["Idempotency-Key"].ToString();
    if (!IsValidIdempotencyKey(idempotencyKey))
    {
        return Results.BadRequest(new { error = "invalid_idempotency_key" });
    }

    ExperimentRequest? request;
    try
    {
        request = await httpRequest.ReadFromJsonAsync<ExperimentRequest>(
            cancellationToken);
    }
    catch (JsonException)
    {
        return Results.BadRequest(new { error = "invalid_request" });
    }

    if (request is null || !request.IsValid())
    {
        return Results.BadRequest(new { error = "invalid_request" });
    }

    var result = await RunOrchestratorSingleton.Service.SubmitAsync(
        idempotencyKey,
        JsonSerializer.Serialize(request));
    if (result.Outcome == "conflict")
    {
        return Results.Conflict(new { error = "idempotency_conflict" });
    }

    if (result.Outcome == "created")
    {
        using var payload = JsonDocument.Parse(result.Payload!);
        var runId = payload.RootElement.GetProperty("run_id").GetGuid();
        return Results.Created(
            $"/v1/runs/{runId:D}",
            payload.RootElement.Clone());
    }

    if (result.Outcome == "existing")
    {
        return Results.Content(result.Payload!, "application/json");
    }

    return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
});

app.MapGet("/v1/runs/{runId:guid}", async (
    Guid runId,
    RunOrchestratorSingleton _) =>
{
    var run = await RunOrchestratorSingleton.Service.GetRunAsync(runId.ToString("D"));
    return run is null
        ? Results.NotFound(new { error = "run_not_found" })
        : Results.Content(run, "application/json");
});

app.MapPost("/v1/runs/{runId:guid}/cancel", async (
    Guid runId,
    RunOrchestratorSingleton _) =>
{
    var result = await RunOrchestratorSingleton.Service.CancelAsync(
        runId.ToString("D"));
    if (result.Outcome == "missing")
    {
        return Results.NotFound(new { error = "run_not_found" });
    }

    if (result.Outcome == "terminal")
    {
        return Results.Conflict(new { error = "run_is_terminal" });
    }

    return Results.Content(result.Payload!, "application/json");
});

app.MapGet("/v1/runs/{runId:guid}/artifacts/{artifactId}", async (
    Guid runId,
    string artifactId,
    RunOrchestratorSingleton _) =>
{
    var artifact = await RunOrchestratorSingleton.Service.GetArtifactAsync(
        runId.ToString("D"),
        artifactId);
    return artifact is null
        ? Results.NotFound(new { error = "artifact_not_found" })
        : Results.Content(artifact, "application/json");
});

await app.RunAsync();
return 0;

static object Capability(string id) => new
{
    id,
    status = "active",
    since_version = "0.2.0",
};

static string GetVersion() =>
    Assembly.GetExecutingAssembly()
        .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
        .InformationalVersion
    ?? Assembly.GetExecutingAssembly().GetName().Version?.ToString()
    ?? "0.0.0+unknown";

static bool IsValidIdempotencyKey(string key) =>
    key.Length is >= 1 and <= 128
    && key.All(character => character is >= (char)0x21 and <= (char)0x7e);
