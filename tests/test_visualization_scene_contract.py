import hashlib
import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "contracts/v1/visualization-scene.schema.json"
FIXTURE_PATH = ROOT / "contracts/v1/fixtures/visualization-scene-e09.json"
EVENT_SCHEMA_PATH = ROOT / "schemas/event.schema.json"
EVENT_FIXTURE_PATH = ROOT / "contracts/v1/fixtures/e09-event-000042.json"
CONFORMANCE_PATH = (
    ROOT / "contracts/v1/fixtures/visualization-scene-conformance.json"
)
EVENT_FIXTURE_PATHS = [
    EVENT_FIXTURE_PATH,
    ROOT / "contracts/v1/fixtures/e09-event-000042-node-b.json",
    ROOT / "contracts/v1/fixtures/e09-event-000043-node-b-invalid.json",
]


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


def test_e09_source_events_match_event_contract():
    schema = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    for fixture_path in EVENT_FIXTURE_PATHS:
        validator.validate(json.loads(fixture_path.read_text(encoding="utf-8")))


def test_e09_visualization_provenance_hashes_match_repository_fixtures():
    scene = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    for artifact in scene["provenance"]:
        source_path = ROOT / artifact["uri"]
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()

        assert digest == artifact["sha256"]


def test_python_json_schema_validator_matches_shared_conformance_corpus():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    corpus = json.loads(CONFORMANCE_PATH.read_text(encoding="utf-8"))
    base = json.loads((ROOT / corpus["base_scene"]).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    for case in corpus["cases"]:
        scene = deepcopy(base)
        for operation in case["operations"]:
            assert operation["op"] == "replace"
            target = scene
            segments = operation["path"].strip("/").split("/")
            for segment in segments[:-1]:
                target = target[int(segment)] if isinstance(target, list) else target[segment]
            final = segments[-1]
            if isinstance(target, list):
                target[int(final)] = operation["value"]
            else:
                target[final] = operation["value"]

        document = json.dumps(scene) + case.get("suffix", "")
        try:
            parsed_scene = json.loads(document)
        except json.JSONDecodeError:
            accepted = False
        else:
            accepted = validator.is_valid(parsed_scene)

        assert accepted is case["valid"], case["name"]
