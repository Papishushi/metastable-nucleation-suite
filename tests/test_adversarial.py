import numpy as np

from metastable_suite.adversarial import block_detrend, memory_sequence, shared_clock_modulation, shared_drift


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
