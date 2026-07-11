from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AdversarialPair:
    left: np.ndarray
    right: np.ndarray
    label: str


def shared_drift(trials: int, strength: float, rng: np.random.Generator) -> AdversarialPair:
    time = np.linspace(-1.0, 1.0, trials)
    drift = strength * time
    left = drift + rng.normal(0.0, 1.0, trials)
    right = drift + rng.normal(0.0, 1.0, trials)
    return AdversarialPair(left, right, "shared_drift")


def shared_clock_modulation(trials: int, amplitude: float, period: int, rng: np.random.Generator) -> AdversarialPair:
    if period < 2:
        raise ValueError("period must be at least 2")
    phase = 2.0 * np.pi * np.arange(trials) / period
    common = amplitude * np.sin(phase)
    left = common + rng.normal(0.0, 1.0, trials)
    right = common + rng.normal(0.0, 1.0, trials)
    return AdversarialPair(left, right, "shared_clock_modulation")


def memory_sequence(trials: int, persistence: float, rng: np.random.Generator) -> np.ndarray:
    if not 0.0 <= persistence < 1.0:
        raise ValueError("persistence must lie in [0, 1)")
    values = np.empty(trials, dtype=int)
    values[0] = rng.choice((-1, 1))
    for index in range(1, trials):
        values[index] = values[index - 1] if rng.random() < persistence else -values[index - 1]
    return values


def setting_dependent_loss(
    settings: np.ndarray,
    outcomes: np.ndarray,
    keep_same: float,
    keep_different: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if settings.shape != outcomes.shape:
        raise ValueError("settings and outcomes must have the same shape")
    if not 0.0 <= keep_same <= 1.0 or not 0.0 <= keep_different <= 1.0:
        raise ValueError("keep probabilities must lie in [0, 1]")
    probabilities = np.where(settings == outcomes, keep_same, keep_different)
    return rng.random(len(settings)) < probabilities


def block_detrend(values: np.ndarray, blocks: int) -> np.ndarray:
    if blocks < 1 or len(values) < blocks:
        raise ValueError("blocks must be positive and no larger than the sample")
    residuals = values.astype(float).copy()
    for indices in np.array_split(np.arange(len(values)), blocks):
        residuals[indices] -= np.mean(residuals[indices])
    return residuals
