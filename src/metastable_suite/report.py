from __future__ import annotations

from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess

import numpy as np

from .bell import chsh_value, no_signalling_deltas, simulate_local_chsh, simulate_quantum_chsh
from .nucleation import common_field_nodes, hazard_ratio_from_seed
from .optical import independent_nodes_correlation, simulate_double_well

ROOT = Path(__file__).resolve().parents[2]


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def _git_commit() -> str:
    if not (ROOT / ".git").exists():
        return "unavailable"
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def build_provenance(seed: int, started_at: datetime, ended_at: datetime) -> dict:
    rng = np.random.default_rng(seed)
    return {
        "generated_at_utc": ended_at.isoformat(),
        "execution_started_at_utc": started_at.isoformat(),
        "execution_ended_at_utc": ended_at.isoformat(),
        "execution_duration_seconds": (ended_at - started_at).total_seconds(),
        "git_commit": _git_commit(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "package_version": _package_version("metastable-nucleation-suite"),
        "rng_algorithm": rng.bit_generator.__class__.__name__,
        "configuration": {
            "seed": seed,
            "catalog_version": 1,
            "specification_version": 1,
        },
    }


def build_report(trials: int, seed: int) -> dict:
    started_at = datetime.now(timezone.utc)
    rng = np.random.default_rng(seed)

    local = simulate_local_chsh(trials, rng)
    qideal = simulate_quantum_chsh(trials, visibility=0.98, rng=rng)
    s_local, e_local = chsh_value(*local)
    s_q, e_q = chsh_value(*qideal)

    a, b, _ = common_field_nodes(trials, rng=rng)
    optical = simulate_double_well(min(trials, 100_000), rng=rng)
    expectations = {
        "seed_odds_ratio_gt_1": hazard_ratio_from_seed(min(trials, 100_000), 1.0, rng),
        "classical_common_cause_correlation": float(np.corrcoef(a, b)[0, 1]),
        "independent_optical_nodes_correlation_near_0": independent_nodes_correlation(min(trials, 80_000), rng),
        "local_chsh_le_2": {"S": s_local, "E": e_local},
        "quantum_entangled_chsh_near_2sqrt2V": {"S": s_q, "E": e_q},
        "quantum_no_signalling_deltas_near_0": no_signalling_deltas(*qideal),
        "optical_metastate_positive_fraction": float(np.mean(optical.outcomes == 1)),
        "optical_mean_commit_step": float(np.mean(optical.commit_steps)),
    }
    ended_at = datetime.now(timezone.utc)

    return {
        "trials": trials,
        "seed": seed,
        "provenance": build_provenance(seed, started_at, ended_at),
        "known_science_expectations": expectations,
    }


def write_report(path: str | Path, trials: int, seed: int) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_report(trials, seed), indent=2), encoding="utf-8")
    return target
