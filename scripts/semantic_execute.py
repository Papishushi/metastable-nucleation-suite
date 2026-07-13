#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable, Iterable

from rdflib import Graph, URIRef

from metastable_suite.backend_config import (
    backend_configuration_fingerprint,
    build_backend_registry,
    load_backend_configuration,
)
from metastable_suite.campaigns import (
    CampaignStateError,
    FailurePolicy,
    campaign_plan_from_graph,
    execute_campaign,
    find_campaigns,
)
from metastable_suite.execution import (
    BackendRegistry,
    execute_request,
    find_planned_runs,
    load_event_schema,
    request_from_graph,
    result_to_abox,
    safe_output_path,
)
from metastable_suite.semantic import load_abox, load_tbox, validate_abox

ROOT = Path(__file__).resolve().parents[1]
TBOX = [
    ROOT / "ontology" / "tbox.ttl",
    ROOT / "ontology" / "execution-extension.ttl",
]
SHAPES = [
    ROOT / "ontology" / "abox-shapes.ttl",
    ROOT / "ontology" / "execution-shapes.ttl",
]
ABOX_SCHEMA = ROOT / "ontology" / "abox.schema.json"
EVENT_SCHEMA = ROOT / "schemas" / "event.schema.json"
BACKEND_CONFIG_SCHEMA = ROOT / "schemas" / "backend-config.schema.json"
DEFAULT_BACKEND_CONTEXT = "default-registry-v1"
INJECTED_BACKEND_CONTEXT = "injected-registry-v1"


def _validated_plan(plan_path: Path):
    graph = load_abox(plan_path, ABOX_SCHEMA)
    ontology = load_tbox(TBOX)
    outcome = validate_abox(graph, SHAPES, ontology)
    if not outcome.conforms:
        raise ValueError(outcome.report_text)
    return graph, ontology


def _completed_artifact_validator(ontology: Graph) -> Callable[[Path], bool]:
    def validate(path: Path) -> bool:
        try:
            graph = load_abox(path, ABOX_SCHEMA)
            return validate_abox(graph, SHAPES, ontology).conforms
        except Exception:
            return False

    return validate


def _resolve_registry(
    backend_config: Path | None,
    registry: BackendRegistry | None,
) -> tuple[BackendRegistry, str]:
    if backend_config is not None and registry is not None:
        raise ValueError("backend_config and registry cannot be supplied together")
    if registry is not None:
        return registry, INJECTED_BACKEND_CONTEXT

    default = BackendRegistry.default()
    if backend_config is None:
        return default, DEFAULT_BACKEND_CONTEXT

    document = load_backend_configuration(
        backend_config,
        BACKEND_CONFIG_SCHEMA,
    )
    fingerprint = backend_configuration_fingerprint(document)
    return (
        build_backend_registry(document, registry=default),
        f"backend-config-sha256:{fingerprint}",
    )


def _write_json_atomic(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _has_reusable_campaign_artifacts(
    output_dir: Path,
    run_ids: Iterable[str],
) -> bool:
    return any(
        safe_output_path(output_dir, f"{run_id}.abox.jsonld").exists()
        and safe_output_path(output_dir, f"{run_id}.events.ndjson").exists()
        for run_id in run_ids
    )


def _guard_campaign_execution_context(
    output_dir: Path,
    campaign_id: str,
    backend_registry_fingerprint: str,
    *,
    resume: bool,
    run_ids: Iterable[str] = (),
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    context_path = safe_output_path(
        output_dir,
        f"{campaign_id}.execution-context.json",
    )
    state_path = safe_output_path(
        output_dir,
        f"{campaign_id}.campaign-state.json",
    )

    reusable_artifacts_exist = _has_reusable_campaign_artifacts(
        output_dir,
        run_ids,
    )
    if (
        resume
        and not context_path.exists()
        and (state_path.exists() or reusable_artifacts_exist)
    ):
        raise CampaignStateError(
            "campaign execution context is missing; use --no-resume to start "
            "with the current backend configuration"
        )

    if resume and context_path.exists():
        try:
            persisted = json.loads(context_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CampaignStateError(
                f"cannot read campaign execution context: {exc}"
            ) from exc
        if not isinstance(persisted, dict):
            raise CampaignStateError(
                "persisted campaign execution context is not a JSON object"
            )
        if (
            persisted.get("backend_registry_fingerprint")
            != backend_registry_fingerprint
        ):
            raise CampaignStateError(
                "backend configuration changed since campaign state was persisted; "
                "use --no-resume to start a new acquisition"
            )

    _write_json_atomic(
        context_path,
        {
            "schema_version": "1.0.0",
            "campaign_id": campaign_id,
            "backend_registry_fingerprint": backend_registry_fingerprint,
        },
    )
    return context_path


def execute_plan(
    plan_path: Path,
    output_dir: Path,
    run_iri: str | None = None,
    *,
    backend_config: Path | None = None,
    registry: BackendRegistry | None = None,
) -> list[dict]:
    plan_graph, ontology = _validated_plan(plan_path)
    runs = find_planned_runs(plan_graph)
    if run_iri is not None:
        runs = [run for run in runs if str(run) == run_iri]
    if not runs:
        raise ValueError("no matching planned execution found")

    event_schema = load_event_schema(EVENT_SCHEMA)
    resolved_registry, _ = _resolve_registry(backend_config, registry)
    documents: list[dict] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for run in runs:
        request = request_from_graph(plan_graph, run)
        result = execute_request(
            request,
            output_dir,
            event_schema,
            resolved_registry,
        )
        document = result_to_abox(result)
        target = safe_output_path(output_dir, f"{request.run_id}.abox.jsonld")
        target.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        completed_graph = load_abox(target, ABOX_SCHEMA)
        completed_validation = validate_abox(completed_graph, SHAPES, ontology)
        if not completed_validation.conforms:
            raise RuntimeError(completed_validation.report_text)
        documents.append(document)
    return documents


def execute_campaign_plan(
    plan_path: Path,
    output_dir: Path,
    campaign_iri: str | None = None,
    failure_policy: str | None = None,
    resume: bool = True,
    *,
    backend_config: Path | None = None,
    registry: BackendRegistry | None = None,
):
    plan_graph, ontology = _validated_plan(plan_path)
    campaigns = find_campaigns(plan_graph)
    if campaign_iri is not None:
        campaigns = [
            campaign
            for campaign in campaigns
            if str(campaign) == campaign_iri
        ]
    if len(campaigns) != 1:
        raise ValueError("select exactly one campaign with --campaign-iri")

    selected_campaign = URIRef(campaigns[0])
    campaign_plan = campaign_plan_from_graph(
        plan_graph,
        selected_campaign,
    )
    resolved_registry, registry_fingerprint = _resolve_registry(
        backend_config,
        registry,
    )
    _guard_campaign_execution_context(
        output_dir,
        campaign_plan.campaign_id,
        registry_fingerprint,
        resume=resume,
        run_ids=(request.run_id for request in campaign_plan.runs.values()),
    )

    result = execute_campaign(
        plan_graph,
        selected_campaign,
        output_dir,
        load_event_schema(EVENT_SCHEMA),
        resolved_registry,
        failure_policy=(
            FailurePolicy.parse(failure_policy)
            if failure_policy
            else None
        ),
        resume=resume,
        artifact_validator=_completed_artifact_validator(ontology),
    )
    campaign_graph = load_abox(result.abox_path, ABOX_SCHEMA)
    validation = validate_abox(campaign_graph, SHAPES, ontology)
    if not validation.conforms:
        raise RuntimeError(validation.report_text)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute SHACL-valid semantic experiment plans"
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--run-iri")
    parser.add_argument("--campaign-iri")
    parser.add_argument(
        "--failure-policy",
        choices=[policy.value for policy in FailurePolicy],
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="start a new campaign instead of reusing persisted state",
    )
    parser.add_argument(
        "--backend-config",
        type=Path,
        help="validated external Serial/TCP/VISA backend configuration",
    )
    arguments = parser.parse_args(argv)
    if arguments.run_iri and arguments.campaign_iri:
        parser.error("--run-iri and --campaign-iri are mutually exclusive")
    if arguments.run_iri and (
        arguments.failure_policy or arguments.no_resume
    ):
        parser.error(
            "--failure-policy and --no-resume require campaign execution"
        )

    plan_graph, _ = _validated_plan(arguments.plan)
    campaigns = find_campaigns(plan_graph)
    campaign_mode = arguments.campaign_iri is not None or (
        arguments.run_iri is None and len(campaigns) == 1
    )
    if campaign_mode:
        result = execute_campaign_plan(
            arguments.plan,
            arguments.output,
            campaign_iri=arguments.campaign_iri,
            failure_policy=arguments.failure_policy,
            resume=not arguments.no_resume,
            backend_config=arguments.backend_config,
        )
        print(json.dumps(result.run_statuses, indent=2, sort_keys=True))
        return 0 if result.status == "Completed" else 1

    documents = execute_plan(
        arguments.plan,
        arguments.output,
        arguments.run_iri,
        backend_config=arguments.backend_config,
    )
    print(json.dumps(documents, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
