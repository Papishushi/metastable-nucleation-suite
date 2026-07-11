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
    partition_size: int = 100_000,
) -> DatasetManifest:
    normalized = infer_storage_format(path, storage_format)
    if normalized == "ndjson":
        return write_ndjson_events(path, dataset_id, events, schema, schema_version)
    from .parquet_storage import write_parquet_events

    return write_parquet_events(
        path,
        dataset_id,
        events,
        schema,
        schema_version,
        partition_size,
    )


def read_manifest_events(manifest: DatasetManifest) -> Iterator[dict[str, object]]:
    for partition in sorted(manifest.partitions, key=lambda item: item.index):
        yield from read_events(partition.path, manifest.storage_format)


def verify_manifest(manifest: DatasetManifest) -> None:
    count = 0
    hashes = []
    for partition in sorted(manifest.partitions, key=lambda item: item.index):
        actual_hash = sha256_file(partition.path)
        if actual_hash != partition.sha256:
            raise ValueError(f"partition hash mismatch: {partition.path}")
        partition_count = sum(1 for _ in read_events(partition.path, manifest.storage_format))
        if partition_count != partition.event_count:
            raise ValueError(f"partition event count mismatch: {partition.path}")
        count += partition_count
        hashes.append(actual_hash)
    if count != manifest.event_count:
        raise ValueError("dataset event count mismatch")
    if aggregate_dataset_hash(hashes) != manifest.sha256:
        raise ValueError("dataset aggregate hash mismatch")


__all__ = [
    "DatasetManifest",
    "DatasetPartitionManifest",
    "DatasetRegistry",
    "EventDatasetWriter",
    "infer_storage_format",
    "read_events",
    "read_manifest_events",
    "sha256_file",
    "validate_event",
    "validate_rfc3339_datetime",
    "verify_manifest",
    "write_events",
]
