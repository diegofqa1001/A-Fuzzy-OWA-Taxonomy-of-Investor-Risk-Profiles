# A Fuzzy-OWA Taxonomy of Investor Risk Profiles

> **Beyond the Conservative–Moderate–Aggressive Triad: An Expanded Behavioral Taxonomy Formalized through Fuzzy Linguistic Vectors and OWA Operators**

## Overview

This repository contains the replication materials, data, and code for an expanded taxonomy of investor risk profiling: replacing the static tripartite classification (conservative–moderate–aggressive) with an expanded taxonomy of **eight behavioral risk profiles** formalized through fuzzy linguistic vectors and calibrated via **Ordered Weighted Averaging (OWA) operators** using Yager's Regular Increasing Monotone (RIM) quantifier. This work is part of a doctoral thesis in Administration at the Universidad Nacional de Colombia, Sede Manizales.

### Key Contributions

1. **Seven behavioral dimensions** identified through a PRISMA 2020 systematic review of 78 studies (2019–2026) indexed in Scopus and Web of Science, spanning cognitive, emotional-affective, contextual-situational, and sociocultural-identity domains.

2. **Eight prototypical investor profiles** (Guardian → Visionary) formalized as fuzzy linguistic vectors with explicit OWA aggregation semantics, producing up to **42.4 percentage points** of difference in asset evaluation depending on profile assignment.

3. **RIM quantifier-based weight derivation** providing a theoretically grounded, auditable, and reproducible weight generation mechanism: $w_j = Q(j/n) - Q((j-1)/n)$ where $Q(r) = r^\alpha$.

4. **Modified Delphi validation** with a synthetic 12-agent panel (6 behavioral finance profile, 6 fuzzy methods profile) as a computational pre-validation / proof-of-concept step — **not a substitute for a human expert panel**. Results are reported as a methodological reference pending the confirmatory round with real experts.

## Repository Structure

```
├── data/
│   ├── delphi/
│   │   ├── expert_panel.csv             # Synthetic panel composition
│   │   ├── raw_section_A.csv            # Raw ratings — Section A (dimensions)
│   │   ├── raw_section_B.csv            # Raw ratings — Section B (profiles)
│   │   ├── raw_section_C.csv            # Raw ratings — Section C (global system)
│   │   ├── results.json                 # Computed statistics (Kendall W, Lawshe IVC, medians)
│   │   ├── decisions.json               # Consensus decisions per item
│   │   └── qualitative.json             # Qualitative observations
│   └── owa/
│       └── owa_profiles.json            # OWA weight vectors, α values, orness for 8 profiles
│
├── code/
│   ├── owa_weights.py                   # OWA weight computation and verification
│   ├── delphi_analysis.py               # Delphi statistical analysis (Kendall W, Lawshe IVC)
│   ├── generate_figures.py              # Reproduce all Delphi validation figures
│   ├── verify_math.py                   # Mathematical verification suite (5 tests)
│   ├── check_reproducibility.py         # Frozen values vs. fresh optimizer run (see note above)
│   └── requirements.txt                 # Python dependencies
│
├── LICENSE
├── .gitignore
└── README.md
```

## The Eight Profiles

| Profile | Name | Centroid | α | Orness | Aggregation Character |
|---------|------|----------|---|--------|----------------------|
| P1 | Guardian | 0.15 | 4.000 | 0.158 | Strong AND (pessimistic) |
| P2 | Sentinel | 0.25 | 2.484 | 0.257 | Moderate AND |
| P3 | Pragmatist | 0.50 | 0.988 | 0.503 | Neutral (≈ arithmetic mean) |
| P6 | Analyst | 0.60 | 0.695 | 0.600 | Mild OR |
| P4 | Strategist | 0.65 | 0.580 | 0.647 | Moderate OR |
| P5 | Adventurer | 0.70 | 0.477 | 0.693 | Moderate-Strong OR |
| P7 | Innovator | 0.75 | 0.389 | 0.738 | Strong OR |
| P8 | Visionary | 0.90 | 0.176 | 0.865 | Very Strong OR (optimistic) |

> **Reproducibility note (added 2026-08-17).** The α and orness values above are the
> **frozen, originally published values**, stored verbatim in `data/owa/owa_profiles.json`
> and cited in the thesis (Table 3.4, Figure 3.2) and in the downstream repositories
> (`repo_OWA`'s `ORNESS_PERFIL`, `motor-owa-v2`'s `TAXONOMY_ORNESS`). Running
> `code/owa_weights.py` **today**, with the optimizer configuration currently in the
> repository, converges instead to the *exact centroid* of each profile (e.g. Guardian:
> α=4.184, orness=0.150, not 0.158; the largest gap is Visionary, α=0.127 vs. 0.176,
> orness 0.900 vs. 0.865). This is not a numerical-precision artifact — the fresh run is
> stable and internally consistent — it indicates the frozen values were produced by an
> earlier optimizer configuration no longer present in this repository. Run
> `python code/check_reproducibility.py` to see the full comparison. The frozen values
> remain the ones to cite; this note exists so that reproducing this repository from
> scratch does not read as a silent discrepancy.

## Quick Start

### Prerequisites

```bash
pip install numpy pandas scipy matplotlib seaborn
```

### Verify Mathematics

```bash
cd code
python verify_math.py
```

This runs 5 verification tests:
1. **α → W**: Weight generation from RIM quantifier
2. **W → orness**: Direct computation from weight vectors
3. **Monotonicity**: Orness strictly increasing with centroid
4. **Normalization**: All weight vectors sum to 1.0
5. **Δ spread**: F₈ − F₁ = 42.4 percentage points

Note that `verify_math.py` checks only the **internal** consistency of the values stored
in `data/owa/owa_profiles.json` (that α reproduces W, that W reproduces the reported
orness, monotonicity, normalization). It does not check whether that file matches a
fresh run of `owa_weights.py`. For that comparison, run:

```bash
python check_reproducibility.py
```

### Reproduce Delphi Analysis

```bash
python delphi_analysis.py
```

### Generate Figures

```bash
python generate_figures.py
```

All figures use the **Okabe-Ito** colorblind-friendly palette on a white background.

## Seven Behavioral Dimensions

| Domain | Dimension | Code |
|--------|-----------|------|
| Cognitive | Risk Tolerance | D1 |
| Cognitive | Financial Self-Efficacy | D4 |
| Emotional-Affective | Loss Aversion | D5 |
| Emotional-Affective | Emotional Regulation | D7 |
| Contextual-Situational | Investment Horizon | D8 |
| Contextual-Situational | Ambiguity Tolerance | D10 |
| Sociocultural-Identity | Perceived Social Influence | D12 |

## Citation

If you use this work, please cite the software directly:

```bibtex
@software{quintero2026fuzzytaxonomy,
  title={A Fuzzy-OWA Taxonomy of Investor Risk Profiles: Replication Code and Data},
  author={Quintero-Avellaneda, Diego and Ram{\'\i}rez-Angulo, Pedro Juli{\'a}n
          and Le{\'o}n-Castro, Ernesto},
  year={2026},
  url={https://github.com/diegofqa1001/A-Fuzzy-OWA-Taxonomy-of-Investor-Risk-Profiles},
  license={MIT}
}
```

## Authors

- **Diego Quintero-Avellaneda** — Doctoral Candidate, Universidad Nacional de Colombia, Sede Manizales
- **Pedro Julián Ramírez-Angulo** — Thesis Advisor, Universidad Nacional de Colombia, Sede Manizales
- **Ernesto León-Castro** — Thesis Co-Advisor, Universidad Católica de la Santísima Concepción, Chile

## License

This work is licensed under the [MIT License](LICENSE). The data are provided for academic review and reproducibility purposes.

## Acknowledgments

This research is part of a doctoral thesis in Administration at the Universidad Nacional de Colombia, Sede Manizales.
