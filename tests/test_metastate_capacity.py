from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys

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
        "active_material_density_kg_m3": 2000.0,
        "cell_pitch_nm": 100.0,
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


def test_volume_and_active_mass_bases_are_separated() -> None:
    scenario = _scenario()
    assert scenario.bits_per_cell == 4.0
    assert scenario.cells_per_total_m3 == pytest.approx(5e20)
    assert scenario.active_material_mass_kg_per_total_m3 == pytest.approx(1000.0)
    assert scenario.cells_per_active_kg == pytest.approx(5e17)
    assert scenario.raw_bits_per_total_m3 == pytest.approx(2e21)
    assert scenario.usable_bits_per_total_m3 == pytest.approx(1.5e21)
    assert scenario.usable_bits_per_active_kg == pytest.approx(1.5e18)
    assert scenario.usable_decimal_tb_per_active_kg == pytest.approx(187_500.0)


def test_active_volume_fraction_changes_volume_not_active_mass_metrics() -> None:
    dense = _scenario(active_volume_fraction=1.0)
    sparse = _scenario(active_volume_fraction=0.2)

    assert sparse.usable_bits_per_total_m3 == pytest.approx(
        dense.usable_bits_per_total_m3 * 0.2
    )
    assert sparse.cells_per_active_kg == pytest.approx(dense.cells_per_active_kg)
    assert sparse.usable_bits_per_active_kg == pytest.approx(
        dense.usable_bits_per_active_kg
    )
    assert sparse.full_rewrite_energy_j_per_active_kg == pytest.approx(
        dense.full_rewrite_energy_j_per_active_kg
    )
    assert sparse.geometry_limited_operations_s_per_active_kg == pytest.approx(
        dense.geometry_limited_operations_s_per_active_kg
    )


def test_energy_and_geometry_limits_are_reported_for_both_bases() -> None:
    scenario = _scenario()
    assert scenario.full_rewrite_energy_j_per_total_m3 == pytest.approx(1e9)
    assert scenario.full_rewrite_energy_j_per_active_kg == pytest.approx(1e6)
    assert scenario.operations_per_joule == pytest.approx(2e15)
    assert scenario.geometry_limited_operations_s_per_total_m3 == pytest.approx(4e26)
    assert scenario.geometry_limited_operations_s_per_active_kg == pytest.approx(4e23)
    assert scenario.geometry_limited_dynamic_power_w_per_total_m3 == pytest.approx(2e11)
    assert scenario.geometry_limited_dynamic_power_w_per_active_kg == pytest.approx(2e8)
    assert scenario.thermal_limited_operations_s_per_active_kg(1000.0) == pytest.approx(2e18)


def test_unknown_physical_inputs_remain_null_in_strict_json() -> None:
    scenario = _scenario(
        write_energy_j_per_cell=None,
        operation_energy_j_per_cell_event=None,
        cell_event_rate_hz=None,
    )
    payload = scenario.as_dict(power_budget_w_per_active_kg=1000.0)

    assert payload["full_rewrite_energy_j_per_active_kg"] is None
    assert payload["geometry_limited_operations_s_per_active_kg"] is None
    assert payload["operations_per_joule"] is None
    assert payload["thermal_limited_operations_s_per_active_kg"] is None
    encoded = json.dumps(payload, allow_nan=False)
    assert json.loads(encoded)["operations_per_joule"] is None


def test_landauer_floor_is_explicitly_only_an_erasure_floor() -> None:
    scenario = _scenario()
    expected = BOLTZMANN_CONSTANT_J_PER_K * 300.0 * math.log(2.0)
    assert scenario.landauer_j_per_erased_bit == pytest.approx(expected)
    assert scenario.landauer_full_erase_j_per_active_kg == pytest.approx(
        scenario.usable_bits_per_active_kg * expected
    )


def test_reference_glass_density_matches_reported_equivalent() -> None:
    glass = reference_scenarios()[0]
    assert glass.name == "laser_written_fused_silica_equivalent"
    assert glass.usable_decimal_tb_per_active_kg == pytest.approx(916.6666667, rel=1e-6)
    assert glass.usable_bits_per_total_m3 == pytest.approx(1.613333333e19, rel=1e-6)
    assert glass.write_energy_j_per_cell is None
    assert glass.as_dict(1000.0)["thermal_limited_operations_s_per_active_kg"] is None


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "metastate_capacity.py"


def test_cli_custom_rejects_missing_mandatory_inputs() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--custom", "--states", "2"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--active-material-density-kg-m3" in result.stderr
    assert "--cell-pitch-nm" in result.stderr


def test_cli_emits_strict_json_with_null_unknowns() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--custom",
            "--active-material-density-kg-m3",
            "2200",
            "--cell-pitch-nm",
            "400",
            "--states",
            "2",
            "--power-budget-w-per-active-kg",
            "1000",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["operations_per_joule"] is None
    assert payload["thermal_limited_operations_s_per_active_kg"] is None
    assert "Infinity" not in result.stdout
    assert "NaN" not in result.stdout


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("active_material_density_kg_m3", 0.0),
        ("cell_pitch_nm", 0.0),
        ("distinguishable_states", 1),
        ("active_volume_fraction", 0.0),
        ("coding_efficiency", 1.1),
        ("active_utilization", -0.1),
        ("temperature_k", 0.0),
        ("write_energy_j_per_cell", 0.0),
        ("operation_energy_j_per_cell_event", float("nan")),
        ("cell_event_rate_hz", float("inf")),
    ],
)
def test_invalid_parameters_fail_closed(field: str, value: float | int) -> None:
    with pytest.raises(ValueError):
        _scenario(**{field: value})
