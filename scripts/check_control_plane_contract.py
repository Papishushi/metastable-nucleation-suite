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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("openapi", type=Path)
    args = parser.parse_args()
    validate_openapi(json.loads(args.openapi.read_text(encoding="utf-8")))
    print("control-plane OpenAPI contract: ok")


if __name__ == "__main__":
    main()
