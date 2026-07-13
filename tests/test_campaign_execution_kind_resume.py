from pathlib import Path

import pytest
from rdflib import RDF

from metastable_suite.campaigns import CampaignStateError, execute_campaign, find_campaigns
from metastable_suite.execution import MNS, load_event_schema
from metastable_suite.semantic import load_abox
from scripts.semantic_execute import ABOX_SCHEMA, EVENT_SCHEMA

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PLAN = ROOT / "ontology" / "examples" / "planned-campaign.jsonld"


def _load_campaign():
    graph = load_abox(CAMPAIGN_PLAN, ABOX_SCHEMA)
    campaign = find_campaigns(graph)[0]
    return graph, campaign


def _change_runs_to_hardware(graph):
    simulation_runs = list(graph.subjects(RDF.type, MNS.SimulationRun))
    for run in simulation_runs:
        graph.remove((run, RDF.type, MNS.SimulationRun))
        graph.add((run, RDF.type, MNS.ExperimentRun))
        graph.remove((run, MNS.randomSeed, None))


def test_campaign_state_fingerprint_includes_execution_kind(tmp_path):
    graph, campaign = _load_campaign()
    schema = load_event_schema(EVENT_SCHEMA)
    first = execute_campaign(graph, campaign, tmp_path, schema)
    assert first.status == "Completed"

    _change_runs_to_hardware(graph)

    with pytest.raises(CampaignStateError, match="campaign plan changed"):
        execute_campaign(graph, campaign, tmp_path, schema, resume=True)


def test_orphaned_simulation_artifacts_are_not_reused_as_hardware(tmp_path):
    graph, campaign = _load_campaign()
    schema = load_event_schema(EVENT_SCHEMA)
    first = execute_campaign(graph, campaign, tmp_path, schema)
    assert first.status == "Completed"

    Path(first.state_path).unlink()
    _change_runs_to_hardware(graph)

    second = execute_campaign(graph, campaign, tmp_path, schema, resume=True)

    assert second.status == "Failed"
    assert second.run_statuses["e09-baseline"] == "Failed"
