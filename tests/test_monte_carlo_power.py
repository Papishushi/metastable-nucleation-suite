import numpy as np
import pytest

from metastable_suite.bell import no_signalling_deltas, simulate_quantum_chsh
from metastable_suite.monte_carlo_power import (
    chsh_power,
    correlation_power,
    inject_no_signalling_delta,
    no_signalling_power,
    proportion_power,
    search_sample_size,
)


def test_proportion_power_increases_with_sample_size():
    small = proportion_power(100, 0.5, 0.6, alpha=0.05, repetitions=400, seed=1)
    large = proportion_power(1000, 0.5, 0.6, alpha=0.05, repetitions=400, seed=1)
    assert large.power > small.power


def test_correlation_power_detects_stronger_signal():
    weak = correlation_power(300, 0.05, alpha=0.05, repetitions=300, seed=2)
    strong = correlation_power(300, 0.25, alpha=0.05, repetitions=300, seed=2)
    assert strong.power > weak.power


def test_chsh_power_improves_with_visibility():
    low = chsh_power(2000, 0.72, alpha=0.05, repetitions=250, seed=3)
    high = chsh_power(2000, 0.98, alpha=0.05, repetitions=250, seed=3)
    assert high.power > low.power


def test_no_signalling_power_increases_with_effect_size():
    small = no_signalling_power(3000, 0.01, alpha=0.05, repetitions=250, seed=4)
    large = no_signalling_power(3000, 0.15, alpha=0.05, repetitions=250, seed=4)
    assert large.power > small.power


@pytest.mark.parametrize("target_delta", [0.20, -0.20])
def test_no_signalling_injection_preserves_requested_marginal_difference(target_delta):
    rng = np.random.default_rng(44)
    x, y, a, b = simulate_quantum_chsh(250_000, visibility=0.98, rng=rng)
    modified = inject_no_signalling_delta(x, y, a, target_delta, rng)
    observed = no_signalling_deltas(x, y, modified, b)["A_x0"]
    assert observed == pytest.approx(target_delta, abs=0.015)


def test_sample_size_search_returns_first_powerful_region():
    def estimator(sample_size):
        return proportion_power(sample_size, 0.5, 0.65, alpha=0.05, repetitions=250, seed=5)

    result = search_sample_size(estimator, target_power=0.75, minimum=50, maximum=1500, tolerance=10)
    assert result.power >= 0.75
    assert result.sample_size <= 3000
