import pytest

from services.scientific_worker import canonical_request_id, validate_request_envelope


VALID_REQUEST = {
    "schema_version": "1.0.0",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "experiment_id": "contract-smoke",
    "submitted_at_utc": "2026-07-12T12:00:00Z",
}


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
    "envelope",
    [
        None,
        {},
        {key: value for key, value in VALID_REQUEST.items() if key != "schema_version"},
        {**VALID_REQUEST, "schema_version": "2.0.0"},
        {**VALID_REQUEST, "submitted_at_utc": "not-a-timestamp"},
        {**VALID_REQUEST, "submitted_at_utc": "2026-07-12T12:00:00"},
        {**VALID_REQUEST, "experiment_id": ""},
        {**VALID_REQUEST, "experiment_id": "x" * 129},
        {**VALID_REQUEST, "unexpected": True},
    ],
)
def test_validate_request_envelope_rejects_malformed_contracts(envelope):
    with pytest.raises(ValueError):
        validate_request_envelope(envelope)
