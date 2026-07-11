#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from metastable_suite.power_calibration import run_benchmark_grid

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRID = ROOT / "benchmarks" / "power-calibration.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate Monte Carlo power estimators")
    parser.add_argument("--grid", type=Path, default=DEFAULT_GRID)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    results = run_benchmark_grid(args.grid)
    payload = {
        "passed": all(result.passed for result in results),
        "cases": [result.as_dict() for result in results],
    }
    encoded = json.dumps(payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
