"""Centrifugal stress of the rotor blade (README Section 1.4.3).

Uniform blade of density rho and length R_b with its root at the axis, spinning at omega:
N(0) = rho A omega^2 R_b^2 / 2, so sigma_root = rho omega^2 R_b^2 / 2 (the same model as F_c = m_p omega^2 r_G
with r_G = R_b/2). Because the centrifugal load is tensile, ceramics are not used for the blades.
"""

from __future__ import annotations

import math


def rpm_to_rad_s(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def blade_root_stress(rho: float, omega: float, R_b: float) -> float:
    """Centrifugal tension [Pa] at the root of a uniform blade of length R_b [m]: rho omega^2 R_b^2 / 2."""
    return rho * omega**2 * R_b**2 / 2.0


def required_strength_for_blade(rho: float, omega: float, R_b: float, safety_factor: float) -> float:
    """Minimum sigma_y [Pa] so that sigma_y >= s * sigma_root (a line of slope 1 on a log-log sigma-rho chart)."""
    return safety_factor * blade_root_stress(rho, omega, R_b)
