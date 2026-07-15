from __future__ import annotations

import math

import pytest

from metastable_suite.metastate_capacity import (
    BOLTZMANN_CONSTANT_J_PER_K,
    MetastateCapacityScenario,
    reference_scenarios,
)


def _scenario(**overrides: object) -> MetastateCapacityScenario:
    values: dict[str, object] = {
        "name": "test",
        "evidence_level": "engineering_scenario",
        "density_kg_m3": 2000.0,
        "pitch_nm": 100.0,
        "distinguishable_states": 16,
        "active_volume_fraction": 0.5,
        "coding_efficiency": 0.75,
        "write_energy_j_per_cell": 2e-12,
        "operation_energy_j_per_cell_event": 4e-15,
        "cell_event_rate_hz": 1e6,
        "active_utilization": 0.1,
        "operations_per_cell_event": 2.0,
        "multiplexing_factor": 4.0,
        "temperature_k": 300.0,
    }
    values.update(overrides)
    return MetastateCapacityScenario(**values)  # type: ignore[arg-type]


def test_information_density_uses_reliable_states_and_overheads() -> None:
    scenario = _scenario()
    assert scenario.bits_per_cell == 4.0
    assert scenario.cells_per_m3 == pytest.approx(5e20)
    assert scenario.raw_bits_per_m3 == pytest.approx(2e21)
    assert scenario.usable_bits_per_m3 == pytest.approx(1.5e21)
    assert scenario.usable_bits_per_kg == pytest.approx(7.5e17)
    assert scenario.usable_decimal_tb_per_kg == pytest.approx(93_750.0)


def test_energy_and_geometry_limits_are_reported_separately() -> None:
    scenario = _scenario()
    assert scenario.cells_per_kg == pytest.approx(2.5e17)
    assert scenario.full_rewrite_energy_j_per_kg == pytest.approx(5e5)
    assert scenario.operations_per_joule == pytest.approx(2e15)
    assert scenario.geometry_limited_operations_s_per_kg == pytest.approx(2e23)
    assert scenario.geometry_limited_dynamic_power_w_per_kg == pytest.approx(1e8)
    assert scenario.thermal_limited_operations_s_per_kg(1000.0) == pytest.approx(2e18)


def test_landauer_floor_is_explicitly_only_an_erasure_floor() -> None:
    scenario = _scenario()
    expected = BOLTZMANN_CONSTANT_J_PER_K * 300.0 * math.log(2.0)
    assert scenario.landauer_j_per_erased_bit == pytest.approx(expected)
    assert scenario.landauer_full_erase_j_per_kg == pytest.approx(scenario.usable_bits_per_kg * expected)


def test_reference_glass_density_matches_reported_equivalent() -> None:
    glass = reference_scenarios()[0]
    assert glass.name == "laser_written_fused_silica_equivalent"
    assert glass.usable_decimal_tb_per_kg == pytest.approx(916.6666667, rel=1e-6)
    assert glass.usable_bits_per_m3 == pytest.approx(1.613333333e19, rel=1e-6)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("density_kg_m3", 0.0),
        ("pitch_nm", 0.0),
        ("distinguishable_states", 1),
        ("active_volume_fraction", 0.0),
        ("coding_efficiency", 1.1),
        ("active_utilization", -0.1),
        ("temperature_k", 0.0),
    ],
)
def test_invalid_parameters_fail_closed(field: str, value: float | int) -> None:
    with pytest.raises(ValueError):
        _scenario(**{field: value})
