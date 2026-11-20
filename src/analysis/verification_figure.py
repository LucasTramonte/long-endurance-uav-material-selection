"""Verification of the physics models: analytic vs numerical solutions, convergence, energy error.

Pattern taken from the course notes on numerical orbits and from the two-mass exercise (see README,
"Figure conventions"): (1) analytic and numerical curves on the same axes; (2) the numerical error shown against
the step size, with its order of accuracy; (3) energy error for several time steps; (4) parameters written
inside the plot.

Panels
  (a) cantilever motor arm, Euler-Bernoulli: analytic deflection w(x) vs numerical double integration of
      E I w'' = M(x)
  (b) tip-deflection error vs number of elements (expected order 2)
  (c) SDOF isolator: analytic transmissibility T(r) vs steady-state amplitude of a time-domain simulation
  (d) undamped SDOF, central-difference (leapfrog) scheme: relative energy error for three time steps

All inputs are project *assumptions* (stated in the figure); they check the models, not the design.

Usage (repository root):  python -m src.analysis.verification_figure
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_ivp

from src.analysis.export_tables import ROOT
from src.math_modeling.vibration_fatigue import transmissibility

# colour-blind-safe palette (Okabe-Ito)
BLUE, ORANGE, GREEN, GREY, VERMILION = "#0072B2", "#E69F00", "#009E73", "#555555", "#D55E00"


@dataclass(frozen=True)
class Arm:
    """Cantilever motor arm (assumed values)."""

    L: float = 0.030        # m, body to motor axis (CAD: motor at 30 mm)
    b: float = 0.005        # m, width
    h: float = 0.0015       # m, thickness
    E: float = 48e9         # Pa, quasi-isotropic CFRP (database value)
    F: float = 0.30         # N, net tip load T - m_m g (assumed)

    @property
    def I(self) -> float:   # noqa: E743 - area moment of inertia
        return self.b * self.h**3 / 12.0


def deflection_analytic(arm: Arm, x: np.ndarray) -> np.ndarray:
    """w(x) = F x^2 (3L - x) / (6 E I), built in at x = 0, tip load F."""
    return arm.F * x**2 * (3 * arm.L - x) / (6 * arm.E * arm.I)


def deflection_numeric(arm: Arm, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Integrate E I w'' = M(x) = F (L - x) twice (trapezoid rule) with w(0) = w'(0) = 0."""
    x = np.linspace(0.0, arm.L, n + 1)
    curvature = arm.F * (arm.L - x) / (arm.E * arm.I)
    slope = cumulative_trapezoid(curvature, x, initial=0.0)
    return x, cumulative_trapezoid(slope, x, initial=0.0)


def tip_error(arm: Arm, n: int) -> float:
    """Relative error of the numerical tip deflection."""
    x, w = deflection_numeric(arm, n)
    exact = float(deflection_analytic(arm, np.array([arm.L]))[0])
    return abs(w[-1] - exact) / exact


def simulated_transmissibility(r: float, zeta: float, fn: float = 200.0) -> float:
    """Steady-state |x|/|y| of m x'' + c (x' - y') + k (x - y) = 0 with base motion y = sin(w t)."""
    wn = 2 * np.pi * fn
    w = r * wn

    def rhs(t, s):
        z, zd = s                                   # relative coordinate z = x - y
        return [zd, w**2 * np.sin(w * t) - 2 * zeta * wn * zd - wn**2 * z]

    t_end = 14.0 / (zeta * wn) + 12 * 2 * np.pi / w
    t = np.linspace(t_end - 8 * 2 * np.pi / w, t_end, 4000)
    sol = solve_ivp(rhs, (0.0, t_end), [0.0, 0.0], t_eval=t, rtol=1e-9, atol=1e-12, method="DOP853")
    x_abs = sol.y[0] + np.sin(w * sol.t)
    return float(np.max(np.abs(x_abs)))


def leapfrog_energy_error(dt_over_period: float, periods: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """Relative energy error E(t)/E0 - 1 of x'' = -x (unit mass, w = 1) with the central-difference scheme.

    x(t + dt) = x(t - dt) + 2 v(t) dt style update in velocity-Verlet form; x(0) = 1, v(0) = 0.
    """
    T = 2 * np.pi
    dt = dt_over_period * T
    n = int(periods / dt_over_period)
    x, v = 1.0, 0.0
    e0 = 0.5
    t = np.arange(n + 1) * dt / T
    err = np.empty(n + 1)
    err[0] = 0.0
    for i in range(1, n + 1):
        v_half = v - 0.5 * dt * x
        x = x + dt * v_half
        v = v_half - 0.5 * dt * x
        err[i] = (0.5 * v**2 + 0.5 * x**2) / e0 - 1.0
    return t, err


TEXT = {
    "en": {"analytic": "analytic", "numerical": "numerical, 12 elements", "x": "x (mm)", "w": "deflection w (mm)",
           "a": "(a) Motor arm, Euler-Bernoulli cantilever", "assumed": "(assumed)", "slope": "slope $-2$",
           "n": "number of elements n", "err": "relative error of $w(L)$", "b": "(b) Convergence of the numerical solution",
           "trap": "trapezoid rule, error $\\propto h^{2}$", "sim": "time-domain simulation", "iso": r"$r=\sqrt{2}$: isolation starts",
           "motor": "motor, 666.7 Hz", "fr": "frequency ratio $r=f/f_n$", "T": "transmissibility $T$",
           "c": "(c) SDOF isolator: analytic vs simulation", "t": "t / T (periods)", "en_err": "relative energy error (%)",
           "d": "(d) Energy error of the central-difference scheme", "undamped": r"undamped SDOF, $x''=-\omega^{2}x$; error bounded, $\propto\Delta t^{2}$",
           "max": "max error", "bxh": "b x h", "dec": "."},
    "pt": {"analytic": "analítico", "numerical": "numérico, 12 elementos", "x": "x (mm)", "w": "flecha w (mm)",
           "a": "(a) Braço do motor, viga engastada de Euler-Bernoulli", "assumed": "(assumidos)", "slope": "inclinação $-2$",
           "n": "número de elementos n", "err": "erro relativo de $w(L)$", "b": "(b) Convergência da solução numérica",
           "trap": "regra do trapézio, erro $\\propto h^{2}$", "sim": "simulação no tempo", "iso": r"$r=\sqrt{2}$: início do isolamento",
           "motor": "motor, 666,7 Hz", "fr": "razão de frequências $r=f/f_n$", "T": "transmissibilidade $T$",
           "c": "(c) Isolador de 1 grau de liberdade: analítico e simulação", "t": "t / T (períodos)", "en_err": "erro relativo de energia (%)",
           "d": "(d) Erro de energia do esquema de diferenças centrais", "undamped": r"sistema sem amortecimento, $x''=-\omega^{2}x$; erro limitado, $\propto\Delta t^{2}$",
           "max": "erro máx.", "bxh": "b × h", "dec": ","},
}


def build_figure(lang: str = "en"):
    arm = Arm()
    tx = TEXT[lang]
    fig, axs = plt.subplots(2, 2, figsize=(12.5, 8.8))
    fig.subplots_adjust(hspace=0.34, wspace=0.26, left=0.07, right=0.98, top=0.93, bottom=0.07)

    # (a) analytic vs numerical deflection --------------------------------------------------------------
    ax = axs[0, 0]
    xs = np.linspace(0, arm.L, 200)
    xn, wn_ = deflection_numeric(arm, 12)
    ax.plot(xs * 1e3, deflection_analytic(arm, xs) * 1e3, color=BLUE, lw=2.2, label=tx["analytic"])
    ax.plot(xn * 1e3, wn_ * 1e3, "o", color=ORANGE, ms=5, mfc="none", mew=1.5, label=tx["numerical"])
    ax.set_xlabel(tx["x"])
    ax.set_ylabel(tx["w"])
    ax.set_title(tx["a"], loc="left", fontsize=10.5)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    w_tip = float(deflection_analytic(arm, np.array([arm.L]))[0])
    ax.text(0.97, 0.06,
            f"L = {arm.L * 1e3:.0f} mm, {tx['bxh']} = {arm.b * 1e3:.0f} × {arm.h * 1e3:.1f} mm\n".replace(".", tx["dec"]) +
            (f"E = {arm.E / 1e9:.0f} GPa, F = {arm.F:.2f} N {tx['assumed']}\n").replace(".", tx["dec"]) +
            (rf"$w(L)=FL^3/3EI$ = {w_tip * 1e3:.3f} mm").replace(".", tx["dec"]),
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=GREY,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.8"))

    # (b) convergence ----------------------------------------------------------------------------------
    ax = axs[0, 1]
    ns = np.array([2, 4, 8, 16, 32, 64, 128])
    errs = np.array([tip_error(arm, int(n)) for n in ns])
    ax.loglog(ns, errs, "o-", color=BLUE, lw=2)
    ax.loglog(ns, errs[0] * (ns[0] / ns) ** 2, "--", color=GREY, lw=1.3)
    ax.text(ns[-2], errs[0] * (ns[0] / ns[-2]) ** 2 * 2.2, tx["slope"], color=GREY, fontsize=10)
    ax.set_xlabel(tx["n"])
    ax.set_ylabel(tx["err"])
    ax.set_title(tx["b"], loc="left", fontsize=10.5)
    ax.text(0.97, 0.94, tx["trap"], transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color=GREY)
    ax.grid(True, which="both", alpha=0.25)

    # (c) transmissibility -----------------------------------------------------------------------------
    ax = axs[1, 0]
    zeta, fn = 0.10, 200.0
    r = np.linspace(0.2, 4.0, 300)
    ax.plot(r, [transmissibility(ri * fn, fn, zeta) for ri in r], color=BLUE, lw=2.2, label=tx["analytic"])
    rs = np.array([0.4, 0.7, 0.9, 1.0, 1.2, 1.6, 2.0, 2.6, 3.4])
    ax.plot(rs, [simulated_transmissibility(float(ri), zeta, fn) for ri in rs], "o", color=ORANGE, ms=6,
            mfc="none", mew=1.5, label=tx["sim"])
    ax.axhline(1.0, color=GREY, lw=0.8, ls=":")
    ax.axvline(np.sqrt(2), color=VERMILION, lw=1.2, ls="--")
    ax.text(np.sqrt(2) + 0.05, 4.6, tx["iso"], color=VERMILION, fontsize=9, va="top")
    r_design = 666.7 / fn
    t_design = transmissibility(666.7, fn, zeta)
    ax.plot([r_design], [t_design], "s", color=GREEN, ms=8)
    ax.annotate(f"{tx['motor']}\nr = {r_design:.2f}, T = {t_design:.2f}".replace(".", tx["dec"]) if lang == "pt" else f"{tx['motor']}\nr = {r_design:.2f}, T = {t_design:.2f}", (r_design, t_design),
                (3.0, 1.9), fontsize=9, color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.8))
    ax.set_xlabel(tx["fr"])
    ax.set_ylabel(tx["T"])
    ax.set_ylim(0, 5.2)
    ax.set_title(tx["c"], loc="left", fontsize=10.5)
    ax.legend(frameon=False, loc="upper right", fontsize=9, bbox_to_anchor=(1.0, 0.86))
    ax.text(0.98, 0.58, rf"$f_n$ = {fn:.0f} Hz, $\zeta$ = {str(zeta).replace('.', tx['dec'])} {tx['assumed']}", transform=ax.transAxes, ha="right",
            va="top", fontsize=8.5, color=GREY)

    # (d) energy error vs time step ---------------------------------------------------------------------
    ax = axs[1, 1]
    for dtp, col in ((1 / 20, VERMILION), (1 / 50, ORANGE), (1 / 200, BLUE)):
        t, e = leapfrog_energy_error(dtp, periods=4)
        ax.plot(t, e * 100, color=col, lw=1.8, label=rf"$\Delta t=T/{round(1 / dtp)}$, {tx['max']} {str(round(np.abs(e).max() * 100, 3)).replace('.', tx['dec'])} %")
    ax.set_xlabel(tx["t"])
    ax.set_ylabel(tx["en_err"])
    ax.set_ylim(-4.4, 1.0)
    ax.set_title(tx["d"], loc="left", fontsize=10.5)
    ax.text(0.02, 0.96, tx["undamped"],
            transform=ax.transAxes, va="top", fontsize=8.5, color=GREY)
    ax.legend(frameon=False, loc="lower center", fontsize=9)
    ax.grid(True, alpha=0.25)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "figures" / "verification.png")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for lang, out in (("en", args.out), ("pt", args.out.with_name(args.out.stem + "_pt.png"))):
        build_figure(lang).savefig(out, dpi=170, facecolor="white")
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
