#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


REQUIRED_PATHS = {
    "/v1/capabilities": "get",
    "/v1/runs": "post",
    "/v1/runs/{runId}": "get",
    "/v1/runs/{runId}/cancel": "post",
    "/v1/runs/{runId}/artifacts/{artifactId}": "get",
}

EXPERIMENT_REQUEST_PROPERTIES = {
    "schema_version",
    "request_id",
    "experiment_id",
    "submitted_at_utc",
}

RUN_PROPERTIES = {
    "schema_version",
    "run_id",
    "request_id",
    "experiment_id",
    "state",
    "created_at_utc",
    "updated_at_utc",
    "artifact",
    "failure",
    "transitions",
}

REQUIRED_RUN_PROPERTIES = RUN_PROPERTIES - {"artifact", "failure"}

ARTIFACT_INDEX_PROPERTIES = {
    "schema_version",
    "run_id",
    "artifact",
    "indexed_at_utc",
}

CAPABILITY_MANIFEST_PROPERTIES = {
    "schema_version",
    "server_version",
    "generated_at_utc",
    "capabilities",
}

CAPABILITY_PROPERTIES = {
    "id",
    "status",
    "since_version",
    "deprecated_since_version",
    "sunset_at_utc",
    "replacement",
}

RFC3339_PATTERN = (
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)


def validate_openapi(document: dict[str, Any]) -> None:
    if document.get("openapi") != "3.1.0":
        raise ValueError("control-plane OpenAPI must use 3.1.0")
    paths = document.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("control-plane OpenAPI has no paths object")
    for path, method in REQUIRED_PATHS.items():
        path_item = paths.get(path)
        if not isinstance(path_item, dict) or method not in path_item:
            raise ValueError(f"missing OpenAPI operation: {method.upper()} {path}")
        operation = path_item[method]
        if not isinstance(operation, dict):
            raise ValueError(f"invalid OpenAPI operation: {method.upper()} {path}")

        expected_parameters = set(re.findall(r"{([^{}]+)}", path))
        declared_parameters = {
            parameter.get("name")
            for parameter in operation.get("parameters", [])
            if isinstance(parameter, dict)
            and parameter.get("in") == "path"
            and parameter.get("required") is True
        }
        if declared_parameters != expected_parameters:
            raise ValueError(
                f"path parameters for {method.upper()} {path} must be "
                f"{sorted(expected_parameters)}, got {sorted(declared_parameters)}"
            )

    schemas = document.get("components", {}).get("schemas", {})
    for name in ("ExperimentRequest", "Run", "ArtifactIndex", "CapabilityManifest"):
        if name not in schemas:
            raise ValueError(f"missing OpenAPI schema: {name}")

    submit = paths["/v1/runs"]["post"]
    responses = submit.get("responses", {})
    for status in ("200", "201"):
        response_schema = (
            responses.get(status, {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        if response_schema.get("$ref") != "#/components/schemas/Run":
            raise ValueError(
                f"POST /v1/runs response {status} must reference Run"
            )

    idempotency_keys = [
        parameter
        for parameter in submit.get("parameters", [])
        if isinstance(parameter, dict)
        and parameter.get("in") == "header"
        and parameter.get("name", "").lower() == "idempotency-key"
        and parameter.get("required") is True
    ]
    if len(idempotency_keys) != 1:
        raise ValueError(
            "POST /v1/runs must declare one required Idempotency-Key header"
        )

    request_body = submit.get("requestBody")
    if not isinstance(request_body, dict) or request_body.get("required") is not True:
        raise ValueError("POST /v1/runs must declare a required request body")
    request_schema = (
        request_body.get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    if request_schema.get("$ref") != "#/components/schemas/ExperimentRequest":
        raise ValueError(
            "POST /v1/runs request body must reference ExperimentRequest"
        )

    experiment_request = schemas["ExperimentRequest"]
    if not isinstance(experiment_request, dict):
        raise ValueError("ExperimentRequest must be an object schema")
    declared_properties = experiment_request.get("properties")
    if not isinstance(declared_properties, dict):
        raise ValueError("ExperimentRequest must declare its properties")
    if set(declared_properties) != EXPERIMENT_REQUEST_PROPERTIES:
        raise ValueError(
            "ExperimentRequest properties must be "
            f"{sorted(EXPERIMENT_REQUEST_PROPERTIES)}, got "
            f"{sorted(declared_properties)}"
        )
    if set(experiment_request.get("required", [])) != EXPERIMENT_REQUEST_PROPERTIES:
        raise ValueError("all ExperimentRequest properties must be required")
    if (
        declared_properties["submitted_at_utc"].get("pattern")
        != RFC3339_PATTERN
    ):
        raise ValueError("ExperimentRequest timestamp must enforce RFC3339 syntax")

    run = schemas["Run"]
    if not isinstance(run, dict) or run.get("type") != "object":
        raise ValueError("Run must be an object schema")
    run_properties = run.get("properties")
    if not isinstance(run_properties, dict) or set(run_properties) != RUN_PROPERTIES:
        raise ValueError(
            f"Run properties must be {sorted(RUN_PROPERTIES)}, got "
            f"{sorted(run_properties) if isinstance(run_properties, dict) else 'none'}"
        )
    if set(run.get("required", [])) != REQUIRED_RUN_PROPERTIES:
        raise ValueError("Run required properties do not match the v1 contract")
    for timestamp in ("created_at_utc", "updated_at_utc"):
        if run_properties[timestamp].get("format") != "date-time":
            raise ValueError(f"Run {timestamp} must use the date-time format")
    transitions = run_properties["transitions"]
    if not isinstance(transitions, dict):
        raise ValueError("Run transitions must be an array schema")
    transition_properties = transitions.get("items", {}).get("properties", {})
    if set(transition_properties) != {"state", "at_utc", "reason"}:
        raise ValueError("Run transitions must declare state, at_utc and reason")

    artifact_index = schemas["ArtifactIndex"]
    artifact_properties = artifact_index.get("properties", {})
    if set(artifact_properties) != ARTIFACT_INDEX_PROPERTIES:
        raise ValueError(
            "ArtifactIndex properties do not match the v1 contract"
        )
    if set(artifact_index.get("required", [])) != ARTIFACT_INDEX_PROPERTIES:
        raise ValueError("all ArtifactIndex properties must be required")
    if artifact_properties["indexed_at_utc"].get("format") != "date-time":
        raise ValueError("ArtifactIndex indexed_at_utc must use date-time")

    capability_manifest = schemas["CapabilityManifest"]
    manifest_properties = capability_manifest.get("properties", {})
    if set(manifest_properties) != CAPABILITY_MANIFEST_PROPERTIES:
        raise ValueError(
            "CapabilityManifest properties do not match the v1 contract"
        )
    if (
        set(capability_manifest.get("required", []))
        != CAPABILITY_MANIFEST_PROPERTIES
    ):
        raise ValueError("all CapabilityManifest properties must be required")
    capability = manifest_properties["capabilities"].get("items", {})
    if set(capability.get("properties", {})) != CAPABILITY_PROPERTIES:
        raise ValueError("Capability properties do not match the v1 contract")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("openapi", type=Path)
    args = parser.parse_args()
    validate_openapi(json.loads(args.openapi.read_text(encoding="utf-8")))
    print("control-plane OpenAPI contract: ok")


if __name__ == "__main__":
    main()
