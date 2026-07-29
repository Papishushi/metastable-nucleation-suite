from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from metastable_suite.metastate_capacity import MetastateCapacityScenario


@pytest.mark.parametrize("cell_pitch_nm", [1e-200, 1e200])
def test_cell_pitch_must_produce_a_finite_positive_cell_volume(
    cell_pitch_nm: float,
) -> None:
    with pytest.raises(ValueError, match="non-finite or zero cell volume"):
        MetastateCapacityScenario(
            name="invalid-pitch",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=2000.0,
            cell_pitch_nm=cell_pitch_nm,
            distinguishable_states=2,
        )


def test_active_cell_mass_must_remain_finite_and_positive() -> None:
    with pytest.raises(ValueError, match="non-finite or zero active cell mass"):
        MetastateCapacityScenario(
            name="invalid-active-cell-mass",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=1e-308,
            cell_pitch_nm=1.0,
            distinguishable_states=2,
        )


def test_volumetric_cell_density_must_remain_finite() -> None:
    with pytest.raises(ValueError, match="non-finite volumetric cell density"):
        MetastateCapacityScenario(
            name="invalid-volumetric-density",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=2000.0,
            cell_pitch_nm=1e-94,
            distinguishable_states=2,
        )


def test_mass_specific_cell_density_must_remain_finite() -> None:
    with pytest.raises(ValueError, match="non-finite mass-specific cell density"):
        MetastateCapacityScenario(
            name="invalid-mass-specific-density",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=1e-20,
            cell_pitch_nm=1e-90,
            distinguishable_states=2,
        )


def test_full_rewrite_energy_per_total_volume_must_not_underflow() -> None:
    with pytest.raises(
        ValueError, match="full_rewrite_energy_j_per_total_m3 must be positive"
    ):
        MetastateCapacityScenario(
            name="invalid-total-rewrite-energy",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=1.0,
            cell_pitch_nm=1e111,
            distinguishable_states=2,
            write_energy_j_per_cell=1e-300,
        )


def test_full_rewrite_energy_per_active_mass_must_not_underflow() -> None:
    with pytest.raises(
        ValueError, match="full_rewrite_energy_j_per_active_kg must be positive"
    ):
        MetastateCapacityScenario(
            name="invalid-mass-rewrite-energy",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=1e20,
            cell_pitch_nm=1e102,
            distinguishable_states=2,
            write_energy_j_per_cell=1e-30,
        )


def test_cli_rejects_underflowing_cell_pitch_without_traceback() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "metastate_capacity.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--custom",
            "--active-material-density-kg-m3",
            "2000",
            "--cell-pitch-nm",
            "1e-200",
            "--states",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Estimation failed: cell_pitch_nm produces a non-finite or zero cell volume" in result.stderr
    assert "ZeroDivisionError" not in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_rejects_underflowing_active_cell_mass_without_traceback() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "metastate_capacity.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--custom",
            "--active-material-density-kg-m3",
            "1e-308",
            "--cell-pitch-nm",
            "1",
            "--states",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "non-finite or zero active cell mass" in result.stderr
    assert "ZeroDivisionError" not in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_rejects_reciprocal_cell_density_overflow_without_json_failure() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "metastate_capacity.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--custom",
            "--active-material-density-kg-m3",
            "2000",
            "--cell-pitch-nm",
            "1e-94",
            "--states",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "non-finite volumetric cell density" in result.stderr
    assert "JSON encoding failed" not in result.stderr
    assert "Infinity" not in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_rejects_rewrite_energy_underflow_without_reporting_free_energy() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "metastate_capacity.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--custom",
            "--active-material-density-kg-m3",
            "1",
            "--cell-pitch-nm",
            "1e111",
            "--states",
            "2",
            "--write-energy-j",
            "1e-300",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "full_rewrite_energy_j_per_total_m3 must be positive" in result.stderr
    assert '"full_rewrite_energy_j_per_total_m3": 0.0' not in result.stdout
    assert "JSON encoding failed" not in result.stderr
    assert "Traceback" not in result.stderr
