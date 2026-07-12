from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .dataset_models import DatasetManifest, DatasetPartitionManifest, sha256_file
from .dataset_ndjson import EventDatasetWriter, read_ndjson_events, write_ndjson_events
from .dataset_registry import DatasetRegistry
from .dataset_verify import verify_manifest


def infer_storage_format(path: str | Path, storage_format: str | None = None) -> str:
    value = storage_format.lower() if storage_format else (
        "parquet" if Path(path).suffix.lower() == ".parquet" else "ndjson"
    )
    if value not in {"ndjson", "parquet"}:
        raise ValueError(f"unsupported dataset format {value!r}")
    return value


def read_events(
    path: str | Path,
    storage_format: str | None = None,
) -> Iterator[dict[str, object]]:
    value = infer_storage_format(path, storage_format)
    if value == "ndjson":
        yield from read_ndjson_events(path)
    else:
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
    value = infer_storage_format(path, storage_format)
    if value == "ndjson":
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


__all__ = [
    "DatasetManifest",
    "DatasetPartitionManifest",
    "DatasetRegistry",
    "EventDatasetWriter",
    "infer_storage_format",
    "read_events",
    "read_manifest_events",
    "sha256_file",
    "verify_manifest",
    "write_events",
]
