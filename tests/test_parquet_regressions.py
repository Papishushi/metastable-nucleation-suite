import json
from pathlib import Path

from metastable_suite.datasets import read_events, write_events


ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = json.loads(
    (ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8")
)


def _event(index: int) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "event_id": f"event-{index}",
        "run_id": "run-1",
        "specification_id": "E09",
        "trial_index": index,
        "timestamp_utc": "2026-07-11T02:10:00Z",
        "backend_id": "reference-simulator",
        "outcome": {"metastate": index},
        "valid": True,
    }


def test_full_single_partition_uses_requested_path(tmp_path):
    target = tmp_path / "events.parquet"
    events = [_event(0), _event(1)]

    manifest = write_events(
        target,
        "full-single-partition",
        events,
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=2,
    )

    assert Path(manifest.path) == target
    assert Path(manifest.partitions[0].path) == target
    assert target.exists()
    assert not (tmp_path / "events.part-00000.parquet").exists()
    assert list(read_events(manifest.path, "parquet")) == events


def test_parquet_round_trip_preserves_omitted_optional_fields(tmp_path):
    event = _event(0)

    manifest = write_events(
        tmp_path / "events.parquet",
        "optional-fields",
        [event],
        EVENT_SCHEMA,
        storage_format="parquet",
    )

    assert list(read_events(manifest.path, "parquet")) == [event]
