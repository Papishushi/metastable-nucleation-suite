#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import quote

from metastable_suite.semantic import execute_query, load_abox, load_tbox, union_graphs, validate_abox

ROOT = Path(__file__).resolve().parents[1]
TBOX = ROOT / "ontology" / "tbox.ttl"
SHAPES = ROOT / "ontology" / "abox-shapes.ttl"
SCHEMA = ROOT / "ontology" / "abox.schema.json"
BASE = "https://w3id.org/metastable-nucleation-suite/resource/"

RESULT_SPECIFICATIONS = {
    "seed_odds_ratio_gt_1": "E02",
    "classical_common_cause_correlation": "E07",
    "independent_optical_nodes_correlation_near_0": "E09",
    "local_chsh_le_2": "E12",
    "quantum_entangled_chsh_near_2sqrt2V": "E11",
    "quantum_no_signalling_deltas_near_0": "E13",
    "optical_metastate_positive_fraction": "E09",
    "optical_mean_commit_step": "E09",
}


def iri(kind: str, identifier: str) -> str:
    return BASE + kind + "/" + quote(identifier, safe="-._~")


def typed(value: object, datatype: str) -> dict:
    return {"@value": value, "@type": datatype}


def report_to_abox(report: dict, run_id: str) -> dict:
    provenance = report.get("provenance", {})
    expectations = report.get("known_science_expectations", {})
    started_at = provenance.get("execution_started_at_utc")
    ended_at = provenance.get("execution_ended_at_utc")
    if not started_at or not ended_at:
        raise ValueError("report provenance must contain real execution start and end timestamps")

    unknown = set(expectations) - RESULT_SPECIFICATIONS.keys()
    if unknown:
        raise ValueError(f"no experiment mapping for report results: {sorted(unknown)}")

    agent_id = f"metastable-suite-{provenance.get('package_version', 'unknown')}"
    agent_iri = iri("agent", agent_id)
    graph: list[dict] = [
        {
            "@id": agent_iri,
            "@type": ["mns:Agent", "mns:SoftwareAgent"],
            "mns:identifier": agent_id,
            "mns:softwareVersion": provenance.get("package_version", "unknown"),
        }
    ]

    by_specification: dict[str, list[tuple[str, object]]] = {}
    for name, value in expectations.items():
        by_specification.setdefault(RESULT_SPECIFICATIONS[name], []).append((name, value))

    for specification, results in sorted(by_specification.items()):
        spec_iri = iri("specification", specification)
        execution_id = f"{run_id}-{specification}"
        execution_iri = iri("run", execution_id)
        result_refs: list[dict] = []

        graph.append(
            {
                "@id": spec_iri,
                "@type": ["mns:ExperimentSpecification", "mns:SimulationSpecification"],
                "mns:identifier": specification,
                "mns:title": f"Specification {specification}",
            }
        )

        for name, value in results:
            result_id = f"{execution_id}-{name}"
            result_iri = iri("result", result_id)
            node = {
                "@id": result_iri,
                "@type": ["mns:Result", "mns:StatisticalResult"],
                "mns:identifier": result_id,
                "mns:resultName": name,
                "mns:derivedFromExecution": {"@id": execution_iri},
            }
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                node["mns:resultValue"] = typed(float(value), "xsd:double")
            else:
                node["mns:resultJson"] = typed(value, "@json")
            graph.append(node)
            result_refs.append({"@id": result_iri})

        graph.append(
            {
                "@id": execution_iri,
                "@type": ["mns:Execution", "mns:SimulationRun"],
                "mns:identifier": execution_id,
                "mns:executesSpecification": {"@id": spec_iri},
                "mns:hasExecutionStatus": {"@id": "mns:Completed"},
                "mns:trialCount": typed(int(report["trials"]), "xsd:positiveInteger"),
                "mns:randomSeed": typed(int(report["seed"]), "xsd:nonNegativeInteger"),
                "mns:startedAt": typed(started_at, "xsd:dateTime"),
                "mns:endedAt": typed(ended_at, "xsd:dateTime"),
                "mns:gitCommit": provenance.get("git_commit", "unavailable"),
                "mns:softwareVersion": provenance.get("package_version", "unknown"),
                "mns:wasExecutedBy": [{"@id": agent_iri}],
                "mns:hasResult": result_refs,
            }
        )

    return {
        "@context": {
            "mns": "https://w3id.org/metastable-nucleation-suite/ontology#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": graph,
    }


def command_validate(path: Path) -> int:
    abox = load_abox(path, SCHEMA)
    outcome = validate_abox(abox, SHAPES, load_tbox(TBOX))
    print(outcome.report_text)
    return 0 if outcome.conforms else 1


def command_query(path: Path, query_path: Path, include_tbox: bool) -> int:
    abox = load_abox(path, SCHEMA)
    graph = union_graphs(load_tbox(TBOX), abox) if include_tbox else abox
    rows = execute_query(graph, query_path.read_text(encoding="utf-8"))
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


def command_from_report(report_path: Path, output: Path, run_id: str) -> int:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    document = report_to_abox(report, run_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return command_validate(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build, validate and query semantic simulation ABoxes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("abox", type=Path)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("abox", type=Path)
    query_parser.add_argument("query", type=Path)
    query_parser.add_argument("--include-tbox", action="store_true")

    report_parser = subparsers.add_parser("from-report")
    report_parser.add_argument("report", type=Path)
    report_parser.add_argument("output", type=Path)
    report_parser.add_argument("--run-id", required=True)

    args = parser.parse_args()
    if args.command == "validate":
        return command_validate(args.abox)
    if args.command == "query":
        return command_query(args.abox, args.query, args.include_tbox)
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.run_id):
        parser.error("--run-id may contain only letters, digits, dot, underscore and hyphen")
    return command_from_report(args.report, args.output, args.run_id)


if __name__ == "__main__":
    raise SystemExit(main())
