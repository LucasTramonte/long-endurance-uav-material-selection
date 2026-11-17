# Lecture References - UNICAMP ER700/EU910 (Prof. Dr. Jeferson Almeida Dias)

Mapping of project sections to the course lectures (slides in `assets/courses/`). Lecture titles were taken from the slide decks (originally in Portuguese).

| Aula | Topic (English) | Original title (PT) | Used in project section |
|---|---|---|---|
| 1 | Review of material classes (metals, ceramics, polymers, composites) | Revisão das classes de materiais | Section 3 - candidate families (CFRP, PEEK-CF, PC, Al 7075) |
| 2 | Review of mechanical properties (tensile test, E, sigma_y, toughness) | Revisão de propriedades mecânicas dos materiais | Sections 1, 2, 4 - property definitions, Hookean regime, K_Ic |
| 3 | Selection criteria; material identification; selection charts | Critérios de seleção de materiais para um projeto; diagramas de seleção | Sections 1 and 3 - requirements, Ashby chart reading |
| 4 | Translating the application; merit indices (function, constraints, objectives, free variables) | Tradução da aplicação e índice de mérito | Section 2 - derivation of IM1, IM2 |
| 5 | Strength-, stiffness- and cost-limited designs; beam in bending | Projetos limitados por resistência, rigidez e custo | Sections 2 and 6 - panel/beam indices, combined constraints |
| 6 | Combining merit indices with Ashby maps; cost diagrams; vertically loaded light, stiff panel | Combinando os índices de mérito com os Mapas de Ashby; diagramas de custo; painel carregado verticalmente | Sections 2, 3 and 6 - IM3, guidelines on E-rho and cost charts, weighted decision |

## Translation table (design problem -> lecture method)

| Element | UAV fuselage panel |
|---|---|
| Function | Light, stiff shell panel carrying bending loads |
| Constraints | Length L, width w fixed; stiffness S prescribed; K_Ic > 2.0; water < 0.2%; UV >= Acceptable |
| Objective | Minimise mass (IM1) and cost (IM3) |
| Free variable | Panel thickness t |

## Not covered in Aulas 1-6 (supplementary sources)

- Laminate theory (`src/math_modeling/composite_anisotropy.py`): Daniel & Ishai [9] (see README References).
- Vibration isolation (`vibration_fatigue.py`): Rao [10].
- Aulas 8-10 are present in `assets/courses/` but are outside the requested mapping; extend this table if they are used (processes, selection with multiple constraints).

> The slides themselves are private course material and are **not** distributed with this repository (`assets/courses/` is git-ignored). Cite them as reference [13] in the README.
