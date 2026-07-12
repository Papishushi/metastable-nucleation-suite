from dataclasses import replace
import json
from pathlib import Path

import pytest

from metastable_suite.datasets import (
    DatasetRegistry,
    read_events,
    verify_manifest,
    write_events,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = json.loads(
    (ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8")
)


def _event(index: int, outcome: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "event_id": f"event-{index}",
        "run_id": "run-1",
        "specification_id": "E09",
        "trial_index": index,
        "timestamp_utc": "2026-07-12T10:00:00Z",
        "backend_id": "reference-simulator",
        "outcome": outcome if outcome is not None else {"metastate": index},
        "valid": True,
    }


def test_verification_rejects_missing_multipart_dataset_root(tmp_path):
    manifest = write_events(
        tmp_path / "events.parquet",
        "multipart-root",
        [_event(0), _event(1), _event(2)],
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=2,
    )
    missing_root = tmp_path / "missing.parquet"
    inconsistent = replace(manifest, path=missing_root.as_posix())

    with pytest.raises(ValueError, match="single-file Parquet dataset path"):
        verify_manifest(inconsistent)


def test_parquet_writer_snapshots_reused_mutable_payloads(tmp_path):
    shared_outcome: dict[str, object] = {"metastate": 0}

    def events():
        for index in range(3):
            shared_outcome["metastate"] = index
            yield _event(index, shared_outcome)

    manifest = write_events(
        tmp_path / "events.parquet",
        "mutable-payloads",
        events(),
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=10,
    )

    stored = list(read_events(manifest.path, "parquet"))
    assert [event["outcome"] for event in stored] == [
        {"metastate": 0},
        {"metastate": 1},
        {"metastate": 2},
    ]


def test_verification_rejects_media_type_format_mismatch(tmp_path):
    manifest = write_events(
        tmp_path / "events.ndjson",
        "media-type-mismatch",
        [_event(0)],
        EVENT_SCHEMA,
    )

    inconsistent = replace(manifest, media_type="application/vnd.apache.parquet")
    with pytest.raises(ValueError, match="media type does not match"):
        verify_manifest(inconsistent)


def test_verification_rejects_non_contiguous_partition_indexes(tmp_path):
    manifest = write_events(
        tmp_path / "events.parquet",
        "bad-indexes",
        [_event(0), _event(1), _event(2)],
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=2,
    )
    bad_second = replace(manifest.partitions[1], index=2)
    inconsistent = replace(manifest, partitions=(manifest.partitions[0], bad_second))

    with pytest.raises(ValueError, match="indexes must be unique and contiguous"):
        verify_manifest(inconsistent)


def test_verification_rejects_duplicate_partition_paths(tmp_path):
    manifest = write_events(
        tmp_path / "events.parquet",
        "duplicate-paths",
        [_event(0), _event(1), _event(2)],
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=2,
    )
    duplicate_second = replace(
        manifest.partitions[1],
        path=manifest.partitions[0].path,
    )
    inconsistent = replace(
        manifest,
        partitions=(manifest.partitions[0], duplicate_second),
    )

    with pytest.raises(ValueError, match="partition paths must be unique"):
        verify_manifest(inconsistent)


def test_verification_rejects_event_schema_version_mismatch(tmp_path):
    manifest = write_events(
        tmp_path / "events.ndjson",
        "schema-version-mismatch",
        [_event(0)],
        EVENT_SCHEMA,
    )

    inconsistent = replace(manifest, schema_version="2.0.0")
    with pytest.raises(ValueError, match="event schema version mismatch"):
        verify_manifest(inconsistent)


def test_registry_rejects_key_manifest_id_mismatch(tmp_path):
    manifest = write_events(
        tmp_path / "events.ndjson",
        "actual-id",
        [_event(0)],
        EVENT_SCHEMA,
    )
    registry_path = tmp_path / "datasets.registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "datasets": {"wrong-key": manifest.as_dict()},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match manifest dataset_id"):
        DatasetRegistry(registry_path).manifests()


def test_registry_rejects_non_canonical_extra_properties(tmp_path):
    manifest = write_events(
        tmp_path / "events.ndjson",
        "extra-property",
        [_event(0)],
        EVENT_SCHEMA,
    )
    entry = manifest.as_dict()
    entry["unexpected"] = True
    registry_path = tmp_path / "datasets.registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "datasets": {manifest.dataset_id: entry},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="is not canonical"):
        DatasetRegistry(registry_path).get(manifest.dataset_id)
