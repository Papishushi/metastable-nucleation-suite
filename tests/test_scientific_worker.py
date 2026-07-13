from pathlib import Path

import pytest

from services.scientific_worker import (
    capability_manifest,
    canonical_request_id,
    resolve_artifacts_path,
    resolve_server_version,
    validate_request_envelope,
)


VALID_REQUEST = {
    "schema_version": "1.0.0",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "experiment_id": "contract-smoke",
    "submitted_at_utc": "2026-07-12T12:00:00Z",
}


def test_default_artifact_path_is_under_user_home():
    assert resolve_artifacts_path() == (
        Path.home() / ".metastable-nucleation-suite" / "artifacts"
    )


def test_configured_artifact_path_is_respected(tmp_path):
    assert resolve_artifacts_path(str(tmp_path)) == tmp_path


def test_configured_server_version_takes_precedence(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.2.0\n", encoding="utf-8")

    assert (
        resolve_server_version("0.3.0-rc.1", version_paths=(version_file,))
        == "0.3.0-rc.1"
    )


def test_server_version_falls_back_to_canonical_version_file(tmp_path):
    missing = tmp_path / "missing" / "VERSION"
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.2.0\n", encoding="utf-8")

    assert resolve_server_version("", version_paths=(missing, version_file)) == "0.2.0"


def test_server_version_uses_placeholder_only_without_configuration_or_file(tmp_path):
    assert (
        resolve_server_version(None, version_paths=(tmp_path / "missing",))
        == "0.0.0+unknown"
    )


def test_capability_manifest_advertises_required_active_capabilities():
    manifest = capability_manifest(generated_at_utc="2026-07-12T12:00:00Z")

    assert manifest["schema_version"] == "1.0.0"
    assert manifest["generated_at_utc"] == "2026-07-12T12:00:00Z"
    assert {
        capability["id"]
        for capability in manifest["capabilities"]
        if capability["status"] == "active"
    } >= {"experiments.execute.v1", "server.capabilities.v1"}
    assert {
        capability["status"] for capability in manifest["capabilities"]
    } <= {"active", "deprecated"}


def test_canonical_request_id_accepts_uuid():
    value = "11111111-1111-1111-1111-111111111111"

    assert canonical_request_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "../tmp/pwn",
        "not-a-uuid",
        "",
        None,
        123,
    ],
)
def test_canonical_request_id_rejects_unsafe_values(value):
    with pytest.raises(ValueError):
        canonical_request_id(value)


def test_validate_request_envelope_accepts_contract_fixture():
    assert validate_request_envelope(VALID_REQUEST) == VALID_REQUEST


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-07-12T12:00:00+00:00",
        "2026-07-12T12:00:00.123456+02:30",
        "2026-07-12t12:00:00z",
    ],
)
def test_validate_request_envelope_accepts_rfc3339_date_times(timestamp):
    envelope = {**VALID_REQUEST, "submitted_at_utc": timestamp}

    assert validate_request_envelope(envelope) == envelope


@pytest.mark.parametrize(
    "envelope",
    [
        None,
        {},
        {key: value for key, value in VALID_REQUEST.items() if key != "schema_version"},
        {**VALID_REQUEST, "schema_version": "2.0.0"},
        {**VALID_REQUEST, "submitted_at_utc": "not-a-timestamp"},
        {**VALID_REQUEST, "submitted_at_utc": "2026-07-12T12:00:00"},
        {**VALID_REQUEST, "submitted_at_utc": "2026-07-12 12:00:00+00:00"},
        {**VALID_REQUEST, "submitted_at_utc": "20260712T120000+00:00"},
        {**VALID_REQUEST, "submitted_at_utc": "2026-07-12T12:00:00+0000"},
        {**VALID_REQUEST, "experiment_id": ""},
        {**VALID_REQUEST, "experiment_id": "x" * 129},
        {**VALID_REQUEST, "unexpected": True},
    ],
)
def test_validate_request_envelope_rejects_malformed_contracts(envelope):
    with pytest.raises(ValueError):
        validate_request_envelope(envelope)
