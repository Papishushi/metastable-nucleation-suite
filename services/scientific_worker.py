#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from typing import Any
from uuid import UUID

HOST = os.environ.get("METASTABLE_WORKER_HOST", "0.0.0.0")
PORT = int(os.environ.get("METASTABLE_WORKER_PORT", "8081"))
CAPABILITY_SCHEMA_VERSION = "1.0.0"
REQUEST_FIELDS = frozenset(
    {"schema_version", "request_id", "experiment_id", "submitted_at_utc"}
)
RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
CAPABILITIES = (
    {
        "id": "experiments.execute.v1",
        "status": "active",
        "since_version": "0.1.0",
    },
    {
        "id": "server.capabilities.v1",
        "status": "active",
        "since_version": "0.1.0",
    },
)


def resolve_server_version(
    configured_version: str | None = None,
    *,
    version_paths: tuple[Path, ...] | None = None,
) -> str:
    configured = (configured_version or "").strip()
    if configured:
        return configured

    candidates = version_paths or (
        Path(__file__).resolve().parent / "VERSION",
        Path(__file__).resolve().parents[1] / "VERSION",
    )
    for candidate in dict.fromkeys(candidates):
        try:
            version = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if version:
            return version

    return "0.0.0+unknown"


SERVER_VERSION = resolve_server_version(os.environ.get("METASTABLE_VERSION"))


def resolve_artifacts_path(configured_path: str | None = None) -> Path:
    if configured_path:
        return Path(configured_path).expanduser()
    return Path.home() / ".metastable-nucleation-suite" / "artifacts"


ARTIFACTS = resolve_artifacts_path(os.environ.get("METASTABLE_ARTIFACTS"))


def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def capability_manifest(*, generated_at_utc: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": CAPABILITY_SCHEMA_VERSION,
        "server_version": SERVER_VERSION,
        "generated_at_utc": generated_at_utc or utc_now_rfc3339(),
        "capabilities": [dict(capability) for capability in CAPABILITIES],
    }


def canonical_request_id(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("request_id must be a UUID string")
    return str(UUID(value))


def validate_request_envelope(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != REQUEST_FIELDS:
        raise ValueError("request must contain exactly the v1 envelope fields")
    if value["schema_version"] != "1.0.0":
        raise ValueError("unsupported schema_version")

    request_id = canonical_request_id(value["request_id"])
    experiment_id = value["experiment_id"]
    if (
        not isinstance(experiment_id, str)
        or not experiment_id.strip()
        or len(experiment_id) > 128
    ):
        raise ValueError("experiment_id must contain between 1 and 128 characters")

    submitted_at_utc = value["submitted_at_utc"]
    if not isinstance(submitted_at_utc, str) or not RFC3339_DATE_TIME.fullmatch(
        submitted_at_utc
    ):
        raise ValueError("submitted_at_utc must be an RFC 3339 date-time string")
    normalized_timestamp = (
        submitted_at_utc[:-1] + "+00:00"
        if submitted_at_utc[-1] in {"Z", "z"}
        else submitted_at_utc
    )
    try:
        parsed_timestamp = datetime.fromisoformat(normalized_timestamp)
    except ValueError as exc:
        raise ValueError("submitted_at_utc must be a valid date-time") from exc
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() is None:
        raise ValueError("submitted_at_utc must include a UTC offset")

    return {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "experiment_id": experiment_id,
        "submitted_at_utc": submitted_at_utc,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = f"metastable-scientific-worker/{SERVER_VERSION}"

    def _json(self, status: int, document: dict[str, Any]) -> None:
        payload = json.dumps(document, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._json(200, {"status": "ok"})
            return
        if self.path == "/v1/capabilities":
            self._json(200, capability_manifest())
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/experiments":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = validate_request_envelope(json.loads(self.rfile.read(length)))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_request"})
            return

        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        artifact = ARTIFACTS / f"{request['request_id']}.json"
        result = {
            "schema_version": "1.0.0",
            "request_id": request["request_id"],
            "experiment_id": request["experiment_id"],
            "status": "completed",
            "artifact": artifact.as_posix(),
        }
        artifact.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        self._json(200, result)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}", flush=True)


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"scientific worker listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
