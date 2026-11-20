# Benchmark: Niero (2024) - Material selection for UAV structural components

**Reference [20]** NIERO, J. P. **Proposta de método para seleção de materiais para componentes estruturais de VANTs**. 2024. 48 p. Trabalho de Conclusão de Curso (Bacharelado em Engenharia Aeronáutica) - Faculdade de Engenharia, Universidade Estadual Paulista (UNESP), São João da Boa Vista, 2024. Advisor: Prof. Dr. Éder Luiz Oliveira. The PDF is kept locally in `assets/benchmark/` (git-ignored; obtain it from the UNESP institutional repository).

This thesis is the closest published case to our project (Ashby-based selection for UAV structures at preliminary-design level), so it is used to **validate our calculations**, to **compare methods and conclusions**, and as a **structural reference** for the written report.

## 1. What the thesis does

- **Component:** internal structure of a flying-wing UAV - spars (beam in bending, stiffness-limited) and ribs (plate in bending, stiffness-limited).
- **Method:** Ashby merit indices + a Pahl & Beitz weighted matrix (scale 0-5) with three extra criteria: **cost, corrosion resistance, manufacturing difficulty**. Implemented in Excel.
- **Indices:** spar $IM_L=E^{1/2}/\rho$; rib $IM_N=E^{1/3}/\rho$ (from Ferrante's table of indices).
- **Screening:** user-defined minimum $E$ and maximum $\rho$, then weighted ranking.
- **Data:** 19 materials (7 aluminium alloys, 4 steels/cast iron, 3 titanium alloys, 5 composites) from MatWeb.
- **Scenarios:** prioritise IM (weights 0.7/0.1/0.1/0.1), prioritise cost (0.1/0.1/0.7/0.1), prioritise corrosion resistance.
- **Findings:** carbon/epoxy has the highest IM for both components; aluminium alloys appear as a good alternative in **all** scenarios; steels are excluded by density, titanium by cost and manufacturing difficulty; composites win when IM weighs most, limited by cost. The author notes that the cost, corrosion and manufacturing scores are subjective and that the final choice needs a documentation step.

## 2. Cross-validation of our code (automated)

The tables of the thesis (E, $\rho$, $IM_L$, $IM_N$ for all 19 materials) are transcribed in [`data/benchmark_niero2024.json`](../data/benchmark_niero2024.json) and tested in [`tests/test_benchmark.py`](../tests/test_benchmark.py).

| Check | Result |
|---|---|
| Our `bending_panel_index` ($E^{1/3}/\rho$) vs thesis $IM_N$, 19 materials | all within 0.5 % (rounding of the published values) |
| Our `bending_beam_index` ($E^{1/2}/\rho$, added for this benchmark) vs thesis $IM_L$, 19 materials | all within 0.5 % |
| Al 7075-T6 plate index | thesis 1.478, this project 1.48 |
| Carbon/epoxy has the highest index; steels/cast iron the lowest four | reproduced |

Not reproduced: the weighted scores of the thesis (its Table 8) - the normalisation of the 0-5 scores is not specified in the text, so only the indices are validated.

## 3. Comparison of methods and results

| Aspect | Niero (2024) | This project |
|---|---|---|
| Component | Flying-wing spars and ribs | Ducted-quadcopter airframe (body, ducts, arms) |
| Indices | $E^{1/2}/\rho$ (beam), $E^{1/3}/\rho$ (plate) | $E/\rho$ (tube, fixed radius), $\sigma_y/\rho$ (tie), $E/C_{v,R}$ (cost); the plate index $E^{1/3}/\rho$ is kept for the benchmark |
| Extra criteria | Cost, corrosion, manufacturing (scores 0-5) | Mechanical, cost (IM3), manufacturability, durability (weights editable) |
| Hard filters | $E_{min}$, $\rho_{max}$ | UV, 24 h water absorption, $K_{Ic}$, temperature, density |
| Candidate set | 19 materials, 4 classes | 4 shortlisted + 3 screening-pool materials |
| Composite modelling | Single UD carbon/epoxy value ($E$ = 142 GPa) | Quasi-isotropic laminate ($E$ = 48 GPa, CLT cross-check) |
| Manufacturing / dynamics | Scored qualitatively | Process engineering (CNC 20,000 RPM, cure cycle), 40,000 RPM isolation |
| Tolerances / CAD | Not covered | ISO 2768-m, CAD drawing |
| Tools | MatWeb + Excel | Ansys Granta + MatWeb + Python |

**Consistency of conclusions** (same scenario logic, our four criteria):

| Scenario | Thesis | This project |
|---|---|---|
| Performance (IM) prioritised | Carbon/epoxy first | CFRP first |
| Cost prioritised | Steels, then aluminium; composites last | Al 7075-T6 first, PC second, CFRP third |
| Durability / corrosion prioritised | 304 stainless steel first, then titanium alloys; aluminium within about 0.03-0.3 points | PEEK-CF30 first, CFRP second, Al 7075-T6 third |
| Overall | Aluminium is a good alternative in every scenario (small score gap to the leaders) | Al 7075-T6 ranks 1st (default, cost priority), 2nd (performance priority), 3rd (durability priority) |

Our results agree with the thesis in direction. The main quantitative difference is the composite: the thesis uses a **unidirectional** value ($E$ = 142 GPa, IM = 3.26), which overstates a real shell; the quasi-isotropic value used here (IM1 = 2.34) is the appropriate one for a multi-directional load path, and still ranks first on mass.

## 4. Lessons applied

- **Scenario analysis** with a fixed set of weights per priority (performance, cost, durability) - adopted in README Section 6.3.
- **Documentation stage** after the numeric ranking (history of use, datasheets) - listed as a caveat and to-do in README Sections 1.3 and 6.4.
- **Honest treatment of subjective scores** - same limitation, stated explicitly.
- Where we go beyond it: hard environmental constraints, laminate anisotropy, process and vibration engineering, tolerancing and CAD.

## 5. Structural reference for the written report

The thesis follows the TCC structure: cover, title page, catalogue card, abstract (PT/EN), lists, table of contents, 1 Introduction (motivation, objectives, structure), 2 Literature review, 3 Methodology, 4 Results analysis (one subsection per scenario), 5 Conclusions (with future work), 6 References, in ABNT. Our deliverable follows the professor's brief [14] instead (cover; project description with technical drawing; methodological research with indices and Ashby maps; recommendations; references in the format used at UNICAMP), borrowing the thesis' habits of: numbered tables/figures with a "Fonte:" line, one results subsection per scenario, and an explicit conclusions/limitations/future-work section.

## 6. Caveats

- The thesis targets a different component (flying wing) and uses MatWeb only; its numbers are a sanity check, not a source of truth for our material data.
- Redistribution: the PDF is a published thesis and is **not** part of the repository (git-ignored, see `assets/README.md`); only the cited numerical tables are in `data/benchmark_niero2024.json`.
