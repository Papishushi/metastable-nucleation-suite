from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from datetime import datetime, timezone
from pathlib import Path

from .dataset_models import (
    NDJSON_MEDIA_TYPE,
    DatasetManifest,
    DatasetPartitionManifest,
    event_validator,
    sha256_file,
    validate_event,
)


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
        self._validator = event_validator(schema)
        self._stream = None
        self._count = 0

    # Keep Python 3.10 support without adding typing_extensions solely for Self.
    def __enter__(self) -> EventDatasetWriter:  # noqa: PYI034
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = self.path.open("w", encoding="utf-8", newline="\n")
        return self

    def write(self, event: Mapping[str, object]) -> None:
        if self._stream is None:
            raise RuntimeError("dataset writer is not open")
        document = validate_event(event, self._validator)
        self._stream.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")
        self._count += 1

    def close(self) -> DatasetManifest:
        if self._stream is None:
            raise RuntimeError("dataset writer is not open")
        self._stream.flush()
        self._stream.close()
        self._stream = None
        digest = sha256_file(self.path)
        partition = DatasetPartitionManifest(
            partition_id=f"{self.dataset_id}-part-00000",
            index=0,
            path=self.path.as_posix(),
            event_count=self._count,
            sha256=digest,
            partition_values={},
        )
        return DatasetManifest(
            dataset_id=self.dataset_id,
            path=self.path.as_posix(),
            media_type=NDJSON_MEDIA_TYPE,
            schema_version=self.schema_version,
            event_count=self._count,
            sha256=digest,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            storage_format="ndjson",
            partitions=(partition,),
        )

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None


def read_ndjson_events(path: str | Path) -> Iterator[dict[str, object]]:
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
                # Preserve the corrupt-artifact contract used by campaign resume.
                raise ValueError(  # noqa: TRY004
                    f"event at line {line_number} is not an object"
                )
            yield value


def write_ndjson_events(
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
