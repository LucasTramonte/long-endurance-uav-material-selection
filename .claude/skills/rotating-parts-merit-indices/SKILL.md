---
name: rotating-parts-merit-indices
description: Material selection for spinning parts (flywheel disc, rotor blade, hub, motor bell) limited by centrifugal stress. Use when a part rotates, when writing the blade or rotor strength check, or when choosing between energy per mass and energy per volume.
---

# Rotating parts: centrifugal stress and merit indices

Source: course flywheel case study ("merit indices and Ashby maps for design limited by plastic deformation"), implemented in `src/math_modeling/rotating_parts.py` and derived symbolically in `tests/test_rotating_fatigue.py`. Report text: README Sections 1.4.3 and 2.7.

## Problem statement (write it this way)

- **Objective:** store kinetic energy $U$ (flywheel), or minimise mass (rotor).
- **Constraint:** $\sigma<\sigma_y/s$ at the given $\omega$, $R$, $t$.
- **Free variable:** the material.

## Equations (solid disc, elastic, constant thickness, $\nu\simeq1/3$ assumed constant)

$$U=\tfrac12 I_z\omega^2,\quad I_z=\tfrac12 mR^2\;\Rightarrow\;U=\tfrac14 mR^2\omega^2=\tfrac14\rho\pi R^4 t\,\omega^2$$

$$\sigma_{max}=\frac{3+\nu}{8}\rho\omega^2R^2\;\Rightarrow\;\omega^2=\frac{8\sigma}{(3+\nu)\rho R^2}$$

## Three objectives, three indices

| Objective | Result | Index to maximise | Chart line |
| --- | --- | --- | --- |
| $U$ at fixed $R,t$ | $U=\dfrac{2}{3+\nu}\pi R^2t\,\sigma$ | $\sigma_f$ | horizontal line on the $\sigma$-$\rho$ chart |
| $U/m$ (light flywheel) | $U/m=\dfrac{2}{3+\nu}\dfrac{\sigma}{\rho}$ | $\sigma_f/\rho$ | slope 1 |
| $U/V$ at fixed $\omega$ | $U/V=\dfrac{\rho R^2\omega^2}{4}$ | $\rho$ | vertical line (densest wins) |

Course reading of the printed chart: for $\sigma_f/\rho$ the order is CFRP, Ti alloys, Mg alloys, GFRP, wood parallel to the grain (Si3N4 is excluded because it is a ceramic); for $U/V$ it is tungsten alloys, lead alloys, Ni alloys, Cu alloys, steels. Never mix the two goals: a lightweight UAV wants the first, not the second.

## Rules

1. **Ceramics are excluded.** Part of the centrifugal force becomes tension, and ceramics have low, scattered tensile strength. The printed strength of a ceramic on the chart is a modulus of rupture. Tungsten carbide (a ceramic) cannot be taken from the "metals" bubble either.
2. For a **blade** (uniform, root at the axis): $\sigma_{root}=\rho\omega^2R_b^2/2$ (`blade_root_stress`). The requirement $\sigma_y\ge s\,\sigma_{root}$ is a **line of slope 1** on the $\log\sigma$-$\log\rho$ chart, so it can be drawn as the constraint line (step 1 of `ashby-chart-selection`).
3. The safety factor $s$ comes from `safety-factor-selection`.
4. State the assumptions with the number: $R_b=2r_G=24$ mm and 40 000 rpm are assumptions of this repository (README 1.4.3); at those values static centrifugal stress uses only 2-15 % of $\sigma_y$ for the shortlist, so **fatigue** (`fatigue-assessment`) is the real risk.
5. A blade is not a disc: use the disc formulas only as a bound for hubs and motor bells.
