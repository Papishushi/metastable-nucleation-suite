from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

BOLTZMANN_CONSTANT_J_PER_K = 1.380649e-23
EVIDENCE_LEVELS = {"measured", "engineering_scenario", "speculative_bound"}


def _require_finite_positive(name: str, value: float, *, allow_zero: bool = False) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {qualifier}")


def _require_optional_finite_positive(name: str, value: float | None) -> None:
    if value is not None:
        _require_finite_positive(name, value)


@dataclass(frozen=True)
class MetastateCapacityScenario:
    """Sensitivity model for independently addressable scalar metastable cells.

    Volumetric outputs use total modelled medium volume. Mass-specific outputs use
    active-material mass only. Packaged-system metrics are deliberately absent
    because no support, addressing, readout, control or cooling mass is modelled.
    """

    name: str
    evidence_level: str
    active_material_density_kg_m3: float
    cell_pitch_nm: float
    distinguishable_states: int
    active_volume_fraction: float = 1.0
    coding_efficiency: float = 1.0
    write_energy_j_per_cell: float | None = None
    operation_energy_j_per_cell_event: float | None = None
    cell_event_rate_hz: float | None = None
    active_utilization: float = 1.0
    operations_per_cell_event: float = 1.0
    multiplexing_factor: float = 1.0
    temperature_k: float = 300.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise ValueError("unsupported evidence_level")
        _require_finite_positive(
            "active_material_density_kg_m3", self.active_material_density_kg_m3
        )
        _require_finite_positive("cell_pitch_nm", self.cell_pitch_nm)
        if self.distinguishable_states < 2:
            raise ValueError("distinguishable_states must be at least two")
        for field_name, value in (
            ("active_volume_fraction", self.active_volume_fraction),
            ("coding_efficiency", self.coding_efficiency),
            ("active_utilization", self.active_utilization),
        ):
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError(f"{field_name} must lie in (0, 1]")
        for field_name, value in (
            ("write_energy_j_per_cell", self.write_energy_j_per_cell),
            ("operation_energy_j_per_cell_event", self.operation_energy_j_per_cell_event),
            ("cell_event_rate_hz", self.cell_event_rate_hz),
        ):
            _require_optional_finite_positive(field_name, value)
        _require_finite_positive("operations_per_cell_event", self.operations_per_cell_event)
        _require_finite_positive("multiplexing_factor", self.multiplexing_factor)
        _require_finite_positive("temperature_k", self.temperature_k)

    @property
    def cell_pitch_m(self) -> float:
        return self.cell_pitch_nm * 1e-9

    @property
    def bits_per_cell(self) -> float:
        return math.log2(self.distinguishable_states)

    @property
    def cells_per_total_m3(self) -> float:
        return self.active_volume_fraction / self.cell_pitch_m**3

    @property
    def active_material_mass_kg_per_total_m3(self) -> float:
        return self.active_volume_fraction * self.active_material_density_kg_m3

    @property
    def cells_per_active_kg(self) -> float:
        return 1.0 / (self.cell_pitch_m**3 * self.active_material_density_kg_m3)

    @property
    def raw_bits_per_total_m3(self) -> float:
        return self.cells_per_total_m3 * self.bits_per_cell

    @property
    def usable_bits_per_total_m3(self) -> float:
        return self.raw_bits_per_total_m3 * self.coding_efficiency

    @property
    def usable_bits_per_active_kg(self) -> float:
        return self.cells_per_active_kg * self.bits_per_cell * self.coding_efficiency

    @property
    def usable_decimal_tb_per_active_kg(self) -> float:
        return self.usable_bits_per_active_kg / 8e12

    @property
    def usable_decimal_pb_per_active_kg(self) -> float:
        return self.usable_bits_per_active_kg / 8e15

    @property
    def full_rewrite_energy_j_per_total_m3(self) -> float | None:
        if self.write_energy_j_per_cell is None:
            return None
        return self.cells_per_total_m3 * self.write_energy_j_per_cell

    @property
    def full_rewrite_energy_j_per_active_kg(self) -> float | None:
        if self.write_energy_j_per_cell is None:
            return None
        return self.cells_per_active_kg * self.write_energy_j_per_cell

    @property
    def full_rewrite_energy_kwh_per_active_kg(self) -> float | None:
        energy = self.full_rewrite_energy_j_per_active_kg
        return None if energy is None else energy / 3.6e6

    @property
    def landauer_j_per_erased_bit(self) -> float:
        return BOLTZMANN_CONSTANT_J_PER_K * self.temperature_k * math.log(2.0)

    @property
    def landauer_full_erase_j_per_total_m3(self) -> float:
        return self.usable_bits_per_total_m3 * self.landauer_j_per_erased_bit

    @property
    def landauer_full_erase_j_per_active_kg(self) -> float:
        return self.usable_bits_per_active_kg * self.landauer_j_per_erased_bit

    @property
    def operations_per_cell_event_total(self) -> float:
        return self.operations_per_cell_event * self.multiplexing_factor

    @property
    def geometry_limited_operations_s_per_total_m3(self) -> float | None:
        if self.cell_event_rate_hz is None:
            return None
        return (
            self.cells_per_total_m3
            * self.cell_event_rate_hz
            * self.active_utilization
            * self.operations_per_cell_event_total
        )

    @property
    def geometry_limited_operations_s_per_active_kg(self) -> float | None:
        if self.cell_event_rate_hz is None:
            return None
        return (
            self.cells_per_active_kg
            * self.cell_event_rate_hz
            * self.active_utilization
            * self.operations_per_cell_event_total
        )

    @property
    def geometry_limited_dynamic_power_w_per_total_m3(self) -> float | None:
        if self.cell_event_rate_hz is None or self.operation_energy_j_per_cell_event is None:
            return None
        return (
            self.cells_per_total_m3
            * self.cell_event_rate_hz
            * self.active_utilization
            * self.operation_energy_j_per_cell_event
        )

    @property
    def geometry_limited_dynamic_power_w_per_active_kg(self) -> float | None:
        if self.cell_event_rate_hz is None or self.operation_energy_j_per_cell_event is None:
            return None
        return (
            self.cells_per_active_kg
            * self.cell_event_rate_hz
            * self.active_utilization
            * self.operation_energy_j_per_cell_event
        )

    @property
    def operations_per_joule(self) -> float | None:
        if self.operation_energy_j_per_cell_event is None:
            return None
        return self.operations_per_cell_event_total / self.operation_energy_j_per_cell_event

    def thermal_limited_operations_s_per_active_kg(
        self, power_budget_w_per_active_kg: float
    ) -> float | None:
        _require_finite_positive(
            "power_budget_w_per_active_kg", power_budget_w_per_active_kg, allow_zero=True
        )
        if self.operations_per_joule is None:
            return None
        return power_budget_w_per_active_kg * self.operations_per_joule

    def as_dict(
        self, power_budget_w_per_active_kg: float | None = None
    ) -> dict[str, object]:
        if power_budget_w_per_active_kg is not None:
            _require_finite_positive(
                "power_budget_w_per_active_kg",
                power_budget_w_per_active_kg,
                allow_zero=True,
            )
        payload = asdict(self)
        payload.update(
            {
                "volume_basis": "total_modelled_medium",
                "mass_basis": "active_material_only",
                "bits_per_cell": self.bits_per_cell,
                "cells_per_total_m3": self.cells_per_total_m3,
                "active_material_mass_kg_per_total_m3": self.active_material_mass_kg_per_total_m3,
                "cells_per_active_kg": self.cells_per_active_kg,
                "raw_bits_per_total_m3": self.raw_bits_per_total_m3,
                "usable_bits_per_total_m3": self.usable_bits_per_total_m3,
                "usable_bits_per_active_kg": self.usable_bits_per_active_kg,
                "usable_decimal_tb_per_active_kg": self.usable_decimal_tb_per_active_kg,
                "usable_decimal_pb_per_active_kg": self.usable_decimal_pb_per_active_kg,
                "full_rewrite_energy_j_per_total_m3": self.full_rewrite_energy_j_per_total_m3,
                "full_rewrite_energy_j_per_active_kg": self.full_rewrite_energy_j_per_active_kg,
                "full_rewrite_energy_kwh_per_active_kg": self.full_rewrite_energy_kwh_per_active_kg,
                "landauer_j_per_erased_bit": self.landauer_j_per_erased_bit,
                "landauer_full_erase_j_per_total_m3": self.landauer_full_erase_j_per_total_m3,
                "landauer_full_erase_j_per_active_kg": self.landauer_full_erase_j_per_active_kg,
                "operations_per_joule": self.operations_per_joule,
                "geometry_limited_operations_s_per_total_m3": self.geometry_limited_operations_s_per_total_m3,
                "geometry_limited_operations_s_per_active_kg": (
                    self.geometry_limited_operations_s_per_active_kg
                ),
                "geometry_limited_dynamic_power_w_per_total_m3": (
                    self.geometry_limited_dynamic_power_w_per_total_m3
                ),
                "geometry_limited_dynamic_power_w_per_active_kg": (
                    self.geometry_limited_dynamic_power_w_per_active_kg
                ),
                "power_budget_w_per_active_kg": power_budget_w_per_active_kg,
                "thermal_limited_operations_s_per_active_kg": (
                    None
                    if power_budget_w_per_active_kg is None
                    else self.thermal_limited_operations_s_per_active_kg(
                        power_budget_w_per_active_kg
                    )
                ),
            }
        )
        return payload


def reference_scenarios() -> tuple[MetastateCapacityScenario, ...]:
    """Return measured, engineering and speculative sensitivity cases."""

    return (
        MetastateCapacityScenario(
            name="laser_written_fused_silica_equivalent",
            evidence_level="measured",
            active_material_density_kg_m3=2200.0,
            cell_pitch_nm=395.75398596243724,
            distinguishable_states=2,
            active_volume_fraction=1.0,
            coding_efficiency=1.0,
            notes=(
                "Equivalent cubic pitch derived from 4.84 TB in 12 cm^2 by 2 mm of fused silica; "
                "it describes achieved archival density, not independently addressable nanocells."
            ),
        ),
        MetastateCapacityScenario(
            name="pcm_3d_conservative",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=6100.0,
            cell_pitch_nm=100.0,
            distinguishable_states=16,
            active_volume_fraction=0.25,
            coding_efficiency=0.70,
            write_energy_j_per_cell=100e-12,
            operation_energy_j_per_cell_event=10e-15,
            cell_event_rate_hz=1e9,
            active_utilization=1e-3,
            operations_per_cell_event=2.0,
            notes="Coarse 3D multilevel phase-change array with substantial routing and coding overhead.",
        ),
        MetastateCapacityScenario(
            name="pcm_3d_aggressive",
            evidence_level="engineering_scenario",
            active_material_density_kg_m3=6100.0,
            cell_pitch_nm=20.0,
            distinguishable_states=16,
            active_volume_fraction=0.25,
            coding_efficiency=0.50,
            write_energy_j_per_cell=1e-12,
            operation_energy_j_per_cell_event=1e-15,
            cell_event_rate_hz=10e9,
            active_utilization=1e-3,
            operations_per_cell_event=2.0,
            multiplexing_factor=8.0,
            notes="Aggressive nanocell and optical-multiplexing sensitivity case.",
        ),
        MetastateCapacityScenario(
            name="pcm_sub_10_nm_speculative_bound",
            evidence_level="speculative_bound",
            active_material_density_kg_m3=6100.0,
            cell_pitch_nm=5.0,
            distinguishable_states=64,
            active_volume_fraction=0.10,
            coding_efficiency=0.25,
            write_energy_j_per_cell=30e-15,
            operation_energy_j_per_cell_event=0.1e-15,
            cell_event_rate_hz=100e9,
            active_utilization=1e-4,
            operations_per_cell_event=2.0,
            multiplexing_factor=16.0,
            notes=(
                "Speculative packing bound. Independent, stable, addressable 5 nm cells with 64 reliable "
                "states have not been demonstrated as a three-dimensional system."
            ),
        ),
        MetastateCapacityScenario(
            name="addressable_amorphous_glass_ensemble",
            evidence_level="speculative_bound",
            active_material_density_kg_m3=2500.0,
            cell_pitch_nm=10.0,
            distinguishable_states=8,
            active_volume_fraction=0.20,
            coding_efficiency=0.30,
            write_energy_j_per_cell=10e-12,
            operation_energy_j_per_cell_event=1e-15,
            cell_event_rate_hz=1e9,
            active_utilization=1e-4,
            operations_per_cell_event=2.0,
            notes=(
                "A sensitivity case for independently addressable local configurations in an amorphous "
                "landscape. The existence of many microscopic minima does not imply that "
                "they are readable cells."
            ),
        ),
    )


def scenarios_as_dicts(
    scenarios: Iterable[MetastateCapacityScenario] | None = None,
    power_budget_w_per_active_kg: float | None = None,
) -> list[dict[str, object]]:
    selected = tuple(scenarios) if scenarios is not None else reference_scenarios()
    return [
        scenario.as_dict(power_budget_w_per_active_kg)
        for scenario in selected
    ]
