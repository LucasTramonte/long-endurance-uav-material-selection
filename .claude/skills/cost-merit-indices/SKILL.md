---
name: cost-merit-indices
description: Cost-based material selection - mass cost, volumetric cost, relative cost, the currency and inflation problem, and the tube cost index IM3. Use when a cost number, cost chart or cost index appears in a report.
---

# Cost merit indices

Code: `src/math_modeling/merit_indices.py` (`volumetric_cost`, `tube_cost_index`, `relative_volumetric_cost`). Report text: README Sections 2.3 and 2.4.

## The problem with prices

- A price depends on the **currency** used in each country and changes with **inflation**, so absolute values age quickly. Always state the date, the currency and the source.
- Definitions: mass cost $C_m$ (currency/kg); volumetric cost $C_v=C_m\rho$ (currency/m^3); cost of a part $C=C_m\,m$ (currency).

## Index of this project

| Case | Cost of the part | Index to maximise |
| --- | --- | --- |
| Stiff thin-walled tube (fixed radius, free wall thickness) | $C=\dfrac{S L^4}{24R^2}\,\dfrac{C_m\rho}{E}$ | $E/C_{v,R}$ (IM3) |

## Relative cost

$$C_{v,R}=\frac{C_m\,\rho}{(C_m\,\rho)_{ref}}$$

Dividing by a reference material removes the currency and most of the inflation. The course notes take **steel** as the reference; Ashby's cost charts are plotted against $C_{v,R}$. **Confirm the reference in Ashby's text before mixing relative values with USD/m^3 on one axis**, and say in the report which one is used.

## Rules

- Guide lines on the cost charts have slope 1 for $E/C_{v,R}$ and for $\sigma_f/C_{v,R}$.
- The strength chart against cost uses the same five-step reading as the mass charts (`ashby-chart-selection`); ceramics stay excluded in tension.
- The relative-cost reference used in the code is a premise (`load_cases.reference_steel`: 0.7 USD/kg, 7850 kg/m^3; the price is not from an official source). Overlaying the DB points on the printed cost chart landed CFRP and PEEK-CF30 in their printed bubbles, which supports the order of magnitude but is not a validation.
- Material prices in `data/materials_db.json` are indicative placeholders until the Granta/MatWeb export replaces them.
