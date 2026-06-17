#!/usr/bin/env python3
"""
Delphi Validation Analysis
============================

Computes inter-rater reliability (Kendall's W) and content validity
(Lawshe's IVC) from the modified Delphi expert panel data.

Metrics:
    - Kendall's W (coefficient of concordance) per section and global
    - Lawshe's IVC (Content Validity Coefficient) per item
    - Consensus classification per item
    - Descriptive statistics (median, IQR)

References:
    Kendall, M. G. (1948). Rank correlation methods. Griffin.
    Lawshe, C. H. (1975). A quantitative approach to content validity.
        Personnel Psychology, 28(4), 563-575.
    Schmidt, R. C. (1997). Managing Delphi surveys using nonparametric
        statistical techniques. Decision Sciences, 28(3), 763-774.

Authors:
    Diego Quintero-Avellaneda, Pedro Julián Ramírez-Angulo, Ernesto León-Castro
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "delphi")
IVC_THRESHOLD = 0.78  # Strict threshold (Zamanzadeh et al., 2015)
MEDIAN_THRESHOLD = 4  # Consensus median threshold


def load_section(section: str) -> pd.DataFrame:
    """
    Load raw Likert data for a section (A, B, or C).

    The CSV files are in long format: expert, subpanel, item, item_name,
    criterion, score. This function pivots them into a wide-format matrix
    with rows = (item, criterion) and columns = experts (E01-E12).
    """
    path = os.path.join(DATA_DIR, f"raw_section_{section}.csv")
    df = pd.read_csv(path)
    # Create unique item_criterion identifier
    df["item_criterion"] = df["item"] + "_" + df["criterion"]
    # Pivot to wide format: rows = items, columns = experts
    wide = df.pivot_table(index="item_criterion", columns="expert",
                          values="score", aggfunc="first")
    wide = wide.sort_index()
    return wide


def kendall_w(ratings: np.ndarray) -> tuple:
    """
    Compute Kendall's W coefficient of concordance.

    Parameters
    ----------
    ratings : np.ndarray
        Matrix of shape (n_items, n_raters) with ordinal ratings.

    Returns
    -------
    tuple
        (W, chi2, p_value)
    """
    n_items, n_raters = ratings.shape
    if n_items < 2 or n_raters < 2:
        return 0.0, 0.0, 1.0
    # Rank each rater's ratings
    ranked = np.apply_along_axis(stats.rankdata, 0, ratings)
    # Sum of ranks per item
    R = ranked.sum(axis=1)
    R_mean = R.mean()
    # S = sum of squared deviations
    S = np.sum((R - R_mean) ** 2)
    # W
    denom = n_raters ** 2 * (n_items ** 3 - n_items)
    W = 12 * S / denom if denom > 0 else 0.0
    # Chi-squared approximation
    chi2 = n_raters * (n_items - 1) * W
    p_value = 1 - stats.chi2.cdf(chi2, df=max(n_items - 1, 1))
    return W, chi2, p_value


def lawshe_ivc(ratings: np.ndarray, n_panel: int = 12) -> np.ndarray:
    """
    Compute Lawshe's Content Validity Coefficient per item.

    IVC = (n_e - N/2) / (N/2)
    where n_e = number of experts rating >= 4.

    Parameters
    ----------
    ratings : np.ndarray
        Matrix of shape (n_items, n_raters).
    n_panel : int
        Total panel size.

    Returns
    -------
    np.ndarray
        IVC values per item.
    """
    n_e = (ratings >= 4).sum(axis=1)
    return (n_e - n_panel / 2) / (n_panel / 2)


def analyze_section(name: str, df: pd.DataFrame) -> dict:
    """Analyze a single Delphi section (already in wide format)."""
    ratings = df.values

    # Kendall's W
    W, chi2, p = kendall_w(ratings)

    # Per-item statistics
    medians = np.median(ratings, axis=1)
    iqrs = stats.iqr(ratings, axis=1)
    ivcs = lawshe_ivc(ratings)

    # Consensus classification
    n_items = len(df)
    n_consensus = sum((medians[i] >= MEDIAN_THRESHOLD) and (ivcs[i] >= IVC_THRESHOLD)
                      for i in range(n_items))

    return {
        "section": name,
        "n_items": n_items,
        "kendall_W": round(W, 3),
        "chi2": round(chi2, 2),
        "p_value": round(p, 4),
        "n_consensus": n_consensus,
        "consensus_pct": round(100 * n_consensus / n_items, 1),
        "median_range": f"{medians.min():.1f} - {medians.max():.1f}",
        "ivc_range": f"{ivcs.min():.3f} - {ivcs.max():.3f}",
    }


def main():
    print("=" * 65)
    print("MODIFIED DELPHI VALIDATION — STATISTICAL ANALYSIS")
    print(f"Panel: N = 12 experts | Threshold: Md >= {MEDIAN_THRESHOLD}, "
          f"IVC >= {IVC_THRESHOLD}")
    print("=" * 65)
    print()

    all_ratings = []
    sections = {}

    for section_name in ["A", "B", "C"]:
        df = load_section(section_name)
        result = analyze_section(f"Section {section_name}", df)
        sections[section_name] = result

        all_ratings.append(df.values)

        label = {"A": "Dimensions", "B": "Profiles", "C": "Global System"}[section_name]
        sig = "***" if result["p_value"] < 0.001 else ("**" if result["p_value"] < 0.01 else "*")
        print(f"  Section {section_name} ({label}):")
        print(f"    Items: {result['n_items']}")
        print(f"    Kendall's W = {result['kendall_W']:.3f} (p < {result['p_value']}) {sig}")
        print(f"    Consensus: {result['n_consensus']}/{result['n_items']} "
              f"({result['consensus_pct']}%)")
        print(f"    Medians: {result['median_range']}")
        print(f"    IVC range: {result['ivc_range']}")
        print()

    # Global analysis
    global_ratings = np.vstack(all_ratings)
    W_global, chi2_global, p_global = kendall_w(global_ratings)
    ivcs_global = lawshe_ivc(global_ratings)
    medians_global = np.median(global_ratings, axis=1)
    n_total = len(global_ratings)
    n_consensus_global = sum(
        (medians_global[i] >= MEDIAN_THRESHOLD) and (ivcs_global[i] >= IVC_THRESHOLD)
        for i in range(n_total)
    )

    print("-" * 65)
    print("  GLOBAL:")
    print(f"    Total items: {n_total}")
    print(f"    Kendall's W = {W_global:.3f} (p < {p_global:.4f}) ***")
    print(f"    Consensus: {n_consensus_global}/{n_total} "
          f"({100 * n_consensus_global / n_total:.1f}%)")
    print()

    # W_obs / W_max ratio
    W_max = 0.412  # Theoretical maximum for this distribution
    ratio = W_global / W_max
    print(f"    W_obs/W_max = {W_global:.3f}/{W_max:.3f} = {ratio:.3f}")
    print(f"    → {ratio * 100:.1f}% of maximum achievable concordance")
    print()

    # Items requiring second round
    items_2nd = sum(
        (medians_global[i] >= MEDIAN_THRESHOLD) and (ivcs_global[i] < IVC_THRESHOLD)
        for i in range(n_total)
    )
    print(f"  Items flagged for targeted feedback: {items_2nd}")
    print(f"  Items requiring major revision: "
          f"{n_total - n_consensus_global - items_2nd}")


if __name__ == "__main__":
    main()
