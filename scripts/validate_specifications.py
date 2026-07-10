#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
import sys

import yaml

from scripts.verify_references import parse_bibtex

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments" / "specifications.yaml"
BIB_PATH = ROOT / "references.bib"
REQUIRED_FIELDS = {
    "id",
    "name",
    "objective",
    "hypothesis",
    "null_hypothesis",
    "primary_observable",
    "secondary_observables",
    "controls",
    "exclusion_rules",
    "stopping_rule",
    "analysis_plan",
    "expected_result",
    "escalation_criteria",
    "references",
}


def validate_specifications(document: dict, reference_keys: set[str]) -> list[str]:
    errors: list[str] = []
    if document.get("version") != 1:
        errors.append("version must equal 1")
    if document.get("suite") != "metastable-nucleation-suite":
        errors.append("suite has an unexpected value")
    experiments = document.get("experiments")
    if not isinstance(experiments, list):
        return errors + ["experiments must be a list"]
    if len(experiments) != 15:
        errors.append(f"expected 15 experiments, found {len(experiments)}")

    expected_ids = {f"E{number:02d}" for number in range(1, 16)}
    observed_ids: set[str] = set()
    observed_names: set[str] = set()

    for index, experiment in enumerate(experiments, start=1):
        if not isinstance(experiment, dict):
            errors.append(f"entry {index} must be an object")
            continue
        missing = REQUIRED_FIELDS - experiment.keys()
        extra = experiment.keys() - REQUIRED_FIELDS
        experiment_id = experiment.get("id", f"entry-{index}")
        if missing:
            errors.append(f"{experiment_id}: missing fields {sorted(missing)}")
        if extra:
            errors.append(f"{experiment_id}: unexpected fields {sorted(extra)}")

        if not isinstance(experiment_id, str) or not re.fullmatch(r"E(0[1-9]|1[0-5])", experiment_id):
            errors.append(f"entry {index}: invalid id {experiment_id!r}")
        elif experiment_id in observed_ids:
            errors.append(f"duplicate experiment id {experiment_id}")
        else:
            observed_ids.add(experiment_id)

        name = experiment.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9_]+", name):
            errors.append(f"{experiment_id}: invalid machine name {name!r}")
        elif name in observed_names:
            errors.append(f"{experiment_id}: duplicate name {name!r}")
        else:
            observed_names.add(name)

        for field, minimum in {
            "objective": 20,
            "hypothesis": 20,
            "null_hypothesis": 20,
            "stopping_rule": 20,
            "analysis_plan": 20,
            "expected_result": 15,
            "escalation_criteria": 15,
        }.items():
            value = experiment.get(field)
            if not isinstance(value, str) or len(value.strip()) < minimum:
                errors.append(f"{experiment_id}: {field} must contain at least {minimum} characters")

        controls = experiment.get("controls")
        if not isinstance(controls, dict) or set(controls) != {"positive", "negative"}:
            errors.append(f"{experiment_id}: controls must define positive and negative controls")
        elif any(not isinstance(value, str) or len(value.strip()) < 15 for value in controls.values()):
            errors.append(f"{experiment_id}: control descriptions are too short")

        for field in ("secondary_observables", "exclusion_rules", "references"):
            values = experiment.get(field)
            if not isinstance(values, list) or not values or len(values) != len(set(values)):
                errors.append(f"{experiment_id}: {field} must be a non-empty unique list")

        references = experiment.get("references", [])
        unknown_references = set(references) - reference_keys if isinstance(references, list) else set()
        if unknown_references:
            errors.append(f"{experiment_id}: unknown references {sorted(unknown_references)}")

    if observed_ids != expected_ids:
        errors.append(f"experiment id coverage mismatch: missing={sorted(expected_ids - observed_ids)}")
    return errors


def main() -> int:
    try:
        document = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
        references = set(parse_bibtex(BIB_PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Specification validation could not start: {exc}", file=sys.stderr)
        return 1

    errors = validate_specifications(document, references)
    if errors:
        print("Specification validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Specification validation passed: 15 experiments with complete controls and analysis plans.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
