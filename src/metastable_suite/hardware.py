from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

import numpy as np

from .bell import simulate_local_chsh, simulate_quantum_chsh
from .nucleation import sample_competing_hazards
from .optical import simulate_double_well


@dataclass(frozen=True)
class TrialRequest:
    run_id: str
    specification_id: str
    trial_index: int
    settings: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrialResponse:
    timestamp_utc: str
    outcome: Mapping[str, Any]
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    valid: bool = True
    exclusion_reasons: tuple[str, ...] = ()


class ExperimentalBackend(ABC):
    """Lifecycle contract for simulators and physical hardware adapters."""

    backend_id: str
    backend_kind: str | None = None
    firmware_version: str = "unknown"

    @abstractmethod
    def prepare(self, specification_id: str, parameters: Mapping[str, Any]) -> None:
        """Allocate resources and configure the backend."""

    @abstractmethod
    def calibrate(self) -> Mapping[str, Any]:
        """Return calibration diagnostics recorded before acquisition."""

    @abstractmethod
    def execute_trial(self, request: TrialRequest) -> TrialResponse:
        """Execute one trial and return a normalized response."""

    @abstractmethod
    def reset(self) -> Mapping[str, Any]:
        """Restore a valid initial condition before the next trial."""

    @abstractmethod
    def collect_diagnostics(self) -> Mapping[str, Any]:
        """Collect backend-level diagnostics at the end of a run."""

    @abstractmethod
    def close(self) -> None:
        """Release hardware resources safely."""


class SimulatorBackend(ExperimentalBackend):
    """Reference backend implementing a subset of E02, E09, E11, E12 and E13."""

    backend_id = "reference-simulator"
    backend_kind = "simulator"
    firmware_version = "python-reference-1"

    def __init__(self, seed: int = 0) -> None:
        self.rng = np.random.default_rng(seed)
        self.specification_id: str | None = None
        self.parameters: dict[str, Any] = {}
        self.prepared = False

    def prepare(self, specification_id: str, parameters: Mapping[str, Any]) -> None:
        supported = {"E02", "E09", "E11", "E12", "E13"}
        if specification_id not in supported:
            raise ValueError(f"simulator backend does not support {specification_id}")
        self.specification_id = specification_id
        self.parameters = dict(parameters)
        self.prepared = True

    def calibrate(self) -> Mapping[str, Any]:
        if not self.prepared:
            raise RuntimeError("backend is not prepared")
        return {"calibration_ok": True, "backend": self.backend_id}

    def execute_trial(self, request: TrialRequest) -> TrialResponse:
        if not self.prepared or request.specification_id != self.specification_id:
            raise RuntimeError("trial does not match prepared specification")

        if request.specification_id == "E02":
            sample = sample_competing_hazards(
                1,
                rates=(
                    float(self.parameters.get("rate_0", 1.0)),
                    float(self.parameters.get("rate_1", 0.7)),
                ),
                seed_bias=float(self.parameters.get("seed_bias", 1.0)),
                rng=self.rng,
            )
            outcome = {
                "state": int(sample.states[0]),
                "transition_time": float(sample.times[0]),
            }
        elif request.specification_id == "E09":
            result = simulate_double_well(
                1,
                steps=int(self.parameters.get("steps", 500)),
                dt=float(self.parameters.get("dt", 0.01)),
                noise=float(self.parameters.get("noise", 0.45)),
                bias=float(self.parameters.get("bias", 0.0)),
                threshold=float(self.parameters.get("threshold", 0.65)),
                rng=self.rng,
            )
            outcome = {
                "metastate": int(result.outcomes[0]),
                "commit_step": int(result.commit_steps[0]),
                "final_amplitude": float(result.final_amplitudes[0]),
            }
        else:
            visibility = float(self.parameters.get("visibility", 0.98))
            if request.specification_id == "E12":
                x, y, a, b = simulate_local_chsh(1, self.rng)
            else:
                x, y, a, b = simulate_quantum_chsh(
                    1,
                    visibility=visibility,
                    rng=self.rng,
                )
            outcome = {
                "x": int(x[0]),
                "y": int(y[0]),
                "a": int(a[0]),
                "b": int(b[0]),
            }

        return TrialResponse(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            outcome=outcome,
            diagnostics={"simulated": True},
        )

    def reset(self) -> Mapping[str, Any]:
        if not self.prepared:
            raise RuntimeError("backend is not prepared")
        return {"reset_ok": True}

    def collect_diagnostics(self) -> Mapping[str, Any]:
        return {
            "prepared": self.prepared,
            "specification_id": self.specification_id,
        }

    def close(self) -> None:
        self.prepared = False
        self.specification_id = None
        self.parameters = {}


class CommandBackend(ExperimentalBackend):
    """Base class for adapters that wrap an external device-control command.

    Concrete adapters implement `_exchange`; the lifecycle and response normalization
    remain identical for serial, TCP, VISA, FPGA or laboratory-control transports.
    """

    backend_id = "command-backend"
    backend_kind = "hardware"

    def __init__(self, firmware_version: str = "unknown") -> None:
        self.firmware_version = firmware_version
        self.specification_id: str | None = None
        self.parameters: dict[str, Any] = {}

    @abstractmethod
    def _exchange(
        self,
        command: str,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    def prepare(self, specification_id: str, parameters: Mapping[str, Any]) -> None:
        response = self._exchange(
            "prepare",
            {
                "specification_id": specification_id,
                "parameters": dict(parameters),
            },
        )
        if not response.get("ok", False):
            raise RuntimeError(f"hardware prepare failed: {response}")
        self.specification_id = specification_id
        self.parameters = dict(parameters)

    def calibrate(self) -> Mapping[str, Any]:
        return self._exchange("calibrate", {})

    def execute_trial(self, request: TrialRequest) -> TrialResponse:
        response = self._exchange(
            "execute_trial",
            {
                "run_id": request.run_id,
                "specification_id": request.specification_id,
                "trial_index": request.trial_index,
                "settings": dict(request.settings),
            },
        )
        return TrialResponse(
            timestamp_utc=str(
                response.get(
                    "timestamp_utc",
                    datetime.now(timezone.utc).isoformat(),
                )
            ),
            outcome=dict(response.get("outcome", {})),
            diagnostics=dict(response.get("diagnostics", {})),
            valid=bool(response.get("valid", True)),
            exclusion_reasons=tuple(response.get("exclusion_reasons", ())),
        )

    def reset(self) -> Mapping[str, Any]:
        return self._exchange("reset", {})

    def collect_diagnostics(self) -> Mapping[str, Any]:
        return self._exchange("diagnostics", {})

    def close(self) -> None:
        self._exchange("close", {})
        self.specification_id = None
        self.parameters = {}
