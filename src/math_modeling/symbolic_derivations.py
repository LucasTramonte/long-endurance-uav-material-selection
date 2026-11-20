"""Symbolic (SymPy) derivation of the merit indices as constrained minimisation problems.

Every Ashby index in README Section 2 comes from the same template

    minimise    f(x; m)        objective (mass or cost)            x = free design variables
    over        x in X
    subject to  g(x; m) >= 0   constraint (stiffness / strength)   m = material properties

Eliminating the free variable with the active constraint gives the *performance equation*
``f* = (functional requirement) * (geometry) * (material group)``; the material group is the
**performance index to minimise**, P = 1/IM. SymPy does the elimination here, so the formulas printed
in the README are checked, not copied, and ``tests/test_symbolic.py`` compares them with the numeric
implementation in ``merit_indices.py``.

Library: SymPy (https://www.sympy.org) - symbolic algebra and LaTeX printing.

Usage (repository root):  python -m src.math_modeling.symbolic_derivations
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

E, rho, sigma_y, Cm = sp.symbols("E rho sigma_y C_m", positive=True)           # material properties
L, w, S, F, C1, R = sp.symbols("L w S F C_1 R", positive=True)                # fixed by the design
t, A, a = sp.symbols("t A a", positive=True)                                   # free variables


@dataclass(frozen=True)
class Problem:
    """One minimisation problem and its symbolic solution."""

    key: str
    title: str
    free_variable: sp.Symbol
    objective: sp.Expr            # f(x; m), before elimination
    constraint: sp.Equality       # active constraint g = 0, written as lhs == rhs
    solution: sp.Expr             # free variable eliminated
    optimum: sp.Expr              # f* = geometry * P
    performance_index: sp.Expr    # P = material group (to minimise), IM = 1/P
    objective_name: str = "m"     # symbol of the objective in the printed formulas (m or C)

    def latex(self) -> str:
        x = sp.latex(self.free_variable)
        return "\n".join([
            rf"\min_{{{x}>0}}\; {sp.latex(sp.Eq(sp.Symbol(self.objective_name), self.objective))}",
            rf"\text{{s.t. }} {sp.latex(self.constraint)}",
            rf"\Rightarrow\; {x}={sp.latex(self.solution)}",
            rf"\Rightarrow\; {self.objective_name}^{{*}}={sp.latex(self.optimum)}",
            rf"P=\min_{{k}}\,{sp.latex(self.performance_index)}\;\Longleftrightarrow\; "
            rf"\max_k\,IM={sp.latex(sp.simplify(1 / self.performance_index))}",
        ])


def _material_group(expr: sp.Expr, material_symbols: tuple[sp.Symbol, ...]) -> sp.Expr:
    """The factor of ``expr`` that depends on the material symbols (design factors removed)."""
    _, dep = sp.powsimp(sp.expand_power_base(expr, force=True), force=True).as_independent(*material_symbols)
    return sp.simplify(dep)


def tube_stiffness() -> Problem:
    """IM1: light thin-walled tube of FIXED radius R and prescribed flexural stiffness S, free wall thickness t."""
    stiffness = 48 * E * sp.pi * R**3 * t / L**3                       # S = 48 E I / L^3, I = pi R^3 t
    mass = 2 * sp.pi * R * t * L * rho
    t_sol = sp.solve(sp.Eq(stiffness, S), t)[0]
    m_opt = sp.simplify(mass.subs(t, t_sol))
    return Problem("IM1", "Stiffness-limited thin-walled tube", t, mass, sp.Eq(S, stiffness), t_sol, m_opt,
                   _material_group(m_opt, (E, rho)))


def panel_stiffness() -> Problem:
    """Benchmark panel index E^(1/3)/rho (flat panel, free thickness); not used in the ranking."""
    stiffness = C1 * E * w * t**3 / (12 * L**3)
    mass = rho * L * w * t
    t_sol = sp.solve(sp.Eq(stiffness, S), t)[0]
    m_opt = sp.simplify(mass.subs(t, t_sol))
    return Problem("IM_panel", "Stiffness-limited flat panel (benchmark)", t, mass, sp.Eq(S, stiffness), t_sol, m_opt,
                   _material_group(m_opt, (E, rho)))


def beam_stiffness() -> Problem:
    """Benchmark beam index E^(1/2)/rho (square section, free side a); not used in the ranking."""
    stiffness = C1 * E * a**4 / (12 * L**3)
    mass = rho * a**2 * L
    a_sol = sp.solve(sp.Eq(stiffness, S), a)[0]
    m_opt = sp.simplify(mass.subs(a, a_sol))
    return Problem("IM_beam", "Stiffness-limited square beam", a, mass, sp.Eq(S, stiffness), a_sol, m_opt,
                   _material_group(m_opt, (E, rho)))


def tie_strength() -> Problem:
    """IM2: light tie carrying a prescribed tensile force F, free area A."""
    mass = rho * A * L
    a_sol = sp.solve(sp.Eq(sigma_y * A, F), A)[0]
    m_opt = sp.simplify(mass.subs(A, a_sol))
    return Problem("IM2", "Strength-limited tie", A, mass, sp.Eq(F, sigma_y * A), a_sol, m_opt,
                   _material_group(m_opt, (sigma_y, rho)))


def tube_cost() -> Problem:
    """IM3: cheapest stiffness-limited tube (cost = C_m * mass), C_{v,R} = C_m * rho."""
    stiffness = 48 * E * sp.pi * R**3 * t / L**3
    cost = Cm * rho * 2 * sp.pi * R * t * L
    t_sol = sp.solve(sp.Eq(stiffness, S), t)[0]
    c_opt = sp.simplify(cost.subs(t, t_sol))
    return Problem("IM3", "Cost-limited thin-walled tube", t, cost, sp.Eq(S, stiffness), t_sol, c_opt,
                   _material_group(c_opt, (E, rho, Cm)), "C")


def all_problems() -> dict[str, Problem]:
    return {p.key: p for p in (tube_stiffness(), panel_stiffness(), beam_stiffness(), tie_strength(), tube_cost())}


if __name__ == "__main__":
    for problem in all_problems().values():
        print(f"--- {problem.key}: {problem.title}")
        print(problem.latex(), end="\n\n")
