import json

import pytest

from metastable_suite.campaigns import CampaignStateError
from scripts.semantic_execute import _guard_campaign_execution_context


def test_campaign_resume_rejects_changed_backend_configuration(tmp_path):
    context_path = _guard_campaign_execution_context(
        tmp_path,
        "hardware-campaign",
        "backend-config-sha256:first",
        resume=True,
    )
    (tmp_path / "hardware-campaign.campaign-state.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        CampaignStateError,
        match="backend configuration changed",
    ):
        _guard_campaign_execution_context(
            tmp_path,
            "hardware-campaign",
            "backend-config-sha256:second",
            resume=True,
        )

    persisted = json.loads(context_path.read_text(encoding="utf-8"))
    assert (
        persisted["backend_registry_fingerprint"]
        == "backend-config-sha256:first"
    )


def test_no_resume_replaces_backend_execution_context(tmp_path):
    context_path = _guard_campaign_execution_context(
        tmp_path,
        "hardware-campaign",
        "backend-config-sha256:first",
        resume=True,
    )

    replaced = _guard_campaign_execution_context(
        tmp_path,
        "hardware-campaign",
        "backend-config-sha256:second",
        resume=False,
    )

    assert replaced == context_path
    persisted = json.loads(context_path.read_text(encoding="utf-8"))
    assert (
        persisted["backend_registry_fingerprint"]
        == "backend-config-sha256:second"
    )


def test_resume_rejects_legacy_state_without_execution_context(tmp_path):
    (tmp_path / "hardware-campaign.campaign-state.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    with pytest.raises(CampaignStateError, match="execution context is missing"):
        _guard_campaign_execution_context(
            tmp_path,
            "hardware-campaign",
            "backend-config-sha256:first",
            resume=True,
        )


def test_resume_rejects_orphan_artifacts_without_execution_context(tmp_path):
    (tmp_path / "orphan-run.abox.jsonld").write_text(
        "{}\n",
        encoding="utf-8",
    )
    (tmp_path / "orphan-run.events.ndjson").write_text(
        "{}\n",
        encoding="utf-8",
    )

    with pytest.raises(CampaignStateError, match="execution context is missing"):
        _guard_campaign_execution_context(
            tmp_path,
            "hardware-campaign",
            "backend-config-sha256:first",
            resume=True,
            run_ids=("orphan-run",),
        )


def test_no_resume_accepts_orphan_artifacts_and_writes_current_context(tmp_path):
    (tmp_path / "orphan-run.abox.jsonld").write_text(
        "{}\n",
        encoding="utf-8",
    )
    (tmp_path / "orphan-run.events.ndjson").write_text(
        "{}\n",
        encoding="utf-8",
    )

    context_path = _guard_campaign_execution_context(
        tmp_path,
        "hardware-campaign",
        "backend-config-sha256:current",
        resume=False,
        run_ids=("orphan-run",),
    )

    persisted = json.loads(context_path.read_text(encoding="utf-8"))
    assert (
        persisted["backend_registry_fingerprint"]
        == "backend-config-sha256:current"
    )


def test_single_orphan_file_does_not_trigger_reuse_guard(tmp_path):
    (tmp_path / "orphan-run.abox.jsonld").write_text(
        "{}\n",
        encoding="utf-8",
    )

    context_path = _guard_campaign_execution_context(
        tmp_path,
        "hardware-campaign",
        "backend-config-sha256:first",
        resume=True,
        run_ids=("orphan-run",),
    )

    assert context_path.exists()
