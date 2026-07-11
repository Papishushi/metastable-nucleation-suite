from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable, Iterator, Mapping

from jsonschema import Draft202012Validator, FormatChecker

RFC3339_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    path: str
    media_type: str
    schema_version: str
    event_count: int
    sha256: str
    generated_at_utc: str

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "path": self.path,
            "media_type": self.media_type,
            "schema_version": self.schema_version,
            "event_count": self.event_count,
            "sha256": self.sha256,
            "generated_at_utc": self.generated_at_utc,
        }


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_rfc3339_datetime(value: object, field_name: str = "timestamp_utc") -> None:
    if not isinstance(value, str) or not RFC3339_DATETIME.fullmatch(value):
        raise ValueError(f"{field_name}: expected an RFC 3339 date-time with an explicit timezone")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name}: invalid RFC 3339 date-time {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name}: timezone offset is required")


class EventDatasetWriter:
    def __init__(
        self,
        path: str | Path,
        dataset_id: str,
        schema: Mapping[str, object] | None = None,
        schema_version: str = "1.0.0",
    ) -> None:
        self.path = Path(path)
        self.dataset_id = dataset_id
        self.schema_version = schema_version
        self._validator = (
            Draft202012Validator(dict(schema), format_checker=FormatChecker())
            if schema is not None
            else None
        )
        self._stream = None
        self._count = 0

    def __enter__(self) -> EventDatasetWriter:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = self.path.open("w", encoding="utf-8", newline="\n")
        return self

    def write(self, event: Mapping[str, object]) -> None:
        if self._stream is None:
            raise RuntimeError("dataset writer is not open")
        document = dict(event)
        if "timestamp_utc" in document:
            validate_rfc3339_datetime(document["timestamp_utc"])
        if self._validator is not None:
            errors = sorted(self._validator.iter_errors(document), key=lambda error: list(error.path))
            if errors:
                details = "; ".join(
                    f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors
                )
                raise ValueError(f"event does not satisfy schema: {details}")
        self._stream.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")
        self._count += 1

    def close(self) -> DatasetManifest:
        if self._stream is None:
            raise RuntimeError("dataset writer is not open")
        self._stream.flush()
        self._stream.close()
        self._stream = None
        return DatasetManifest(
            dataset_id=self.dataset_id,
            path=self.path.as_posix(),
            media_type="application/x-ndjson",
            schema_version=self.schema_version,
            event_count=self._count,
            sha256=sha256_file(self.path),
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
        )

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None


def read_events(path: str | Path) -> Iterator[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid NDJSON at line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"event at line {line_number} is not an object")
            yield value


def write_events(
    path: str | Path,
    dataset_id: str,
    events: Iterable[Mapping[str, object]],
    schema: Mapping[str, object] | None = None,
    schema_version: str = "1.0.0",
) -> DatasetManifest:
    writer = EventDatasetWriter(path, dataset_id, schema, schema_version)
    with writer:
        for event in events:
            writer.write(event)
        return writer.close()
