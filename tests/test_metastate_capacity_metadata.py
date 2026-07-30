from __future__ import annotations

import json

import pytest

from metastable_suite.metastate_capacity import MetastateCapacityScenario


def _scenario(**metadata: object) -> MetastateCapacityScenario:
    values: dict[str, object] = {
        "name": "metadata-test",
        "evidence_level": "engineering_scenario",
        "active_material_density_kg_m3": 2000.0,
        "cell_pitch_nm": 100.0,
        "distinguishable_states": 2,
        "notes": "serializable metadata",
    }
    values.update(metadata)
    return MetastateCapacityScenario(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), object(), 1])
def test_name_must_be_a_string(value: object) -> None:
    with pytest.raises(TypeError, match="name must be a string"):
        _scenario(name=value)


def test_empty_string_name_keeps_specific_validation_error() -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        _scenario(name="")


@pytest.mark.parametrize("value", [object(), float("nan"), ["measured"]])
def test_evidence_level_must_be_a_string(value: object) -> None:
    with pytest.raises(TypeError, match="evidence_level must be a string"):
        _scenario(evidence_level=value)


@pytest.mark.parametrize("value", [object(), float("nan"), {"note": "invalid"}])
def test_notes_must_be_a_string(value: object) -> None:
    with pytest.raises(TypeError, match="notes must be a string"):
        _scenario(notes=value)


def test_valid_metadata_survives_strict_json_round_trip() -> None:
    scenario = _scenario(
        name="strict-json-metadata",
        evidence_level="speculative_bound",
        notes="Assumptions remain explicit.",
    )

    encoded = json.dumps(scenario.as_dict(), allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["name"] == "strict-json-metadata"
    assert decoded["evidence_level"] == "speculative_bound"
    assert decoded["notes"] == "Assumptions remain explicit."
