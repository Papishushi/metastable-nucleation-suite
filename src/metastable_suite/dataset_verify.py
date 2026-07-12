from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .dataset_models import DatasetManifest, aggregate_dataset_hash, sha256_file


def _read_partition(path: str, storage_format: str) -> Iterator[dict[str, object]]:
    if storage_format == "ndjson":
        from .dataset_ndjson import read_ndjson_events

        yield from read_ndjson_events(path)
        return
    from .parquet_storage import read_parquet_events

    yield from read_parquet_events(path)


def _verify_parquet_directory_contents(manifest: DatasetManifest) -> None:
    if manifest.storage_format != "parquet":
        return

    dataset_path = Path(manifest.path)
    if not dataset_path.is_dir():
        return

    expected_paths = {Path(partition.path).resolve() for partition in manifest.partitions}
    actual_paths = {
        partition_path.resolve() for partition_path in dataset_path.glob("part-*.parquet")
    }

    unexpected_paths = sorted(actual_paths - expected_paths)
    if unexpected_paths:
        unexpected = ", ".join(path.as_posix() for path in unexpected_paths)
        raise ValueError(f"unmanifested Parquet partition(s): {unexpected}")

    missing_paths = sorted(expected_paths - actual_paths)
    if missing_paths:
        missing = ", ".join(path.as_posix() for path in missing_paths)
        raise ValueError(
            f"manifested Parquet partition(s) missing from dataset directory: {missing}"
        )


def verify_manifest(manifest: DatasetManifest) -> None:
    _verify_parquet_directory_contents(manifest)

    count = 0
    hashes: list[str] = []
    for partition in sorted(manifest.partitions, key=lambda item: item.index):
        actual_hash = sha256_file(partition.path)
        if actual_hash != partition.sha256:
            raise ValueError(f"partition hash mismatch: {partition.path}")
        partition_count = sum(
            1 for _ in _read_partition(partition.path, manifest.storage_format)
        )
        if partition_count != partition.event_count:
            raise ValueError(f"partition event count mismatch: {partition.path}")
        count += partition_count
        hashes.append(actual_hash)
    if count != manifest.event_count:
        raise ValueError("dataset event count mismatch")
    expected_hash = (
        hashes[0]
        if manifest.storage_format == "ndjson" and len(hashes) == 1
        else aggregate_dataset_hash(hashes)
    )
    if expected_hash != manifest.sha256:
        raise ValueError("dataset aggregate hash mismatch")
