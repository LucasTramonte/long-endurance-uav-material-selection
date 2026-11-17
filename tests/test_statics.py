"""Section 1.4 formulas, recomputed with SymPy's vector module and compared with the README."""

from __future__ import annotations

import sympy as sp

from src.math_modeling import statics_torsors as st


def test_torsor_at_G_matches_the_readme():
    (rx, ry, rz), (mx, my, mz) = st.rotor_torsor_at_G()
    t1, t2, t3, t4 = st.T
    c = st.kQ / st.kT
    assert (rx, ry) == (0, 0)
    assert sp.simplify(rz - (sum(st.T) - st.m * st.g)) == 0
    assert sp.simplify(mx - st.a * (t1 + t2 - t3 - t4)) == 0           # sum y_i T_i
    assert sp.simplify(my - st.a * (-t1 + t2 + t3 - t4)) == 0          # -sum x_i T_i
    assert sp.simplify(mz + c * (t1 - t2 + t3 - t4)) == 0              # sum Q_i


def test_mixing_matrix_is_the_one_in_the_readme():
    a, c = st.a, st.kQ / st.kT
    expected = sp.Matrix([[1, 1, 1, 1], [a, a, -a, -a], [-a, a, a, -a], [-c, c, -c, c]])
    assert sp.simplify(st.mixing_matrix() - expected) == sp.zeros(4, 4)


def test_hover_equilibrium_gives_a_null_torsor():
    hover = {t: st.m * st.g / 4 for t in st.T}
    (rx, ry, rz), moment = st.rotor_torsor_at_G()
    assert sp.simplify(rz.subs(hover)) == 0
    assert all(sp.simplify(comp.subs(hover)) == 0 for comp in moment)


def test_centrifugal_force_of_a_uniform_blade():
    n0, m_blade, r_g = st.blade_root_force()
    w = sp.Symbol("omega", positive=True)
    assert sp.simplify(n0 - m_blade * w**2 * r_g) == 0


def test_cantilever_cohesion_navier_and_deflection():
    r = st.cantilever_cohesion()
    F, L, x, b, h, E = sp.symbols("F L x b h E", positive=True)
    assert sp.simplify(r["Tz"] - F) == 0
    assert sp.simplify(r["Mfy"] + F * (L - x)) == 0
    assert sp.simplify(r["sigma_max"] - 6 * F * L / (b * h**2)) == 0
    assert sp.simplify(r["w_tip"] - F * L**3 / (3 * E * r["I"])) == 0
