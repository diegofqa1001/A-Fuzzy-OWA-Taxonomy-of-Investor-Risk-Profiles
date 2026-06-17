#!/usr/bin/env python3
"""
OWA Weight Computation via Yager's RIM Quantifier
==================================================

Computes Ordered Weighted Averaging (OWA) weight vectors for eight
behavioral investor risk profiles using the Regular Increasing Monotone
(RIM) quantifier Q(r) = r^alpha (Yager, 1996).

Key formulas:
    w_j = Q(j/n) - Q((j-1)/n)  where Q(r) = r^alpha
    orness(W) = (1/(n-1)) * sum_{j=1}^{n} (n-j) * w_j

Note: The continuous-case approximation orness ≈ 1/(1+alpha) is only
exact as n → infinity. For finite n=7, alpha is determined by numerical
optimization to achieve the desired orness value.

Reference:
    Yager, R. R. (1996). Quantifier guided aggregation using OWA operators.
    International Journal of Intelligent Systems, 11(1), 49-73.

Authors:
    Diego Quintero-Avellaneda, Pedro Julián Ramírez-Angulo, Ernesto León-Castro
"""

import json
import os
import numpy as np
from scipy.optimize import minimize_scalar


# ─── Profile Definitions ────────────────────────────────────────────────────

PROFILES = {
    "P1": {"name": "Guardian",    "centroid": 0.15},
    "P2": {"name": "Sentinel",   "centroid": 0.25},
    "P3": {"name": "Pragmatist", "centroid": 0.50},
    "P6": {"name": "Analyst",    "centroid": 0.60},
    "P4": {"name": "Strategist", "centroid": 0.65},
    "P5": {"name": "Adventurer", "centroid": 0.70},
    "P7": {"name": "Innovator",  "centroid": 0.75},
    "P8": {"name": "Visionary",  "centroid": 0.90},
}

N_DIMENSIONS = 7  # Number of behavioral dimensions

# Numerical example: ordered input vector b (descending)
B_EXAMPLE = [0.90, 0.75, 0.65, 0.55, 0.45, 0.35, 0.20]


# ─── Core Functions ─────────────────────────────────────────────────────────

def rim_weights(alpha: float, n: int = N_DIMENSIONS) -> np.ndarray:
    """
    Generate OWA weight vector from RIM quantifier Q(r) = r^alpha.

    Parameters
    ----------
    alpha : float
        RIM quantifier exponent (alpha > 0).
    n : int
        Number of dimensions (default: 7).

    Returns
    -------
    np.ndarray
        Weight vector W of length n, where w_j = (j/n)^alpha - ((j-1)/n)^alpha.
    """
    return np.array([(j / n) ** alpha - ((j - 1) / n) ** alpha for j in range(1, n + 1)])


def compute_orness(W: np.ndarray) -> float:
    """
    Compute the orness measure of an OWA weight vector.

    orness(W) = (1/(n-1)) * sum_{j=1}^{n} (n - j) * w_j

    Parameters
    ----------
    W : np.ndarray
        OWA weight vector.

    Returns
    -------
    float
        Orness value in [0, 1].
    """
    n = len(W)
    return sum((n - j) * W[j - 1] for j in range(1, n + 1)) / (n - 1)


def find_alpha_for_orness(target_orness: float, n: int = N_DIMENSIONS,
                           tol: float = 1e-4) -> float:
    """
    Numerically find alpha such that orness(W(alpha)) = target_orness.

    Uses bounded scalar optimization on [0.01, 50].

    Parameters
    ----------
    target_orness : float
        Desired orness value in (0, 1).
    n : int
        Number of dimensions.
    tol : float
        Optimization tolerance.

    Returns
    -------
    float
        Optimal alpha value.
    """
    def objective(alpha):
        W = rim_weights(alpha, n)
        return (compute_orness(W) - target_orness) ** 2

    result = minimize_scalar(objective, bounds=(0.01, 50), method="bounded",
                             options={"xatol": tol})
    return result.x


def aggregate_owa(W: np.ndarray, b: list) -> float:
    """
    Compute OWA aggregation F = W . b (dot product).

    Parameters
    ----------
    W : np.ndarray
        OWA weight vector.
    b : list or np.ndarray
        Input vector (must be pre-sorted in descending order).

    Returns
    -------
    float
        Aggregated value F.
    """
    return float(np.dot(W, b))


# ─── Main Computation ───────────────────────────────────────────────────────

def compute_all_profiles() -> dict:
    """
    Compute OWA parameters for all eight profiles.

    For each profile:
      1. Set target orness = centroid (identity mapping phi(c) = c)
      2. Find alpha via numerical optimization
      3. Generate weight vector W
      4. Verify orness matches target
      5. Compute aggregation example F = W . b

    Returns
    -------
    dict
        Profile data including alpha, orness, W, and F_example.
    """
    results = {}
    for pk, info in sorted(PROFILES.items(), key=lambda x: x[1]["centroid"]):
        centroid = info["centroid"]
        alpha = find_alpha_for_orness(centroid)
        W = rim_weights(alpha)
        orness = compute_orness(W)
        F = aggregate_owa(W, B_EXAMPLE)

        results[pk] = {
            "name": info["name"],
            "centroid": centroid,
            "alpha": round(alpha, 3),
            "orness": round(orness, 3),
            "W": [round(w, 3) for w in W],
            "F_example": round(F, 3),
        }

        print(f"  {pk} ({info['name']:12s}): c={centroid:.2f}, "
              f"alpha={alpha:.3f}, orness={orness:.3f}, F={F:.3f}")

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("OWA Weight Computation via Yager's RIM Quantifier")
    print(f"Dimensions: n = {N_DIMENSIONS}")
    print(f"Quantifier: Q(r) = r^alpha")
    print(f"Mapping:    phi(c) = c (identity)")
    print("=" * 70)
    print()

    profiles = compute_all_profiles()

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "owa", "owa_profiles.json")
    with open(output_path, "w") as f:
        json.dump(profiles, f, indent=2)

    print(f"\nResults saved to {output_path}")

    # Summary
    F_min = min(p["F_example"] for p in profiles.values())
    F_max = max(p["F_example"] for p in profiles.values())
    delta = (F_max - F_min) * 100
    print(f"\nSpread: Delta = {F_max:.3f} - {F_min:.3f} = {delta:.1f} pp")
    print(f"This demonstrates that profile assignment produces up to "
          f"{delta:.1f} percentage points of difference in asset evaluation.")
