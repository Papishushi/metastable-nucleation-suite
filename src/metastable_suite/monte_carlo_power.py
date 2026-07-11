from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Mapping

import numpy as np

from .bell import chsh_value, no_signalling_deltas, simulate_quantum_chsh


@dataclass(frozen=True)
class PowerEstimate:
    design: str
    sample_size: int
    repetitions: int
    rejection_count: int
    power: float
    standard_error: float
    parameters: Mapping[str, float | int | bool]

    def as_dict(self) -> dict[str, object]:
        return {
            "design": self.design,
            "sample_size": self.sample_size,
            "repetitions": self.repetitions,
            "rejection_count": self.rejection_count,
            "power": self.power,
            "standard_error": self.standard_error,
            "parameters": dict(self.parameters),
        }


def _estimate(
    design: str,
    sample_size: int,
    repetitions: int,
    simulator: Callable[[np.random.Generator], bool],
    seed: int,
    parameters: Mapping[str, float | int | bool],
) -> PowerEstimate:
    if sample_size <= 0 or repetitions <= 0:
        raise ValueError("sample_size and repetitions must be positive")
    rng = np.random.default_rng(seed)
    rejections = sum(bool(simulator(rng)) for _ in range(repetitions))
    power = rejections / repetitions
    standard_error = math.sqrt(power * (1.0 - power) / repetitions)
    return PowerEstimate(design, sample_size, repetitions, rejections, power, standard_error, parameters)


def proportion_power(
    sample_size_per_group: int,
    p0: float,
    p1: float,
    alpha: float = 0.001,
    repetitions: int = 2000,
    seed: int = 0,
) -> PowerEstimate:
    if not 0 < p0 < 1 or not 0 < p1 < 1:
        raise ValueError("p0 and p1 must lie in (0, 1)")

    def trial(rng: np.random.Generator) -> bool:
        x0 = rng.binomial(sample_size_per_group, p0)
        x1 = rng.binomial(sample_size_per_group, p1)
        estimate0 = x0 / sample_size_per_group
        estimate1 = x1 / sample_size_per_group
        pooled = (x0 + x1) / (2 * sample_size_per_group)
        variance = pooled * (1 - pooled) * (2 / sample_size_per_group)
        if variance <= 0:
            return False
        z = abs(estimate1 - estimate0) / math.sqrt(variance)
        threshold = _normal_quantile(1 - alpha / 2)
        return z >= threshold

    return _estimate(
        "two_proportions",
        2 * sample_size_per_group,
        repetitions,
        trial,
        seed,
        {"p0": p0, "p1": p1, "alpha": alpha, "sample_size_per_group": sample_size_per_group},
    )


def correlation_power(
    sample_size: int,
    rho: float,
    alpha: float = 0.001,
    repetitions: int = 2000,
    seed: int = 0,
    memory: float = 0.0,
) -> PowerEstimate:
    if not -1 < rho < 1 or rho == 0:
        raise ValueError("rho must be non-zero and lie in (-1, 1)")
    if not 0 <= memory < 1:
        raise ValueError("memory must lie in [0, 1)")

    covariance = np.array([[1.0, rho], [rho, 1.0]])

    def trial(rng: np.random.Generator) -> bool:
        values = rng.multivariate_normal([0.0, 0.0], covariance, size=sample_size)
        if memory:
            for index in range(1, sample_size):
                values[index] += memory * values[index - 1]
        observed = float(np.corrcoef(values[:, 0], values[:, 1])[0, 1])
        fisher = math.atanh(max(min(observed, 0.999999), -0.999999))
        z = abs(fisher) * math.sqrt(max(sample_size - 3, 1))
        return z >= _normal_quantile(1 - alpha / 2)

    return _estimate(
        "correlation",
        sample_size,
        repetitions,
        trial,
        seed,
        {"rho": rho, "alpha": alpha, "memory": memory},
    )


def chsh_power(
    sample_size: int,
    visibility: float,
    alpha: float = 0.001,
    repetitions: int = 2000,
    seed: int = 0,
    loss_by_setting: float = 0.0,
) -> PowerEstimate:
    if not 0 <= visibility <= 1:
        raise ValueError("visibility must lie in [0, 1]")
    if not 0 <= loss_by_setting < 1:
        raise ValueError("loss_by_setting must lie in [0, 1)")

    threshold = _normal_quantile(1 - alpha)

    def trial(rng: np.random.Generator) -> bool:
        x, y, a, b = simulate_quantum_chsh(sample_size, visibility=visibility, rng=rng)
        if loss_by_setting:
            keep_probability = np.where((x == 1) & (y == 1), 1.0 - loss_by_setting, 1.0)
            keep = rng.random(sample_size) < keep_probability
            x, y, a, b = x[keep], y[keep], a[keep], b[keep]
        try:
            s, terms = chsh_value(x, y, a, b)
        except ValueError:
            return False
        variances = []
        for xi in (0, 1):
            for yi in (0, 1):
                mask = (x == xi) & (y == yi)
                count = int(mask.sum())
                if count < 2:
                    return False
                mean = terms[f"E{xi}{yi}"]
                variances.append(max(1.0 - mean**2, 0.0) / count)
        standard_error = math.sqrt(sum(variances))
        return standard_error > 0 and (s - 2.0) / standard_error >= threshold

    return _estimate(
        "chsh",
        sample_size,
        repetitions,
        trial,
        seed,
        {"visibility": visibility, "alpha": alpha, "loss_by_setting": loss_by_setting},
    )


def inject_no_signalling_delta(
    x: np.ndarray,
    y: np.ndarray,
    a: np.ndarray,
    delta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Inject an expected A_x0 marginal difference equal to ``delta``.

    The two remote-setting arms are shifted symmetrically around an unbiased
    marginal: P(a=+1|x=0,y=0)=0.5+delta/2 and
    P(a=+1|x=0,y=1)=0.5-delta/2.
    """
    if x.shape != y.shape or x.shape != a.shape:
        raise ValueError("x, y and a must have the same shape")
    if not -1 < delta < 1 or delta == 0:
        raise ValueError("delta must be non-zero and lie in (-1, 1)")

    modified = a.copy()
    targets = {0: 0.5 + delta / 2.0, 1: 0.5 - delta / 2.0}
    for remote_setting, probability in targets.items():
        mask = (x == 0) & (y == remote_setting)
        count = int(mask.sum())
        if count == 0:
            raise ValueError("missing x=0 remote-setting arm")
        modified[mask] = np.where(rng.random(count) < probability, 1, -1)
    return modified


def no_signalling_power(
    sample_size: int,
    delta: float,
    alpha: float = 0.001,
    repetitions: int = 2000,
    seed: int = 0,
    multiplicity: int = 4,
) -> PowerEstimate:
    if not -1 < delta < 1 or delta == 0:
        raise ValueError("delta must be non-zero and lie in (-1, 1)")
    if multiplicity < 1:
        raise ValueError("multiplicity must be positive")
    corrected_alpha = alpha / multiplicity
    threshold = _normal_quantile(1 - corrected_alpha / 2)

    def trial(rng: np.random.Generator) -> bool:
        x, y, a, b = simulate_quantum_chsh(sample_size, visibility=0.98, rng=rng)
        a = inject_no_signalling_delta(x, y, a, delta, rng)
        deltas = no_signalling_deltas(x, y, a, b)
        observed = abs(deltas["A_x0"])
        n0 = max(int(((x == 0) & (y == 0)).sum()), 1)
        n1 = max(int(((x == 0) & (y == 1)).sum()), 1)
        standard_error = math.sqrt(0.25 / n0 + 0.25 / n1)
        return observed / standard_error >= threshold

    return _estimate(
        "no_signalling",
        sample_size,
        repetitions,
        trial,
        seed,
        {"delta": delta, "alpha": alpha, "multiplicity": multiplicity},
    )


def search_sample_size(
    estimator: Callable[[int], PowerEstimate],
    target_power: float,
    minimum: int,
    maximum: int,
    tolerance: int = 1,
) -> PowerEstimate:
    if not 0 < target_power < 1:
        raise ValueError("target_power must lie in (0, 1)")
    if minimum <= 0 or maximum < minimum or tolerance <= 0:
        raise ValueError("invalid search bounds")

    best: PowerEstimate | None = None
    low, high = minimum, maximum
    while low <= high:
        midpoint = (low + high) // 2
        estimate = estimator(midpoint)
        if estimate.power >= target_power:
            best = estimate
            high = midpoint - tolerance
        else:
            low = midpoint + tolerance
    if best is None:
        return estimator(maximum)
    return best


def _normal_quantile(probability: float) -> float:
    from statistics import NormalDist

    return NormalDist().inv_cdf(probability)
