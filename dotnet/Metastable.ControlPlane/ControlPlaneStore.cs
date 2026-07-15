using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Extend0.Metadata;
using Extend0.Metadata.Contract;
using Extend0.Metadata.Schema;
using Extend0.Metadata.Storage;
using Extend0.Metadata.Typed;

namespace Metastable.ControlPlane;

internal sealed class ControlPlaneStore : IDisposable
{
    private const uint InitialCapacity = 256;
    private const int KeyBytes = 128;
    private const int RunValueBytes = 32 * 1024;
    private const int ArtifactValueBytes = 8 * 1024;
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    private readonly Lock _gate = new();
    private readonly IMetaDBManager _manager;
    private readonly IMetadataTable _runs;
    private readonly IMetadataTable _artifacts;
    private readonly MetadataUtf8Column _runDocuments;
    private readonly MetadataUtf8Column _artifactDocuments;

    internal ControlPlaneStore(string stateDirectory)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(stateDirectory);
        Directory.CreateDirectory(stateDirectory);

        _manager = MetaDB.CreateManager(
            capacityPolicy: CapacityPolicy.AutoGrowZeroInit,
            deleteQueuePath: Path.Combine(stateDirectory, "delete-queue.json"));

        _runs = CreateTable(
            "metastable-control-plane-runs-v1",
            "https://w3id.org/metastable-nucleation-suite/metadb/runs",
            Path.Combine(stateDirectory, "runs.meta"),
            RunValueBytes);
        _artifacts = CreateTable(
            "metastable-control-plane-artifacts-v1",
            "https://w3id.org/metastable-nucleation-suite/metadb/artifacts",
            Path.Combine(stateDirectory, "artifacts.meta"),
            ArtifactValueBytes);

        _runDocuments = new MetadataUtf8Column(
            _runs, 0, "Documents", KeyBytes, RunValueBytes);
        _artifactDocuments = new MetadataUtf8Column(
            _artifacts, 0, "Documents", KeyBytes, ArtifactValueBytes);
    }

    internal CreateRunResult CreateRun(
        string idempotencyKey,
        ExperimentRequest request)
    {
        lock (_gate)
        {
            request = request with
            {
                RequestId = Guid.Parse(request.RequestId).ToString("D"),
            };
            foreach (var existing in ReadAllRunsUnsafe())
            {
                if (string.Equals(
                    existing.IdempotencyKey,
                    idempotencyKey,
                    StringComparison.Ordinal))
                {
                    var sameRequest = existing.Request == request;
                    return new CreateRunResult(existing, false, !sameRequest);
                }

                if (string.Equals(
                    existing.Request.RequestId,
                    request.RequestId,
                    StringComparison.OrdinalIgnoreCase))
                {
                    return new CreateRunResult(existing, false, true);
                }
            }

            var now = DateTimeOffset.UtcNow;
            var run = new RunRecord(
                "1.0.0",
                Guid.CreateVersion7(),
                idempotencyKey,
                request,
                RunStates.Queued,
                now,
                now,
                null,
                null,
                [new RunTransition(RunStates.Queued, now, "accepted")]);
            WriteRunUnsafe(run);
            return new CreateRunResult(run, true, false);
        }
    }

    internal RunRecord? GetRun(Guid runId)
    {
        lock (_gate)
        {
            return ReadByKeyUnsafe<RunRecord>(
                _runs,
                _runDocuments,
                runId.ToString("D"));
        }
    }

    internal ArtifactIndexRecord? GetArtifact(Guid runId, string artifactId)
    {
        lock (_gate)
        {
            return ReadByKeyUnsafe<ArtifactIndexRecord>(
                _artifacts,
                _artifactDocuments,
                ArtifactKey(runId, artifactId));
        }
    }

    internal IReadOnlyList<Guid> RecoverInterruptedRuns()
    {
        lock (_gate)
        {
            var queued = new List<Guid>();
            foreach (var run in ReadAllRunsUnsafe())
            {
                if (run.State == RunStates.Queued)
                {
                    queued.Add(run.RunId);
                    continue;
                }

                if (run.State != RunStates.Running)
                {
                    continue;
                }

                WriteRunUnsafe(Transition(
                    run,
                    RunStates.RecoveryRequired,
                    "control-plane restarted during dispatch"));
            }

            return queued;
        }
    }

    internal bool TryBeginDispatch(Guid runId, out RunRecord? run)
    {
        lock (_gate)
        {
            run = GetRunUnsafe(runId);
            if (run?.State != RunStates.Queued)
            {
                return false;
            }

            run = Transition(run, RunStates.Running, "worker dispatch started");
            WriteRunUnsafe(run);
            return true;
        }
    }

    internal bool TryCancel(Guid runId, out RunRecord? run)
    {
        lock (_gate)
        {
            run = GetRunUnsafe(runId);
            if (run is null || RunStates.IsTerminal(run.State))
            {
                return false;
            }

            run = Transition(run, RunStates.Cancelled, "cancellation requested");
            WriteRunUnsafe(run);
            return true;
        }
    }

    internal void Complete(Guid runId, string artifactUri, string workerResponse)
    {
        lock (_gate)
        {
            var run = GetRequiredRunUnsafe(runId);
            if (run.State == RunStates.Cancelled)
            {
                return;
            }

            var artifact = new ArtifactReference(
                "primary",
                artifactUri,
                "application/json",
                Convert.ToHexStringLower(
                    SHA256.HashData(Encoding.UTF8.GetBytes(workerResponse))));
            var completed = Transition(run, RunStates.Succeeded, "worker completed")
                with { Artifact = artifact, Failure = null };
            WriteRunUnsafe(completed);
            WriteDocumentUnsafe(
                _artifacts,
                _artifactDocuments,
                ArtifactKey(runId, artifact.ArtifactId),
                new ArtifactIndexRecord("1.0.0", runId, artifact, DateTimeOffset.UtcNow));
        }
    }

    internal void Fail(Guid runId, string reason)
    {
        lock (_gate)
        {
            var run = GetRequiredRunUnsafe(runId);
            if (run.State == RunStates.Cancelled)
            {
                return;
            }

            var failed = Transition(run, RunStates.Failed, "worker dispatch failed")
                with { Failure = reason };
            WriteRunUnsafe(failed);
        }
    }

    internal void Interrupt(Guid runId)
    {
        lock (_gate)
        {
            var run = GetRequiredRunUnsafe(runId);
            if (run.State == RunStates.Running)
            {
                WriteRunUnsafe(Transition(
                    run,
                    RunStates.RecoveryRequired,
                    "dispatch interrupted by control-plane shutdown"));
            }
        }
    }

    public void Dispose()
    {
        _manager.Dispose();
    }

    private IMetadataTable CreateTable(
        string name,
        string schemaId,
        string path,
        int valueBytes)
    {
        var spec = new TableSpec(
            name,
            path,
            [TableSpec.Helpers.Column(
                "Documents",
                InitialCapacity,
                valueBytes,
                KeyBytes)])
        {
            SchemaVersion = 1,
            SchemaId = schemaId,
            SchemaDescription = "Derived operational index; scientific artifacts remain authoritative.",
        };
        var tableId = _manager.RegisterTable(spec, createNow: true);
        return _manager.GetOrCreate(tableId);
    }

    private RunRecord? GetRunUnsafe(Guid runId) =>
        ReadByKeyUnsafe<RunRecord>(
            _runs,
            _runDocuments,
            runId.ToString("D"));

    private RunRecord GetRequiredRunUnsafe(Guid runId) =>
        GetRunUnsafe(runId)
        ?? throw new InvalidOperationException($"Run '{runId:D}' is not registered.");

    private List<RunRecord> ReadAllRunsUnsafe()
    {
        var runs = new List<RunRecord>();
        _runs.WithExclusiveAccess(table =>
        {
            if (!table.TryGetColumnCapacity(0, out var capacity))
            {
                return;
            }

            for (uint row = 0; row < capacity; row++)
            {
                if (!TryReadKey(table, row, out _)
                    || !_runDocuments.TryGet(row, out var json)
                    || string.IsNullOrWhiteSpace(json))
                {
                    continue;
                }

                var run = JsonSerializer.Deserialize<RunRecord>(json, JsonOptions)
                    ?? throw new InvalidDataException($"Run row {row} is empty.");
                runs.Add(run);
            }
        });
        return runs;
    }

    private static T? ReadByKeyUnsafe<T>(
        IMetadataTable table,
        MetadataUtf8Column documents,
        string key)
    {
        T? result = default;
        table.WithExclusiveAccess(locked =>
        {
            if (!TryFindRow(locked, key, out var row)
                || !documents.TryGet(row, out var json)
                || string.IsNullOrWhiteSpace(json))
            {
                return;
            }

            result = JsonSerializer.Deserialize<T>(json, JsonOptions)
                ?? throw new InvalidDataException($"MetaDB record '{key}' is empty.");
        });
        return result;
    }

    private void WriteRunUnsafe(RunRecord run) =>
        WriteDocumentUnsafe(
            _runs,
            _runDocuments,
            run.RunId.ToString("D"),
            run);

    private static void WriteDocumentUnsafe<T>(
        IMetadataTable table,
        MetadataUtf8Column documents,
        string key,
        T value)
    {
        var json = JsonSerializer.Serialize(value, JsonOptions);
        table.WithExclusiveAccess(locked =>
        {
            var exists = TryFindRow(locked, key, out var row);
            if (!exists)
            {
                row = FindFreeRow(locked);
                if (!documents.TrySetKey(row, key))
                {
                    throw new InvalidOperationException($"MetaDB key '{key}' does not fit.");
                }
            }

            if (!documents.TrySet(row, json))
            {
                throw new InvalidOperationException(
                    $"MetaDB document '{key}' exceeds its schema capacity.");
            }
        });
    }

    private static uint FindFreeRow(IMetadataTable table)
    {
        if (!table.TryGetColumnCapacity(0, out var capacity))
        {
            throw new InvalidOperationException("MetaDB does not report table capacity.");
        }

        for (uint row = 0; row < capacity; row++)
        {
            if (!TryReadKey(table, row, out _))
            {
                return row;
            }
        }

        var target = checked(Math.Max(capacity + 1, capacity * 2));
        if (!table.TryGrowColumnTo(0, target, zeroInit: true))
        {
            throw new InvalidOperationException(
                $"MetaDB could not grow the operational table to {target} rows.");
        }

        return capacity;
    }

    private static bool TryFindRow(
        IMetadataTable table,
        string expected,
        out uint row)
    {
        row = 0;
        if (!table.TryGetColumnCapacity(0, out var capacity))
        {
            return false;
        }

        for (uint candidate = 0; candidate < capacity; candidate++)
        {
            if (TryReadKey(table, candidate, out var key)
                && string.Equals(key, expected, StringComparison.Ordinal))
            {
                row = candidate;
                return true;
            }
        }

        return false;
    }

    private static bool TryReadKey(
        IMetadataTable table,
        uint row,
        out string key)
    {
        key = string.Empty;
        if (!table.TryGetCell(0, row, out var cell)
            || !cell.TryGetKeyRaw(out var raw))
        {
            return false;
        }

        var end = raw.IndexOf((byte)0);
        var trimmed = end < 0 ? raw : raw[..end];
        if (trimmed.IsEmpty)
        {
            return false;
        }

        key = Encoding.UTF8.GetString(trimmed);
        return true;
    }

    private static RunRecord Transition(
        RunRecord run,
        string state,
        string reason)
    {
        var now = DateTimeOffset.UtcNow;
        return run with
        {
            State = state,
            UpdatedAtUtc = now,
            Transitions = [.. run.Transitions, new RunTransition(state, now, reason)],
        };
    }

    private static string ArtifactKey(Guid runId, string artifactId) =>
        $"{runId:D}:{artifactId}";
}
