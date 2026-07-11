from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist
from typing import Callable, Mapping

import numpy as np

from .bell import chsh_value, no_signalling_deltas, simulate_quantum_chsh


@dataclass(frozen=True)
class PowerEstimate:
    design: str
