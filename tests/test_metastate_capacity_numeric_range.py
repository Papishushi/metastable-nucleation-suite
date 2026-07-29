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
