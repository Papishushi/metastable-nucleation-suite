import numpy as np
from metastable_suite.optical import simulate_double_well, independent_nodes_correlation


def test_symmetric_double_well_is_roughly_balanced():
    out = simulate_double_well(60_000, rng=np.random.default_rng(6)).outcomes
    p = np.mean(out == 1)
    assert 0.47 < p < 0.53


def test_independent_nodes_are_uncorrelated():
    corr = independent_nodes_correlation(60_000, np.random.default_rng(7))
    assert abs(corr) < 0.02
