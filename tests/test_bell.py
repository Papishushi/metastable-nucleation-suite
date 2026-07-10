import math
import numpy as np
from metastable_suite.bell import simulate_local_chsh, simulate_quantum_chsh, chsh_value, no_signalling_deltas


def test_local_model_does_not_violate_chsh():
    data = simulate_local_chsh(300_000, np.random.default_rng(3))
    s, _ = chsh_value(*data)
    assert s < 2.03


def test_quantum_benchmark_violates_chsh():
    data = simulate_quantum_chsh(300_000, 0.98, np.random.default_rng(4))
    s, _ = chsh_value(*data)
    assert 2.65 < s < 2.90


def test_quantum_benchmark_no_signalling():
    data = simulate_quantum_chsh(500_000, 0.98, np.random.default_rng(5))
    d = no_signalling_deltas(*data)
    assert max(abs(v) for v in d.values()) < 0.012
