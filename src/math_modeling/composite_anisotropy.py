"""Effective laminate stiffness from ply angles and fibre volume fraction (extension module).

Implements a compact Classical Laminate Theory (CLT) in-plane model:
  1. Ply properties from micromechanics (rule of mixtures; inverse rule for E2, G12).
  2. Reduced stiffness Q of an orthotropic ply, rotated to Q-bar for each angle.
  3. Extensional stiffness matrix A = sum(Qbar_k * t_k); effective Ex = 1 / (h * a11),
     where a = A^-1.

Limitations (to be refined by the team): in-plane only (B and D matrices ignored, so
no bending-extension coupling or stacking-sequence effects on flexure); no
Halpin-Tsai correction; no ply failure criteria (Tsai-Wu), no hygrothermal effects.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Constituents:
    """Fibre/matrix properties (defaults: standard-modulus carbon / epoxy)."""

    Ef_GPa: float = 230.0
    Gf_GPa: float = 15.0
    nuf: float = 0.20
    Em_GPa: float = 3.5
    Gm_GPa: float = 1.3
    num: float = 0.35


def ply_engineering_constants(Vf: float, c: Constituents = Constituents()) -> dict[str, float]:
    """Unidirectional ply constants E1, E2, G12 [GPa] and nu12 from Vf."""
    if not 0.0 < Vf < 1.0:
        raise ValueError("Vf must lie in (0, 1)")
    Vm = 1.0 - Vf
    E1 = Vf * c.Ef_GPa + Vm * c.Em_GPa
    E2 = 1.0 / (Vf / c.Ef_GPa + Vm / c.Em_GPa)
    G12 = 1.0 / (Vf / c.Gf_GPa + Vm / c.Gm_GPa)
    nu12 = Vf * c.nuf + Vm * c.num
    return {"E1": E1, "E2": E2, "G12": G12, "nu12": nu12}


def reduced_stiffness(E1: float, E2: float, G12: float, nu12: float) -> np.ndarray:
    """Plane-stress reduced stiffness matrix Q (3x3) in material axes [GPa]."""
    nu21 = nu12 * E2 / E1
    d = 1.0 - nu12 * nu21
    return np.array(
        [
            [E1 / d, nu12 * E2 / d, 0.0],
            [nu12 * E2 / d, E2 / d, 0.0],
            [0.0, 0.0, G12],
        ]
    )


def transformed_stiffness(Q: np.ndarray, theta_deg: float) -> np.ndarray:
    """Rotate Q by ply angle theta (Reuter-corrected tensor-shear convention)."""
    th = np.radians(theta_deg)
    c, s = np.cos(th), np.sin(th)
    T = np.array(
        [
            [c * c, s * s, 2 * c * s],
            [s * s, c * c, -2 * c * s],
            [-c * s, c * s, c * c - s * s],
        ]
    )
    R = np.diag([1.0, 1.0, 2.0])
    # Qbar = T^-1 Q R T R^-1
    return np.linalg.inv(T) @ Q @ R @ T @ np.linalg.inv(R)


def laminate_extensional_stiffness(
    angles_deg: Sequence[float], Vf: float, ply_thickness_mm: float = 0.125,
    c: Constituents = Constituents(),
) -> tuple[np.ndarray, float]:
    """Return (A [GPa*mm], total thickness h [mm]) for a stack of equal-thickness plies."""
    k = ply_engineering_constants(Vf, c)
    Q = reduced_stiffness(k["E1"], k["E2"], k["G12"], k["nu12"])
    A = sum(transformed_stiffness(Q, a) * ply_thickness_mm for a in angles_deg)
    return A, ply_thickness_mm * len(angles_deg)


def effective_modulus(
    angles_deg: Sequence[float], Vf: float = 0.55, ply_thickness_mm: float = 0.125,
    c: Constituents = Constituents(),
) -> dict[str, float]:
    """Effective in-plane laminate moduli Ex, Ey, Gxy [GPa] (E_eff = Ex)."""
    A, h = laminate_extensional_stiffness(angles_deg, Vf, ply_thickness_mm, c)
    a = np.linalg.inv(A)
    return {"Ex": 1.0 / (h * a[0, 0]), "Ey": 1.0 / (h * a[1, 1]), "Gxy": 1.0 / (h * a[2, 2]),
            "nuxy": -a[0, 1] / a[0, 0], "thickness_mm": h}


def quasi_isotropic_layup() -> list[float]:
    """Symmetric quasi-isotropic stack [0/+45/-45/90]s."""
    half = [0.0, 45.0, -45.0, 90.0]
    return half + half[::-1]


if __name__ == "__main__":
    for name, stack in [("UD [0]8", [0.0] * 8), ("Cross-ply [0/90]2s", [0, 90, 0, 90, 90, 0, 90, 0]),
                        ("QI [0/45/-45/90]s", quasi_isotropic_layup())]:
        r = effective_modulus(stack, Vf=0.55)
        print(f"{name:<20} Ex={r['Ex']:.1f} GPa  Ey={r['Ey']:.1f} GPa  Gxy={r['Gxy']:.1f} GPa")
