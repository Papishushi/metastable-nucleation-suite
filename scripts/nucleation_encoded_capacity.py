#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from metastable_suite.nucleation_encoded_capacity import (
    NucleationEncodedEnsembleScenario,
    reference_nucleation_encoded_scenario,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate recoverable configurational information and energy for a nucleation-encoded "
            "chalcogenide ensemble. Without --custom, prints the documented speculative reference case."
        )
    )
    parser.add_argument("--custom", action="store_true")
    parser.add_argument("--name", default="custom-nece")
    parser.add_argument(
        "--evidence-level",
        choices=["measured", "engineering_scenario", "speculative_bound"],
        default="speculative_bound",
    )
    parser.add_argument("--density-kg-m3", type=float)
    parser.add_argument("--addressable-pitch-nm", type=float)
    parser.add_argument("--site-pitch-nm", type=float)
    parser.add_argument("--local-states", type=int)
    parser.add_argument("--addressable-volume-fraction", type=float, default=1.0)
    parser.add_argument("--site-volume-fraction", type=float, default=1.0)
    parser.add_argument("--configurational-efficiency", type=float, default=1.0)
    parser.add_argument("--readout-efficiency", type=float, default=1.0)
    parser.add_argument("--coding-efficiency", type=float, default=1.0)
    parser.add_argument("--write-energy-j-per-site", type=float, default=0.0)
    parser.add_argument("--rewritten-site-fraction", type=float, default=1.0)
    parser.add_argument("--operation-energy-j", type=float, default=0.0)
    parser.add_argument("--event-rate-hz", type=float, default=0.0)
    parser.add_argument("--active-utilization", type=float, default=1.0)
    parser.add_argument("--operations-per-event", type=float, default=1.0)
    parser.add_argument("--multiplexing-factor", type=float, default=1.0)
    parser.add_argument("--power-budget-w-per-kg", type=float, default=1000.0)
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        if args.custom:
            required = {
                "--density-kg-m3": args.density_kg_m3,
                "--addressable-pitch-nm": args.addressable_pitch_nm,
                "--site-pitch-nm": args.site_pitch_nm,
                "--local-states": args.local_states,
            }
            missing = [name for name, value in required.items() if value is None]
            if missing:
                parser.error("--custom requires " + ", ".join(missing))
            scenario = NucleationEncodedEnsembleScenario(
                name=args.name,
                evidence_level=args.evidence_level,
                density_kg_m3=args.density_kg_m3,
                addressable_pitch_nm=args.addressable_pitch_nm,
                metastable_site_pitch_nm=args.site_pitch_nm,
                local_states_per_site=args.local_states,
                addressable_volume_fraction=args.addressable_volume_fraction,
                metastable_site_volume_fraction=args.site_volume_fraction,
                configurational_entropy_efficiency=args.configurational_efficiency,
                readout_efficiency=args.readout_efficiency,
                coding_efficiency=args.coding_efficiency,
                write_energy_j_per_site_transition=args.write_energy_j_per_site,
                mean_rewritten_site_fraction=args.rewritten_site_fraction,
                operation_energy_j_per_ensemble_event=args.operation_energy_j,
                ensemble_event_rate_hz=args.event_rate_hz,
                active_utilization=args.active_utilization,
                operations_per_ensemble_event=args.operations_per_event,
                multiplexing_factor=args.multiplexing_factor,
            )
        else:
            scenario = reference_nucleation_encoded_scenario()
        payload = scenario.as_dict(args.power_budget_w_per_kg)
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
