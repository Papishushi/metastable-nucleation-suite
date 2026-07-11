#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from metastable_suite.execution import (
    BackendRegistry,
    execute_request,
    find_planned_runs,
    load_event_schema,
    request_from_graph,
    result_to_abox,
)
from metastable_suite.semantic import load_abox, load_tbox, validate_abox

ROOT = Path(__file__).resolve().parents[1]
TBOX = [ROOT / "ontology" / "tbox.ttl", ROOT / "ontology" / "execution-extension.ttl"]
SHAPES = [ROOT / "ontology" / "abox-shapes.ttl", ROOT / "ontology" / "execution-shapes.ttl"]
ABOX_SCHEMA = ROOT / "ontology" / "abox.schema.json"
EVENT_SCHEMA = ROOT / "schemas" / "event.schema.json"


def execute_plan(plan_path: Path, output_dir: Path, run_iri: str | None = None) -> list[dict]:
    plan_graph = load_abox(plan_path, ABOX_SCHEMA)
    ontology = load_tbox(TBOX)
    outcome = validate_abox(plan_graph, SHAPES, ontology)
    if not outcome.conforms:
        raise ValueError(outcome.report_text)

    runs = find_planned_runs(plan_graph)
    if run_iri is not None:
        runs = [run for run in runs if str(run) == run_iri]
    if not runs:
        raise ValueError("no matching planned execution found")

    event_schema = load_event_schema(EVENT_SCHEMA)
    registry = BackendRegistry.default()
    documents: list[dict] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for run in runs:
        request = request_from_graph(plan_graph, run)
        result = execute_request(request, output_dir, event_schema, registry)
        document = result_to_abox(result)
        target = output_dir / f"{request.run_id}.abox.jsonld"
        target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        completed_graph = load_abox(target, ABOX_SCHEMA)
        completed_validation = validate_abox(completed_graph, SHAPES, ontology)
        if not completed_validation.conforms:
            raise RuntimeError(completed_validation.report_text)
        documents.append(document)
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute SHACL-valid semantic experiment plans")
    parser.add_argument("plan", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--run-iri")
    args = parser.parse_args()

    documents = execute_plan(args.plan, args.output_dir, args.run_iri)
    print(json.dumps({"executed_runs": len(documents), "output_dir": args.output_dir.as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
