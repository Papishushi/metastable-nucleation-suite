from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping

from rdflib import Graph, Namespace, RDF, URIRef

from .datasets import DatasetManifest, EventDatasetWriter
from .hardware import ExperimentalBackend, SimulatorBackend, TrialRequest

MNS = Namespace("https://w3id.org/metastable-nucleation-suite/ontology#")
RESOURCE = "https://w3id.org/metastable-nucleation-suite/resource/"
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
BACKEND_KINDS = frozenset({"hardware", "simulator"})


@dataclass(frozen=True)
class ExecutionRequest:
    run_id: str
    specification_id: str
    backend_id: str
    trial_count: int
    parameters: Mapping[str, Any]
    random_seed: int | None = None


@dataclass(frozen=True)
class ExecutionResult:
    run_id: str
    specification_id: str
    backend_id: str
    backend_kind: str
    started_at_utc: str
    ended_at_utc: str
    manifest: DatasetManifest
    calibration: Mapping[str, Any]
    diagnostics: Mapping[str, Any]
    valid_trials: int
    invalid_trials: int
    random_seed: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "specification_id": self.specification_id,
            "backend_id": self.backend_id,
            "backend_kind": self.backend_kind,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "manifest": self.manifest.as_dict(),
            "calibration": dict(self.calibration),
            "diagnostics": dict(self.diagnostics),
            "valid_trials": self.valid_trials,
            "invalid_trials": self.invalid_trials,
            "random_seed": self.random_seed,
        }


class BackendRegistry:
    def __init__(self) -> None:
        self._factories: dict[
            str,
            Callable[[ExecutionRequest], ExperimentalBackend],
        ] = {}

    def register(
        self,
        backend_id: str,
        factory: Callable[[ExecutionRequest], ExperimentalBackend],
    ) -> None:
        if not backend_id or backend_id in self._factories:
            raise ValueError(f"backend already registered or invalid: {backend_id!r}")
        self._factories[backend_id] = factory

    def create(self, request: ExecutionRequest) -> ExperimentalBackend:
        try:
            factory = self._factories[request.backend_id]
        except KeyError as exc:
            raise ValueError(f"unknown backend {request.backend_id!r}") from exc
        return factory(request)

    @classmethod
    def default(cls) -> BackendRegistry:
        registry = cls()
        registry.register(
            "reference-simulator",
            lambda request: SimulatorBackend(seed=request.random_seed or 0),
        )
        return registry


def validate_run_id(run_id: str) -> str:
    if not SAFE_RUN_ID.fullmatch(run_id):
        raise ValueError(
            "run_id must start with an ASCII letter or digit and contain only "
            "letters, digits, dot, underscore or hyphen (maximum 128 characters)"
        )
    return run_id


def safe_output_path(output_dir: str | Path, filename: str) -> Path:
    base = Path(output_dir).resolve()
    target = (base / filename).resolve()
    if not target.is_relative_to(base) or target.parent != base:
        raise ValueError(f"output path escapes configured directory: {filename!r}")
    return target


def load_event_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def request_from_graph(graph: Graph, run_iri: URIRef) -> ExecutionRequest:
    identifier = graph.value(run_iri, MNS.identifier)
    specification = graph.value(run_iri, MNS.executesSpecification)
    backend = graph.value(run_iri, MNS.usesBackend)
    trial_count = graph.value(run_iri, MNS.trialCount)
    seed = graph.value(run_iri, MNS.randomSeed)

    missing = [
        name
        for name, value in {
            "identifier": identifier,
            "executesSpecification": specification,
            "usesBackend": backend,
            "trialCount": trial_count,
        }.items()
        if value is None
    ]
    if missing:
        raise ValueError(f"execution request is missing {missing}")

    run_id = validate_run_id(str(identifier))
    specification_id = str(
        graph.value(specification, MNS.identifier)
        or str(specification).rsplit("/", 1)[-1]
    )
    backend_id = str(
        graph.value(backend, MNS.identifier)
        or str(backend).rsplit("/", 1)[-1]
    )

    parameters: dict[str, Any] = {}
    for parameter in graph.objects(run_iri, MNS.hasParameter):
        name = graph.value(parameter, MNS.parameterName)
        numeric = graph.value(parameter, MNS.numericValue)
        text = graph.value(parameter, MNS.stringValue)
        if name is None:
            raise ValueError(f"parameter {parameter} has no parameterName")
        if numeric is not None:
            parameters[str(name)] = float(numeric)
        elif text is not None:
            parameters[str(name)] = str(text)
        else:
            raise ValueError(f"parameter {parameter} has no value")

    return ExecutionRequest(
        run_id=run_id,
        specification_id=specification_id,
        backend_id=backend_id,
        trial_count=int(trial_count),
        parameters=parameters,
        random_seed=int(seed) if seed is not None else None,
    )


def find_planned_runs(graph: Graph) -> list[URIRef]:
    return sorted(
        {
            subject
            for subject in graph.subjects(RDF.type, MNS.Execution)
            if graph.value(subject, MNS.hasExecutionStatus) == MNS.Planned
        },
        key=str,
    )


def execute_request(
    request: ExecutionRequest,
    output_dir: str | Path,
    schema: Mapping[str, Any],
    registry: BackendRegistry | None = None,
) -> ExecutionResult:
    run_id = validate_run_id(request.run_id)
    if request.trial_count <= 0:
        raise ValueError("trial_count must be positive")
    registry = registry or BackendRegistry.default()
    backend = registry.create(request)
    backend_kind = str(getattr(backend, "backend_kind", "hardware"))
    if backend_kind not in BACKEND_KINDS:
        raise ValueError(
            f"backend {request.backend_id!r} declares unsupported kind {backend_kind!r}"
        )
    effective_random_seed = request.random_seed
    if backend_kind == "simulator" and effective_random_seed is None:
        effective_random_seed = 0
    dataset_path = safe_output_path(output_dir, f"{run_id}.events.ndjson")
    dataset_id = f"{run_id}-events"

    started_at = datetime.now(timezone.utc)
    valid_trials = 0
    invalid_trials = 0
    try:
        backend.prepare(request.specification_id, request.parameters)
        calibration = backend.calibrate()
        writer = EventDatasetWriter(dataset_path, dataset_id, schema)
        with writer:
            for trial_index in range(request.trial_count):
                reset = backend.reset()
                response = backend.execute_trial(
                    TrialRequest(
                        run_id=run_id,
                        specification_id=request.specification_id,
                        trial_index=trial_index,
                    )
                )
                event = {
                    "schema_version": "1.0.0",
                    "event_id": f"{run_id}-{trial_index}",
                    "run_id": run_id,
                    "specification_id": request.specification_id,
                    "trial_index": trial_index,
                    "timestamp_utc": response.timestamp_utc,
                    "backend_id": request.backend_id,
                    "settings": {},
                    "outcome": dict(response.outcome),
                    "diagnostics": {
                        **dict(reset),
                        **dict(response.diagnostics),
                    },
                    "valid": response.valid,
                    "exclusion_reasons": list(response.exclusion_reasons),
                    "firmware_version": backend.firmware_version,
                }
                writer.write(event)
                if response.valid:
                    valid_trials += 1
                else:
                    invalid_trials += 1
            manifest = writer.close()
        diagnostics = backend.collect_diagnostics()
    finally:
        backend.close()
    ended_at = datetime.now(timezone.utc)

    return ExecutionResult(
        run_id=run_id,
        specification_id=request.specification_id,
        backend_id=request.backend_id,
        backend_kind=backend_kind,
        started_at_utc=started_at.isoformat(),
        ended_at_utc=ended_at.isoformat(),
        manifest=manifest,
        calibration=calibration,
        diagnostics=diagnostics,
        valid_trials=valid_trials,
        invalid_trials=invalid_trials,
        random_seed=effective_random_seed,
    )


def result_to_abox(result: ExecutionResult) -> dict[str, Any]:
    run_id = validate_run_id(result.run_id)
    if result.backend_kind not in BACKEND_KINDS:
        raise ValueError(f"unsupported backend kind {result.backend_kind!r}")

    run_iri = RESOURCE + "run/" + run_id
    spec_iri = RESOURCE + "specification/" + result.specification_id
    backend_iri = RESOURCE + "backend/" + result.backend_id
    dataset_iri = RESOURCE + "dataset/" + result.manifest.dataset_id
    result_iri = RESOURCE + "result/" + run_id + "-execution-summary"

    simulator = result.backend_kind == "simulator"
    run_types = [
        "mns:Execution",
        "mns:SimulationRun" if simulator else "mns:ExperimentRun",
    ]
    specification_types = [
        "mns:ExperimentSpecification",
        (
            "mns:SimulationSpecification"
            if simulator
            else "mns:PhysicalExperimentSpecification"
        ),
    ]
    backend_types = ["mns:Agent", "mns:ExecutionBackend"]
    backend_types.append(
        "mns:SimulatorBackend" if simulator else "mns:HardwareBackend"
    )

    run_node: dict[str, Any] = {
        "@id": run_iri,
        "@type": run_types,
        "mns:identifier": run_id,
        "mns:executesSpecification": {"@id": spec_iri},
        "mns:usesBackend": {"@id": backend_iri},
        "mns:usesDataset": {"@id": dataset_iri},
        "mns:hasResult": {"@id": result_iri},
        "mns:hasExecutionStatus": {"@id": "mns:Completed"},
        "mns:trialCount": {
            "@value": result.manifest.event_count,
            "@type": "xsd:positiveInteger",
        },
        "mns:startedAt": {
            "@value": result.started_at_utc,
            "@type": "xsd:dateTime",
        },
        "mns:endedAt": {
            "@value": result.ended_at_utc,
            "@type": "xsd:dateTime",
        },
        "mns:wasExecutedBy": {"@id": backend_iri},
    }
    if result.random_seed is not None:
        run_node["mns:randomSeed"] = {
            "@value": result.random_seed,
            "@type": "xsd:nonNegativeInteger",
        }

    return {
        "@context": {
            "mns": str(MNS),
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": [
            {
                "@id": spec_iri,
                "@type": specification_types,
                "mns:identifier": result.specification_id,
            },
            {
                "@id": backend_iri,
                "@type": backend_types,
                "mns:identifier": result.backend_id,
            },
            {
                "@id": dataset_iri,
                "@type": "mns:Dataset",
                "mns:identifier": result.manifest.dataset_id,
                "mns:datasetPath": result.manifest.path,
                "mns:mediaType": result.manifest.media_type,
                "mns:schemaVersion": result.manifest.schema_version,
                "mns:eventCount": {
                    "@value": result.manifest.event_count,
                    "@type": "xsd:nonNegativeInteger",
                },
                "mns:sha256": result.manifest.sha256,
            },
            {
                "@id": result_iri,
                "@type": ["mns:Result", "mns:ExecutionSummary"],
                "mns:identifier": run_id + "-execution-summary",
                "mns:resultName": "execution_summary",
                "mns:resultJson": {
                    "@value": result.as_dict(),
                    "@type": "@json",
                },
                "mns:derivedFromExecution": {"@id": run_iri},
            },
            run_node,
        ],
    }
