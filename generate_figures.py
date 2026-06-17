#!/usr/bin/env python3
"""
Figure Generation for Delphi Validation Results
=================================================

Generates all six validation figures using the Okabe-Ito
colorblind-friendly palette on white backgrounds.

Figures:
    1. Kendall's W concordance by section
    2. IVC heatmap for dimension items (Section A)
    3. IVC heatmap for profile items (Section B)
    4. Global system evaluation (Section C)
    5. IVC distribution across all items
    6. Subpanel A vs B comparison

Palette: Okabe-Ito (https://jfly.uni-koeln.de/color/)

Authors:
    Diego Quintero-Avellaneda, Pedro Julián Ramírez-Angulo, Ernesto León-Castro
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ─── Configuration ──────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "delphi")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Okabe-Ito palette
OI = {
    "orange":    "#E69F00",
    "skyblue":   "#56B4E9",
    "green":     "#009E73",
    "yellow":    "#F0E442",
    "blue":      "#0072B2",
    "vermillion": "#D55E00",
    "purple":    "#CC79A7",
    "black":     "#000000",
}

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

IVC_THRESHOLD = 0.78


# ─── Data Loading ───────────────────────────────────────────────────────────

def load_section(section):
    """Load and pivot long-format CSV to wide-format matrix."""
    path = os.path.join(DATA_DIR, f"raw_section_{section}.csv")
    df = pd.read_csv(path)
    df["item_criterion"] = df["item"] + "_" + df["criterion"]
    wide = df.pivot_table(index="item_criterion", columns="expert",
                          values="score", aggfunc="first")
    wide = wide.sort_index()
    return wide


def load_results():
    path = os.path.join(DATA_DIR, "results.json")
    with open(path) as f:
        return json.load(f)


def kendall_w(ratings):
    n_items, n_raters = ratings.shape
    if n_items < 2 or n_raters < 2:
        return 0.0, 0.0, 1.0
    ranked = np.apply_along_axis(stats.rankdata, 0, ratings)
    R = ranked.sum(axis=1)
    S = np.sum((R - R.mean()) ** 2)
    denom = n_raters ** 2 * (n_items ** 3 - n_items)
    W = 12 * S / denom if denom > 0 else 0.0
    chi2 = n_raters * (n_items - 1) * W
    p = 1 - stats.chi2.cdf(chi2, df=max(n_items - 1, 1))
    return W, chi2, p


def compute_ivc(ratings, n_panel=12):
    n_e = (ratings >= 4).sum(axis=1)
    return (n_e - n_panel / 2) / (n_panel / 2)


# ─── Figure 1: Concordance ─────────────────────────────────────────────────

def fig_concordance():
    sections = ["A", "B", "C"]
    labels = ["Section A\n(Dimensions)", "Section B\n(Profiles)", "Section C\n(Global)"]
    W_values = []
    section_data = {}
    for s in sections:
        df = load_section(s)
        section_data[s] = df
        W, _, _ = kendall_w(df.values)
        W_values.append(W)

    # Add global
    all_r = np.vstack([section_data[s].values for s in sections])
    W_g, _, _ = kendall_w(all_r)
    W_values.append(W_g)
    labels.append("Global")

    colors = [OI["skyblue"]] * 3 + [OI["blue"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, W_values, color=colors, edgecolor="white", width=0.6)
    for bar, val in zip(bars, W_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"W = {val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Kendall's W")
    ax.set_title("Inter-rater Concordance by Section", fontweight="bold")
    ax.set_ylim(0, max(W_values) * 1.2)
    ax.axhline(y=0.1, color=OI["vermillion"], linestyle="--", alpha=0.5, label="Weak threshold")
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_concordance.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_concordance.png")


# ─── Figure 2: Dimension IVC Heatmap ───────────────────────────────────────

def fig_dimensions():
    df = load_section("A")
    ratings = df.values
    ivcs = compute_ivc(ratings)
    medians = np.median(ratings, axis=1)

    items = [idx.replace("_", "\n") for idx in df.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = [OI["green"] if ivc >= IVC_THRESHOLD else OI["orange"] if ivc >= 0.56 else OI["vermillion"]
              for ivc in ivcs]
    bars = ax.barh(range(len(items)), ivcs, color=colors, edgecolor="white")
    ax.axvline(x=IVC_THRESHOLD, color=OI["vermillion"], linestyle="--", linewidth=1.5,
               label=f"IVC threshold = {IVC_THRESHOLD}")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=8)
    ax.set_xlabel("IVC (Lawshe)")
    ax.set_title("Content Validity — Section A (Behavioral Dimensions)", fontweight="bold")
    ax.legend(loc="lower right")
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_dimensions.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_dimensions.png")


# ─── Figure 3: Profile IVC Heatmap ─────────────────────────────────────────

def fig_profiles():
    df = load_section("B")
    ratings = df.values
    ivcs = compute_ivc(ratings)

    items = [idx.replace("_", "\n") for idx in df.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = [OI["green"] if ivc >= IVC_THRESHOLD else OI["orange"] if ivc >= 0.56 else OI["vermillion"]
              for ivc in ivcs]
    ax.barh(range(len(items)), ivcs, color=colors, edgecolor="white")
    ax.axvline(x=IVC_THRESHOLD, color=OI["vermillion"], linestyle="--", linewidth=1.5,
               label=f"IVC threshold = {IVC_THRESHOLD}")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=8)
    ax.set_xlabel("IVC (Lawshe)")
    ax.set_title("Content Validity — Section B (Risk Profiles)", fontweight="bold")
    ax.legend(loc="lower right")
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_profiles.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_profiles.png")


# ─── Figure 4: Global System ───────────────────────────────────────────────

def fig_global():
    df = load_section("C")
    ratings = df.values
    medians = np.median(ratings, axis=1)
    ivcs = compute_ivc(ratings)

    items = [idx.replace("_", "\n") for idx in df.index]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Medians
    colors_m = [OI["green"] if m >= 4 else OI["orange"] for m in medians]
    ax1.bar(items, medians, color=colors_m, edgecolor="white")
    ax1.axhline(y=4, color=OI["vermillion"], linestyle="--", label="Md = 4 threshold")
    ax1.set_ylabel("Median")
    ax1.set_title("Medians — Section C", fontweight="bold")
    ax1.set_ylim(0, 5.5)
    ax1.legend()

    # IVCs
    colors_i = [OI["green"] if ivc >= IVC_THRESHOLD else OI["orange"] for ivc in ivcs]
    ax2.bar(items, ivcs, color=colors_i, edgecolor="white")
    ax2.axhline(y=IVC_THRESHOLD, color=OI["vermillion"], linestyle="--", label=f"IVC = {IVC_THRESHOLD}")
    ax2.set_ylabel("IVC")
    ax2.set_title("Content Validity — Section C", fontweight="bold")
    ax2.set_ylim(0, 1.1)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_global.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_global.png")


# ─── Figure 5: IVC Distribution ────────────────────────────────────────────

def fig_ivc_distribution():
    all_ivcs = []
    for s in ["A", "B", "C"]:
        df = load_section(s)
        ivcs = compute_ivc(df.values)
        all_ivcs.extend(ivcs)

    fig, ax = plt.subplots(figsize=(8, 5))
    n_above = sum(1 for v in all_ivcs if v >= IVC_THRESHOLD)
    n_total = len(all_ivcs)

    ax.hist(all_ivcs, bins=15, color=OI["skyblue"], edgecolor="white", alpha=0.8)
    ax.axvline(x=IVC_THRESHOLD, color=OI["vermillion"], linestyle="--", linewidth=2,
               label=f"Threshold = {IVC_THRESHOLD}")
    ax.set_xlabel("IVC (Lawshe)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"IVC Distribution — All Items (n={n_total}, "
                 f"{n_above}/{n_total} above threshold)", fontweight="bold")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_ivc.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_ivc.png")


# ─── Figure 6: Subpanel Comparison ─────────────────────────────────────────

def fig_subpanel():
    panel = pd.read_csv(os.path.join(DATA_DIR, "expert_panel.csv"))
    sub_a = panel[panel["sub"] == "A"]["id"].tolist()
    sub_b = panel[panel["sub"] == "B"]["id"].tolist()

    medians_a, medians_b = [], []
    for s in ["A", "B", "C"]:
        df = load_section(s)  # wide format: index=item_criterion, columns=experts
        cols_a = [c for c in sub_a if c in df.columns]
        cols_b = [c for c in sub_b if c in df.columns]
        if cols_a:
            medians_a.extend(np.median(df[cols_a].values, axis=1))
        if cols_b:
            medians_b.extend(np.median(df[cols_b].values, axis=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot([medians_a, medians_b],
                     tick_labels=["Subpanel A\n(Behavioral Finance)", "Subpanel B\n(Fuzzy/OWA)"],
                     patch_artist=True, widths=0.5)
    bp["boxes"][0].set_facecolor(OI["skyblue"])
    bp["boxes"][1].set_facecolor(OI["orange"])
    for element in ["whiskers", "caps"]:
        for item in bp[element]:
            item.set_color(OI["black"])

    ax.set_ylabel("Median Rating")
    ax.set_title("Subpanel Comparison — Median Ratings", fontweight="bold")
    ax.set_ylim(2.5, 5.5)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_delphi_subpanel_comparison.png"), dpi=300)
    plt.close()
    print("  ✓ fig_delphi_subpanel_comparison.png")


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("GENERATING DELPHI VALIDATION FIGURES")
    print(f"Palette: Okabe-Ito | Background: white | DPI: 300")
    print("=" * 55)
    print()

    fig_concordance()
    fig_dimensions()
    fig_profiles()
    fig_global()
    fig_ivc_distribution()
    fig_subpanel()

    print()
    print(f"All figures saved to: {os.path.abspath(FIG_DIR)}")


if __name__ == "__main__":
    main()
