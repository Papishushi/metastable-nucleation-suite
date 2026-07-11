from pathlib import Path

import pytest

from metastable_suite.monte_carlo_power import (
    analytical_correlation_power,
    analytical_proportion_power,
    wilson_interval,
)
from metastable_suite.power_calibration import run_benchmark_grid

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / "benchmarks" / "power-calibration.json"


def test_wilson_interval_handles_boundary_counts():
    assert wilson_interval(0, 100)[0] == 0.0
    assert wilson_interval(100, 100)[1] == 1.0


def test_analytical_power_increases_with_information():
    assert analytical_proportion_power(300, 0.5, 0.6, 0.05) > analytical_proportion_power(
        100, 0.5, 0.6, 0.05
    )
    assert analytical_correlation_power(200, 0.2, 0.05) > analytical_correlation_power(
        100, 0.2, 0.05
    )


def test_benchmark_grid_stays_within_expected_ranges():
    results = run_benchmark_grid(GRID)
    assert {result.design for result in results} == {
        "proportion",
        "correlation",
        "chsh",
        "no-signalling",
    }
    assert all(result.passed for result in results)
    for result in results:
        low, high = result.estimate.confidence_interval
        assert low <= result.estimate.power <= high
        assert result.estimate.power == pytest.approx(result.reference_power, abs=0.03)
