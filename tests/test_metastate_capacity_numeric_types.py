from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction

import pytest

from metastable_suite.metastate_capacity import MetastateCapacityScenario


def _scenario(**overrides: object) -> MetastateCapacityScenario:
    values: dict[str, object] = {
        "name": "numeric-type-test",
        "evidence_level": "engineering_scenario",
        "active_material_density_kg_m3": 2000.0,
        "cell_pitch_nm": 100.0,
        "distinguishable_states": 2,
    }
    values.update(overrides)
    return MetastateCapacityScenario(**values)  # type: ignore[arg-type]


def test_supported_numeric_scalars_are_normalized_before_strict_json() -> None:
    scenario = _scenario(
        active_material_density_kg_m3=Decimal("2000"),
        cell_pitch_nm=Fraction(100, 1),
        active_volume_fraction=Fraction(1, 2),
        coding_efficiency=Decimal("0.75"),
        write_energy_j_per_cell=Fraction(1, 10**12),
        operation_energy_j_per_cell_event=Decimal("4e-15"),
        cell_event_rate_hz=Fraction(1_000_000, 1),
        active_utilization=Fraction(1, 10),
        operations_per_cell_event=Decimal("2"),
        multiplexing_factor=Fraction(4, 1),
        temperature_k=Decimal("300"),
    )

    payload = scenario.as_dict(Fraction(1000, 1))  # type: ignore[arg-type]
    continuous_inputs = (
        "active_material_density_kg_m3",
        "cell_pitch_nm",
        "active_volume_fraction",
        "coding_efficiency",
        "write_energy_j_per_cell",
        "operation_energy_j_per_cell_event",
        "cell_event_rate_hz",
        "active_utilization",
        "operations_per_cell_event",
        "multiplexing_factor",
        "temperature_k",
        "power_budget_w_per_active_kg",
    )

    assert all(isinstance(payload[name], float) for name in continuous_inputs)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["active_volume_fraction"] == 0.5
    assert decoded["coding_efficiency"] == 0.75
    assert decoded["power_budget_w_per_active_kg"] == 1000.0


def test_fractional_thermal_budget_returns_a_native_float() -> None:
    scenario = _scenario(operation_energy_j_per_cell_event=Fraction(1, 4))

    result = scenario.thermal_limited_operations_s_per_active_kg(Fraction(1, 2))  # type: ignore[arg-type]

    assert isinstance(result, float)
    assert result == pytest.approx(2.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("active_material_density_kg_m3", "2000"),
        ("active_volume_fraction", object()),
        ("cell_event_rate_hz", True),
    ],
)
def test_non_numeric_or_boolean_scalars_are_rejected(field: str, value: object) -> None:
    with pytest.raises(TypeError, match=rf"{field} must be a real number"):
        _scenario(**{field: value})


def test_unrepresentably_large_numeric_scalar_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="active_material_density_kg_m3 must be representable as a float",
    ):
        _scenario(active_material_density_kg_m3=10**10000)
