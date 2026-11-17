---
name: ashby-chart-selection
description: Select a material on an Ashby chart with a constraint line and a merit-index guide line, and say so explicitly in English. Use when adding or changing material-selection text, figures or tables in this repository.
---

# Ashby chart selection

The selection is made **on the chart**, with the five steps below, and the report must state each step explicitly in English. The numbers behind the chart are computed by `src/math_modeling/ashby_selection.py`; the drawing is made by `src/analysis/ashby_charts.py`. Never hand-place a line.

## The five steps

1. **Mark the constraint.** Draw the limit as a straight line on the chart: a horizontal line for a minimum $E$ or $\sigma$, a vertical line for a maximum density. The limit comes from the load model (README Section 1.4), never from a guess. The region on the wrong side is shaded.
2. **Discard what the constraint cuts.** If the line crosses a material bubble, part of that material cannot meet the requirement, so the whole material is discarded. (With the point values of `data/materials_db.json` a material is either above or below the line; on the printed charts the bubble is an ellipse and the test is visual.)
3. **Choose the guide line of the merit index.** It is the straight line $y^{a}/x=C$ of slope $1/a$ on log-log axes. Slope 3 for $E^{1/3}/\rho$ (stiff panel), 2 for $E^{1/2}/\rho$ (stiff beam), 1 for $E/\rho$ and $\sigma/\rho$ (stiff tie, strong tie). The slopes are the `GUIDE_SLOPES` table; the derivations are in README Section 2.
4. **Slide the ruler along the slope.** Keep the slope fixed and move the line (as with a ruler on the printed chart) until it reaches the best surviving material. Materials above or to the left of the line have a higher index (`offset_decades > 0`).
5. **Keep a material only if the guide line passes through the centre of its bubble.** Report the material the line passes through, and the ones above it if any. Materials far from the line are ranked by `offset_decades`, not selected.

## Fixed rules

- **Ceramics and glasses are not used in tension.** Their tensile strength is low and scattered; the printed $\sigma_f$ for ceramics is the modulus of rupture (bending), not a tensile strength. `excluded_in_tension()` removes them from every tension-loaded selection. State this next to any chart that shows the yellow ceramic bubbles.
- **The strength constraint includes the safety factor** $s$: $\sigma_y\ge s\,\sigma_{max}$. $s$ comes from the literature through the `safety-factor-selection` skill, never from the team's preference.
- For a spinning part the constraint is a slope-1 line: `rotating-parts-merit-indices`. For cyclic loads check fatigue first: `fatigue-assessment`. Cost charts: `cost-merit-indices`.
- Print the **assumptions with the chart**: arm dimensions, load, allowable deflection, $s$. They are assumptions until the team replaces them.
- Cost charts use *relative* cost per unit volume (Ashby), not USD/m^3; do not mix the two on one axis.
- The source PDFs in `assets/ashby_charts/` are third-party and stay git-ignored (never `git add -f` them); the annotated images made from them (`python -m src.analysis.ashby_charts --print`) are published by the team's decision with the source credited. `--open` draws blank axes from `data/materials_db.json` only for machines without the PDFs.

## Premises and the original charts

- Every number (arm, rotor, safety factor, balance grade, fatigue ratio, steel reference) is a **premise** in `data/granta_filters.json` -> `load_cases`. Change it there, never in a chart script. The same premises feed `decision_matrix.screen()` (`load_case_screening.py`), so charts and ranking cannot disagree.
- `python -m src.analysis.ashby_charts --print` draws the steps on the four ORIGINAL course charts (E-rho, sigma-rho, E-cost, sigma-cost) with numbered arrows: 1 constraint, 2 discarded, 3 guide line, 4 ruler slides along the slope, 5 selected; a green arrow shows the direction of a higher index. The annotated images go to `docs/figures/ashby_*_annotated.png` and are published (team decision, source credited in the image); the source PDFs in `assets/ashby_charts/` stay git-ignored. Embed the annotated images in the README, not blank charts.
- Printed axes can contain typos (the strength-cost chart labels its last decade 1000 for 100): calibrate on the gridlines and check by overlay.

## Workflow

1. Compute the requirements: `arm_requirements(F, L, b, h, w_max, s)`.
2. Screen: `screen_by_constraint(materials, constraint, tension=True)`.
3. Draw: `python -m src.analysis.ashby_charts --open --print --safety <s>`.
4. Look at the PNG (labels must not overlap; `tests/test_ashby.py` checks it), then write the step-by-step reading under the figure.
5. State what could not be verified (data are representative until the Granta/MatWeb export replaces them).
