from __future__ import annotations

from typing import Any

from .datasets import DatasetManifest

RESOURCE = "https://w3id.org/metastable-nucleation-suite/resource/"


def manifest_to_abox(manifest: DatasetManifest, registry_path: str | None = None) -> dict[str, Any]:
    """Represent NDJSON and Parquet manifests through the same mns:Dataset model."""
    dataset_iri = RESOURCE + "dataset/" + manifest.dataset_id
    partition_refs = [
        {"@id": f"{dataset_iri}/partition/{partition.index}"} for partition in manifest.partitions
    ]
    dataset: dict[str, Any] = {
        "@id": dataset_iri,
        "@type": "mns:Dataset",
        "mns:identifier": manifest.dataset_id,
        "mns:datasetPath": manifest.path,
        "mns:storageFormat": manifest.storage_format,
        "mns:mediaType": manifest.media_type,
        "mns:schemaVersion": manifest.schema_version,
        "mns:eventCount": {"@value": manifest.event_count, "@type": "xsd:nonNegativeInteger"},
        "mns:partitionCount": {
            "@value": len(manifest.partitions),
            "@type": "xsd:positiveInteger",
        },
        "mns:sha256": manifest.sha256,
        "mns:hasDatasetPartition": partition_refs,
    }
    if registry_path is not None:
        dataset["mns:datasetRegistryPath"] = registry_path

    partitions = []
    for partition in manifest.partitions:
        partitions.append(
            {
                "@id": f"{dataset_iri}/partition/{partition.index}",
                "@type": "mns:DatasetPartition",
                "mns:identifier": partition.partition_id,
                "mns:partitionIndex": {
                    "@value": partition.index,
                    "@type": "xsd:nonNegativeInteger",
                },
                "mns:partitionPath": partition.path,
                "mns:partitionEventCount": {
                    "@value": partition.event_count,
                    "@type": "xsd:nonNegativeInteger",
                },
                "mns:partitionSha256": partition.sha256,
                "mns:partitionValuesJson": {
                    "@value": dict(partition.partition_values),
                    "@type": "@json",
                },
            }
        )

    return {
        "@context": {
            "mns": "https://w3id.org/metastable-nucleation-suite/ontology#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": [dataset, *partitions],
    }
