from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import heapq
import json
from pathlib import Path
from typing import Any, Mapping

from rdflib import Graph, RDF, URIRef

from .datasets import sha256_file
from .execution import (
    BackendRegistry,
    ExecutionRequest,
    MNS,
    execute_request,
    request_from_graph,
    result_to_abox,
    safe_output_path,
    validate_run_id,
)


class CampaignCycleError(ValueError):
    """The campaign dependency graph is cyclic."""


class CampaignStateError(RuntimeError):
    """Persisted campaign state is incompatible or corrupt."""


class FailurePolicy(str, Enum):
    FAIL_FAST = "fail-fast"
    CONTINUE_ON_ERROR = "continue-on-error"

    @classmethod
    def parse(cls, value: FailurePolicy | str | None) -> FailurePolicy:
        if value is None:
            return cls.FAIL_FAST
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError("failure policy must be fail-fast or continue-on-error") from exc


@dataclass(frozen=True)
class CampaignPlan:
    campaign_iri: URIRef
    campaign_id: str
    runs: Mapping[URIRef, ExecutionRequest]
    dependencies: Mapping[URIRef, tuple[URIRef, ...]]
    order: tuple[URIRef, ...]
    configured_policy: FailurePolicy | None


@dataclass(frozen=True)
class CampaignResult:
    campaign_id: str
    status: str
    failure_policy: FailurePolicy
    state_path: str
    abox_path: str
    run_statuses: Mapping[str, str]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_campaigns(graph: Graph) -> list[URIRef]:
    values = set(graph.subjects(RDF.type, MNS.SuiteRun))
    values.update(graph.subjects(RDF.type, MNS.ExperimentalCampaign))
    return sorted((value for value in values if isinstance(value, URIRef)), key=str)


def topological_order(
    dependencies: Mapping[URIRef, tuple[URIRef, ...]],
) -> tuple[URIRef, ...]:
    indegree = {run: len(set(required)) for run, required in dependencies.items()}
    followers: dict[URIRef, set[URIRef]] = {run: set() for run in dependencies}
    for run, required in dependencies.items():
        for dependency in required:
            if dependency not in indegree:
                raise ValueError(f"{run} depends on an execution outside its campaign: {dependency}")
            followers[dependency].add(run)

    ready = [(str(run), run) for run, count in indegree.items() if count == 0]
    heapq.heapify(ready)
    ordered: list[URIRef] = []
    while ready:
        _, run = heapq.heappop(ready)
        ordered.append(run)
        for follower in sorted(followers[run], key=str):
            indegree[follower] -= 1
            if indegree[follower] == 0:
                heapq.heappush(ready, (str(follower), follower))

    if len(ordered) != len(dependencies):
        cycle = ", ".join(sorted(str(run) for run, count in indegree.items() if count))
        raise CampaignCycleError(f"campaign dependency cycle detected: {cycle}")
    return tuple(ordered)


def campaign_plan_from_graph(graph: Graph, campaign_iri: URIRef) -> CampaignPlan:
    identifier = graph.value(campaign_iri, MNS.identifier)
    if identifier is None:
        raise ValueError(f"campaign {campaign_iri} has no identifier")
    campaign_id = validate_run_id(str(identifier))
    members = {run for run in graph.objects(campaign_iri, MNS.hasSubExecution) if isinstance(run, URIRef)}
    members.update(
        run for run in graph.subjects(MNS.partOfSuiteRun, campaign_iri) if isinstance(run, URIRef)
    )
    if not members:
        raise ValueError(f"campaign {campaign_iri} has no subexecutions")

    runs: dict[URIRef, ExecutionRequest] = {}
    dependencies: dict[URIRef, tuple[URIRef, ...]] = {}
    identifiers: set[str] = set()
    for run in sorted(members, key=str):
        request = request_from_graph(graph, run)
        if request.run_id in identifiers:
            raise ValueError(f"duplicate run identifier {request.run_id!r}")
        identifiers.add(request.run_id)
        runs[run] = request
        dependencies[run] = tuple(
            sorted(
                (
                    dependency
                    for dependency in graph.objects(run, MNS.dependsOnExecution)
                    if isinstance(dependency, URIRef)
                ),
                key=str,
            )
        )

    configured = graph.value(campaign_iri, MNS.failurePolicy)
    return CampaignPlan(
        campaign_iri=campaign_iri,
        campaign_id=campaign_id,
        runs=runs,
        dependencies=dependencies,
        order=topological_order(dependencies),
        configured_policy=FailurePolicy.parse(str(configured)) if configured is not None else None,
    )


def _fingerprint(plan: CampaignPlan) -> str:
    payload = [
        {
            "iri": str(run),
            "request": {
                "run_id": plan.runs[run].run_id,
                "specification_id": plan.runs[run].specification_id,
                "backend_id": plan.runs[run].backend_id,
                "trial_count": plan.runs[run].trial_count,
                "parameters": dict(plan.runs[run].parameters),
                "random_seed": plan.runs[run].random_seed,
            },
            "dependencies": [str(value) for value in plan.dependencies[run]],
        }
        for run in plan.order
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _new_state(plan: CampaignPlan, policy: FailurePolicy) -> dict[str, Any]:
    started = _now()
    return {
        "schema_version": "1.0.0",
        "campaign_id": plan.campaign_id,
        "campaign_iri": str(plan.campaign_iri),
        "plan_fingerprint": _fingerprint(plan),
        "failure_policy": policy.value,
        "status": "Running",
        "started_at_utc": started,
        "ended_at_utc": None,
        "runs": {
            str(run): {
                "run_id": plan.runs[run].run_id,
                "status": "Planned",
                "attempts": 0,
                "started_at_utc": None,
                "ended_at_utc": None,
                "abox_file": None,
                "events_file": None,
                "sha256": None,
                "error": None,
            }
            for run in plan.order
        },
    }


def _load_state(path: Path, plan: CampaignPlan, policy: FailurePolicy, resume: bool) -> dict[str, Any]:
    if not resume or not path.exists():
        return _new_state(plan, policy)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignStateError(f"cannot read campaign state: {exc}") from exc
    if state.get("campaign_iri") != str(plan.campaign_iri):
        raise CampaignStateError("persisted state belongs to another campaign")
    if state.get("plan_fingerprint") != _fingerprint(plan):
        raise CampaignStateError("campaign plan changed since state was persisted")
    if set(state.get("runs", {})) != {str(run) for run in plan.order}:
        raise CampaignStateError("persisted state has a different run set")
    state["failure_policy"] = policy.value
    state["status"] = "Running"
    state["ended_at_utc"] = None
    return state


def _valid_completed_artifact(output: Path, request: ExecutionRequest) -> bool:
    abox = safe_output_path(output, f"{request.run_id}.abox.jsonld")
    events = safe_output_path(output, f"{request.run_id}.events.ndjson")
    if not abox.exists() or not events.exists():
        return False
    try:
        document = json.loads(abox.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    datasets = []
    for node in document.get("@graph", []):
        if not isinstance(node, dict):
            continue
        node_types = node.get("@type", [])
        if node_types == "mns:Dataset" or (
            isinstance(node_types, list) and "mns:Dataset" in node_types
        ):
            datasets.append(node)
    return bool(datasets) and datasets[0].get("mns:sha256") == sha256_file(events)


def _campaign_abox(plan: CampaignPlan, state: Mapping[str, Any]) -> dict[str, Any]:
    summaries = []
    nodes: list[dict[str, Any]] = []
    for run in plan.order:
        request = plan.runs[run]
        record = state["runs"][str(run)]
        summary_iri = f"{plan.campaign_iri}/summary/{request.run_id}"
        summaries.append({"@id": summary_iri})
        node: dict[str, Any] = {
            "@id": summary_iri,
            "@type": "mns:CampaignRunSummary",
            "mns:identifier": request.run_id,
            "mns:summarizesExecution": {"@id": str(run)},
            "mns:summarizedExecutionStatus": {"@id": f"mns:{record['status']}"},
            "mns:executionAttemptCount": {
                "@value": record["attempts"],
                "@type": "xsd:nonNegativeInteger",
            },
        }
        if plan.dependencies[run]:
            node["mns:summarizesDependency"] = [
                {"@id": str(dependency)} for dependency in plan.dependencies[run]
            ]
        if record.get("abox_file"):
            node["mns:executionArtifactPath"] = record["abox_file"]
        if record.get("events_file"):
            node["mns:eventArtifactPath"] = record["events_file"]
        if record.get("sha256"):
            node["mns:artifactSha256"] = record["sha256"]
        if record.get("error"):
            node["mns:failureMessage"] = record["error"]["message"]
        nodes.append(node)

    campaign = {
        "@id": str(plan.campaign_iri),
        "@type": ["mns:SuiteRun", "mns:ExperimentalCampaign"],
        "mns:identifier": plan.campaign_id,
        "mns:hasCampaignStatus": {"@id": f"mns:{state['status']}"},
        "mns:failurePolicy": state["failure_policy"],
        "mns:campaignStartedAt": {"@value": state["started_at_utc"], "@type": "xsd:dateTime"},
        "mns:campaignEndedAt": {"@value": state["ended_at_utc"], "@type": "xsd:dateTime"},
        "mns:hasCampaignRunSummary": summaries,
    }
    return {
        "@context": {
            "mns": str(MNS),
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": [campaign, *nodes],
    }


def execute_campaign(
    graph: Graph,
    campaign_iri: URIRef,
    output_dir: str | Path,
    schema: Mapping[str, Any],
    registry: BackendRegistry | None = None,
    failure_policy: FailurePolicy | str | None = None,
    resume: bool = True,
) -> CampaignResult:
    plan = campaign_plan_from_graph(graph, campaign_iri)
    policy = FailurePolicy.parse(failure_policy or plan.configured_policy)
    registry = registry or BackendRegistry.default()
    output = Path(output_dir)
    state_path = safe_output_path(output, f"{plan.campaign_id}.campaign-state.json")
    abox_path = safe_output_path(output, f"{plan.campaign_id}.campaign.abox.jsonld")
    output.mkdir(parents=True, exist_ok=True)
    state = _load_state(state_path, plan, policy, resume)

    for run in plan.order:
        record = state["runs"][str(run)]
        request = plan.runs[run]
        if record["status"] == "Completed":
            if not _valid_completed_artifact(output, request):
                raise CampaignStateError(f"completed artifacts are missing or corrupt for {request.run_id}")
            continue
        if resume and _valid_completed_artifact(output, request):
            record["status"] = "Completed"
            record["abox_file"] = f"{request.run_id}.abox.jsonld"
            record["events_file"] = f"{request.run_id}.events.ndjson"
            record["sha256"] = sha256_file(output / record["events_file"])
            continue

        dependency_statuses = {
            str(dependency): state["runs"][str(dependency)]["status"]
            for dependency in plan.dependencies[run]
        }
        if any(value != "Completed" for value in dependency_statuses.values()):
            record["status"] = "Invalidated"
            record["ended_at_utc"] = _now()
            record["error"] = {
                "type": "DependencyFailure",
                "message": "a required execution did not complete",
            }
            _write_json(state_path, state)
            continue

        events_path = safe_output_path(output, f"{request.run_id}.events.ndjson")
        run_abox_path = safe_output_path(output, f"{request.run_id}.abox.jsonld")
        events_path.unlink(missing_ok=True)
        run_abox_path.unlink(missing_ok=True)
        record["status"] = "Running"
        record["attempts"] += 1
        record["started_at_utc"] = _now()
        record["error"] = None
        _write_json(state_path, state)
        try:
            result = execute_request(request, output, schema, registry)
            _write_json(run_abox_path, result_to_abox(result))
            record["status"] = "Completed"
            record["ended_at_utc"] = _now()
            record["abox_file"] = run_abox_path.name
            record["events_file"] = events_path.name
            record["sha256"] = result.manifest.sha256
        except Exception as exc:
            events_path.unlink(missing_ok=True)
            run_abox_path.unlink(missing_ok=True)
            record["status"] = "Failed"
            record["ended_at_utc"] = _now()
            record["error"] = {"type": exc.__class__.__name__, "message": str(exc)}
            _write_json(state_path, state)
            if policy is FailurePolicy.FAIL_FAST:
                break
        _write_json(state_path, state)

    state["status"] = (
        "Completed"
        if all(record["status"] == "Completed" for record in state["runs"].values())
        else "Failed"
    )
    state["ended_at_utc"] = _now()
    _write_json(abox_path, _campaign_abox(plan, state))
    _write_json(state_path, state)
    return CampaignResult(
        campaign_id=plan.campaign_id,
        status=state["status"],
        failure_policy=policy,
        state_path=state_path.as_posix(),
        abox_path=abox_path.as_posix(),
        run_statuses={
            plan.runs[run].run_id: state["runs"][str(run)]["status"] for run in plan.order
        },
    )
