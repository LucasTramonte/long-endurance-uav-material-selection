"""The numerical checks behind docs/figures/verification.png are tests, not just pictures."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis import verification_figure as vf
from src.math_modeling.vibration_fatigue import transmissibility

ARM = vf.Arm()


def test_numerical_deflection_matches_the_analytic_solution():
    x, w = vf.deflection_numeric(ARM, 400)
    assert np.max(np.abs(w - vf.deflection_analytic(ARM, x))) / w[-1] < 1e-4


def test_tip_deflection_is_F_L3_over_3EI():
    exact = ARM.F * ARM.L**3 / (3 * ARM.E * ARM.I)
    assert vf.deflection_analytic(ARM, np.array([ARM.L]))[0] == pytest.approx(exact)


def test_trapezoid_error_is_second_order():
    e1, e2 = vf.tip_error(ARM, 16), vf.tip_error(ARM, 32)
    assert e1 / e2 == pytest.approx(4.0, rel=0.05)


@pytest.mark.parametrize("r", [0.5, 1.0, 2.0, 3.4])
def test_time_domain_amplitude_matches_transmissibility(r):
    sim = vf.simulated_transmissibility(r, 0.10)
    assert sim == pytest.approx(transmissibility(r * 200.0, 200.0, 0.10), rel=0.02)


def test_central_difference_energy_error_scales_with_dt_squared():
    worst = [np.abs(vf.leapfrog_energy_error(1 / n, periods=4)[1]).max() for n in (20, 40)]
    assert worst[0] / worst[1] == pytest.approx(4.0, rel=0.1)
