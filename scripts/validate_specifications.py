#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments" / "specifications.yaml"
SCHEMA_PATH = ROOT / "experiments" / "specifications.schema.json"
BIB_PATH = ROOT / "references.bib"


def bibtex_keys(text: str) -> set[str]:
    return set(re.findall(r"^@\w+\s*\{\s*([^,\s]+)\s*,", text, flags=re.MULTILINE))


def schema_errors(document: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    return [
        f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in errors
    ]


def cross_document_errors(document: dict, reference_keys: set[str]) -> list[str]:
    errors: list[str] = []
    experiments = document.get("experiments", [])
    if not isinstance(experiments, list):
        return errors

    expected_ids = {f"E{number:02d}" for number in range(1, 16)}
    observed_ids: set[str] = set()
    observed_names: set[str] = set()

    for index, experiment in enumerate(experiments, start=1):
        if not isinstance(experiment, dict):
            continue
        experiment_id = experiment.get("id", f"entry-{index}")
        if isinstance(experiment_id, str):
            if experiment_id in observed_ids:
                errors.append(f"duplicate experiment id {experiment_id}")
            observed_ids.add(experiment_id)

        name = experiment.get("name")
        if isinstance(name, str):
            if name in observed_names:
                errors.append(f"{experiment_id}: duplicate name {name!r}")
            observed_names.add(name)

        references = experiment.get("references", [])
        if isinstance(references, list):
            unknown = set(references) - reference_keys
            if unknown:
                errors.append(f"{experiment_id}: unknown references {sorted(unknown)}")

    if observed_ids != expected_ids:
        errors.append(
            "experiment id coverage mismatch: "
            f"missing={sorted(expected_ids - observed_ids)}, unexpected={sorted(observed_ids - expected_ids)}"
        )
    return errors


def validate_specifications(document: dict, schema: dict, reference_keys: set[str]) -> list[str]:
    return schema_errors(document, schema) + cross_document_errors(document, reference_keys)


def main() -> int:
    try:
        document = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        references = bibtex_keys(BIB_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Specification validation could not start: {exc}", file=sys.stderr)
        return 1

    errors = validate_specifications(document, schema, references)
    if errors:
        print("Specification validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Specification validation passed: JSON Schema and cross-document invariants are satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
