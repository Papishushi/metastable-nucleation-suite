from scripts.plan_experiment import (
    chsh_trials,
    chsh_trials_per_setting,
    correlation_trials,
    no_signalling_trials,
    no_signalling_trials_per_arm,
    proportion_trials,
)


def test_smaller_effects_require_more_proportion_trials():
    large_effect = proportion_trials(0.50, 0.60, 0.001, 0.90)
    small_effect = proportion_trials(0.50, 0.53, 0.001, 0.90)
    assert small_effect > large_effect > 0


def test_weaker_correlations_require_more_trials():
    assert correlation_trials(0.02, 0.001, 0.90) > correlation_trials(0.10, 0.001, 0.90)


def test_chsh_margin_controls_required_trials():
    assert chsh_trials(2.05, 0.001, 0.90) > chsh_trials(2.50, 0.001, 0.90)


def test_chsh_total_is_four_balanced_setting_pairs():
    per_setting = chsh_trials_per_setting(2.4, 0.001, 0.90)
    assert chsh_trials(2.4, 0.001, 0.90) == 4 * per_setting


def test_smaller_signalling_difference_requires_more_trials():
    assert no_signalling_trials(0.005, 0.001, 0.90) > no_signalling_trials(0.02, 0.001, 0.90)


def test_no_signalling_total_contains_two_balanced_arms():
    per_arm = no_signalling_trials_per_arm(0.01, 0.001, 0.90)
    assert no_signalling_trials(0.01, 0.001, 0.90) == 2 * per_arm
