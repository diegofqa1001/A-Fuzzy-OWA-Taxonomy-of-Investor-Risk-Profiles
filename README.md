# A Fuzzy-OWA Taxonomy of Investor Risk Profiles

> **Beyond the Conservative–Moderate–Aggressive Triad: An Expanded Behavioral Taxonomy Formalized through Fuzzy Linguistic Vectors and OWA Operators**

## Overview

This repository contains the replication materials, data, and code for the research article proposing a paradigm shift in investor risk profiling: replacing the static tripartite classification (conservative–moderate–aggressive) with an expanded taxonomy of **eight behavioral risk profiles** formalized through fuzzy linguistic vectors and calibrated via **Ordered Weighted Averaging (OWA) operators** using Yager's Regular Increasing Monotone (RIM) quantifier.

### Key Contributions

1. **Seven behavioral dimensions** identified through a PRISMA 2020 systematic review of 78 studies (2019–2026) indexed in Scopus and Web of Science, spanning cognitive, emotional-affective, contextual-situational, and sociocultural-identity domains.

2. **Eight prototypical investor profiles** (Guardian → Visionary) formalized as fuzzy linguistic vectors with explicit OWA aggregation semantics, producing up to **42.4 percentage points** of difference in asset evaluation depending on profile assignment.

3. **RIM quantifier-based weight derivation** providing a theoretically grounded, auditable, and reproducible weight generation mechanism: $w_j = Q(j/n) - Q((j-1)/n)$ where $Q(r) = r^\alpha$.

4. **Modified Delphi validation** with 12 international experts (6 behavioral finance, 6 fuzzy methods) from 6 countries achieving 89.2% consensus (Md ≥ 4, IVC ≥ 0.78) with statistically significant inter-rater concordance (Kendall's W = 0.278, p < 0.001).

## Repository Structure

```
├── manuscript/
│   └── Articulo_2_V7_Springer.docx     # Full article (Spanish body, English tables/figures)
│
├── data/
│   ├── delphi/
│   │   ├── expert_panel.csv             # Panel composition (12 experts, 6 countries)
│   │   ├── raw_section_A.csv            # Raw Likert ratings — Section A (dimensions)
│   │   ├── raw_section_B.csv            # Raw Likert ratings — Section B (profiles)
│   │   ├── raw_section_C.csv            # Raw Likert ratings — Section C (global system)
│   │   ├── results.json                 # Computed statistics (Kendall W, Lawshe IVC, medians)
│   │   ├── decisions.json               # Consensus decisions per item
│   │   └── qualitative.json             # Expert qualitative observations
│   └── owa/
│       └── owa_profiles.json            # OWA weight vectors, α values, orness for 8 profiles
│
├── code/
│   ├── owa_weights.py                   # OWA weight computation and verification
│   ├── delphi_analysis.py               # Delphi statistical analysis (Kendall W, Lawshe IVC)
│   ├── generate_figures.py              # Reproduce all Delphi validation figures
│   ├── verify_math.py                   # Mathematical verification suite (5 tests)
│   └── requirements.txt                 # Python dependencies
│
├── figures/
│   ├── fig_delphi_concordance.png       # Kendall's W by section
│   ├── fig_delphi_dimensions.png        # IVC heatmap for dimension items
│   ├── fig_delphi_profiles.png          # IVC heatmap for profile items
│   ├── fig_delphi_global.png            # Global system evaluation
│   ├── fig_delphi_ivc.png               # IVC distribution across all items
│   └── fig_delphi_subpanel_comparison.png  # Subpanel A vs B comparison
│
├── validation/
│   └── Protocolo_Validacion_Expertos.docx  # Expert validation protocol (65 items)
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
3. **Monotonicity**: Proposition 1 (orness strictly increasing with centroid)
4. **Normalization**: All weight vectors sum to 1.0
5. **Δ spread**: F₈ − F₁ = 42.4 percentage points

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

If you use this work, please cite:

```bibtex
@article{quintero2026fuzzy,
  title={Beyond the Conservative--Moderate--Aggressive Triad: An Expanded Behavioral
         Taxonomy of Investor Risk Profiles Formalized through Fuzzy Linguistic
         Vectors and OWA Operators},
  author={Quintero-Avellaneda, Diego and Ram{\'\i}rez-Angulo, Pedro Juli{\'a}n
          and Le{\'o}n-Castro, Ernesto},
  journal={Manuscript submitted for publication},
  year={2026}
}
```

## Authors

- **Diego Quintero-Avellaneda** — Doctoral Candidate, Universidad Nacional de Colombia, Sede Manizales
- **Pedro Julián Ramírez-Angulo** — Thesis Advisor, Universidad Nacional de Colombia, Sede Manizales
- **Ernesto León-Castro** — Thesis Co-Advisor, Universidad Católica de la Santísima Concepción, Chile

## License

This work is licensed under the [MIT License](LICENSE). The data and manuscript are provided for academic review and reproducibility purposes.

## Acknowledgments

This research is part of a doctoral thesis in Administration at the Universidad Nacional de Colombia, Sede Manizales. We thank the 12 international experts who participated in the Delphi validation panel.
