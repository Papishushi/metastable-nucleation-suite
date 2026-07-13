import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "contracts/v1/visualization-scene.schema.json"
FIXTURE_PATH = ROOT / "contracts/v1/fixtures/visualization-scene-e09.json"
EVENT_SCHEMA_PATH = ROOT / "schemas/event.schema.json"
EVENT_FIXTURE_PATH = ROOT / "contracts/v1/fixtures/e09-event-000042.json"


def test_e09_visualization_scene_matches_v1_contract():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(fixture)


def test_visualization_scene_contract_is_itself_valid_json_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)


def test_e09_source_event_matches_event_contract():
    schema = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(EVENT_FIXTURE_PATH.read_text(encoding="utf-8"))

    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(fixture)


def test_e09_visualization_provenance_hashes_match_repository_fixtures():
    scene = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    for artifact in scene["provenance"]:
        source_path = ROOT / artifact["uri"]
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()

        assert digest == artifact["sha256"]
