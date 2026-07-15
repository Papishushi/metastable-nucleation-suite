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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("openapi", type=Path)
    args = parser.parse_args()
    validate_openapi(json.loads(args.openapi.read_text(encoding="utf-8")))
    print("control-plane OpenAPI contract: ok")


if __name__ == "__main__":
    main()
