from scripts.plan_experiment import chsh_trials, correlation_trials, no_signalling_trials, proportion_trials


def test_smaller_effects_require_more_proportion_trials():
    large_effect = proportion_trials(0.50, 0.60, 0.001, 0.90)
    small_effect = proportion_trials(0.50, 0.53, 0.001, 0.90)
    assert small_effect > large_effect > 0


def test_weaker_correlations_require_more_trials():
    assert correlation_trials(0.02, 0.001, 0.90) > correlation_trials(0.10, 0.001, 0.90)


def test_chsh_margin_controls_required_trials():
    assert chsh_trials(2.05, 0.001, 0.90) > chsh_trials(2.50, 0.001, 0.90)


def test_smaller_signalling_difference_requires_more_trials():
    assert no_signalling_trials(0.005, 0.001, 0.90) > no_signalling_trials(0.02, 0.001, 0.90)
