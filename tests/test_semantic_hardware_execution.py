import copy
import json
from pathlib import Path
import socketserver
from threading import Thread

import pytest

from metastable_suite.datasets import read_events, sha256_file
from metastable_suite.semantic import load_abox, load_tbox, validate_abox
from scripts.semantic_execute import (
    ABOX_SCHEMA,
    SHAPES,
    TBOX,
    execute_plan,
)

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "ontology" / "examples" / "planned-e09-hardware.jsonld"


class FakeLaboratoryDeviceHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw_request in self.rfile:
            request = json.loads(raw_request)
            command = request["command"]
            payload = request["payload"]
            self.server.commands.append((command, payload))

            if command == "prepare":
                response = {"ok": True}
            elif command == "calibrate":
                response = {"calibration_ok": True, "offset": 0.01}
            elif command == "reset":
                response = {"reset_ok": True}
            elif command == "execute_trial":
                response = {
                    "timestamp_utc": "2026-07-12T16:00:00Z",
                    "outcome": {"count": payload["trial_index"] + 10},
                    "diagnostics": {"laser_lock": True},
                    "valid": True,
                }
            elif command == "diagnostics":
                response = {"temperature_c": 22.5, "laser_lock": True}
            elif command == "close":
                response = {"ok": True}
            else:
                response = {"error": f"unsupported command {command}"}

            self.wfile.write(json.dumps(response).encode("utf-8") + b"\n")
            self.wfile.flush()


class FakeLaboratoryDevice(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), FakeLaboratoryDeviceHandler)
        self.commands = []


def backend_configuration(port):
    return {
        "schema_version": "1.0.0",
        "backends": [
            {
                "id": "lab-counter-tcp",
                "transport": "tcp",
                "host": "127.0.0.1",
                "port": port,
                "timeout_s": 1.0,
                "firmware_version": "fake-counter-1.0.0",
                "supported_specifications": ["E09"],
                "retry_policy": {
                    "attempts": 1,
                    "initial_delay_s": 0,
                    "backoff": 1,
                    "maximum_delay_s": 0,
                },
            }
        ],
    }


def write_configuration(tmp_path, port):
    configuration_path = tmp_path / "hardware-backends.json"
    configuration_path.write_text(
        json.dumps(backend_configuration(port)),
        encoding="utf-8",
    )
    return configuration_path


def test_semantic_plan_executes_end_to_end_through_tcp_hardware(tmp_path):
    server = FakeLaboratoryDevice()
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        configuration_path = write_configuration(
            tmp_path,
            server.server_address[1],
        )
        output_dir = tmp_path / "output"

        documents = execute_plan(
            PLAN,
            output_dir,
            backend_config=configuration_path,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert len(documents) == 1
    events_path = output_dir / "planned-e09-hardware-demo.events.ndjson"
    abox_path = output_dir / "planned-e09-hardware-demo.abox.jsonld"
    events = list(read_events(events_path))

    assert len(events) == 2
    assert [event["outcome"]["count"] for event in events] == [10, 11]
    assert all(
        event["backend_id"] == "lab-counter-tcp" for event in events
    )
    assert all(
        event["firmware_version"] == "fake-counter-1.0.0"
        for event in events
    )

    document = json.loads(abox_path.read_text(encoding="utf-8"))
    run = next(
        node
        for node in document["@graph"]
        if node.get("mns:identifier") == "planned-e09-hardware-demo"
    )
    backend = next(
        node
        for node in document["@graph"]
        if node.get("mns:identifier") == "lab-counter-tcp"
    )
    specification = next(
        node
        for node in document["@graph"]
        if node.get("mns:identifier") == "E09"
    )
    dataset = next(
        node
        for node in document["@graph"]
        if node.get("@type") == "mns:Dataset"
    )

    assert "mns:ExperimentRun" in run["@type"]
    assert "mns:SimulationRun" not in run["@type"]
    assert "mns:ExecutionBackend" in backend["@type"]
    assert "mns:HardwareBackend" in backend["@type"]
    assert "mns:SimulatorBackend" not in backend["@type"]
    assert "mns:PhysicalExperimentSpecification" in specification["@type"]
    assert "mns:SimulationSpecification" not in specification["@type"]
    assert dataset["mns:eventCount"]["@value"] == 2
    assert dataset["mns:sha256"] == sha256_file(events_path)

    graph = load_abox(abox_path, ABOX_SCHEMA)
    outcome = validate_abox(graph, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text

    assert [command for command, _ in server.commands] == [
        "prepare",
        "calibrate",
        "reset",
        "execute_trial",
        "reset",
        "execute_trial",
        "diagnostics",
        "close",
    ]


def test_simulation_plan_cannot_activate_hardware_backend(tmp_path):
    server = FakeLaboratoryDevice()
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        configuration_path = write_configuration(
            tmp_path,
            server.server_address[1],
        )
        document = json.loads(PLAN.read_text(encoding="utf-8"))
        mismatched = copy.deepcopy(document)
        run = next(
            node
            for node in mismatched["@graph"]
            if "mns:ExperimentRun" in node.get("@type", [])
        )
        run["@type"] = ["mns:Execution", "mns:SimulationRun"]
        run["mns:randomSeed"] = {
            "@value": 7,
            "@type": "xsd:nonNegativeInteger",
        }
        plan_path = tmp_path / "mismatched-plan.jsonld"
        plan_path.write_text(json.dumps(mismatched), encoding="utf-8")

        with pytest.raises(ValueError, match="expects 'simulator'"):
            execute_plan(
                plan_path,
                tmp_path / "output",
                backend_config=configuration_path,
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert server.commands == []
