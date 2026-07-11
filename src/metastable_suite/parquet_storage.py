from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .dataset_models import (
    DatasetManifest,
    DatasetPartitionManifest,
    PARQUET_MEDIA_TYPE,
    aggregate_dataset_hash,
    event_validator,
    sha256_file,
    validate_event,
)

_JSON_COLUMNS = ("settings", "outcome", "diagnostics")


def _pyarrow():
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "Parquet support requires the optional 'storage' dependency: "
            "pip install -e '.[storage]'"
        ) from exc
    return pa, pq


def _partition_path(base: Path, index: int, partition_count: int | None = None) -> Path:
    if index == 0 and partition_count == 1:
        return base
    suffix = base.suffix or ".parquet"
    stem = base.name[: -len(suffix)] if base.name.endswith(suffix) else base.name
    return base.with_name(f"{stem}.part-{index:05d}{suffix}")


def _json_dump(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _event_to_row(event: Mapping[str, object]) -> dict[str, object]:
    row = dict(event)
    for name in _JSON_COLUMNS:
        row[name] = _json_dump(row.get(name, {}))
    row["exclusion_reasons"] = list(row.get("exclusion_reasons", []))
    return row


def _row_to_event(row: Mapping[str, object]) -> dict[str, object]:
    event = dict(row)
    for name in _JSON_COLUMNS:
        value = event.get(name)
        event[name] = json.loads(value) if isinstance(value, str) else {}
    event["exclusion_reasons"] = list(event.get("exclusion_reasons") or [])
    return {key: value for key, value in event.items() if value is not None}


def _arrow_schema(pa):
    return pa.schema(
        [
            ("schema_version", pa.string()),
            ("event_id", pa.string()),
            ("run_id", pa.string()),
            ("specification_id", pa.string()),
            ("trial_index", pa.int64()),
            ("timestamp_utc", pa.string()),
            ("backend_id", pa.string()),
            ("settings", pa.string()),
            ("outcome", pa.string()),
            ("diagnostics", pa.string()),
            ("valid", pa.bool_()),
            ("exclusion_reasons", pa.list_(pa.string())),
            ("clock_uncertainty_ns", pa.float64()),
            ("firmware_version", pa.string()),
        ]
    )


def _common_partition_values(events: list[Mapping[str, object]]) -> dict[str, object]:
    values: dict[str, object] = {}
    for key in ("run_id", "specification_id", "backend_id", "schema_version"):
        observed = {event.get(key) for event in events}
        if len(observed) == 1:
            value = next(iter(observed))
            if isinstance(value, (str, int, float, bool)) or value is None:
                values[key] = value
    return values


def _write_partition(
    base: Path,
    dataset_id: str,
    index: int,
    events: list[Mapping[str, object]],
    schema_version: str,
    partition_count: int | None = None,
) -> DatasetPartitionManifest:
    pa, pq = _pyarrow()
    path = _partition_path(base, index, partition_count)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [_event_to_row(event) for event in events]
    table = pa.Table.from_pylist(rows, schema=_arrow_schema(pa))
    metadata = {
        b"mns.dataset_id": dataset_id.encode(),
        b"mns.schema_version": schema_version.encode(),
        b"mns.partition_index": str(index).encode(),
    }
    table = table.replace_schema_metadata(metadata)
    pq.write_table(table, path, compression="zstd")
    return DatasetPartitionManifest(
        partition_id=f"{dataset_id}-part-{index:05d}",
        index=index,
        path=path.as_posix(),
        event_count=len(events),
        sha256=sha256_file(path),
        partition_values=_common_partition_values(events),
    )


def write_parquet_events(
    path: str | Path,
    dataset_id: str,
    events: Iterable[Mapping[str, object]],
    schema: Mapping[str, object] | None = None,
    schema_version: str = "1.0.0",
    partition_size: int = 100_000,
) -> DatasetManifest:
    if partition_size <= 0:
        raise ValueError("partition_size must be positive")

    validator = event_validator(schema)
    base = Path(path)
    partitions: list[DatasetPartitionManifest] = []
    chunk: list[Mapping[str, object]] = []
    event_count = 0

    for event in events:
        chunk.append(validate_event(event, validator))
        event_count += 1
        if len(chunk) == partition_size:
            partitions.append(
                _write_partition(
                    base,
                    dataset_id,
                    len(partitions),
                    chunk,
                    schema_version,
                )
            )
            chunk = []

    if chunk or not partitions:
        partitions.append(
            _write_partition(
                base,
                dataset_id,
                len(partitions),
                chunk,
                schema_version,
                1 if event_count == 0 else None,
            )
        )

    return DatasetManifest(
        dataset_id=dataset_id,
        path=base.as_posix(),
        media_type=PARQUET_MEDIA_TYPE,
        schema_version=schema_version,
        event_count=event_count,
        sha256=aggregate_dataset_hash(partition.sha256 for partition in partitions),
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        storage_format="parquet",
        partitions=tuple(partitions),
    )


def read_parquet_events(path: str | Path) -> Iterator[dict[str, object]]:
    _, pq = _pyarrow()
    table = pq.read_table(path)
    for row in table.to_pylist():
        yield _row_to_event(row)
