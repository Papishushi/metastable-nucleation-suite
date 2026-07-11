import json
from pathlib import Path

import pytest

from metastable_suite.datasets import EventDatasetWriter

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))


def event(timestamp_utc: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "event_id": "event-1",
        "run_id": "run-1",
        "specification_id": "E09",
        "trial_index": 0,
        "timestamp_utc": timestamp_utc,
        "backend_id": "reference-simulator",
        "settings": {},
        "outcome": {"metastate": 1},
        "diagnostics": {},
        "valid": True,
        "exclusion_reasons": [],
        "firmware_version": "test",
    }


def test_valid_utc_timestamp_is_written_and_manifested(tmp_path):
    target = tmp_path / "events.ndjson"
    writer = EventDatasetWriter(target, "dataset-1", SCHEMA)
    with writer:
        writer.write(event("2026-07-11T02:10:00Z"))
        manifest = writer.close()
    assert manifest.event_count == 1
    assert target.exists()


@pytest.mark.parametrize(
    "timestamp",
    [
        "not-a-date",
        "2026-07-11T02:10:00",
        "2026-13-99T25:61:61Z",
    ],
)
def test_invalid_or_timezone_less_timestamps_are_rejected(tmp_path, timestamp):
    target = tmp_path / "events.ndjson"
    writer = EventDatasetWriter(target, "dataset-1", SCHEMA)
    with writer:
        with pytest.raises(ValueError, match="timestamp_utc"):
            writer.write(event(timestamp))
