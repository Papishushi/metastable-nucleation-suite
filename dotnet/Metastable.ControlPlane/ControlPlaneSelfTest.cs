namespace Metastable.ControlPlane;

internal static class ControlPlaneSelfTest
{
    internal static int Run()
    {
        var root = Path.Combine(
            Path.GetTempPath(),
            $"metastable-control-plane-self-test-{Guid.NewGuid():N}");
        try
        {
            Guid runId;
            Guid completedRunId;
            using (var store = new ControlPlaneStore(root))
            {
                var nonRfc3339Request = NewRequest("invalid-timestamp") with
                {
                    SubmittedAtUtc = "2026-07-15 00:00:00+00:00",
                };
                if (nonRfc3339Request.IsValid())
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: non-RFC3339 timestamp was accepted");
                    return 1;
                }

                var created = store.CreateRun(
                    "self-test-key",
                    new ExperimentRequest(
                        "1.0.0",
                        Guid.NewGuid().ToString("D"),
                        "control-plane-self-test",
                        DateTimeOffset.UtcNow.ToString("O")));
                if (!created.Created)
                {
                    Console.Error.WriteLine("control-plane self-test: run was not created");
                    return 1;
                }

                if (store.GetRun(created.Run.RunId)?.State != RunStates.Queued)
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: queued run was not readable");
                    return 1;
                }

                if (!store.TryBeginDispatch(created.Run.RunId, out var running)
                    || running?.State != RunStates.Running)
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: run did not enter running state");
                    return 1;
                }

                runId = created.Run.RunId;

                var cancelled = store.CreateRun(
                    "self-test-cancelled-key",
                    NewRequest("control-plane-cancelled-self-test"));
                if (!store.TryCancel(cancelled.Run.RunId, out var cancelledRun)
                    || cancelledRun?.State != RunStates.Cancelled
                    || store.TryBeginDispatch(cancelled.Run.RunId, out _))
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: cancelled run could enter dispatch");
                    return 1;
                }

                var completed = store.CreateRun(
                    "self-test-completed-key",
                    NewRequest("control-plane-completed-self-test"));
                if (!store.TryBeginDispatch(completed.Run.RunId, out _))
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: completed run did not start");
                    return 1;
                }

                store.Complete(
                    completed.Run.RunId,
                    "/artifacts/self-test.json",
                    "{\"status\":\"completed\"}");
                completedRunId = completed.Run.RunId;
                store.Fail(completed.Run.RunId, "late artifact-index failure");
                if (store.GetRun(completed.Run.RunId)?.State != RunStates.Succeeded)
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: failure overwrote terminal success");
                    return 1;
                }

                var failed = store.CreateRun(
                    "self-test-failed-key",
                    NewRequest("control-plane-failure-self-test"));
                if (!store.TryBeginDispatch(failed.Run.RunId, out _))
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: failed run did not start");
                    return 1;
                }

                store.Fail(
                    failed.Run.RunId,
                    new string('x', ControlPlaneStore.MaxFailureReasonCharacters + 4096));
                var boundedFailure = store.GetRun(failed.Run.RunId);
                if (boundedFailure?.State != RunStates.Failed
                    || boundedFailure?.Failure?.Length
                        != ControlPlaneStore.MaxFailureReasonCharacters + 1)
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: persisted failure was not bounded");
                    return 1;
                }
            }

            using (var recovered = new ControlPlaneStore(root))
            {
                recovered.RecoverInterruptedRuns();
                var recoveredRun = recovered.GetRun(runId);
                if (recoveredRun?.State != RunStates.RecoveryRequired)
                {
                    Console.Error.WriteLine(
                        $"control-plane self-test: expected recovery_required, got {recoveredRun?.State ?? "missing"}");
                    return 1;
                }

                if (recovered.GetRun(completedRunId)?.State != RunStates.Succeeded
                    || recovered.GetArtifact(completedRunId, "primary") is null)
                {
                    Console.Error.WriteLine(
                        "control-plane self-test: completed artifact index was not durable");
                    return 1;
                }
            }

            Console.WriteLine("control-plane self-test: ok");
            return 0;
        }
        finally
        {
            try
            {
                Directory.Delete(root, recursive: true);
            }
            catch (IOException)
            {
                // A failed cleanup must not hide the persistence assertion result.
            }
            catch (UnauthorizedAccessException)
            {
                // Windows may release mapped files asynchronously after disposal.
            }
        }
    }

    private static ExperimentRequest NewRequest(string experimentId) =>
        new(
            "1.0.0",
            Guid.NewGuid().ToString("D"),
            experimentId,
            DateTimeOffset.UtcNow.ToString("O"));
}
