from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .dataset_models import DatasetManifest, REGISTRY_SCHEMA_VERSION


def _parse_registry_manifest(dataset_id: str, value: object) -> DatasetManifest:
    if not isinstance(value, Mapping):
        raise ValueError(f"dataset registry entry {dataset_id!r} must be an object")
    try:
        manifest = DatasetManifest.from_dict(value)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid dataset registry entry {dataset_id!r}: {exc}") from exc
    if manifest.dataset_id != dataset_id:
        raise ValueError(
            f"dataset registry key {dataset_id!r} does not match manifest dataset_id "
            f"{manifest.dataset_id!r}"
        )
    if manifest.as_dict() != dict(value):
        raise ValueError(f"dataset registry entry {dataset_id!r} is not canonical")
    return manifest


class DatasetRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": REGISTRY_SCHEMA_VERSION, "datasets": {}}
        document = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("dataset registry must be an object")
        if set(document) != {"schema_version", "datasets"}:
            raise ValueError("dataset registry contains unsupported properties")
        if document.get("schema_version") != REGISTRY_SCHEMA_VERSION:
            raise ValueError("unsupported dataset registry schema version")
        datasets = document.get("datasets")
        if not isinstance(datasets, dict):
            raise ValueError("dataset registry must contain a datasets object")
        for dataset_id, value in datasets.items():
            _parse_registry_manifest(dataset_id, value)
        return document

    def _write(self, document: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.path)

    def register(self, manifest: DatasetManifest, replace: bool = False) -> None:
        document = self._read()
        datasets = document["datasets"]
        existing = datasets.get(manifest.dataset_id)
        serialized = manifest.as_dict()
        _parse_registry_manifest(manifest.dataset_id, serialized)
        if existing is not None and existing != serialized and not replace:
            raise ValueError(f"dataset {manifest.dataset_id!r} is already registered")
        datasets[manifest.dataset_id] = serialized
        self._write(document)

    def get(self, dataset_id: str) -> DatasetManifest:
        document = self._read()
        try:
            value = document["datasets"][dataset_id]
        except KeyError as exc:
            raise KeyError(f"dataset {dataset_id!r} is not registered") from exc
        return _parse_registry_manifest(dataset_id, value)

    def manifests(self) -> list[DatasetManifest]:
        document = self._read()
        return [
            _parse_registry_manifest(dataset_id, document["datasets"][dataset_id])
            for dataset_id in sorted(document["datasets"])
        ]
