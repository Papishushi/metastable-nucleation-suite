from __future__ import annotations

import math
import numpy as np

ANGLES_A = np.array([0.0, math.pi / 4])
ANGLES_B = np.array([math.pi / 8, -math.pi / 8])


def simulate_local_chsh(n: int, rng: np.random.Generator | None = None):
    """Local hidden-variable benchmark using a shared random polarization."""
    if n <= 0:
        raise ValueError("n must be positive")
    rng = rng or np.random.default_rng()
    x = rng.integers(0, 2, n)
    y = rng.integers(0, 2, n)
    lam = rng.uniform(0.0, 2 * math.pi, n)
    a = np.where(np.cos(2 * (lam - ANGLES_A[x])) >= 0, 1, -1)
    b = -np.where(np.cos(2 * (lam - ANGLES_B[y])) >= 0, 1, -1)
    return x, y, a, b


def simulate_quantum_chsh(n: int, visibility: float = 1.0, rng=None):
    """Sample an ideal singlet correlation P(a*b|x,y) with visibility V.

    Marginals are exactly unbiased in expectation, so the model obeys
    no-signalling while reaching 2*sqrt(2)*V for the chosen settings.
    """
    if n <= 0 or not (0 <= visibility <= 1):
        raise ValueError("invalid parameters")
    rng = rng or np.random.default_rng()
    x = rng.integers(0, 2, n)
    y = rng.integers(0, 2, n)
    theta = ANGLES_A[x] - ANGLES_B[y]
    corr = -visibility * np.cos(2 * theta)
    a = rng.choice(np.array([-1, 1]), size=n)
    p_same = (1 + corr) / 2
    same = rng.random(n) < p_same
    b = np.where(same, a, -a)
    return x, y, a, b


def chsh_value(x, y, a, b) -> tuple[float, dict[str, float]]:
    terms: dict[str, float] = {}
    for xi in (0, 1):
        for yi in (0, 1):
            mask = (x == xi) & (y == yi)
            if not np.any(mask):
                raise ValueError("missing setting pair")
            terms[f"E{xi}{yi}"] = float(np.mean(a[mask] * b[mask]))
    # Chosen sign convention matches the angle set above.
    s = terms["E00"] + terms["E01"] + terms["E10"] - terms["E11"]
    return float(abs(s)), terms


def no_signalling_deltas(x, y, a, b) -> dict[str, float]:
    out: dict[str, float] = {}
    for xi in (0, 1):
        p0 = np.mean(a[(x == xi) & (y == 0)] == 1)
        p1 = np.mean(a[(x == xi) & (y == 1)] == 1)
        out[f"A_x{xi}"] = float(p0 - p1)
    for yi in (0, 1):
        p0 = np.mean(b[(y == yi) & (x == 0)] == 1)
        p1 = np.mean(b[(y == yi) & (x == 1)] == 1)
        out[f"B_y{yi}"] = float(p0 - p1)
    return out
