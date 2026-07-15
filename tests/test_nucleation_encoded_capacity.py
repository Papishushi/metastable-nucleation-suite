from __future__ import annotations

import pytest

from metastable_suite.nucleation_encoded_capacity import (
    NucleationEncodedEnsembleScenario,
    reference_nucleation_encoded_scenario,
)


def test_configuration_capacity_is_not_scalar_pcm_capacity() -> None:
    scenario = NucleationEncodedEnsembleScenario(
        name="test",
        evidence_level="engineering_scenario",
        density_kg_m3=2000.0,
        addressable_pitch_nm=100.0,
        metastable_site_pitch_nm=10.0,
        local_states_per_site=4,
        addressable_volume_fraction=0.5,
        metastable_site_volume_fraction=0.5,
        configurational_entropy_efficiency=0.5,
        readout_efficiency=0.25,
        coding_efficiency=0.8,
        write_energy_j_per_site_transition=2e-12,
        mean_rewritten_site_fraction=0.1,
        operation_energy_j_per_ensemble_event=4e-15,
        ensemble_event_rate_hz=1e6,
        active_utilization=0.1,
        operations_per_ensemble_event=2.0,
        multiplexing_factor=4.0,
    )

    assert scenario.metastable_sites_per_unit == pytest.approx(500.0)
    assert scenario.ideal_configurational_bits_per_unit == pytest.approx(1000.0)
    assert scenario.recoverable_bits_per_unit == pytest.approx(100.0)
    assert scenario.addressable_units_per_m3 == pytest.approx(5e20)
    assert scenario.recoverable_bits_per_kg == pytest.approx(2.5e19)
    assert scenario.full_configuration_rewrite_energy_j_per_kg == pytest.approx(2.5e7)
    assert scenario.operations_per_joule == pytest.approx(2e15)
    assert scenario.thermal_limited_operations_s_per_kg(1000.0) == pytest.approx(2e18)


def test_reference_scenario_is_explicitly_speculative_and_discounted() -> None:
    scenario = reference_nucleation_encoded_scenario()
    assert scenario.evidence_level == "speculative_bound"
    assert scenario.metastable_sites_per_unit == pytest.approx(500.0)
    assert scenario.ideal_configurational_bits_per_unit == pytest.approx(1000.0)
    assert scenario.recoverable_bits_per_unit == pytest.approx(43.75)
    assert scenario.recoverable_decimal_pb_per_kg == pytest.approx(224.12909836065575)
    assert scenario.full_configuration_rewrite_energy_kwh_per_kg == pytest.approx(0.569216757741348)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("density_kg_m3", 0.0),
        ("addressable_pitch_nm", 0.0),
        ("metastable_site_pitch_nm", 101.0),
        ("local_states_per_site", 1),
        ("configurational_entropy_efficiency", 0.0),
        ("readout_efficiency", 1.1),
        ("mean_rewritten_site_fraction", -0.1),
    ],
)
def test_invalid_ensemble_parameters_fail_closed(field: str, value: float | int) -> None:
    values: dict[str, object] = {
        "name": "invalid",
        "evidence_level": "engineering_scenario",
        "density_kg_m3": 2000.0,
        "addressable_pitch_nm": 100.0,
        "metastable_site_pitch_nm": 10.0,
        "local_states_per_site": 4,
    }
    values[field] = value
    with pytest.raises(ValueError):
        NucleationEncodedEnsembleScenario(**values)  # type: ignore[arg-type]
