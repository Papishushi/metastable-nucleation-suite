from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as installed_version
from pathlib import Path

PACKAGE_NAME = "metastable-nucleation-suite"


def resolve_version() -> str:
    source_version = Path(__file__).resolve().parents[2] / "VERSION"
    if source_version.is_file():
        return source_version.read_text(encoding="utf-8").strip()
    try:
        return installed_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0+unknown"


VERSION = resolve_version()
