import copy
import json
from pathlib import Path

import pytest

from scripts.semantic_execute import main


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PLAN = ROOT / "ontology" / "examples" / "planned-campaign.jsonld"
RESOURCE = "https://w3id.org/metastable-nucleation-suite/resource/"


def _multi_campaign_plan(tmp_path: Path) -> Path:
    document = json.loads(CAMPAIGN_PLAN.read_text(encoding="utf-8"))
    graph = document["@graph"]
    campaign = next(
        node
        for node in graph
        if "mns:ExperimentalCampaign" in node.get("@type", [])
    )
    runs = [
        node
        for node in graph
        if "mns:Execution" in node.get("@type", [])
    ]

    second_campaign = copy.deepcopy(campaign)
    second_campaign["@id"] = RESOURCE + "campaign/e09-sequence-second"
    second_campaign["mns:identifier"] = "e09-sequence-second"
    second_campaign["mns:hasSubExecution"] = []

    replacement_ids = {
        run["@id"]: run["@id"] + "-second"
        for run in runs
    }
    second_runs = []
    for run in runs:
        copied = copy.deepcopy(run)
        copied["@id"] = replacement_ids[run["@id"]]
        copied["mns:identifier"] = run["mns:identifier"] + "-second"
        copied["mns:partOfSuiteRun"] = {"@id": second_campaign["@id"]}
        dependency = copied.get("mns:dependsOnExecution")
        if dependency is not None:
            copied["mns:dependsOnExecution"] = {
                "@id": replacement_ids[dependency["@id"]]
            }
        second_campaign["mns:hasSubExecution"].append({"@id": copied["@id"]})
        second_runs.append(copied)

    graph.extend([second_campaign, *second_runs])
    plan_path = tmp_path / "multiple-campaigns.jsonld"
    plan_path.write_text(json.dumps(document), encoding="utf-8")
    return plan_path


def test_cli_requires_campaign_iri_when_plan_contains_multiple_campaigns(tmp_path):
    plan_path = _multi_campaign_plan(tmp_path)
    output_dir = tmp_path / "output"

    with pytest.raises(
        ValueError,
        match="select exactly one campaign with --campaign-iri",
    ):
        main([plan_path.as_posix(), output_dir.as_posix()])

    assert not output_dir.exists()
