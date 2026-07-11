#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from metastable_suite.monte_carlo_power import (
    chsh_power,
    correlation_power,
    no_signalling_power,
    proportion_power,
    search_sample_size,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Monte Carlo power planning for suite experiments")
    parser.add_argument("--design", required=True, choices=["proportion", "correlation", "chsh", "no-signalling"])
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--target-power", type=float)
    parser.add_argument("--minimum", type=int, default=100)
    parser.add_argument("--maximum", type=int, default=1_000_000)
    parser.add_argument("--repetitions", type=int, default=2000)
    parser.add_argument("--alpha", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--p0", type=float)
    parser.add_argument("--p1", type=float)
    parser.add_argument("--rho", type=float)
    parser.add_argument("--memory", type=float, default=0.0)
    parser.add_argument("--visibility", type=float)
    parser.add_argument("--loss-by-setting", type=float, default=0.0)
    parser.add_argument("--delta", type=float)
    parser.add_argument("--multiplicity", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    def estimate(sample_size: int):
        if args.design == "proportion":
            if args.p0 is None or args.p1 is None:
                parser.error("proportion requires --p0 and --p1")
            return proportion_power(sample_size, args.p0, args.p1, args.alpha, args.repetitions, args.seed)
        if args.design == "correlation":
            if args.rho is None:
                parser.error("correlation requires --rho")
            return correlation_power(sample_size, args.rho, args.alpha, args.repetitions, args.seed, args.memory)
        if args.design == "chsh":
            if args.visibility is None:
                parser.error("chsh requires --visibility")
            return chsh_power(
                sample_size,
                args.visibility,
                args.alpha,
                args.repetitions,
                args.seed,
                args.loss_by_setting,
            )
        if args.delta is None:
            parser.error("no-signalling requires --delta")
        return no_signalling_power(
            sample_size,
            args.delta,
            args.alpha,
            args.repetitions,
            args.seed,
            args.multiplicity,
        )

    if args.target_power is not None:
        result = search_sample_size(estimate, args.target_power, args.minimum, args.maximum)
    else:
        if args.sample_size is None:
            parser.error("provide --sample-size or --target-power")
        result = estimate(args.sample_size)

    payload = json.dumps(result.as_dict(), indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
