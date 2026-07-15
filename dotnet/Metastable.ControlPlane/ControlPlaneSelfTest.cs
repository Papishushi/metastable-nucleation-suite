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
            using (var store = new ControlPlaneStore(root))
            {
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
}
