from __future__ import annotations

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class NucleationEncodedEnsembleScenario:
    """Capacity model for a resolved ensemble of metastable nuclei or domains.

    This is intentionally distinct from conventional multilevel PCM. A conventional
    PCM cell is normally read as one aggregate resistance or optical-transmission
    level. Here, the codeword is the reproducibly writable and readable configuration
    of many local metastable sites inside one addressable three-dimensional unit.

    The configurational entropy and readout efficiencies prevent the mere existence
    of microscopic minima from being counted as usable information.
    """

    name: str
    evidence_level: str
    density_kg_m3: float
    addressable_pitch_nm: float
    metastable_site_pitch_nm: float
    local_states_per_site: int
    addressable_volume_fraction: float = 1.0
    metastable_site_volume_fraction: float = 1.0
    configurational_entropy_efficiency: float = 1.0
    readout_efficiency: float = 1.0
    coding_efficiency: float = 1.0
    write_energy_j_per_site_transition: float = 0.0
    mean_rewritten_site_fraction: float = 1.0
    operation_energy_j_per_ensemble_event: float = 0.0
    ensemble_event_rate_hz: float = 0.0
    active_utilization: float = 1.0
    operations_per_ensemble_event: float = 1.0
    multiplexing_factor: float = 1.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        if self.evidence_level not in {"measured", "engineering_scenario", "speculative_bound"}:
            raise ValueError("unsupported evidence_level")
        if self.density_kg_m3 <= 0:
            raise ValueError("density_kg_m3 must be positive")
        if self.addressable_pitch_nm <= 0 or self.metastable_site_pitch_nm <= 0:
            raise ValueError("pitches must be positive")
        if self.metastable_site_pitch_nm > self.addressable_pitch_nm:
            raise ValueError("metastable_site_pitch_nm must not exceed addressable_pitch_nm")
        if self.local_states_per_site < 2:
            raise ValueError("local_states_per_site must be at least two")
        for field_name, value in (
            ("addressable_volume_fraction", self.addressable_volume_fraction),
            ("metastable_site_volume_fraction", self.metastable_site_volume_fraction),
            ("configurational_entropy_efficiency", self.configurational_entropy_efficiency),
            ("readout_efficiency", self.readout_efficiency),
            ("coding_efficiency", self.coding_efficiency),
            ("mean_rewritten_site_fraction", self.mean_rewritten_site_fraction),
            ("active_utilization", self.active_utilization),
        ):
            if not 0 < value <= 1:
                raise ValueError(f"{field_name} must lie in (0, 1]")
        for field_name, value in (
            ("write_energy_j_per_site_transition", self.write_energy_j_per_site_transition),
            ("operation_energy_j_per_ensemble_event", self.operation_energy_j_per_ensemble_event),
            ("ensemble_event_rate_hz", self.ensemble_event_rate_hz),
            ("operations_per_ensemble_event", self.operations_per_ensemble_event),
            ("multiplexing_factor", self.multiplexing_factor),
        ):
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative")

    @property
    def addressable_pitch_m(self) -> float:
        return self.addressable_pitch_nm * 1e-9

    @property
    def metastable_site_pitch_m(self) -> float:
        return self.metastable_site_pitch_nm * 1e-9

    @property
    def addressable_units_per_m3(self) -> float:
        return self.addressable_volume_fraction / self.addressable_pitch_m**3

    @property
    def addressable_units_per_kg(self) -> float:
        return self.addressable_units_per_m3 / self.density_kg_m3

    @property
    def metastable_sites_per_unit(self) -> float:
        linear_ratio = self.addressable_pitch_m / self.metastable_site_pitch_m
        return self.metastable_site_volume_fraction * linear_ratio**3

    @property
    def ideal_configurational_bits_per_unit(self) -> float:
        return self.metastable_sites_per_unit * math.log2(self.local_states_per_site)

    @property
    def recoverable_bits_per_unit(self) -> float:
        return (
            self.ideal_configurational_bits_per_unit
            * self.configurational_entropy_efficiency
            * self.readout_efficiency
            * self.coding_efficiency
        )

    @property
    def recoverable_bits_per_m3(self) -> float:
        return self.addressable_units_per_m3 * self.recoverable_bits_per_unit

    @property
    def recoverable_bits_per_kg(self) -> float:
        return self.recoverable_bits_per_m3 / self.density_kg_m3

    @property
    def recoverable_decimal_pb_per_kg(self) -> float:
        return self.recoverable_bits_per_kg / 8e15

    @property
    def recoverable_decimal_eb_per_kg(self) -> float:
        return self.recoverable_bits_per_kg / 8e18

    @property
    def full_configuration_rewrite_energy_j_per_kg(self) -> float:
        return (
            self.addressable_units_per_kg
            * self.metastable_sites_per_unit
            * self.mean_rewritten_site_fraction
            * self.write_energy_j_per_site_transition
        )

    @property
    def full_configuration_rewrite_energy_kwh_per_kg(self) -> float:
        return self.full_configuration_rewrite_energy_j_per_kg / 3.6e6

    @property
    def operations_per_ensemble_event_total(self) -> float:
        return self.operations_per_ensemble_event * self.multiplexing_factor

    @property
    def geometry_limited_operations_s_per_kg(self) -> float:
        return (
            self.addressable_units_per_kg
            * self.ensemble_event_rate_hz
            * self.active_utilization
            * self.operations_per_ensemble_event_total
        )

    @property
    def operations_per_joule(self) -> float:
        if self.operation_energy_j_per_ensemble_event == 0:
            return math.inf
        return self.operations_per_ensemble_event_total / self.operation_energy_j_per_ensemble_event

    def thermal_limited_operations_s_per_kg(self, power_budget_w_per_kg: float) -> float:
        if power_budget_w_per_kg < 0:
            raise ValueError("power_budget_w_per_kg must be non-negative")
        if math.isinf(self.operations_per_joule):
            return math.inf
        return power_budget_w_per_kg * self.operations_per_joule

    def as_dict(self, power_budget_w_per_kg: float | None = None) -> dict[str, object]:
        payload = asdict(self)
        payload.update(
            {
                "addressable_units_per_m3": self.addressable_units_per_m3,
                "addressable_units_per_kg": self.addressable_units_per_kg,
                "metastable_sites_per_unit": self.metastable_sites_per_unit,
                "ideal_configurational_bits_per_unit": self.ideal_configurational_bits_per_unit,
                "recoverable_bits_per_unit": self.recoverable_bits_per_unit,
                "recoverable_bits_per_m3": self.recoverable_bits_per_m3,
                "recoverable_bits_per_kg": self.recoverable_bits_per_kg,
                "recoverable_decimal_pb_per_kg": self.recoverable_decimal_pb_per_kg,
                "recoverable_decimal_eb_per_kg": self.recoverable_decimal_eb_per_kg,
                "full_configuration_rewrite_energy_j_per_kg": self.full_configuration_rewrite_energy_j_per_kg,
                "full_configuration_rewrite_energy_kwh_per_kg": self.full_configuration_rewrite_energy_kwh_per_kg,
                "operations_per_joule": self.operations_per_joule,
                "geometry_limited_operations_s_per_kg": self.geometry_limited_operations_s_per_kg,
            }
        )
        if power_budget_w_per_kg is not None:
            payload["power_budget_w_per_kg"] = power_budget_w_per_kg
            payload["thermal_limited_operations_s_per_kg"] = self.thermal_limited_operations_s_per_kg(
                power_budget_w_per_kg
            )
        return payload


def reference_nucleation_encoded_scenario() -> NucleationEncodedEnsembleScenario:
    """Return an explicitly speculative sensitivity case, not a device forecast."""

    return NucleationEncodedEnsembleScenario(
        name="nucleation_encoded_chalcogenide_ensemble",
        evidence_level="speculative_bound",
        density_kg_m3=6100.0,
        addressable_pitch_nm=100.0,
        metastable_site_pitch_nm=10.0,
        local_states_per_site=4,
        addressable_volume_fraction=0.25,
        metastable_site_volume_fraction=0.50,
        configurational_entropy_efficiency=0.25,
        readout_efficiency=0.25,
        coding_efficiency=0.70,
        write_energy_j_per_site_transition=1e-12,
        mean_rewritten_site_fraction=0.10,
        operation_energy_j_per_ensemble_event=10e-15,
        ensemble_event_rate_hz=1e9,
        active_utilization=1e-3,
        operations_per_ensemble_event=2.0,
        multiplexing_factor=8.0,
        notes=(
            "Illustrative 100 nm addressable voxel containing an effective ensemble of 10 nm local sites. "
            "Only a small fraction of ideal configurational entropy is assumed writable and recoverable. "
            "No such complete three-dimensional device has been demonstrated."
        ),
    )
