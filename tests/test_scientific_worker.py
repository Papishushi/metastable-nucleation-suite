import pytest

from services.scientific_worker import canonical_request_id


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
