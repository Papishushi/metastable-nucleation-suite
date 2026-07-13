import json
from pathlib import Path

import pytest

from metastable_suite.datasets import read_events, sha256_file
from metastable_suite.execution import (
    BackendRegistry,
    ExecutionRequest,
    execute_request,
    load_event_schema,
    request_from_graph,
)
from metastable_suite.hardware import SimulatorBackend
from metastable_suite.semantic import MNS, load_abox, load_tbox, validate_abox
from scripts.semantic_execute import (
    ABOX_SCHEMA,
    EVENT_SCHEMA,
    SHAPES,
    TBOX,
    execute_plan,
)

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "ontology" / "examples" / "planned-e09.jsonld"


def test_planned_abox_is_valid_and_materializes_request():
    graph = load_abox(PLAN, ABOX_SCHEMA)
    outcome = validate_abox(graph, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text

    run = next(graph.subjects(MNS.hasExecutionStatus, MNS.Planned))
    request = request_from_graph(graph, run)
    assert request.specification_id == "E09"
    assert request.backend_id == "reference-simulator"
    assert request.execution_kind == "simulator"
    assert request.trial_count == 25
    assert request.random_seed == 7
    assert request.parameters["noise"] == 0.45


def test_simulator_default_seed_is_normalized_before_factory(tmp_path):
    observed_seeds = []
    registry = BackendRegistry()

    def factory(request):
        observed_seeds.append(request.random_seed)
        return SimulatorBackend(seed=request.random_seed)

    registry.register(
        "seeded-simulator",
        factory,
        backend_kind="simulator",
    )
    request = ExecutionRequest(
        run_id="default-seed",
        specification_id="E09",
        backend_id="seeded-simulator",
        trial_count=1,
        parameters={},
        execution_kind="simulator",
    )

    result = execute_request(
        request,
        tmp_path,
        load_event_schema(EVENT_SCHEMA),
        registry,
    )

    assert observed_seeds == [0]
    assert result.random_seed == 0


def test_semantic_request_rejects_untyped_registry_before_factory(tmp_path):
    activations = []
    registry = BackendRegistry()

    def factory(request):
        activations.append(request.run_id)
        return SimulatorBackend(seed=0)

    registry.register("legacy-untyped", factory)
    request = ExecutionRequest(
        run_id="semantic-kind-guard",
        specification_id="E09",
        backend_id="legacy-untyped",
        trial_count=1,
        parameters={},
        execution_kind="simulator",
    )

    with pytest.raises(ValueError, match="explicit backend_kind"):
        execute_request(
            request,
            tmp_path,
            load_event_schema(EVENT_SCHEMA),
            registry,
        )

    assert activations == []
    assert not any(tmp_path.iterdir())


def test_untyped_direct_request_uses_backend_declared_kind(tmp_path):
    registry = BackendRegistry()
    registry.register(
        "direct-simulator",
        lambda request: SimulatorBackend(seed=request.random_seed or 0),
    )
    request = ExecutionRequest(
        run_id="direct-untyped",
        specification_id="E09",
        backend_id="direct-simulator",
        trial_count=1,
        parameters={},
        random_seed=9,
    )

    result = execute_request(
        request,
        tmp_path,
        load_event_schema(EVENT_SCHEMA),
        registry,
    )

    assert result.backend_kind == "simulator"
    assert result.random_seed == 9


def test_semantic_plan_round_trip_creates_valid_abox_and_hashed_events(
    tmp_path,
):
    documents = execute_plan(PLAN, tmp_path)
    assert len(documents) == 1

    events_path = tmp_path / "planned-e09-demo.events.ndjson"
    abox_path = tmp_path / "planned-e09-demo.abox.jsonld"
    events = list(read_events(events_path))
    assert len(events) == 25
    assert all(event["specification_id"] == "E09" for event in events)
    assert all(
        event["backend_id"] == "reference-simulator" for event in events
    )

    document = json.loads(abox_path.read_text(encoding="utf-8"))
    run = next(
        node
        for node in document["@graph"]
        if node.get("mns:identifier") == "planned-e09-demo"
    )
    backend = next(
        node
        for node in document["@graph"]
        if node.get("mns:identifier") == "reference-simulator"
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

    assert "mns:SimulationRun" in run["@type"]
    assert "mns:ExperimentRun" not in run["@type"]
    assert "mns:ExecutionBackend" in backend["@type"]
    assert "mns:SimulatorBackend" in backend["@type"]
    assert "mns:HardwareBackend" not in backend["@type"]
    assert "mns:SimulationSpecification" in specification["@type"]
    assert "mns:PhysicalExperimentSpecification" not in specification["@type"]
    assert dataset["mns:eventCount"]["@value"] == 25
    assert dataset["mns:sha256"] == sha256_file(events_path)

    graph = load_abox(abox_path, ABOX_SCHEMA)
    outcome = validate_abox(graph, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text


def test_path_traversal_run_identifier_is_rejected_before_writing(tmp_path):
    document = json.loads(PLAN.read_text(encoding="utf-8"))
    run = next(
        node
        for node in document["@graph"]
        if "mns:SimulationRun" in node.get("@type", [])
    )
    run["mns:identifier"] = "../outside/run"
    malicious_plan = tmp_path / "malicious-plan.jsonld"
    malicious_plan.write_text(json.dumps(document), encoding="utf-8")
    output_dir = tmp_path / "output"

    with pytest.raises(ValueError):
        execute_plan(malicious_plan, output_dir)

    assert not (tmp_path / "outside").exists()
    assert not output_dir.exists() or not any(output_dir.rglob("*"))
