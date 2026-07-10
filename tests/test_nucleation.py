import numpy as np
from metastable_suite.nucleation import sample_competing_hazards, hazard_ratio_from_seed


def test_seed_increases_state_one_odds():
    rng = np.random.default_rng(1)
    assert hazard_ratio_from_seed(80_000, 1.0, rng) > 2.0


def test_times_are_positive_and_states_binary():
    s = sample_competing_hazards(1000, rng=np.random.default_rng(2))
    assert np.all(s.times > 0)
    assert set(np.unique(s.states)).issubset({0, 1})
