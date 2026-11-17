"""Rotating-part stresses, flywheel merit index, fatigue-cycle parameters and relative cost."""

import math

import pytest
import sympy as sp

from src.math_modeling import rotating_parts as rp
from src.math_modeling.merit_indices import beam_cost_index, relative_volumetric_cost
from src.math_modeling.vibration_fatigue import cycles_in_flight, hours_for_cycles, stress_cycle


def test_flywheel_energy_per_mass_symbolic():
    """U/m = 2/(3+nu) sigma/rho follows from U = rho pi R^4 t w^2/4 and sigma = (3+nu)/8 rho w^2 R^2."""
    rho, R, t, w, nu, sigma = sp.symbols("rho R t omega nu sigma", positive=True)
    U = rho * sp.pi * R**4 * t * w**2 / 4
    m = rho * sp.pi * R**2 * t
    w_sq = sp.solve(sp.Eq(sigma, (3 + nu) / 8 * rho * w**2 * R**2), w**2)[0]
    u_per_m = sp.simplify((U / m).subs(w**2, w_sq))
    assert sp.simplify(u_per_m - 2 / (3 + nu) * sigma / rho) == 0


def test_energy_two_forms_agree():
    rho, R, t, w = 7800.0, 0.1, 0.02, 300.0
    m = rho * math.pi * R**2 * t
    assert rp.disc_energy(rho, w, R, t) == pytest.approx(0.25 * m * R**2 * w**2)


def test_disc_speed_and_stress_are_inverse():
    rho, R, sigma = 1550.0, 0.05, 300e6
    w = rp.disc_max_speed(sigma, rho, R)
    assert rp.disc_max_stress(rho, w, R) == pytest.approx(sigma)


def test_blade_root_stress_matches_force_model_of_the_readme():
    """sigma_root * A = F_c = m_p omega^2 r_G with r_G = R_b/2 (README 1.4.3)."""
    rho, A, Rb, w = 1550.0, 1e-6, 0.024, rp.rpm_to_rad_s(40_000)
    f_c = rho * A * Rb * w**2 * (Rb / 2)
    assert rp.blade_root_stress(rho, w, Rb) * A == pytest.approx(f_c)


def test_blade_requirement_is_a_slope_one_line_in_log_log():
    w, Rb, s = rp.rpm_to_rad_s(40_000), 0.024, 1.5
    lo, hi = 1000.0, 10000.0
    slope = (math.log10(rp.required_strength_for_blade(hi, w, Rb, s))
             - math.log10(rp.required_strength_for_blade(lo, w, Rb, s))) / (math.log10(hi) - math.log10(lo))
    assert slope == pytest.approx(1.0)


def test_stress_cycle_course_example():
    c = stress_cycle(20, -10)
    assert (c["range"], c["amplitude"], c["mean"], c["R"]) == (30, 15, 5, -0.5)
    assert stress_cycle(100, -100)["R"] == -1 and stress_cycle(100, -100)["mean"] == 0


def test_fatigue_hours_at_40000_rpm():
    f = 40_000 / 60
    assert hours_for_cycles(1e7, f) == pytest.approx(4.1667, rel=1e-3)
    assert cycles_in_flight(f, hours_for_cycles(1e9, f)) == pytest.approx(1e9)


def test_relative_cost_is_currency_independent():
    a = relative_volumetric_cost(60, 1550, 0.8, 7850)
    b = relative_volumetric_cost(60 * 5.0, 1550, 0.8 * 5.0, 7850)       # same prices in another currency
    assert a == pytest.approx(b)


def test_beam_cost_index_ordering():
    assert beam_cost_index(70, 12_000) > beam_cost_index(2.3, 4_200)
