"""Symbolic statics of the airframe (README Section 1.4) with SymPy's vector module.

The torsor formalism of Section 1.4 is computed, not typed: a reference frame ``R = (G; x, y, z)``, position
vectors, cross products and the reduction of the actions at G are done with ``sympy.physics.vector``.
``tests/test_statics.py`` compares the results with the formulas printed in the README.

Contents
  rotor_torsor_at_G()      resultant and moment at G of thrust, reaction torque and weight (1.4.2)
  mixing_matrix()          control wrench vs thrust variations (1.4.2)
  blade_root_force()       centrifugal force at the blade root, uniform blade (1.4.3)
  cantilever_cohesion()    cohesion torsor, Navier stress and tip deflection of the arm (1.4.4)

Library: SymPy (https://www.sympy.org), module ``sympy.physics.vector``.
"""

from __future__ import annotations

import sympy as sp
from sympy.physics.vector import ReferenceFrame

R = ReferenceFrame("R")
a, kT, kQ, m, g = sp.symbols("a k_T k_Q m g", positive=True)
T = sp.symbols("T1:5", positive=True)                       # thrust of rotors 1..4
EPS = (1, -1, 1, -1)                                        # spin signs, rotors at (+,+), (-,+), (-,-), (+,-)
POSITIONS = ((a, a), (-a, a), (-a, -a), (a, -a))


def _components(vec) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    return tuple(sp.simplify(vec.dot(axis)) for axis in (R.x, R.y, R.z))


def rotor_torsor_at_G():
    """Torsor {R; M_G} of all external actions on the airframe, reduced at G: ((Rx,Ry,Rz), (Mx,My,Mz))."""
    c = kQ / kT
    resultant = -m * g * R.z
    moment = 0 * R.z
    for t_i, eps, (x_i, y_i) in zip(T, EPS, POSITIONS, strict=True):
        gm = x_i * R.x + y_i * R.y                          # vector G -> M_i
        thrust = t_i * R.z
        reaction = -eps * c * t_i * R.z                     # Q_i = -eps_i k_Q w_i^2 z, with k_Q w^2 = (k_Q/k_T) T_i
        resultant += thrust
        moment += gm.cross(thrust) + reaction
    return _components(resultant), _components(moment)


def mixing_matrix() -> sp.Matrix:
    """Matrix B with (dFz, tau_x, tau_y, tau_z)^T = B (dT1..dT4)^T (weight removed from Fz)."""
    resultant, moment = rotor_torsor_at_G()
    wrench = sp.Matrix([resultant[2] + m * g, *moment])
    return sp.simplify(wrench.jacobian(T))


def blade_root_force():
    """N(0) = w^2 * integral_0^Rb mu(rho) rho d rho for a uniform blade of linear mass mu0 and length Rb.

    Returns (N0, m_blade, r_G) so that N0 = m_blade * w^2 * r_G with r_G = Rb/2.
    """
    w, mu0, Rb, rho = sp.symbols("omega mu_0 R_b rho", positive=True)
    n0 = sp.integrate(w**2 * mu0 * rho, (rho, 0, Rb))
    return sp.simplify(n0), mu0 * Rb, Rb / 2


def cantilever_cohesion():
    """Cohesion torsor at abscissa x of a cantilever (built in at x = 0) with tip load F along z.

    Action of the downstream part on the upstream part, reduced at the section centroid G_x.
    Returns a dict with the torsor components, the maximum Navier stress and the tip deflection.
    """
    F, L, x, b, h, E = sp.symbols("F L x b h E", positive=True)
    S_, I = b * h, b * h**3 / 12
    f_tip = F * R.z                                         # external load on the downstream part
    g_to_tip = (L - x) * R.x                                # G_x -> point of application
    coh_resultant = f_tip
    coh_moment = g_to_tip.cross(f_tip)                      # = -(L - x) F y
    mfy = sp.simplify(coh_moment.dot(R.y))
    sigma_max = sp.simplify(sp.Abs(mfy.subs(x, 0)) / I * (h / 2))
    w_fun = sp.Function("w")
    # E I w'' = -M_fy(x), w(0) = w'(0) = 0
    ics = {w_fun(0): 0, w_fun(x).diff(x).subs(x, 0): 0}
    sol = sp.dsolve(sp.Eq(E * I * w_fun(x).diff(x, 2), -mfy), w_fun(x), ics=ics)
    tip = sp.simplify(sol.rhs.subs(x, L))
    return {
        "Tz": sp.simplify(coh_resultant.dot(R.z)),
        "Mfy": mfy,
        "sigma_max": sigma_max,
        "w_tip": tip,
        "I": I,
        "S": S_,
    }


if __name__ == "__main__":
    res, mom = rotor_torsor_at_G()
    print("R_G =", res, "\nM_G =", mom, "\nB =", mixing_matrix())
    print(cantilever_cohesion())
