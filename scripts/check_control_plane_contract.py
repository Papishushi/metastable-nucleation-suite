#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
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
        operation = paths.get(path)
        if not isinstance(operation, dict) or method not in operation:
            raise ValueError(f"missing OpenAPI operation: {method.upper()} {path}")

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
