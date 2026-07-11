from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .dataset_models import (
    DatasetManifest,
    DatasetPartitionManifest,
    aggregate_dataset_hash,
    sha256_file,
    validate_event,
    validate_rfc3339_datetime,
)
from .dataset_ndjson import EventDatasetWriter, read_ndjson_events, write_ndjson_events
from .dataset_registry import DatasetRegistry


def infer_storage_format(path: str | Path, storage_format: str | None = None) -> str:
    if storage_format is not None:
        normalized = storage_format.lower()
    else:
        suffix = Path(path).suffix.lower()
        normalized = "parquet" if suffix == ".parquet" else "ndjson"
    if normalized not in {"ndjson", "parquet"}:
        raise ValueError(f"unsupported dataset format {normalized!r}")
    return normalized


def read_events(
    path: str | Path,
    storage_format: str | None = None,
) -> Iterator[dict[str, object]]:
    normalized = infer_storage_format(path, storage_format)
    if normalized == "ndjson":
        yield from read_ndjson_events(path)
        return
    from .parquet_storage import read_parquet_events

    yield from read_parquet_events(path)


def write_events(
    path: str | Path,
    dataset_id: str,
    events: Iterable[Mapping[str, object]],
    schema: Mapping[str, object] | None = None,
    schema_version: str = "1.0.0",
    storage_format: str | None = None,
   