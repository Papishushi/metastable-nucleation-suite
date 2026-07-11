from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

RFC3339_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
NDJSON_MEDIA_TYPE = "application/x-ndjson"
PARQUET_MEDIA_TYPE = "application/vnd.apache.parquet"
REGISTRY_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class DatasetPartitionManifest:
    partition_id: str
    index: int
    path: str
    event_count: int
    sha256: str
    partition_values: Mapping[str, str | int | float | bool | None]

    def as_dict(self) -> dict[str, object]:
        return {
            "partition_id": self.partition_id,
            "index": self.index,
            "path": self.path,
            "event_count": self.event_count,
            "sha256": self.sha256,
            "partition_values": dict(self.partition_values),
        }

    @classmethod
    def from_dict(cls, document: Mapping[str, Any]) -> DatasetPartitionManifest:
        return cls(
            partition_id=str(document["partition_id"]),
            index=int(document["index"]),
            path=str(document["path"]),
            event_count=int(document["event_count"]),
            sha256=str(document["sha256"]),
            partition_values=dict(document.get("partition_values", {})),
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
    storage_format: str = "ndjson"
    partitions: tuple[DatasetPartitionManifest, ...] = ()

    def as_dict(self) -> dict[str, object]:
        partitions = self.partitions or (
            DatasetPartitionManifest(
                partition_id=f"{self.dataset_id}-part-00000",
                index=0,
                path=self.path,
                event_count=self.event_count,
                sha256=self.sha256,
                partition_values={},
            ),
        )
        return {
            "dataset_id": self.dataset_id,
            "path": self.path,
            "format": self.storage_format,
            "media_type": self.media_type,
            "schema_version": self.schema_version,
            "event_count": self.event_count,
            "sha256": self.sha256,
            "generated_at_utc": self.generated_at_utc,
            "partitions": [partition.as_dict() for partition in partitions],
        }

    @classmethod
    def from_dict(cls, document: Mapping[str, Any]) -> DatasetManifest:
        return cls(
            dataset_id=str(document["dataset_id"]),
            path=str(document["path"]),
            storage_format=str(document.get("format", "ndjson")),
            media_type=str(document["media_type"]),
            schema_version=str(document["schema_version"]),
            event_count=int(document["event_count"]),
            sha256=str(document["sha256"]),
            generated_at_utc=str(document["generated_at_utc"]),
            partitions=tuple(
                DatasetPartitionManifest.from_dict(item)
                for item in document.get("partitions", [])
            ),
        )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_dataset_hash(partition_hashes: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in partition_hashes:
        digest.update(value.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def validate_rfc3339_datetime(value: object, field_name: str = "timestamp_utc") -> None:
    if not isinstance(value, str) or not RFC3339_DATETIME.fullmatch(value):
        raise ValueError(
            f"{field_name}: expected an RFC 3339 date-time with an explicit timezone"
        )
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name}: invalid RFC 3339 date-time {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name}: timezone offset is required")


def validate_event(
    event: Mapping[str, object],
    validator: Draft202012Validator | None,
) -> dict[str, object]:
    document = dict(event)
    if "timestamp_utc" in document:
        validate_rfc3339_datetime(document["timestamp_utc"])
    if validator is not None:
        errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
        if errors:
            details = "; ".join(
                f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
                for error in errors
            )
            raise ValueError(f"event does not satisfy schema: {details}")
    return document


def event_validator(schema: Mapping[str, object] | None) -> Draft202012Validator | None:
    if schema is None:
        return None
    return Draft202012Validator(dict(schema), format_checker=FormatChecker())
