import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from rdflib import Graph
from pyshacl import validate

from metastable_suite.dataset_semantics import manifest_to_abox
from metastable_suite.datasets import (
    DatasetRegistry,
    read_manifest_events,
    verify_manifest,
    write_events,
)

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = json.loads((ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
REGISTRY_SCHEMA = json.loads(
    (ROOT / "schemas" / "dataset-registry.schema.json").read_text(encoding="utf-8")
)


def _event(index: int) -> dict:
    return {
        "schema_version": "1.0.0",
        "event_id": f"event-{index}",
        "run_id": "run-1",
        "specification_id": "E09",
        "trial_index": index,
        "timestamp_utc": "2026-07-11T02:10:00Z",
        "backend_id": "reference-simulator",
        "settings": {"phase": index, "enabled": True},
        "outcome": {"metastate": index % 2, "score": index + 0.25},
        "diagnostics": {"temperature": 21.5, "stable": True},
        "valid": index != 2,
        "exclusion_reasons": ["synthetic_exclusion"] if index == 2 else [],
        "firmware_version": "test",
    }


def test_parquet_round_trip_preserves_schema_values_and_partitions(tmp_path):
    expected = [_event(index) for index in range(5)]
    manifest = write_events(
        tmp_path / "events.parquet",
        "dataset-parquet",
        expected,
        EVENT_SCHEMA,
        storage_format="parquet",
        partition_size=2,
    )

    assert list(read_manifest_events(manifest)) == expected
    assert manifest.storage_format == "parquet"
    assert manifest.media_type == "application/vnd.apache.parquet"
    assert [partition.event_count for partition in manifest.partitions] == [2, 2, 1]
    assert manifest.partitions[0].partition_values["run_id"] == "run-1"
    verify_manifest(manifest)


def test_registry_records_format_schema_partitions_and_hashes(tmp_path):
    manifest = write_events(
        tmp_path / "events.ndjson",
        "dataset-ndjson",
        [_event(0), _event(1)],
        EVENT_SCHEMA,
    )
    registry_path = tmp_path / "datasets.registry.json"
    registry = DatasetRegistry(registry_path)
    registry.register(manifest)

    document = json.loads(registry_path.read_text(encoding="utf-8"))
    Draft202012Validator(REGISTRY_SCHEMA).validate(document)
    assert registry.get(manifest.dataset_id) == manifest
    assert document["datasets"][manifest.dataset_id]["format"] == "ndjson"
    assert document["datasets"][manifest.dataset_id]["schema_version"] == "1.0.0"
    assert len(document["datasets"][manifest.dataset_id]["partitions"]) == 1


def test_rdf_manifest_uses_same_dataset_model_for_ndjson_and_parquet(tmp_path):
    shapes = Graph().parse(ROOT / "ontology" / "dataset-storage-shapes.ttl")
    ontology = Graph().parse(ROOT / "ontology" / "tbox.ttl")
    ontology.parse(ROOT / "ontology" / "dataset-storage-extension.ttl")

    for storage_format, suffix in (("ndjson", "ndjson"), ("parquet", "parquet")):
        manifest = write_events(
            tmp_path / f"events.{suffix}",
            f"dataset-{storage_format}",
            [_event(0), _event(1), _event(2)],
            EVENT_SCHEMA,
            storage_format=storage_format,
            partition_size=2,
        )
        document = manifest_to_abox(manifest, "datasets.registry.json")
        graph = Graph().parse(data=json.dumps(document), format="json-ld")
        conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=ontology)
        assert conforms, report
        dataset = document["@graph"][0]
        assert dataset["@type"] == "mns:Dataset"
        assert dataset["mns:storageFormat"] == storage_format


def test_integrity_verification_detects_partition_tampering(tmp_path):
    manifest = write_events(
        tmp_path / "events.parquet",
        "dataset-parquet",
        [_event(0)],
        EVENT_SCHEMA,
        storage_format="parquet",
    )
    partition = Path(manifest.partitions[0].path)
    partition.write_bytes(partition.read_bytes() + b"tampered")

    with pytest.raises(ValueError, match="hash mismatch"):
        verify_manifest(manifest)
