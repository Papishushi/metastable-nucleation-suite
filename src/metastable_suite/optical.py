from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class BifurcationResult:
    outcomes: np.ndarray
    commit_steps: np.ndarray
    final_amplitudes: np.ndarray


def simulate_double_well(
    n: int,
    steps: int = 500,
    dt: float = 0.01,
    noise: float = 0.45,
    bias: float = 0.0,
    threshold: float = 0.65,
    rng: np.random.Generator | None = None,
) -> BifurcationResult:
    """Overdamped Langevin toy model in V(q)=-q²/2+q⁴/4-bias*q.

    dq = (q - q³ + bias)dt + sqrt(2Ddt)dW.
    The two wells represent optical metastates. This is a reference model,
    not a microscopic polariton simulation.
    """
    if n <= 0 or steps <= 0 or dt <= 0 or noise < 0:
        raise ValueError("invalid parameters")
    rng = rng or np.random.default_rng()
    q = rng.normal(scale=0.01, size=n)
    commit = np.full(n, -1, dtype=int)
    sigma = np.sqrt(2 * noise * dt)
    for step in range(steps):
        q += (q - q**3 + bias) * dt + sigma * rng.normal(size=n)
        newly = (commit < 0) & (np.abs(q) >= threshold)
        commit[newly] = step
    commit[commit < 0] = steps
    outcome = np.where(q >= 0, 1, -1)
    return BifurcationResult(outcome, commit, q)


def independent_nodes_correlation(n: int, rng=None) -> float:
    rng = rng or np.random.default_rng()
    a = simulate_double_well(n, rng=rng).outcomes
    b = simulate_double_well(n, rng=rng).outcomes
    return float(np.corrcoef(a, b)[0, 1])
