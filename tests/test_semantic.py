import json
from pathlib import Path

from rdflib import RDF

from metastable_suite.report import build_report
from metastable_suite.semantic import MNS, execute_query, load_abox, load_tbox, validate_abox
from scripts.semantic_graph import RESULT_SPECIFICATIONS, report_to_abox

ROOT = Path(__file__).resolve().parents[1]
TBOX = ROOT / "ontology" / "tbox.ttl"
SHAPES = ROOT / "ontology" / "abox-shapes.ttl"
SCHEMA = ROOT / "ontology" / "abox.schema.json"
EXAMPLE = ROOT / "ontology" / "examples" / "reference-run.jsonld"


def test_example_abox_conforms_to_json_schema_and_shacl():
    abox = load_abox(EXAMPLE, SCHEMA)
    outcome = validate_abox(abox, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text


def test_completed_run_query_returns_reference_run():
    abox = load_abox(EXAMPLE, SCHEMA)
    query = (ROOT / "ontology" / "queries" / "completed-runs.rq").read_text(encoding="utf-8")
    rows = execute_query(abox, query)
    assert len(rows) == 1
    assert rows[0]["identifier"] == "reference-seed-7"
    assert rows[0]["seed"] == "7"


def test_report_is_partitioned_into_valid_per_specification_runs(tmp_path):
    report = build_report(10_000, 7)
    document = report_to_abox(report, "pytest-seed-7")
    target = tmp_path / "run.jsonld"
    target.write_text(json.dumps(document), encoding="utf-8")

    abox = load_abox(target, SCHEMA)
    outcome = validate_abox(abox, SHAPES, load_tbox(TBOX))
    assert outcome.conforms, outcome.report_text

    expected_specs = set(RESULT_SPECIFICATIONS.values())
    executions = set(abox.subjects(RDF.type, MNS.SimulationRun))
    assert len(executions) == len(expected_specs)

    for execution in executions:
        specifications = list(abox.objects(execution, MNS.executesSpecification))
        assert len(specifications) == 1
        specification_id = str(specifications[0]).rsplit("/", 1)[-1]
        assert specification_id in expected_specs

    total_results = sum(
        len(list(abox.objects(execution, MNS.hasResult)))
        for execution in executions
    )
    assert total_results == len(report["known_science_expectations"])


def test_json_results_use_json_ld_json_literals(tmp_path):
    report = build_report(10_000, 7)
    document = report_to_abox(report, "json-literal-test")
    json_values = [
        node["mns:resultJson"]
        for node in document["@graph"]
        if "mns:resultJson" in node
    ]
    assert json_values
    assert all(value["@type"] == "@json" for value in json_values)

    target = tmp_path / "json-literals.jsonld"
    target.write_text(json.dumps(document), encoding="utf-8")
    graph = load_abox(target, SCHEMA)
    assert len(graph) > 0


def test_materializer_rejects_reports_without_execution_timestamps():
    report = build_report(10_000, 7)
    del report["provenance"]["execution_started_at_utc"]
    try:
        report_to_abox(report, "missing-time")
    except ValueError as exc:
        assert "start and end timestamps" in str(exc)
    else:
        raise AssertionError("materializer accepted provenance without a real start timestamp")


def test_simulation_without_seed_violates_shacl(tmp_path):
    document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    run = next(
        node
        for node in document["@graph"]
        if "mns:SimulationRun" in node.get("@type", [])
    )
    del run["randomSeed"]
    target = tmp_path / "invalid.jsonld"
    target.write_text(json.dumps(document), encoding="utf-8")

    abox = load_abox(target, SCHEMA)
    outcome = validate_abox(abox, SHAPES, load_tbox(TBOX))
    assert not outcome.conforms
    assert "randomSeed" in outcome.report_text
