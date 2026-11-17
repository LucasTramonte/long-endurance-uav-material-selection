"""Ashby-chart selection rules as code: constraints, safety factor, guide lines, screening and ranking.

The five steps of the chart procedure (see ``.claude/skills/ashby-chart-selection``) are implemented here so
that the drawn charts and the numbers cannot disagree:

1. mark the constraint            -> :class:`Constraint`, :func:`arm_requirements`
2. discard materials it cuts      -> :func:`screen_by_constraint`
3. choose the guide line          -> :data:`GUIDE_SLOPES` (log-log slope of each merit index)
4. slide the line along its slope -> :func:`guide_line_log` (the line through a material, in log10 space)
5. keep a material only if the line passes through it -> :func:`on_guide_line`

Chart coordinates are log10 of the property values, so a merit index ``y^a / x = C`` is the straight line
``log y = (1/a) (log x + log C)`` of slope ``1/a`` (3 for ``E^(1/3)/rho``, 1 for ``sigma/rho``).

Brittle materials: ceramics have a useful compressive but a very low and scattered tensile strength, so they
are removed from every tension-loaded selection (:func:`excluded_in_tension`).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Slope of the guide line of each merit index on a log-log chart (y against rho).
GUIDE_SLOPES = {"E^(1/3)/rho": 3.0, "E^(1/2)/rho": 2.0, "E/rho": 1.0, "sigma/rho": 1.0, "sigma^(2/3)/rho": 1.5}

TENSION_EXCLUDED_FAMILIES = ("Ceramic", "Glass")


@dataclass(frozen=True)
class SafetyFactor:
    """A safety factor with its provenance. ``verified`` is True only when the primary text was read."""

    value: float
    applies_to: str
    source: str
    verified: bool


# The numbers are NOT chosen by the team: they come from the literature below. None of these is a UAV rule.
SAFETY_FACTORS = (
    SafetyFactor(1.5, "limit load -> ultimate load, manned transport aircraft structure",
                 "14 CFR 25.303 (US Federal Aviation Regulations); read through secondary copies, "
                 "confirm on eCFR / Cornell LII", False),
    SafetyFactor(2.5, "lower end of 2.5-4 for static ductile parts with uncertain loads (course slides)",
                 "ABE 4171 lecture slides, Univ. of Florida; secondary source, not the textbook table", False),
    SafetyFactor(3.0, "lower end of 3-4 for brittle parts under static load with reliable data",
                 "Machine Design, 'What's the difference between failure theories?'; secondary", False),
)
DEFAULT_SAFETY_FACTOR = 1.5


@dataclass(frozen=True)
class Constraint:
    """A lower limit on one property, drawn as a straight line on the chart (step 1)."""

    prop: str                 # key of data/materials_db.json, e.g. "youngs_modulus_GPa"
    minimum: float
    label: str


def excluded_in_tension(material: dict) -> bool:
    """Ceramics and glasses are not used where the load path is tensile (brittle, scattered tensile strength)."""
    return material.get("family") in TENSION_EXCLUDED_FAMILIES


def arm_requirements(F: float, L: float, b: float, h: float, w_max: float, s: float = DEFAULT_SAFETY_FACTOR):
    """Constraints on the motor arm of README 1.4.4 (cantilever, tip load F in N, lengths in m).

    Stiffness: w(L) = 4 F L^3 / (E b h^3) <= w_max   ->  E >= 4 F L^3 / (b h^3 w_max)      [GPa]
    Strength : sigma_max = 6 F L / (b h^2), required sigma_y >= s * sigma_max             [MPa]
    """
    e_min = 4 * F * L**3 / (b * h**3 * w_max) / 1e9
    sigma_req = s * 6 * F * L / (b * h**2) / 1e6
    return (Constraint("youngs_modulus_GPa", e_min, f"E >= {e_min:.2f} GPa (tip deflection <= {w_max * 1e3:.2g} mm)"),
            Constraint("yield_strength_MPa", sigma_req, f"sigma >= {sigma_req:.1f} MPa (s = {s:g})"))


def screen_by_constraint(materials: list[dict], constraint: Constraint, tension: bool = True):
    """Step 2. Returns (kept, discarded) where discarded entries carry the reason."""
    kept, discarded = [], []
    for m in materials:
        if tension and excluded_in_tension(m):
            discarded.append((m, "brittle: no tensile use"))
        elif m[constraint.prop] < constraint.minimum:
            discarded.append((m, f"below {constraint.label}"))
        else:
            kept.append(m)
    return kept, discarded


def guide_line_log(slope: float, through_log: tuple[float, float], x_log: np.ndarray) -> np.ndarray:
    """Step 4: log10 y of the guide line of given slope through the point (log10 x, log10 y)."""
    return through_log[1] + slope * (np.asarray(x_log) - through_log[0])


def log_point(material: dict, x_prop: str, y_prop: str) -> tuple[float, float]:
    return float(np.log10(material[x_prop])), float(np.log10(material[y_prop]))


def on_guide_line(material: dict, anchor: dict, x_prop: str, y_prop: str, slope: float, tol_decades: float = 0.05):
    """Step 5: True when ``material`` lies on the guide line through ``anchor`` (within ``tol_decades``)."""
    (xa, ya), (xm, ym) = log_point(anchor, x_prop, y_prop), log_point(material, x_prop, y_prop)
    return abs(ym - (ya + slope * (xm - xa))) <= tol_decades


def offset_decades(material: dict, anchor: dict, x_prop: str, y_prop: str, slope: float) -> float:
    """Vertical distance (decades of y) from the guide line through ``anchor``; > 0 means better than anchor."""
    (xa, ya), (xm, ym) = log_point(anchor, x_prop, y_prop), log_point(material, x_prop, y_prop)
    return ym - (ya + slope * (xm - xa))
