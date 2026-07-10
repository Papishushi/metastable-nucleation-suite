from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from .bell import simulate_local_chsh, simulate_quantum_chsh, chsh_value, no_signalling_deltas
from .nucleation import hazard_ratio_from_seed, common_field_nodes
from .optical import independent_nodes_correlation, simulate_double_well


def build_report(trials: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)

    local = simulate_local_chsh(trials, rng)
    qideal = simulate_quantum_chsh(trials, visibility=0.98, rng=rng)
    s_local, e_local = chsh_value(*local)
    s_q, e_q = chsh_value(*qideal)

    a, b, _ = common_field_nodes(trials, rng=rng)
    optical = simulate_double_well(min(trials, 100_000), rng=rng)

    return {
        "trials": trials,
        "seed": seed,
        "known_science_expectations": {
            "seed_odds_ratio_gt_1": hazard_ratio_from_seed(min(trials, 100_000), 1.0, rng),
            "classical_common_cause_correlation": float(np.corrcoef(a, b)[0, 1]),
            "independent_optical_nodes_correlation_near_0": independent_nodes_correlation(min(trials, 80_000), rng),
            "local_chsh_le_2": {"S": s_local, "E": e_local},
            "quantum_entangled_chsh_near_2sqrt2V": {"S": s_q, "E": e_q},
            "quantum_no_signalling_deltas_near_0": no_signalling_deltas(*qideal),
            "optical_metastate_positive_fraction": float(np.mean(optical.outcomes == 1)),
            "optical_mean_commit_step": float(np.mean(optical.commit_steps)),
        },
    }


def write_report(path: str | Path, trials: int, seed: int) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_report(trials, seed), indent=2), encoding="utf-8")
    return target
