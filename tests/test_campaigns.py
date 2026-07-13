import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from rdflib import Graph, URIRef

from metastable_suite.campaigns import (
    CampaignCycleError,
    CampaignStateError,
    execute_campaign,
)
from metastable_suite.execution import BackendRegistry
from metastable_suite.hardware import ExperimentalBackend, TrialResponse
from metastable_suite.semantic import load_abox, load_tbox, validate_abox
from scripts.semantic_execute import (
    ABOX_SCHEMA,
    EVENT_SCHEMA,
    SHAPES,
    TBOX,
    main,
)

RESOURCE = "https://w3id.org/metastable-nucleation-suite/resource/"
CAMPAIGN = URIRef(RESOURCE + "campaign/test-campaign")
ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PLAN = ROOT / "ontology" / "examples" / "planned-campaign.jsonld"
BASELINE_RUN = RESOURCE + "run/e09-baseline"


def campaign_graph(run_ids, dependencies=None, policy="fail-fast"):
    dependencies = dependencies or {}
    document = {
        "@context": {
            "mns": "https://w3id.org/metastable-nucleation-suite/ontology#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": [
            {
                "@id": RESOURCE + "specification/E09",
                "@type": ["mns:ExperimentSpecification", "mns:SimulationSpecification"],
                "mns:identifier": "E09",
            },
            {
                "@id": RESOURCE + "backend/test-backend",
                "@type": ["mns:Agent", "mns:HardwareBackend", "mns:SimulatorBackend"],
                "mns:identifier": "test-backend",
            },
            {
                "@id": str(CAMPAIGN),
                "@type": ["mns:SuiteRun", "mns:ExperimentalCampaign"],
                "mns:identifier": "test-campaign",
                "mns:failurePolicy": policy,
                "mns:hasSubExecution": [
                    {"@id": RESOURCE + "run/" + run_id} for run_id in run_ids
                ],
            },
        ],
    }
    for index, run_id in enumerate(run_ids):
        run = {
            "@id": RESOURCE + "run/" + run_id,
            "@type": ["mns:Execution", "mns:SimulationRun"],
            "mns:identifier": run_id,
            "mns:executesSpecification": {"@id": RESOURCE + "specification/E09"},
            "mns:usesBackend": {"@id": RESOURCE + "backend/test-backend"},
            "mns:hasExecutionStatus": {"@id": "mns:Planned"},
            "mns:trialCount": {"@value": 1, "@type": "xsd:positiveInteger"},
            "mns:randomSeed": {"@value": index + 1, "@type": "xsd:nonNegativeInteger"},
            "mns:partOfSuiteRun": {"@id": str(CAMPAIGN)},
        }
        if dependencies.get(run_id):
            run["mns:dependsOnExecution"] = [
                {"@id": RESOURCE + "run/" + required}
                for required in dependencies[run_id]
            ]
        document["@graph"].append(run)
    graph = Graph()
    graph.parse(data=json.dumps(document), format="json-ld")
    return graph


class RecordingBackend(ExperimentalBackend):
    firmware_version = "test-1"

    def __init__(self, run_id, activations, failures):
        self.run_id = run_id
        self.activations = activations
        self.failures = failures
        self.activations.append(run_id)

    def prepare(self, specification_id, parameters):
        if self.run_id in self.failures:
            raise RuntimeError(f"forced failure for {self.run_id}")

    def calibrate(self):
        return {"calibration_ok": True}

    def execute_trial(self, request):
        return TrialResponse(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            outcome={"run_id": request.run_id},
        )

    def reset(self):
        return {"reset_ok": True}

    def collect_diagnostics(self):
        return {"run_id": self.run_id}

    def close(self):
        pass


def registry(activations, failures=()):
    result = BackendRegistry()
    failed = set(failures)
    result.register(
        "test-backend",
        lambda request: RecordingBackend(request.run_id, activations, failed),
        backend_kind="simulator",
    )
    return result


def event_schema():
    return json.loads(EVENT_SCHEMA.read_text(encoding="utf-8"))


def semantic_artifact_validator(path):
    try:
        completed = load_abox(path, ABOX_SCHEMA)
        return validate_abox(completed, SHAPES, load_tbox(TBOX)).conforms
    except Exception:
        return False


def test_campaign_executes_dependencies_in_topological_order(tmp_path):
    graph = campaign_graph(["second", "first"], {"second": ["first"]})
    activations = []

    result = execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry(activations),
        artifact_validator=semantic_artifact_validator,
    )

    assert activations == ["first", "second"]
    assert result.status == "Completed"
    assert result.run_statuses == {"first": "Completed", "second": "Completed"}


def test_cycle_is_rejected_before_any_backend_is_created(tmp_path):
    graph = campaign_graph(["a", "b"], {"a": ["b"], "b": ["a"]})
    activations = []

    with pytest.raises(CampaignCycleError, match="cycle"):
        execute_campaign(graph, CAMPAIGN, tmp_path, event_schema(), registry(activations))
    assert activations == []
    assert not any(tmp_path.iterdir())


def test_continue_on_error_invalidates_dependents_and_runs_independent_work(tmp_path):
    graph = campaign_graph(
        ["a", "b", "c"],
        {"b": ["a"]},
        policy="continue-on-error",
    )
    activations = []

    result = execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry(activations, failures={"a"}),
        artifact_validator=semantic_artifact_validator,
    )

    assert activations == ["a", "c"]
    assert result.run_statuses == {
        "a": "Failed",
        "b": "Invalidated",
        "c": "Completed",
    }


def test_resume_does_not_repeat_completed_runs(tmp_path):
    graph = campaign_graph(["a", "b"], {"b": ["a"]})
    first_activations = []
    first = execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry(first_activations, failures={"b"}),
        artifact_validator=semantic_artifact_validator,
    )
    assert first.status == "Failed"
    assert first_activations == ["a", "b"]

    resumed_activations = []
    resumed = execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry(resumed_activations),
        artifact_validator=semantic_artifact_validator,
    )

    assert resumed.status == "Completed"
    assert resumed_activations == ["b"]
    state = json.loads((tmp_path / "test-campaign.campaign-state.json").read_text())
    assert state["runs"][RESOURCE + "run/a"]["attempts"] == 1
    assert state["runs"][RESOURCE + "run/b"]["attempts"] == 2


def test_resume_rejects_semantically_corrupt_completed_abox(tmp_path):
    graph = campaign_graph(["a", "b"], {"b": ["a"]})
    execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry([], failures={"b"}),
        artifact_validator=semantic_artifact_validator,
    )

    abox_path = tmp_path / "a.abox.jsonld"
    document = json.loads(abox_path.read_text(encoding="utf-8"))
    run_node = next(
        node
        for node in document["@graph"]
        if "mns:Execution" in node.get("@type", [])
    )
    run_node.pop("mns:hasResult")
    abox_path.write_text(json.dumps(document), encoding="utf-8")

    resumed_activations = []
    with pytest.raises(CampaignStateError, match="missing or corrupt"):
        execute_campaign(
            graph,
            CAMPAIGN,
            tmp_path,
            event_schema(),
            registry(resumed_activations),
            artifact_validator=semantic_artifact_validator,
        )

    assert resumed_activations == []


def test_campaign_result_abox_is_shacl_valid(tmp_path):
    graph = campaign_graph(["a", "b"], {"b": ["a"]})
    result = execute_campaign(
        graph,
        CAMPAIGN,
        tmp_path,
        event_schema(),
        registry([]),
        artifact_validator=semantic_artifact_validator,
    )

    completed = load_abox(result.abox_path, ABOX_SCHEMA)
    validation = validate_abox(completed, SHAPES, load_tbox(TBOX))

    assert validation.conforms, validation.report_text


def test_run_iri_takes_precedence_when_plan_contains_campaign(tmp_path):
    exit_code = main(
        [
            CAMPAIGN_PLAN.as_posix(),
            tmp_path.as_posix(),
            "--run-iri",
            BASELINE_RUN,
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "e09-baseline.abox.jsonld").exists()
    assert (tmp_path / "e09-baseline.events.ndjson").exists()
    assert not (tmp_path / "e09-confirmation.abox.jsonld").exists()
    assert not (tmp_path / "e09-sequence.campaign-state.json").exists()


def test_run_iri_rejects_campaign_only_options(tmp_path):
    with pytest.raises(SystemExit):
        main(
            [
                CAMPAIGN_PLAN.as_posix(),
                tmp_path.as_posix(),
                "--run-iri",
                BASELINE_RUN,
                "--failure-policy",
                "fail-fast",
            ]
        )
