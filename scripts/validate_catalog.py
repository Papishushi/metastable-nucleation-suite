#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import yaml

REQUIRED = {
    "id",
    "name",
    "class",
    "observable",
    "null_prediction",
    "escalation",
}
ID_PATTERN = re.compile(r"^E\d{2}$")


def validate(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if data.get("suite") != "metastable-nucleation-suite":
        errors.append("suite must be metastable-nucleation-suite")
    if not isinstance(data.get("version"), int) or data["version"] < 1:
        errors.append("version must be a positive integer")

    experiments = data.get("experiments")
    if not isinstance(experiments, list) or not experiments:
        return errors + ["experiments must be a non-empty list"]

    seen: set[str] = set()
    for index, experiment in enumerate(experiments):
        prefix = f"experiments[{index}]"
        if not isinstance(experiment, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED - experiment.keys()
        extra = experiment.keys() - REQUIRED
        if missing:
            errors.append(f"{prefix} missing: {sorted(missing)}")
        if extra:
            errors.append(f"{prefix} unexpected: {sorted(extra)}")
        identifier = experiment.get("id")
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            errors.append(f"{prefix}.id must match E00")
        elif identifier in seen:
            errors.append(f"duplicate experiment id: {identifier}")
        else:
            seen.add(identifier)
        observables = experiment.get("observable")
        if not isinstance(observables, list) or not observables or not all(
            isinstance(item, str) and item for item in observables
        ):
            errors.append(f"{prefix}.observable must be a non-empty string list")

    expected = {f"E{i:02d}" for i in range(1, 16)}
    if seen != expected:
        errors.append(
            "catalog IDs differ from E01-E15: "
            f"missing={sorted(expected - seen)}, extra={sorted(seen - expected)}"
        )
    return errors


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "experiments" / "catalog.yaml"
    errors = validate(path)
    if errors:
        print("Catalog validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Catalog validation passed: 15 experiments, E01-E15.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
