"""Hard constraints derived from the load model of the drone (README Sections 1.4 and 3.3).

Every number comes from the premises block ``load_cases`` of ``data/granta_filters.json``; nothing is measured.

Checks applied to each candidate material (a failed check removes the material). Granta gives a range per property;
the lowest strength and stiffness and the highest density are used, because a constraint that cuts a bubble discards it:

1. tension   - ceramics and glasses are not used where the load path is tensile;
2. stiffness - arm tip deflection:  E >= 4 F L^3 / (b h^3 w_max);
3. strength of the arm:             sigma_y >= s * 6 F L / (b h^2);
4. strength of the blade root:      sigma_y >= s * rho * omega^2 * R_b^2 / 2   (a slope-1 line on the sigma-rho chart).

The arm geometry is fixed by the CAD premise, so check 2 is a screen at that geometry: a thicker arm would let a
softer material pass at the price of mass (that trade is what the merit indices rank).
"""

from __future__ import annotations

from src.math_modeling.ashby_selection import excluded_in_tension
from src.math_modeling.rotating_parts import blade_root_stress, rpm_to_rad_s


def derived_limits(case: dict) -> dict:
    """Quantities that do not depend on the material: omega, E_min and the static arm stress."""
    arm, rotor = case["arm"], case["rotor"]
    F, L, b, h = arm["tip_load_N"], arm["length_m"], arm["width_m"], arm["thickness_m"]
    return {
        "omega_rad_s": rpm_to_rad_s(rotor["rpm"]),
        "E_min_GPa": 4.0 * F * L**3 / (b * h**3 * arm["allowable_tip_deflection_m"]) / 1e9,
        "sigma_mean_MPa": 6.0 * L * F / (b * h**2) / 1e6,
    }


def check_material(m: dict, case: dict) -> list[str]:
    """Reasons why ``m`` fails the load-case constraints (empty list = passes)."""
    lim, s = derived_limits(case), case["safety_factor"]
    fails = []
    if excluded_in_tension(m):
        fails.append("ceramic/glass: not used in tension")
    # a bubble cut by the constraint is discarded, so the lowest stiffness and strength are checked
    e_lo = m.get("youngs_modulus_GPa_min", m["youngs_modulus_GPa"])
    y_lo = m.get("yield_strength_MPa_min", m["yield_strength_MPa"])
    rho_hi = m.get("density_kg_m3_max", m["density_kg_m3"])
    if e_lo < lim["E_min_GPa"]:
        fails.append(f"arm stiffness: E down to {e_lo:g} GPa < {lim['E_min_GPa']:.2f} GPa")
    if y_lo < s * lim["sigma_mean_MPa"]:
        fails.append("arm strength: sigma_y below s*sigma_arm")
    sigma_blade = blade_root_stress(rho_hi, lim["omega_rad_s"], case["rotor"]["blade_length_m"]) / 1e6
    if y_lo < s * sigma_blade:
        fails.append(f"blade root: sigma_y below s*{sigma_blade:.1f} MPa")
    return fails


def screen_load_cases(materials: list[dict], case: dict) -> tuple[list[dict], dict[str, list[str]]]:
    survivors, rejected = [], {}
    for m in materials:
        fails = check_material(m, case)
        if fails:
            rejected[m["id"]] = fails
        else:
            survivors.append(m)
    return survivors, rejected
