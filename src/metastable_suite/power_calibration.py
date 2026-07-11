from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .monte_carlo_power import (
    PowerEstimate,
    analytical_chsh_power,
    analytical_correlation_power,
    analytical_no_signalling_power,
    analytical_proportion_power,
    chsh_power,
    correlation_power,
    no_signalling_power,
    proportion_power,
)


@dataclass(frozen=True)
class CalibrationResult:
    case_id: str
    design: str
    estimate: PowerEstimate
    reference_power: float
    expected_range: tuple[float, float]
    reference_tolerance: float
    reference_error: float
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "design": self.design,
            "estimate": self.estimate.as_dict(),
            "reference_power": self.reference_power,
            "expected_range": list(self.expected_range),
            "reference_tolerance": self.reference_tolerance,
            "reference_error": self.reference_error,
            "passed": self.passed,
        }


def load_benchmark_grid(path: str | Path) -> dict[str, Any]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("schema_version") != "1.0.0":
        raise ValueError("unsupported benchmark schema version")
    if not isinstance(document.get("cases"), list) or not document["cases"]:
        raise ValueError("benchmark grid must contain cases")
    tolerance = float(document.get("reference_tolerance", 0.03))
    if tolerance < 0:
        raise ValueError("reference_tolerance must be non-negative")
    return document


def run_benchmark_grid(path: str | Path) -> list[CalibrationResult]:
    document = load_benchmark_grid(path)
    repetitions = int(document["repetitions"])
    default_tolerance = float(document.get("reference_tolerance", 0.03))
    results = []
    for case in document["cases"]:
        estimate, reference = _run_case(case, repetitions)
        lower, upper = map(float, case["expected_range"])
        tolerance = float(case.get("reference_tolerance", default_tolerance))
        if tolerance < 0:
            raise ValueError("reference_tolerance must be non-negative")
        reference_error = abs(estimate.power - reference)
        within_expected_range = lower <= estimate.power <= upper
        within_reference_tolerance = reference_error <= tolerance
        results.append(
            CalibrationResult(
                case_id=str(case["id"]),
                design=str(case["design"]),
                estimate=estimate,
                reference_power=reference,
                expected_range=(lower, upper),
                reference_tolerance=tolerance,
                reference_error=reference_error,
                passed=within_expected_range and within_reference_tolerance,
            )
        )
    return results


def _run_case(case: Mapping[str, Any], repetitions: int) -> tuple[PowerEstimate, float]:
    design = str(case["design"])
    seed = int(case["seed"])
    parameters = dict(case["parameters"])
    if design == "proportion":
        estimate = proportion_power(repetitions=repetitions, seed=seed, **parameters)
        reference = analytical_proportion_power(**parameters)
    elif design == "correlation":
        estimate = correlation_power(repetitions=repetitions, seed=seed, **parameters)
        reference = analytical_correlation_power(**parameters)
    elif design == "chsh":
        estimate = chsh_power(repetitions=repetitions, seed=seed, **parameters)
        reference = analytical_chsh_power(**parameters)
    elif design == "no-signalling":
        estimate = no_signalling_power(repetitions=repetitions, seed=seed, **parameters)
        reference = analytical_no_signalling_power(**parameters)
    else:
        raise ValueError(f"unknown benchmark design {design!r}")
    return estimate, reference
