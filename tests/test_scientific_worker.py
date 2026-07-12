import pytest

from services.scientific_worker import (
    capability_manifest,
    canonical_request_id,
    validate_request_envelope,
)


VALID_REQUEST = {
    "schema_version": "1.0.0",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "experiment_id": "contract-smoke",
    "submitted_at_utc": "2026-07-12T12:00:00Z",
}


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
