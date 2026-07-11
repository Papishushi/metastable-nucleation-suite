import json
from pathlib import Path

import pytest

from metastable_suite.monte_carlo_power import (
    PowerEstimate,
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
        assert result.reference_error <= result.reference_tolerance
        assert result.estimate.power == pytest.approx(result.reference_power, abs=0.03)


def test_reference_drift_fails_even_when_estimate_is_inside_expected_range(tmp_path, monkeypatch):
    grid = {
        "schema_version": "1.0.0",
        "repetitions": 100,
        "reference_tolerance": 0.03,
        "cases": [
            {
                "id": "drift",
                "design": "proportion",
                "seed": 1,
                "parameters": {},
                "expected_range": [0.4, 0.6],
            }
        ],
    }
    grid_path = tmp_path / "grid.json"
    grid_path.write_text(json.dumps(grid), encoding="utf-8")
    estimate = PowerEstimate(
        design="two_proportions",
        sample_size=100,
        repetitions=100,
        rejection_count=50,
        power=0.5,
        standard_error=0.05,
        confidence_level=0.95,
        confidence_interval=(0.4, 0.6),
        parameters={},
    )

    monkeypatch.setattr(
        "metastable_suite.power_calibration._run_case",
        lambda case, repetitions: (estimate, 0.4),
    )

    result = run_benchmark_grid(grid_path)[0]

    assert result.estimate.power == pytest.approx(0.5)
    assert result.expected_range == (0.4, 0.6)
    assert result.reference_error == pytest.approx(0.1)
    assert not result.passed
