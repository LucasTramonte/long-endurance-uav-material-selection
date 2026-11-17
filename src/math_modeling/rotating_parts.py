"""Centrifugal stress and stored energy of rotating parts (flywheel disc, uniform blade).

Used for the rotor of the ducted fan (README Sections 1.4.3 and 3.3) and for the "spin-limited" merit indices.

Uniform solid disc of density rho, radius R, spinning at omega (Poisson ratio nu, elastic, constant thickness t):

    sigma_max = (3 + nu)/8 * rho * omega^2 * R^2                 (at the centre)
    U         = 1/2 I omega^2 = 1/4 m R^2 omega^2 = rho pi R^4 t omega^2 / 4
    U/m at sigma_max = sigma_y/s   ->   U/m = 2/(3 + nu) * (sigma_y/s) / rho

so the best material for a light flywheel maximises sigma_y/rho, and for energy per volume at fixed speed maximises rho.
Ceramics are not used: the centrifugal load is tensile and their tensile strength is low and scattered.

Uniform blade of length R_b (root at the axis): N(0) = rho A omega^2 R_b^2 / 2, so sigma_root = rho omega^2 R_b^2 / 2
(the same model as README 1.4.3, F_c = m_p omega^2 r_G with r_G = R_b/2).
"""

from __future__ import annotations

import math

POISSON_DEFAULT = 1.0 / 3.0


def rpm_to_rad_s(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def disc_max_stress(rho: float, omega: float, R: float, nu: float = POISSON_DEFAULT) -> float:
    """Peak stress [Pa] of a spinning solid disc; rho [kg/m^3], omega [rad/s], R [m]."""
    return (3.0 + nu) / 8.0 * rho * omega**2 * R**2


def disc_max_speed(sigma_allow: float, rho: float, R: float, nu: float = POISSON_DEFAULT) -> float:
    """Largest omega [rad/s] for which the disc stress stays below ``sigma_allow`` [Pa]."""
    return math.sqrt(8.0 * sigma_allow / ((3.0 + nu) * rho * R**2))


def disc_energy(rho: float, omega: float, R: float, t: float) -> float:
    """Kinetic energy [J] of the disc: rho pi R^4 t omega^2 / 4."""
    return rho * math.pi * R**4 * t * omega**2 / 4.0


def disc_energy_per_mass_at_limit(sigma_allow: float, rho: float, nu: float = POISSON_DEFAULT) -> float:
    """U/m [J/kg] at the speed that reaches ``sigma_allow`` [Pa]: 2/(3+nu) * sigma_allow / rho."""
    return 2.0 / (3.0 + nu) * sigma_allow / rho


def blade_root_stress(rho: float, omega: float, R_b: float) -> float:
    """Centrifugal tension [Pa] at the root of a uniform blade of length R_b [m]: rho omega^2 R_b^2 / 2."""
    return rho * omega**2 * R_b**2 / 2.0


def required_strength_for_blade(rho: float, omega: float, R_b: float, safety_factor: float) -> float:
    """Minimum sigma_y [Pa] so that sigma_y >= s * sigma_root (a line of slope 1 on a log-log sigma-rho chart)."""
    return safety_factor * blade_root_stress(rho, omega, R_b)


def unbalance_force(rotating_mass_kg: float, grade_G_m_s: float, omega: float) -> float:
    """Amplitude [N] of the rotating force of a rotor balanced to ISO 21940-11 grade G.

    The grade is G = e_per * omega (e_per: permissible specific unbalance = eccentricity of the centre of mass),
    so F = m e omega^2 = m G omega. ``grade_G_m_s`` is in m/s (G 6.3 means 0.0063 m/s).
    """
    return rotating_mass_kg * grade_G_m_s * omega
