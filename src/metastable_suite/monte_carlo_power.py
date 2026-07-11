from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist
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
    confidence_level: float
    confidence_interval: tuple[float, float]
    parameters: Mapping[str, float | int | bool]

    def as_dict(self) -> dict[str, object]:
        return {
            "design": self.design,
            "sample_size": self.sample_size,
            "repetitions": self.repetitions,
            "rejection_count": self.rejection_count,
            "power": self.power,
            "standard_error": self.standard_error,
            "confidence_level": self.confidence_level,
            "confidence_interval": list(self.confidence_interval),
            "parameters": dict(self.parameters),
        }


def wilson_interval(successes: int, trials: int, confidence_level: float = 0.95) -> tuple[float, float]:
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("successes must lie in [0, trials] and trials must be positive")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must lie in (0, 1)")
    probability = successes / trials
    z = NormalDist().inv_cdf(0.5 + confidence_level / 2)
    denominator = 1 + z**2 / trials
    centre = (probability + z**2 / (2 * trials)) / denominator
    radius = z * math.sqrt(
        probability * (1 - probability) / trials + z**2 / (4 * trials**2)
    ) / denominator
    return max(0.0, centre - radius), min(1.0, centre + radius)


def _estimate(
    design: str,
    sample_size: int,
    repetitions: int,
    simulator: Callable[[np.random.Generator], bool],
    seed: int,
    parameters: Mapping[str, float | int | bool],
    confidence_level: float = 0.95,
) -> PowerEstimate:
    if sample_size <= 0 or repetitions <= 0:
        raise ValueError("sample_size and repetitions must be positive")
    rng = np.random.default_rng(seed)
    rejections = sum(bool(simulator(rng)) for _ in range(repetitions))
    power = rejections / repetitions
    standard_error = math.sqrt(power * (1.0 - power) / repetitions)
    interval = wilson_interval(rejections, repetitions, confidence_level)
    return PowerEstimate(
        design,
        sample_size,
        repetitions,
        rejections,
        power,
        standard_error,
        confidence_level,
        interval,
        parameters,
    )


def analytical_proportion_power(
    sample_size_per_group: int,
    p0: float,
    p1: float,
    alpha: float = 0.001,
) -> float:
    if sample_size_per_group <= 0:
        raise ValueError("sample_size_per_group must be positive")
    if not 0 < p0 < 1 or not 0 < p1 < 1:
        raise ValueError("p0 and p1 must lie in (0, 1)")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    pooled = (p0 + p1) / 2
    null_se = math.sqrt(2 * pooled * (1 - pooled) / sample_size_per_group)
    alternative_se = math.sqrt(
        (p0 * (1 - p0) + p1 * (1 - p1)) / sample_size_per_group
    )
    critical = _normal_quantile(1 - alpha / 2) * null_se
    effect = abs(p1 - p0)
    return _two_sided_normal_power(effect, alternative_se, critical)


def analytical_correlation_power(sample_size: int, rho: float, alpha: float = 0.001) -> float:
    if sample_size <= 3:
        raise ValueError("sample_size must exceed 3")
    if not -1 < rho < 1 or rho == 0:
        raise ValueError("rho must be non-zero and lie in (-1, 1)")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    mean = math.atanh(rho) * math.sqrt(sample_size - 3)
    critical = _normal_quantile(1 - alpha / 2)
    return _two_sided_standard_normal_power(mean, critical)


def analytical_chsh_power(sample_size: int, visibility: float, alpha: float = 0.001) -> float:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if not 0 <= visibility <= 1:
        raise ValueError("visibility must lie in [0, 1]")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    correlation = visibility / math.sqrt(2)
    mean_s = 2 * math.sqrt(2) * visibility
    standard_error = 4 * math.sqrt(max(1 - correlation**2, 0.0) / sample_size)
    if standard_error == 0:
        return float(mean_s > 2)
    mean_z = (mean_s - 2) / standard_error
    critical = _normal_quantile(1 - alpha)
    return _normal_survival(critical - mean_z)


def analytical_no_signalling_power(
    sample_size: int,
    delta: float,
    alpha: float = 0.001,
    multiplicity: int = 4,
) -> float:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if not -1 < delta < 1 or delta == 0:
        raise ValueError("delta must be non-zero and lie in (-1, 1)")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    if multiplicity < 1:
        raise ValueError("multiplicity must be positive")
    standard_error = math.sqrt(2 / sample_size)
    mean_z = abs(delta) / standard_error
    critical = _normal_quantile(1 - alpha / multiplicity / 2)
    return _two_sided_standard_normal_power(mean_z, critical)


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
    """Inject an expected A_x0 marginal difference equal to ``delta``."""
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


def _two_sided_normal_power(effect: float, standard_error: float, critical: float) -> float:
    if standard_error <= 0:
        return float(effect > critical)
    mean = effect / standard_error
    threshold = critical / standard_error
    return _two_sided_standard_normal_power(mean, threshold)


def _two_sided_standard_normal_power(mean: float, critical: float) -> float:
    return _normal_survival(critical - mean) + _normal_cdf(-critical - mean)


def _normal_cdf(value: float) -> float:
    return NormalDist().cdf(value)


def _normal_survival(value: float) -> float:
    return 1.0 - _normal_cdf(value)


def _normal_quantile(probability: float) -> float:
    return NormalDist().inv_cdf(probability)
