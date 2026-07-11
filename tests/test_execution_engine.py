import json
from pathlib import Path

from metastable_suite.datasets import read_events, sha256_file
from metastable_suite.execution import request_from_graph
from metastable_suite.semantic import MNS, load_abox, load_tbox, validate_abox
from scripts.semantic_execute import ABOX_SCHEMA, SHAPES, TBOX, execute_plan

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
    assert request.trial_count == 25
    assert request.random_seed == 7
    assert request.parameters["noise"] == 0.45


def test_semantic_plan_round_trip_creates_valid_abox_and_hashed_events(tmp_path):
    documents = execute_plan(PLAN, tmp_path)
    assert len(documents) == 1

    events_path = tmp_path / "planned-e09-demo.events.ndjson"
    abox_path = tmp_path / "planned-e09-demo.abox.jsonld"
    events = list(read_events(events_path))
    assert len(events) == 25
    assert all(event["specification_id"] == "E09" for event in events)
    assert all(event["backend_id"] == "reference-simulator" for event in events)

    document = json.loads(abox_path.read_text(encoding="utf-8"))
    dataset = next(node for node in document["@graph"] if node.get("@type") == "mns:Dataset")
    assert dataset["mns:eventCount"]["@value"] == 25
    assert dataset["mns:sha256"] == sha256_file(events_path)

    graph = load_abox(abox_path, ABOX_SCHEMA)
    outcome = validate_abox(graph, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text
