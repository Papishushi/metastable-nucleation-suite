#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


EXPECTED_KEYS = {
    "seed_odds_ratio_gt_1",
    "classical_common_cause_correlation",
    "independent_optical_nodes_correlation_near_0",
    "local_chsh_le_2",
    "quantum_entangled_chsh_near_2sqrt2V",
    "quantum_no_signalling_deltas_near_0",
    "optical_metastate_positive_fraction",
    "optical_mean_commit_step",
}
CORRELATION_KEYS = {"E00", "E01", "E10", "E11"}
NO_SIGNALLING_KEYS = {"A_x0", "A_x1", "B_y0", "B_y1"}


def _finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _chsh_standard_error(correlations: dict[str, float], trials: int) -> float:
    samples_per_setting = max(trials / 4.0, 1.0)
    variance = sum(max(0.0, 1.0 - value**2) / samples_per_setting for value in correlations.values())
    return math.sqrt(variance)


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    trials = report.get("trials")
    seed = report.get("seed")
    values = report.get("known_science_expectations")

    if not isinstance(trials, int) or isinstance(trials, bool) or trials < 10_000:
        errors.append("trials must be an integer >= 10,000")
        return errors
    if not isinstance(seed, int) or isinstance(seed, bool):
        errors.append("seed must be an integer")
    if not isinstance(values, dict):
        errors.append("known_science_expectations must be an object")
        return errors

    missing = EXPECTED_KEYS - values.keys()
    extra = values.keys() - EXPECTED_KEYS
    if missing:
        errors.append(f"missing report fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected report fields: {sorted(extra)}")
    if missing:
        return errors

    odds_ratio = values["seed_odds_ratio_gt_1"]
    if not _finite_number(odds_ratio) or not 1.5 <= odds_ratio <= 4.5:
        errors.append(f"seed odds ratio outside expected benchmark range: {odds_ratio}")

    common_cause = values["classical_common_cause_correlation"]
    if not _finite_number(common_cause) or not 0.10 <= common_cause <= 0.40:
        errors.append(f"classical common-cause correlation outside expected range: {common_cause}")

    independent = values["independent_optical_nodes_correlation_near_0"]
    independent_limit = max(0.02, 6.0 / math.sqrt(min(trials, 80_000)))
    if not _finite_number(independent) or abs(independent) > independent_limit:
        errors.append(
            "independent optical-node correlation exceeds finite-sample limit: "
            f"|{independent}| > {independent_limit:.5f}"
        )

    local = values["local_chsh_le_2"]
    if not isinstance(local, dict) or not _finite_number(local.get("S")) or not isinstance(local.get("E"), dict):
        errors.append("local CHSH result has an invalid structure")
    elif set(local["E"]) != CORRELATION_KEYS or not all(_finite_number(v) for v in local["E"].values()):
        errors.append("local CHSH correlations are invalid")
    else:
        local_se = _chsh_standard_error(local["E"], trials)
        local_limit = 2.0 + 5.0 * local_se
        if not 1.75 <= local["S"] <= local_limit:
            errors.append(f"local CHSH S outside expected range: {local['S']:.5f}, limit={local_limit:.5f}")

    quantum = values["quantum_entangled_chsh_near_2sqrt2V"]
    if not isinstance(quantum, dict) or not _finite_number(quantum.get("S")) or not isinstance(quantum.get("E"), dict):
        errors.append("quantum CHSH result has an invalid structure")
    elif set(quantum["E"]) != CORRELATION_KEYS or not all(_finite_number(v) for v in quantum["E"].values()):
        errors.append("quantum CHSH correlations are invalid")
    else:
        quantum_se = _chsh_standard_error(quantum["E"], trials)
        expected_quantum = 2.0 * math.sqrt(2.0) * 0.98
        tolerance = max(0.08, 5.0 * quantum_se)
        if quantum["S"] <= 2.0 + 5.0 * quantum_se:
            errors.append(f"quantum benchmark does not clearly violate CHSH: S={quantum['S']:.5f}")
        if abs(quantum["S"] - expected_quantum) > tolerance:
            errors.append(
                "quantum CHSH benchmark differs from 2sqrt(2)V beyond tolerance: "
                f"S={quantum['S']:.5f}, expected={expected_quantum:.5f}, tolerance={tolerance:.5f}"
            )

    no_signalling = values["quantum_no_signalling_deltas_near_0"]
    no_signalling_limit = max(0.02, 5.0 * math.sqrt(2.0 / trials))
    if not isinstance(no_signalling, dict) or set(no_signalling) != NO_SIGNALLING_KEYS:
        errors.append("no-signalling deltas have an invalid structure")
    elif not all(_finite_number(v) for v in no_signalling.values()):
        errors.append("no-signalling deltas must be finite numbers")
    elif max(abs(value) for value in no_signalling.values()) > no_signalling_limit:
        errors.append(f"no-signalling delta exceeds limit {no_signalling_limit:.5f}")

    positive_fraction = values["optical_metastate_positive_fraction"]
    optical_trials = min(trials, 100_000)
    balance_limit = 5.0 * math.sqrt(0.25 / optical_trials)
    if not _finite_number(positive_fraction) or abs(positive_fraction - 0.5) > balance_limit:
        errors.append(
            "optical metastate balance exceeds finite-sample limit: "
            f"fraction={positive_fraction}, limit={balance_limit:.5f}"
        )

    mean_commit = values["optical_mean_commit_step"]
    if not _finite_number(mean_commit) or not 1.0 <= mean_commit <= 499.0:
        errors.append(f"optical mean commit step is invalid: {mean_commit}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate statistical properties of a reference report")
    parser.add_argument("path", nargs="?", default="artifacts/reference_report.json")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Reference report could not be read: {exc}", file=sys.stderr)
        return 1

    errors = validate_report(report)
    if errors:
        print("Reference report validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Reference report validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
