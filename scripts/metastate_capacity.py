#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from metastable_suite.metastate_capacity import MetastateCapacityScenario, scenarios_as_dicts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate information density, rewrite energy and compute density for an addressable "
            "three-dimensional metastable medium. Without --custom, prints documented reference scenarios."
        )
    )
    parser.add_argument("--custom", action="store_true", help="evaluate one custom scenario")
    parser.add_argument("--name", default="custom")
    parser.add_argument(
        "--evidence-level",
        choices=["measured", "engineering_scenario", "speculative_bound"],
        default="engineering_scenario",
    )
    parser.add_argument("--density-kg-m3", type=float)
    parser.add_argument("--pitch-nm", type=float)
    parser.add_argument("--states", type=int)
    parser.add_argument("--active-volume-fraction", type=float, default=1.0)
    parser.add_argument("--coding-efficiency", type=float, default=1.0)
    parser.add_argument("--write-energy-j", type=float, default=0.0)
    parser.add_argument("--operation-energy-j", type=float, default=0.0)
    parser.add_argument("--event-rate-hz", type=float, default=0.0)
    parser.add_argument("--active-utilization", type=float, default=1.0)
    parser.add_argument("--operations-per-event", type=float, default=1.0)
    parser.add_argument("--multiplexing-factor", type=float, default=1.0)
    parser.add_argument("--temperature-k", type=float, default=300.0)
    parser.add_argument(
        "--power-budget-w-per-kg",
        type=float,
        default=1000.0,
        help="cooling/power budget used for the thermal-limited throughput estimate",
    )
    parser.add_argument("--output")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.custom:
            missing = [
                flag
                for flag, value in (
                    ("--density-kg-m3", args.density_kg_m3),
                    ("--pitch-nm", args.pitch_nm),
                    ("--states", args.states),
                )
                if value is None
            ]
            if missing:
                parser.error("--custom requires " + ", ".join(missing))
            scenario = MetastateCapacityScenario(
                name=args.name,
                evidence_level=args.evidence_level,
                density_kg_m3=args.density_kg_m3,
                pitch_nm=args.pitch_nm,
                distinguishable_states=args.states,
                active_volume_fraction=args.active_volume_fraction,
                coding_efficiency=args.coding_efficiency,
                write_energy_j_per_cell=args.write_energy_j,
                operation_energy_j_per_cell_event=args.operation_energy_j,
                cell_event_rate_hz=args.event_rate_hz,
                active_utilization=args.active_utilization,
                operations_per_cell_event=args.operations_per_event,
                multiplexing_factor=args.multiplexing_factor,
                temperature_k=args.temperature_k,
            )
            payload: object = scenario.as_dict(args.power_budget_w_per_kg)
        else:
            payload = scenarios_as_dicts(power_budget_w_per_kg=args.power_budget_w_per_kg)
    except ValueError as exc:
        print(f"Estimation failed: {exc}", file=sys.stderr)
        return 1

    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        from pathlib import Path

        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
