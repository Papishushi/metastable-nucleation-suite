from pathlib import Path

from scripts.validate_catalog import validate


def test_catalog_is_valid():
    root = Path(__file__).resolve().parents[1]
    assert validate(root / "experiments" / "catalog.yaml") == []
