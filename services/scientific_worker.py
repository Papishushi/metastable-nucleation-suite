#!/usr/bin/env python3
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID

HOST = os.environ.get("METASTABLE_WORKER_HOST", "0.0.0.0")
PORT = int(os.environ.get("METASTABLE_WORKER_PORT", "8081"))
ARTIFACTS = Path(os.environ.get("METASTABLE_ARTIFACTS", "/artifacts"))


def canonical_request_id(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("request_id must be a UUID string")
    return str(UUID(value))


class Handler(BaseHTTPRequestHandler):
    server_version = "metastable-scientific-worker/0.1.0"

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
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/experiments":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            experiment_id = request["experiment_id"]
            request_id = canonical_request_id(request["request_id"])
            if not isinstance(experiment_id, str) or not experiment_id.strip():
                raise ValueError("experiment_id must be a non-empty string")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_request"})
            return

        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        artifact = ARTIFACTS / f"{request_id}.json"
        result = {
            "schema_version": "1.0.0",
            "request_id": request_id,
            "experiment_id": experiment_id,
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
