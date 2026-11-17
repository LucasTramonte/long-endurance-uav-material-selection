---
name: fatigue-assessment
description: Fatigue checks for dynamic loads - stress-cycle parameters, S-N curve, endurance limit, life at 40,000 RPM, fractography and surface engineering. Use whenever a part sees cyclic load (rotor unbalance, vibration, arms, mounts) or a report states a fatigue life.
---

# Fatigue assessment

Implemented in `src/math_modeling/vibration_fatigue.py` (`stress_cycle`, `basquin_cycles`, `miner_damage`, `cycles_in_flight`, `hours_for_cycles`) and tested in `tests/test_rotating_fatigue.py`. Report text: README Section 5.4.

## 1. When fatigue must be checked

Dynamic (cyclic) loads must be assessed for fatigue; **static loads are not enough**. Any part loaded by rotor unbalance, vibration or repeated manoeuvres is in scope.

## 2. Stress-cycle parameters (tension positive, compression negative)

| Quantity | Definition |
| --- | --- |
| Stress range $\Delta\sigma$ | $\sigma_{max}-\sigma_{min}$ |
| Stress amplitude $\sigma_a$ | $\Delta\sigma/2$ |
| Mean stress $\sigma_m$ | $(\sigma_{max}+\sigma_{min})/2$ |
| Stress ratio $R$ | $\sigma_{min}/\sigma_{max}$ |

Worked check (must reproduce): 20 MPa tension and 10 MPa compression give $\Delta\sigma=30$ MPa, $\sigma_a=15$ MPa, $\sigma_m=5$ MPa, $R=-0.5$. Fully reversed: $R=-1$, $\sigma_m=0$.

## 3. S-N curve

- Plot amplitude $\sigma_a$ (MPa) against cycles $N$, both on log scales; mark the **fatigue (endurance) limit** where the curve flattens, commonly read at $10^7$ cycles.
- The curve falls because of how the test runs: load is lowered after each failure and a new machined, normalised specimen is mounted (rotating-bending test; watch the course video).
- Not every material has a true limit. Ferrous alloys are commonly described as having one; aluminium alloys, polymers and composites are not, so quote a life at a stated amplitude. *This is general knowledge and has not been checked against a source in this repository: cite before publishing.*
- Models in the code: Basquin $\sigma_a=\sigma_f'(2N)^b$; Miner $D=\sum n_i/N_i\ge1$ means failure.

## 4. Life at the drone's excitation

At 40 000 rpm, $f=666.7$ Hz: $10^7$ cycles in 4.2 h, $10^9$ cycles in about 417 h, 4.8 million cycles in a 2 h flight. A long-endurance airframe reaches the high-cycle regime within a few flights: design arms and mounts **for life**.

## 5. Fractography (reading a failed part)

- Each cycle advances the crack microscopically and leaves **striations**; at the macro scale they appear as **beach marks** around an origin, plus a fast-fracture (catastrophic) zone.
- Beach marks present: probably fatigue. Absent: a catastrophic failure may still have occurred, depending on the material.

## 6. Improving fatigue life (surface engineering)

Coatings, shot peening, and rounding sharp angles (fillets) where cracks start.

## Report rules

- State $\sigma_a$, $\sigma_m$ and $R$ for every fatigue claim, and where they come from. Nothing is measured in this project: the unbalance amplitude comes from the premised ISO 21940-11 balance grade (`unbalance_force`, premises in `data/granta_filters.json` -> `load_cases`), and the fatigue strength from a premised fatigue-to-tensile ratio until the Granta value replaces it. Label every such number as a premise, never as a result; never invent a measurement.
- Do not use ceramics for cyclic or tensile loads.
- Pair with `safety-factor-selection` and `rotating-parts-merit-indices`.
