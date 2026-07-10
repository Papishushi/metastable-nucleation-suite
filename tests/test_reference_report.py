import json
from pathlib import Path

from scripts.validate_reference_report import validate_report


def test_reference_report_is_statistically_valid():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "examples" / "reference-report.json").read_text(encoding="utf-8"))
    assert validate_report(report) == []
