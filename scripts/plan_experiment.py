#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist
import sys


def z_for_two_sided_alpha(alpha: float) -> float:
    return NormalDist().inv_cdf(1.0 - alpha / 2.0)


def z_for_power(power: float) -> float:
    return NormalDist().inv_cdf(power)


def proportion_trials(p0: float, p1: float, alpha: float, power: float) -> int:
    if not 0 < p0 < 1 or not 0 < p1 < 1 or p0 == p1:
        raise ValueError("p0 and p1 must be distinct probabilities strictly between 0 and 1")
    z_alpha = z_for_two_sided_alpha(alpha)
    z_beta = z_for_power(power)
    pooled = (p0 + p1) / 2.0
    numerator = (
        z_alpha * math.sqrt(2.0 * pooled * (1.0 - pooled))
        + z_beta * math.sqrt(p0 * (1.0 - p0) + p1 * (1.0 - p1))
    ) ** 2
    return math.ceil(numerator / ((p1 - p0) ** 2))


def correlation_trials(rho: float, alpha: float, power: float) -> int:
    if not 0 < abs(rho) < 1:
        raise ValueError("rho must be non-zero and have magnitude below 1")
    z_alpha = z_for_two_sided_alpha(alpha)
    z_beta = z_for_power(power)
    fisher = math.atanh(abs(rho))
    return math.ceil(((z_alpha + z_beta) / fisher) ** 2 + 3)


def chsh_trials_per_setting(target_s: float, alpha: float, power: float, settings: int = 4) -> int:
    if settings < 2:
        raise ValueError("settings must be at least 2")
    if not 2.0 < target_s <= 2.0 * math.sqrt(2.0):
        raise ValueError("target_s must lie in (2, 2sqrt(2)]")
    z_alpha = z_for_two_sided_alpha(alpha)
    z_beta = z_for_power(power)
    margin = target_s - 2.0
    # For balanced settings, Var(S) <= settings / n_per_setting.
    return math.ceil(settings * ((z_alpha + z_beta) / margin) ** 2)


def chsh_trials(target_s: float, alpha: float, power: float, settings: int = 4) -> int:
    """Return the total balanced trial count across all CHSH setting pairs."""
    return settings * chsh_trials_per_setting(target_s, alpha, power, settings)


def no_signalling_trials_per_arm(delta: float, alpha: float, power: float) -> int:
    if not 0 < abs(delta) < 1:
        raise ValueError("delta must be non-zero and have magnitude below 1")
    z_alpha = z_for_two_sided_alpha(alpha)
    z_beta = z_for_power(power)
    # For two Bernoulli arms, Var(p0 - p1) <= 0.25/n + 0.25/n = 0.5/n.
    return math.ceil(0.5 * ((z_alpha + z_beta) / abs(delta)) ** 2)


def no_signalling_trials(delta: float, alpha: float, power: float) -> int:
    """Return the total trial count across two balanced remote-setting arms."""
    return 2 * no_signalling_trials_per_arm(delta, alpha, power)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan approximate sample sizes for suite experiments")
    parser.add_argument(
        "--experiment",
        required=True,
        choices=["proportion", "correlation", "chsh", "no-signalling"],
    )
    parser.add_argument("--alpha", type=float, default=0.001)
    parser.add_argument("--power", type=float, default=0.90)
    parser.add_argument("--p0", type=float)
    parser.add_argument("--p1", type=float)
    parser.add_argument("--rho", type=float)
    parser.add_argument("--target-s", type=float)
    parser.add_argument("--delta", type=float)
    parser.add_argument("--output")
    args = parser.parse_args()

    if not 0 < args.alpha < 1 or not 0.5 < args.power < 1:
        parser.error("alpha must lie in (0,1) and power in (0.5,1)")

    try:
        if args.experiment == "proportion":
            if args.p0 is None or args.p1 is None:
                parser.error("proportion planning requires --p0 and --p1")
            per_group = proportion_trials(args.p0, args.p1, args.alpha, args.power)
            result = {
                "design": "two_proportions",
                "required_trials_per_group": per_group,
                "required_trials_total": 2 * per_group,
            }
        elif args.experiment == "correlation":
            if args.rho is None:
                parser.error("correlation planning requires --rho")
            result = {
                "design": "single_correlation",
                "required_trials_total": correlation_trials(args.rho, args.alpha, args.power),
            }
        elif args.experiment == "chsh":
            if args.target_s is None:
                parser.error("CHSH planning requires --target-s")
            settings = 4
            per_setting = chsh_trials_per_setting(args.target_s, args.alpha, args.power, settings)
            result = {
                "design": "balanced_chsh",
                "setting_pairs": settings,
                "required_trials_per_setting_pair": per_setting,
                "required_trials_total": settings * per_setting,
            }
        else:
            if args.delta is None:
                parser.error("no-signalling planning requires --delta")
            per_arm = no_signalling_trials_per_arm(args.delta, args.alpha, args.power)
            result = {
                "design": "single_marginal_two_remote_settings",
                "remote_setting_arms": 2,
                "required_trials_per_arm": per_arm,
                "required_trials_total": 2 * per_arm,
            }
    except ValueError as exc:
        print(f"Planning failed: {exc}", file=sys.stderr)
        return 1

    result.update({"alpha": args.alpha, "power": args.power, "method": "normal_approximation_conservative"})
    payload = json.dumps(result, indent=2)
    if args.output:
        from pathlib import Path

        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
