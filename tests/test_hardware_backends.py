from datetime import datetime, timezone

from metastable_suite.hardware import CommandBackend, TrialRequest


class FakeCommandBackend(CommandBackend):
    backend_id = "fake-command"

    def __init__(self):
        super().__init__(firmware_version="fake-1")
        self.commands = []

    def _exchange(self, command, payload):
        self.commands.append((command, dict(payload)))
        if command == "prepare":
            return {"ok": True}
        if command == "calibrate":
            return {"ok": True, "offset": 0.01}
        if command == "execute_trial":
            return {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "outcome": {"count": 1},
                "diagnostics": {"temperature_c": 21.5},
                "valid": True,
            }
        if command == "reset":
            return {"reset_ok": True}
        if command == "diagnostics":
            return {"laser_lock": True}
        if command == "close":
            return {"ok": True}
        raise AssertionError(command)


def test_command_backend_normalizes_hardware_lifecycle():
    backend = FakeCommandBackend()
    backend.prepare("E09", {"pump_power": 1.2})
    assert backend.calibrate()["ok"] is True
    assert backend.reset()["reset_ok"] is True

    response = backend.execute_trial(TrialRequest("run-1", "E09", 0, {"phase": 1}))
    assert response.valid
    assert response.outcome["count"] == 1
    assert response.diagnostics["temperature_c"] == 21.5
    assert backend.collect_diagnostics()["laser_lock"] is True
    backend.close()

    assert [command for command, _ in backend.commands] == [
        "prepare",
        "calibrate",
        "reset",
        "execute_trial",
        "diagnostics",
        "close",
    ]
