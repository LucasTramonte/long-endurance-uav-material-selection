# Ansys Granta Integration Notes (Template)

Use this document as the lab notebook for every manual Granta session. Everything the report cites must be reproducible from here.

## 1. Session log

| Field | Entry |
|---|---|
| Date / operator | November 2026 / Lucas Tramonte (records read: CFRP epoxy isotropic, Aluminum alloys, Magnesium alloys, PEEK, PC, ABS, Low carbon steel; GFRP epoxy isotropic only density and price) |
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
- [ ] GFRP, epoxy matrix (isotropic): only density and price read; read E, strength, toughness and temperature
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
