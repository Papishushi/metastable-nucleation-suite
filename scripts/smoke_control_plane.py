#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from check_control_plane_contract import validate_openapi


def request_json(
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers=headers or {})
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=10) as response:
        return response.status, json.load(response)


def wait_ready(base_url: str) -> None:
    for _ in range(60):
        try:
            status, _ = request_json(f"{base_url}/healthz")
            if status == 200:
                return
        except (HTTPError, URLError, TimeoutError):
            pass
        time.sleep(1)
    raise RuntimeError("control plane did not become ready")


def submit(base_url: str, state_path: Path) -> None:
    wait_ready(base_url)
    _, openapi = request_json(f"{base_url}/openapi/v1.json")
    validate_openapi(openapi)

    request_id = str(uuid4())
    idempotency_key = f"compose-{uuid4()}"
    envelope = {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "experiment_id": "control-plane-compose-smoke",
        "submitted_at_utc": "2026-07-15T00:00:00Z",
    }
    headers = {"Idempotency-Key": idempotency_key}
    status, run = request_json(
        f"{base_url}/v1/runs",
        payload=envelope,
        headers=headers,
    )
    if status != 201:
        raise RuntimeError(f"first submission returned HTTP {status}")

    duplicate_status, duplicate = request_json(
        f"{base_url}/v1/runs",
        payload=envelope,
        headers=headers,
    )
    if duplicate_status != 200 or duplicate["run_id"] != run["run_id"]:
        raise RuntimeError("idempotent resubmission did not return the original run")

    for _ in range(60):
        _, run = request_json(f"{base_url}/v1/runs/{run['run_id']}")
        if run["state"] in {"succeeded", "failed", "cancelled"}:
            break
        time.sleep(0.5)
    if run["state"] != "succeeded":
        raise RuntimeError(f"control-plane run ended in {run['state']}")

    _, artifact = request_json(
        f"{base_url}/v1/runs/{run['run_id']}/artifacts/primary"
    )
    if artifact["run_id"] != run["run_id"]:
        raise RuntimeError("artifact index refers to another run")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"run_id": run["run_id"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(run["run_id"])


def verify(base_url: str, state_path: Path) -> None:
    wait_ready(base_url)
    saved = json.loads(state_path.read_text(encoding="utf-8"))
    _, run = request_json(f"{base_url}/v1/runs/{saved['run_id']}")
    if run["state"] != "succeeded":
        raise RuntimeError("durable run state was not preserved across restart")
    request_json(f"{base_url}/v1/runs/{saved['run_id']}/artifacts/primary")
    print("control-plane restart smoke: ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("submit", "verify"))
    parser.add_argument("state", type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    if args.mode == "submit":
        submit(args.base_url, args.state)
    else:
        verify(args.base_url, args.state)


if __name__ == "__main__":
    main()
