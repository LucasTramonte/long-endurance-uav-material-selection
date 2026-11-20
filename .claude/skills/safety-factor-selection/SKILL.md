---
name: safety-factor-selection
description: Choose and cite a safety factor N (s) for a strength constraint from reliable literature, with its verification status. Use whenever a strength or load requirement is written, or an Ashby strength constraint is drawn.
---

# Safety factor from the literature

A safety factor is **taken from a cited source and written with its scope**. It is not tuned to make a material pass.

## Rules

1. Write the requirement as $\sigma_{max}\le\sigma_y/s$ (README Section 1.4.4) and give $s$, its source and what it applies to.
2. Use the table `SAFETY_FACTORS` in `src/math_modeling/ashby_selection.py`. Add a row only after reading the source; set `verified=True` only when the primary text (standard or textbook table) was read, otherwise leave it `False` and say so in the report.
3. Say which load the factor multiplies: the **limit load** (maximum expected in service) gives the **ultimate load**. Do not apply a factor twice to a load that is already ultimate.
4. Brittle materials and composites need more care: use design allowables (A- or B-basis for composites, MIL-HDBK-17 / CMH-17) *before* the factor, and a larger factor for brittle fracture. Ceramics are excluded from tension altogether (`ashby-chart-selection`).
5. Show a sensitivity: re-run the selection for two or three values of $s$ (`safety_factor` in `data/granta_filters.json`, then `python -m src.analysis.decision_matrix`) and state whether the ranking changes.

## What has been read so far (honest status)

| Value | Scope | Source | Verified |
| --- | --- | --- | --- |
| 1.5 | limit to ultimate load, transport aircraft structure | 14 CFR 25.303 (secondary copies read, confirm on eCFR / Cornell LII) | no |
| 2.5-4 | static ductile parts, uncertain loads | lecture slides (ABE 4171, Univ. of Florida) | no, not the textbook table |
| 3-4 | brittle parts, static load, reliable data | Machine Design article on failure theories | no |

Shigley's design-factor table and the UAS / military rules (NASA-STD-5001, MIL-HDBK-17) were searched for and **not** read: they must be consulted before the factor is declared final. 14 CFR Part 25 is not a rule for a 150 g UAV; it is used here as an aeronautical reference value only.
