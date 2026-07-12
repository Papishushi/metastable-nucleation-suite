import json
from pathlib import Path

import pytest

from scripts.dataset_storage import main


ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "schemas" / "event.schema.json"


def test_convert_rejects_in_place_source_and_target(tmp_path):
    source = tmp_path / "events.ndjson"
    source.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "event_id": "event-0",
                "run_id": "run-1",
                "specification_id": "E09",
                "trial_index": 0,
                "timestamp_utc": "2026-07-11T02:10:00Z",
                "backend_id": "reference-simulator",
                "outcome": {"metastate": 0},
                "valid": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    original = source.read_bytes()

    with pytest.raises(SystemExit, match="2"):
        main(
            [
                "convert",
                str(source),
                str(source),
                "--dataset-id",
                "same-path",
                "--target-format",
                "ndjson",
                "--registry",
                str(tmp_path / "datasets.registry.json"),
                "--schema",
                str(EVENT_SCHEMA),
            ]
        )

    assert source.read_bytes() == original
