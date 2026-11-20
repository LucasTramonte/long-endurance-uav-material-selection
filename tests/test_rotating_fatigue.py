"""Blade centrifugal stress, stress-cycle parameters, fatigue hours and relative cost."""

import math

import pytest

from src.math_modeling import rotating_parts as rp
from src.math_modeling.merit_indices import relative_volumetric_cost
from src.math_modeling.vibration_fatigue import cycles_in_flight, hours_for_cycles, stress_cycle


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
