import numpy as np

from metastable_suite.adversarial import (
    block_detrend,
    memory_sequence,
    setting_dependent_loss,
    shared_clock_modulation,
    shared_drift,
)


def test_shared_drift_creates_spurious_raw_correlation_but_detrending_reduces_it():
    pair = shared_drift(50_000, 2.0, np.random.default_rng(11))
    raw = float(np.corrcoef(pair.left, pair.right)[0, 1])
    corrected = float(np.corrcoef(block_detrend(pair.left, 100), block_detrend(pair.right, 100))[0, 1])
    assert raw > 0.45
    assert abs(corrected) < 0.05


def test_shared_clock_modulation_is_detectable_as_a_common_cause():
    pair = shared_clock_modulation(30_000, 1.5, 250, np.random.default_rng(12))
    correlation = float(np.corrcoef(pair.left, pair.right)[0, 1])
    assert correlation > 0.45


def test_memory_sequence_has_strong_lag_one_autocorrelation():
    values = memory_sequence(40_000, 0.9, np.random.default_rng(13))
    lag_one = float(np.corrcoef(values[:-1], values[1:])[0, 1])
    assert lag_one > 0.75


def test_setting_dependent_loss_creates_detectable_selection_bias():
    rng = np.random.default_rng(14)
    trials = 100_000
    settings = rng.choice((-1, 1), trials)
    outcomes = rng.choice((-1, 1), trials)
    keep = setting_dependent_loss(settings, outcomes, keep_same=0.95, keep_different=0.20, rng=rng)

    retained_same = float(np.mean(keep[settings == outcomes]))
    retained_different = float(np.mean(keep[settings != outcomes]))
    selected_agreement = float(np.mean(settings[keep] == outcomes[keep]))

    assert retained_same - retained_different > 0.70
    assert selected_agreement > 0.80
