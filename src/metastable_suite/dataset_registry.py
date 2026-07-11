from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .dataset_models import DatasetManifest, REGISTRY_SCHEMA_VERSION


class DatasetRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": REGISTRY_SCHEMA_VERSION, "datasets": {}}
        document = json.loads(self.path.read_text(encoding="utf-8"))
        if document.get("schema_version") != REGISTRY_SCHEMA_VERSION:
            raise ValueError("unsupported dataset registry schema version")
        if not isinstance(document.get("datasets"), dict):
            raise ValueError("dataset registry must contain a datasets object")
        return document

    def _write(self, document: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.path)

    def register(self, manifest: DatasetManifest, replace: bool = False) -> None:
        document = self._read()
        datasets = document["datasets"]
        existing = datasets.get(manifest.dataset_id)
        serialized = manifest.as_dict()
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
        return DatasetManifest.from_dict(value)

    def manifests(self) -> list[DatasetManifest]:
        document = self._read()
        return [
            DatasetManifest.from_dict(document["datasets"][dataset_id])
            for dataset_id in sorted(document["datasets"])
        ]
