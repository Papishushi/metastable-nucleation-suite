#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metastable_suite.report import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reference null/benchmark models")
    parser.add_argument("--trials", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="artifacts/reference_report.json")
    args = parser.parse_args()
    if args.trials < 10_000:
        parser.error("use at least 10,000 trials for stable reference estimates")
    path = write_report(ROOT / args.output, args.trials, args.seed)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
