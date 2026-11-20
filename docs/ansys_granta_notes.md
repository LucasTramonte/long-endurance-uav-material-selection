# Ansys Granta Integration Notes (Template)

Use this document as the lab notebook for every manual Granta session. Everything the report cites must be reproducible from here.

## 1. Session log

| Field | Entry |
|---|---|
| Date / operator | November 2026 / Lucas Tramonte (records read: CFRP epoxy isotropic, GFRP epoxy isotropic, Aluminum alloys, Magnesium alloys, PEEK, PC, ABS, Low carbon steel) |
| Product | Granta EduPack 2024 R1, version 24.1.1 (Help > About) |
| Database / level | MaterialUniverse tree with family-level records (the EduPack level still has to be confirmed) |
| Units | SI (GPa, MPa, kg/m^3); price in BRL/kg (currency of this installation) |
| Export files | `data/granta_exports/<name>.xlsx` (create folder; large files via Git LFS or share drive) |

## 2. Stage 1 - Limit stage (hard constraints)

Mirror of `data/granta_filters.json`. Enter each as a Limit stage in Granta.

| Attribute (Granta name) | Limit | Materials remaining | Screenshot |
|---|---|---|---|
| Durability > UV radiation (sunlight) | >= Acceptable | | `docs/figures/granta_limit_uv.png` |
| Durability > Water (fresh) / Water absorption @ 24 h | < 0.2 % | | `docs/figures/granta_limit_water.png` |
| Fracture toughness | > 2.0 MPa.m^0.5 | | `docs/figures/granta_limit_kic.png` |
| Maximum service temperature | > 80 C | | |
| Density | < 3000 kg/m^3 | | |

## 3. Stage 2 - Chart stages (Ashby maps)

| Chart | Axes (log-log) | Guideline | Selection line | Screenshot |
|---|---|---|---|---|
| A | Young's modulus E vs Density | slope 1 (E/rho = C) | Maximise IM1 | `docs/figures/granta_E_rho.png` |
| B | Yield (tensile) strength vs Density | slope 1 (sigma_y/rho = C) | Maximise IM2 | `docs/figures/granta_sy_rho.png` |
| C | E vs relative cost per unit volume (or price x density) | slope 1 (E/Cv = C) | Maximise IM3 | `docs/figures/granta_E_cost.png` |
| D | Fracture toughness vs Young's modulus | none | Toughness check | |

Procedure: add the chart stage, set axes, add *Selection Line* with the stated slope, drag it until only the shortlist remains above the line, and note the intercept value C used. Blank charts (local, git-ignored): `assets/ashby_charts/mapas_ashby.pdf`, `assets/ashby_charts/diagrama_custo.pdf` (Ashby [1]; see README References).

## 4. Property export checklist

The dataset (`data/materials_db.json`) holds the **[minimum, maximum] range** of each property exactly as Granta shows it; the code takes the centre of the range (geometric mean) as the representative value and the lowest/highest value for screening. An asterisk in Granta marks an estimated value (listed in `estimated` of each record).

Records read (November 2026):

- [x] CFRP, epoxy matrix (isotropic): density, price, E, yield and tensile strength, fatigue strength at 10^7 cycles, fracture toughness, maximum service temperature, thermal conductivity, CTE
- [x] Aluminum alloys: same properties
- [x] Magnesium alloys: same properties
- [x] GFRP, epoxy matrix (isotropic): all properties (almost every value is estimated in Granta)
- [x] Polyetheretherketone (PEEK, unfilled) and Polycarbonate (PC): all mechanical, thermal and price properties
- [x] Acrylonitrile butadiene styrene (ABS)
- [ ] PEEK with 30 % carbon fibre (not in the tree seen so far; try the advanced search)
- [ ] UV resistance and water absorption in 24 h: not among the attributes of this installation (axis and limit lists have no Durability category); the two filters stay not evaluated
- [x] Low carbon steel (Metals > Ferrous): price 6.31-9.2 BRL/kg, density 7800-7820 kg/m^3 (reference of the relative cost; `reference_steel` in `data/granta_filters.json`)
- [ ] Specific alloy grades (e.g. 7075-T6) if the EduPack level offers them
- [ ] Record the Granta record name exactly as shown and keep the screenshot

Then regenerate the tables: `python -m src.analysis.export_tables --shortlist`.

## 5. MatWeb cross-check

| Material | MatWeb datasheet URL | Property | Granta | MatWeb | Delta % |
|---|---|---|---|---|---|
| | | | | | |

Differences above 15% must be explained (grade, temper, layup, test method).

## 6. Screenshot conventions

PNG, >= 1600 px wide, light background, axes legible. Name: `granta_<chart>_<nn>.png` in `docs/figures/`. Add a one-line caption below each one in the report.

## 7. Known pitfalls

- Granta ranges for composites span layups; do not mix UD properties with quasi-isotropic assumptions.
- "Price" is indicative and volatile; record the date.
- Water absorption in Granta may be 24 h or saturation; the 0.2 % limit in this project refers to 24 h (ASTM D570).

## 7. Status of the Granta prints and checklist for the team

Done (screens collected in the team's local PDF `assets/Informacoes granta (2).pdf`, not published): the material tree; the property records of CFRP, GFRP, aluminium alloys, magnesium alloys, PEEK, PC, ABS and low carbon steel; the Help > About screen (EduPack 2024 R1, 24.1.1); the chart-stage and limit-stage dialogs; the limit stages (density <= 3000, K_Ic >= 2, T_max >= 80, then E >= 3.84, then yield >= 7.2) with their result lists; and single-property bar charts (fatigue strength, Young's modulus, yield strength). Granta keeps PEEK at E >= 3.84 because its range (3.76-3.95 GPa) overlaps the limit; the report discards it (the constraint cuts its bubble).

**Still to do: the two-axis Ashby charts** (set the property on the X tab *and* on the Y tab of the chart-stage dialog; the bar charts so far have only the Y axis). Make them in a selection *without* limit stages, so the materials that the constraint cuts stay visible. Every chart has log axes, the seven records labelled with the same colours, a horizontal constraint line and a slope-1 guide line.

| # | Chart (X axis, Y axis) | Constraint line | Guide line (slope 1, through) | Print names | In the report |
|---|---|---|---|---|---|
| 1 | Density, Young's modulus | E = 3.84 GPa (cuts PEEK, PC, ABS) | E = 0.0657 rho, through CFRP (1549 kg/m3; 101.7 GPa) | `granta_E_rho_eixos.png`, `_restricao.png`, `_guia.png`, `_final.png` | `_final` in the body, the rest in the appendix |
| 2 | Density, Yield strength | 7.2 MPa and the line sigma = 0.00758 rho | sigma = 0.4905 rho, through CFRP (1549; 760 MPa) | `granta_sigma_rho_restricoes.png`, `_final.png` | `_final` in the body |
| 3 | Price x Density (BRL/m3, Advanced button), Young's modulus | E = 3.84 GPa | E = 1.498 GPa per 1000 BRL/m3, through aluminium (48,017 BRL/m3; 71.9 GPa) | `granta_E_custo_restricao.png`, `_final.png` | `_final` in the body (steel lies above the line but is excluded by density) |
| 4 | Density, Fatigue strength at 10^7 cycles | none (the stress amplitude is unknown) | sigma = 0.1369 rho, through CFRP (1549; 212.1 MPa) | `granta_fadiga_rho.png` | appendix |

Save the prints as `docs/figures/granta_*.png`. Centres of the bubbles used for the lines: CFRP (1549 kg/m3, 101.7 GPa, 759.9 MPa, 321,781 BRL/m3), aluminium (2724, 71.9, 218.7, 48,017), magnesium (1810, 44.0, 153.4, 63,469), PEEK (1310, 3.85, 99.5, 508,832), PC (1200, 2.38, 62.1, 22,001), ABS (1045, 2.39, 41.4, 13,703), GFRP (1857, 21.4, 250.9, 344,950), steel (7810, 209.8, 300.9, 59,506).

