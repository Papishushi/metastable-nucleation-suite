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


def _verify_dataset_path_contract(manifest: DatasetManifest) -> None:
    dataset_path = Path(manifest.path).resolve()
    partition_paths = [Path(partition.path).resolve() for partition in manifest.partitions]

    if manifest.storage_format == "ndjson":
        if len(partition_paths) != 1 or partition_paths[0] != dataset_path:
            raise ValueError("NDJSON dataset path must match its single partition path")
        return

    if dataset_path.is_dir():
        expected_paths = set(partition_paths)
        actual_paths = {
            partition_path.resolve()
            for partition_path in dataset_path.glob("part-*.parquet")
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
        return

    if len(partition_paths) != 1 or partition_paths[0] != dataset_path:
        raise ValueError("single-file Parquet dataset path must match its partition path")


def verify_manifest(manifest: DatasetManifest) -> None:
    _verify_dataset_path_contract(manifest)

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
