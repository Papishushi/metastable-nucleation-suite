from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class NucleationSample:
    times: np.ndarray
    states: np.ndarray


def sample_competing_hazards(
    n: int,
    rates: tuple[float, float] = (1.0, 0.7),
    seed_bias: float = 0.0,
    rng: np.random.Generator | None = None,
) -> NucleationSample:
    """Sample two independent exponential nucleation channels.

    `seed_bias` multiplies the second channel as exp(seed_bias), mimicking a
    barrier reduction by compatible seeds. The first event fixes the state.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if min(rates) <= 0:
        raise ValueError("rates must be positive")
    rng = rng or np.random.default_rng()
    r0, r1 = rates[0], rates[1] * np.exp(seed_bias)
    t0 = rng.exponential(1.0 / r0, n)
    t1 = rng.exponential(1.0 / r1, n)
    states = (t1 < t0).astype(np.int8)
    times = np.minimum(t0, t1)
    return NucleationSample(times=times, states=states)


def common_field_nodes(
    n: int,
    coupling_a: float = 0.8,
    coupling_b: float = 0.8,
    noise: float = 1.0,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate two binary nodes coupled to a classical shared latent field."""
    if n <= 0 or noise <= 0:
        raise ValueError("invalid parameters")
    rng = rng or np.random.default_rng()
    field = rng.normal(size=n)
    a = np.sign(coupling_a * field + rng.normal(scale=noise, size=n)).astype(int)
    b = np.sign(coupling_b * field + rng.normal(scale=noise, size=n)).astype(int)
    a[a == 0] = 1
    b[b == 0] = 1
    return a, b, field


def hazard_ratio_from_seed(
    n: int = 100_000,
    seed_bias: float = 1.0,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate the state-1 odds ratio induced by seeding."""
    rng = rng or np.random.default_rng()
    base = sample_competing_hazards(n, seed_bias=0.0, rng=rng).states
    seeded = sample_competing_hazards(n, seed_bias=seed_bias, rng=rng).states
    eps = 0.5
    odds_base = (base.sum() + eps) / ((base == 0).sum() + eps)
    odds_seed = (seeded.sum() + eps) / ((seeded == 0).sum() + eps)
    return float(odds_seed / odds_base)
