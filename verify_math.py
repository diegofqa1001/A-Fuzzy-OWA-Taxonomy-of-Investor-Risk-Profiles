#!/usr/bin/env python3
"""
Mathematical Verification Suite
=================================

Runs 5 independent verification tests on the OWA weight vectors
reported in the article to confirm internal consistency.

Tests:
    1. alpha -> W: Weight generation from RIM quantifier reproduces reported W
    2. W -> orness: Computed orness matches reported values
    3. Monotonicity: Orness is strictly increasing with centroid (Proposition 1)
    4. Normalization: All weight vectors sum to 1.0
    5. Delta spread: F8 - F1 = 42.4 percentage points

Authors:
    Diego Quintero-Avellaneda, Pedro Julián Ramírez-Angulo, Ernesto León-Castro
"""

import json
import os
import sys


def load_profiles():
    """Load OWA profile data from JSON."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "owa", "owa_profiles.json")
    with open(path) as f:
        return json.load(f)


def test_alpha_to_weights(data):
    """Test 1: Verify that alpha generates the reported weight vectors."""
    n = 7
    passed = True
    for pk, info in sorted(data.items()):
        alpha = info["alpha"]
        W_reported = info["W"]
        W_computed = [(j / n) ** alpha - ((j - 1) / n) ** alpha for j in range(1, n + 1)]
        max_diff = max(abs(W_computed[j] - W_reported[j]) for j in range(n))
        if max_diff > 0.002:
            print(f"    FAIL: {pk} max_diff={max_diff:.4f}")
            passed = False
    return passed


def test_weights_to_orness(data):
    """Test 2: Verify that weight vectors produce the reported orness values."""
    n = 7
    passed = True
    for pk, info in sorted(data.items()):
        W = info["W"]
        orness_reported = info["orness"]
        orness_computed = sum((n - j) * W[j - 1] for j in range(1, n + 1)) / (n - 1)
        diff = abs(orness_computed - orness_reported)
        if diff > 0.002:
            print(f"    FAIL: {pk} diff={diff:.4f}")
            passed = False
    return passed


def test_monotonicity(data):
    """Test 3: Verify Proposition 1 — orness strictly increases with centroid."""
    profile_order = ["P1", "P2", "P3", "P6", "P4", "P5", "P7", "P8"]
    centroids = [data[p]["centroid"] for p in profile_order]
    orness_vals = [data[p]["orness"] for p in profile_order]
    F_vals = [data[p]["F_example"] for p in profile_order]

    c_mono = all(centroids[i] < centroids[i + 1] for i in range(len(centroids) - 1))
    o_mono = all(orness_vals[i] < orness_vals[i + 1] for i in range(len(orness_vals) - 1))
    f_mono = all(F_vals[i] < F_vals[i + 1] for i in range(len(F_vals) - 1))

    if not c_mono:
        print("    FAIL: centroids not strictly increasing")
    if not o_mono:
        print("    FAIL: orness values not strictly increasing")
    if not f_mono:
        print("    FAIL: F values not strictly increasing")

    return c_mono and o_mono and f_mono


def test_normalization(data):
    """Test 4: Verify all weight vectors sum to 1.0."""
    passed = True
    for pk, info in sorted(data.items()):
        W = info["W"]
        total = sum(W)
        if abs(total - 1.0) > 0.005:
            print(f"    FAIL: {pk} sum(W) = {total:.4f}")
            passed = False
    return passed


def test_delta_spread(data):
    """Test 5: Verify Delta = F8 - F1 = 42.4 percentage points."""
    F1 = data["P1"]["F_example"]
    F8 = data["P8"]["F_example"]
    delta = (F8 - F1) * 100
    passed = abs(delta - 42.4) < 0.5
    if not passed:
        print(f"    FAIL: delta = {delta:.1f} pp (expected 42.4)")
    return passed


def main():
    print("=" * 60)
    print("MATHEMATICAL VERIFICATION SUITE")
    print("OWA Weight Vectors — Fuzzy Investor Risk Profiles")
    print("=" * 60)
    print()

    data = load_profiles()
    tests = [
        ("Test 1: alpha -> W (weight generation)", test_alpha_to_weights),
        ("Test 2: W -> orness (direct computation)", test_weights_to_orness),
        ("Test 3: Monotonicity (Proposition 1)", test_monotonicity),
        ("Test 4: Normalization (sum W = 1.0)", test_normalization),
        ("Test 5: Delta spread (F8 - F1 = 42.4 pp)", test_delta_spread),
    ]

    results = []
    for name, func in tests:
        passed = func(data)
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}: {status}")
        results.append(passed)

    print()
    print("-" * 60)
    all_pass = all(results)
    if all_pass:
        print(f"RESULT: ALL {len(tests)} TESTS PASSED")
    else:
        n_fail = sum(1 for r in results if not r)
        print(f"RESULT: {n_fail} TEST(S) FAILED")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
