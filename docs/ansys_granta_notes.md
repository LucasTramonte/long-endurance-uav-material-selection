# Ansys Granta Integration Notes (Template)

Use this document as the lab notebook for every manual Granta session. Everything the report cites must be reproducible from here.

## 1. Session log

| Field | Entry |
|---|---|
| Date / operator | |
| Product | Granta EduPack / Selector (version: ) |
| Database / level | e.g. Level 3 Aerospace |
| Units | SI (GPa, MPa, kg/m^3, USD/kg) |
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
| C | E vs volumetric cost (price x density) | slope 1 (E/Cv,R = C) | Maximise IM3 | `docs/figures/granta_E_cost.png` |
| D | Fracture toughness vs Young's modulus | none | Toughness check | |

Procedure: add the chart stage, set axes, add *Selection Line* with the stated slope, drag it until only the shortlist remains above the line, and note the intercept value C used. Blank charts (local, git-ignored): `assets/ashby_charts/mapas_ashby.pdf`, `assets/ashby_charts/diagrama_custo.pdf` (Ashby [1]; see README References).

## 4. Property export checklist

For the four shortlisted materials, copy **Mean (or range min/max)** of each property into `data/materials_db.json`:

- [ ] density, Young's modulus, yield / tensile strength, fracture toughness
- [ ] water absorption (24 h), UV resistance (categorical), max service temperature
- [ ] thermal conductivity, CTE, price (USD/kg)
- [ ] For composites: record layup, Vf and direction (quasi-isotropic assumed - see `composite_anisotropy.py` to cross-check E)
- [ ] Record the Granta record name, e.g. "Epoxy/HS carbon fiber, UD prepreg, quasi-isotropic lay-up"
- [ ] Update `metadata.verification_status` in the JSON to "Verified against Granta <date>"

Then regenerate the tables: `python -m src.analysis.export_tables --out outputs`.

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
