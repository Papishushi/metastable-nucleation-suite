import json
from pathlib import Path

from metastable_suite.datasets import read_events, write_events


ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = json.loads((ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))


def test_single_partition_parquet_uses_requested_path(tmp_path):
    event = {
        "schema_version": "1.0.0",
        "event_id": "event-0",
        "run_id": "run-1",
        "specification_id": "E09",
        "trial_index": 0,
        "timestamp_utc": "2026-07-11T02:10:00Z",
        "backend_id": "reference-simulator",
        "settings": {},
        "outcome": {"metastate": 0},
        "diagnostics": {},
        "valid": True,
        "exclusion_reasons": [],
    }
    target = tmp_path / "events.parquet"

    manifest = write_events(
        target,
        "single-partition",
        [event],
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=100,
    )

    assert Path(manifest.partitions[0].path) == target
    assert list(read_events(manifest.path, "parquet")) == [event]
