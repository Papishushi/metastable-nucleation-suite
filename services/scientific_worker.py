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
        raise ValueError