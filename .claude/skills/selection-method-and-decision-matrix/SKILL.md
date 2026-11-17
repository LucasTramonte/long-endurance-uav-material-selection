---
name: selection-method-and-decision-matrix
description: Method for choosing materials - selection criteria, three pre-selection methods, 1-5 decision matrix, classification of materials by composition, shear basics and the manufacturing process tree. Use when writing selection or manufacturing sections, or when classifying a material.
---

# Selection method, decision matrix and process tree

Report text: README Sections 5 (process tree) and 6.1 (criteria, pre-selection, matrix). Code: `src/analysis/decision_matrix.py`.

## 1. Selection criteria (all four must appear)

1. Application (use) and load case.
2. Geometry.
3. Properties (the merit indices, `ashby-chart-selection`).
4. Manufacturing process. Machining is done on the chosen material, after it.

## 2. Pre-selection: three methods

1. **Documentation** - property lists.
2. **Selection diagrams** - bubble maps, bar charts, Ashby charts.
3. **Software / computational resources** - for example Granta.

There are on the order of 200 000 engineering materials (course notes; confirm the figure before quoting), so a shortlist is mandatory before any matrix.

## 3. Decision matrix

Score each option 1-5 on each criterion, weight, and sum. Example shape from the notes (3 options, criteria mechanical / thermal / cost):

| Criterion | Option 1 | Option 2 | Option 3 |
| --- | --- | --- | --- |
| Mechanical | 3 | 4 | 5 |
| Thermal | 2 | 5 | 2 |
| Cost | 3 | 3 | 5 |

The repository's version normalises merit indices to [0, 1] and uses team scores for manufacturability and durability (README 6.1). Report the weights and test their sensitivity (README 6.3).

## 4. Identify the class from the composition

| Class | Rule | Examples from the exercise |
| --- | --- | --- |
| Metal | metallic elements, alloys | stainless steel Fe-18Cr-8Ni (<= 0.08 % C), Ti-6Al-4V, 6061 and Al-4.4Cu-1.5Mg-0.6Mn alloys, brass Cu-35Zn, bronze Cu-8Sn |
| Ceramic | metal bonded to oxygen, nitrogen, sulphur or carbon; inorganic non-metal | Al2O3, SiC, Si3N4, ZrO2, vitreous SiO2 (glass 72 SiO2-14 Na2O-10 CaO-4 MgO), quartz, CdS |
| Polymer | carbon-hydrogen chains | LDPE, HDPE, PP, PS, PMMA, PVC, PTFE, PA 6.6 |
| Composite | two phases | CFRP, GFRP, wood (with polymeric adhesive), reinforced concrete, SiC-reinforced aluminium, SBR with steel reinforcement |

(Electronegativity order used in the notes: F O N Cl Br I S C P H.)

## 5. Shear and mechanical behaviour

$\tau=G\gamma$ ($\tau$ shear stress, $\gamma$ shear strain, $G$ shear modulus). Metals carry tension and shear better than ceramics, which is why ceramics are not selected for tension-loaded parts.

## 6. Process tree

- **Primary (general shape):** casting (metals), extrusion, injection moulding; powder-forming methods such as pressing (ceramics).
- **Secondary (adjust shape, change properties):** heat treatment, drilling, cutting, machining.
- **Finishing:** joining (fasteners) and surface engineering (paint, coatings).

## Report rules

- Name the criterion that eliminates each material; keep screening (hard constraints) apart from ranking (weights).
- Say which scores are data and which are team judgement.
