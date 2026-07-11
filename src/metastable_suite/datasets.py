from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Iterator, Mapping, Protocol

from jsonschema import Draft202012Validator, FormatChecker

RFC3339_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2