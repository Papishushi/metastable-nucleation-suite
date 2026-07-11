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
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "design": self.design,
            "estimate": self.estimate.as_dict(),
            "reference_power": self.reference_power,
            "expected_range": list(self.expected_range),
            "passed": self.passed,
        }


def load_benchmark_grid(path: str | Path) -> dict[str, Any]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("schema_version") != "1.0.0":
        raise ValueError("unsupported benchmark schema version")
    if not isinstance(document.get("cases"), list) or not document["cases"]:
        raise ValueError("benchmark grid must contain cases")
    return document


def run_benchmark_grid(path: str | Path) -> list[CalibrationResult]:
    document = load_benchmark_grid(path)
    repetitions = int(document["repetitions"])
    results = []
    for case in document["cases"]:
        estimate, reference = _run_case(case, repetitions)
        lower, upper = map(float, case["expected_range"])
        results.append(
            CalibrationResult(
                case_id=str(case["id"]),
                design=str(case["design"]),
                estimate=estimate,
                reference_power=reference,
                expected_range=(lower, upper),
                passed=lower <= estimate.power <= upper,
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
