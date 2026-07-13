import json
from pathlib import Path

import pytest

from metastable_suite.campaigns import CampaignStateError
from metastable_suite.execution import BackendRegistry
from scripts.semantic_execute import execute_campaign_plan

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PLAN = ROOT / "ontology" / "examples" / "planned-campaign.jsonld"


def test_injected_registry_resume_requires_explicit_fingerprint(tmp_path):
    output_dir = tmp_path / "output"

    with pytest.raises(
        CampaignStateError,
        match="requires an explicit registry_fingerprint",
    ):
        execute_campaign_plan(
            CAMPAIGN_PLAN,
            output_dir,
            registry=BackendRegistry.default(),
            resume=True,
        )

    assert not output_dir.exists()


def test_changed_injected_registry_fingerprint_blocks_resume(tmp_path):
    output_dir = tmp_path / "output"

    first = execute_campaign_plan(
        CAMPAIGN_PLAN,
        output_dir,
        registry=BackendRegistry.default(),
        registry_fingerprint="sha256:first-registry",
        resume=False,
    )
    assert first.status == "Completed"

    context_path = output_dir / "e09-sequence.execution-context.json"
    persisted = json.loads(context_path.read_text(encoding="utf-8"))
    assert (
        persisted["backend_registry_fingerprint"]
        == "injected-registry:sha256:first-registry"
    )

    with pytest.raises(
        CampaignStateError,
        match="backend configuration changed",
    ):
        execute_campaign_plan(
            CAMPAIGN_PLAN,
            output_dir,
            registry=BackendRegistry.default(),
            registry_fingerprint="sha256:second-registry",
            resume=True,
        )

    unchanged = json.loads(context_path.read_text(encoding="utf-8"))
    assert unchanged == persisted


def test_unfingerprinted_injected_registry_can_only_start_fresh(tmp_path):
    output_dir = tmp_path / "output"

    result = execute_campaign_plan(
        CAMPAIGN_PLAN,
        output_dir,
        registry=BackendRegistry.default(),
        resume=False,
    )
    assert result.status == "Completed"

    context = json.loads(
        (output_dir / "e09-sequence.execution-context.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        context["backend_registry_fingerprint"]
        == "injected-registry-unfingerprinted-v1"
    )

    with pytest.raises(
        CampaignStateError,
        match="requires an explicit registry_fingerprint",
    ):
        execute_campaign_plan(
            CAMPAIGN_PLAN,
            output_dir,
            registry=BackendRegistry.default(),
            resume=True,
        )
