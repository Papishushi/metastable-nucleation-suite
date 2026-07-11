from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate
from rdflib import Graph, Namespace, RDF, URIRef

MNS = Namespace("https://w3id.org/metastable-nucleation-suite/ontology#")


@dataclass(frozen=True)
class ValidationOutcome:
    conforms: bool
    report_text: str
    report_graph: Graph


def validate_abox_json(document: dict, schema: dict) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        messages = [f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors]
        raise ValueError("ABox JSON Schema validation failed:\n" + "\n".join(messages))


def _inline_local_context(document: dict, source: Path) -> dict:
    context = document.get("@context")
    if not isinstance(context, str) or "://" in context:
        return document
    context_path = (source.parent / context).resolve()
    context_document = json.loads(context_path.read_text(encoding="utf-8"))
    inlined = dict(document)
    inlined["@context"] = context_document.get("@context", context_document)
    return inlined


def load_abox(path: str | Path, schema_path: str | Path | None = None) -> Graph:
    source = Path(path)
    document = json.loads(source.read_text(encoding="utf-8"))
    if schema_path is not None:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        validate_abox_json(document, schema)
    document = _inline_local_context(document, source)
    graph = Graph()
    graph.parse(data=json.dumps(document), format="json-ld", publicID=source.resolve().as_uri())
    return graph


def load_tbox(path: str | Path) -> Graph:
    graph = Graph()
    graph.parse(Path(path).as_posix(), format="turtle")
    return graph


def validate_abox(
    abox: Graph,
    shapes_path: str | Path,
    tbox: Graph | None = None,
    inference: str = "rdfs",
) -> ValidationOutcome:
    shapes = Graph()
    shapes.parse(Path(shapes_path).as_posix(), format="turtle")
    conforms, report_graph, report_text = validate(
        data_graph=abox,
        shacl_graph=shapes,
        ont_graph=tbox,
        inference=inference,
        advanced=True,
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=True,
    )
    return ValidationOutcome(bool(conforms), str(report_text), report_graph)


def union_graphs(*graphs: Graph) -> Graph:
    merged = Graph()
    for graph in graphs:
        for triple in graph:
            merged.add(triple)
    return merged


def execute_query(graph: Graph, query: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in graph.query(query):
        rows.append({str(variable): str(value) for variable, value in row.asdict().items()})
    return rows


def execution_iris(graph: Graph) -> Iterable[URIRef]:
    yield from graph.subjects(RDF.type, MNS.Execution)
