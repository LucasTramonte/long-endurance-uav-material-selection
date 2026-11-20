"""Ashby performance (merit) indices for the UAV fuselage.

Derivations are given in README.md, Section 2. Summary
------------------------------------------------------
* IM1 = E / rho            - minimum-mass thin-walled tube (fixed radius, free wall thickness),
                             prescribed flexural stiffness (course monitor's formulation)
* IM2 = sigma_y / rho      - minimum-mass tie/skin, prescribed tensile strength
* IM3 = E / C_v,R          - minimum-cost tube, prescribed flexural stiffness,
                             with C_v = C_m * rho (volumetric cost, currency/m^3; BRL in the Granta data)

Assumptions: Hookean (linear-elastic) regime, small-deflection (Euler-Bernoulli /
Kirchhoff) theory, isotropic (or quasi-isotropic) material, fixed length and width
with free thickness. Larger index = better material.

Unit convention (kept explicit to avoid silent errors)
------------------------------------------------------
* E          : GPa
* sigma_y    : MPa
* rho        : kg/m^3  (converted internally to Mg/m^3, the Ashby convention)
* price      : currency/kg (Granta: BRL/kg)  ->  C_v in currency/m^3 (converted to k-currency/m^3 inside IM3)
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

ArrayLike = float | Sequence[float] | np.ndarray


def _as_array(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


def _check_positive(**kwargs: ArrayLike) -> None:
    for name, value in kwargs.items():
        if np.any(_as_array(value) <= 0):
            raise ValueError(f"{name} must be strictly positive")


def bending_panel_index(E_GPa: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """IM1 = E^(1/3)/rho  [GPa^(1/3) / (Mg/m^3)].

    Light, stiff panel: for a panel of fixed length L and width w, the bending
    stiffness is S = C1 * E * w * t^3 / L^3, so t = (S L^3 / (C1 E w))^(1/3) and the
    mass m = rho * L * w * t scales as rho / E^(1/3).
    """
    _check_positive(E_GPa=E_GPa, rho_kg_m3=rho_kg_m3)
    return np.cbrt(_as_array(E_GPa)) / (_as_array(rho_kg_m3) / 1000.0)


def bending_beam_index(E_GPa: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """IM = E^(1/2)/rho  [GPa^(1/2) / (Mg/m^3)] - stiffness-limited beam, free square section.

    For a beam of fixed length L and prescribed bending stiffness S ~ E I / L^3 with a
    solid square section of free side a (I = a^4/12): a ~ E^(-1/4), m = rho a^2 L ~ rho/E^(1/2).
    Used for spars in the benchmark thesis (Niero, 2024; reference [20] in README).
    """
    _check_positive(E_GPa=E_GPa, rho_kg_m3=rho_kg_m3)
    return np.sqrt(_as_array(E_GPa)) / (_as_array(rho_kg_m3) / 1000.0)


def tensile_strength_index(sigma_y_MPa: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """IM2 = sigma_y/rho  [MPa / (Mg/m^3)] (numerically kN*m/kg).

    Light tie/skin carrying a prescribed tensile force F with free area A:
    A = F/sigma_y and m = rho * A * L, so m scales as rho / sigma_y.
    """
    _check_positive(sigma_y_MPa=sigma_y_MPa, rho_kg_m3=rho_kg_m3)
    return _as_array(sigma_y_MPa) / (_as_array(rho_kg_m3) / 1000.0)


def volumetric_cost(price_per_kg: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """Volumetric cost C_v = C_m * rho  [currency/m^3]."""
    _check_positive(price_per_kg=price_per_kg, rho_kg_m3=rho_kg_m3)
    return _as_array(price_per_kg) * _as_array(rho_kg_m3)


def relative_volumetric_cost(price_per_kg: float, rho_kg_m3: float, ref_price_per_kg: float,
                             ref_rho_kg_m3: float) -> float:
    """C_v,R = (C_m rho) / (C_m,ref rho_ref): cost per unit volume relative to a reference material.

    Comparing relative cost removes the currency and the inflation of the price list. Ashby's charts use a
    reference material (course notes: steel; confirm the exact reference before mixing with currency/m^3).
    """
    _check_positive(price=price_per_kg, rho=rho_kg_m3, ref_price=ref_price_per_kg, ref_rho=ref_rho_kg_m3)
    return (price_per_kg * rho_kg_m3) / (ref_price_per_kg * ref_rho_kg_m3)


def cost_index(E_GPa: ArrayLike, Cv_m3: ArrayLike) -> np.ndarray:
    """IM3 = E^(1/3)/C_v,R  [GPa^(1/3) / (kcurrency/m^3)].

    Minimum-cost panel for prescribed bending stiffness: cost = C_m * m =
    C_v,R * L * w * t with t ~ E^(-1/3), so cost scales as C_v,R / E^(1/3).
    """
    _check_positive(E_GPa=E_GPa, Cv_m3=Cv_m3)
    return np.cbrt(_as_array(E_GPa)) / (_as_array(Cv_m3) / 1000.0)


def tube_bending_index(E_GPa: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """IM1 = E/rho  [GPa / (Mg/m^3)] - thin-walled tube of FIXED radius R and free wall thickness t.

    Flexural stiffness S = 48 E I / L^3 with I = pi R^3 t (simply supported, central load), so
    t = S L^3 / (48 pi E R^3) and m = 2 pi R t L rho = S L^4 rho / (24 E R^2): the mass scales as rho/E.
    """
    _check_positive(E_GPa=E_GPa, rho_kg_m3=rho_kg_m3)
    return _as_array(E_GPa) / (_as_array(rho_kg_m3) / 1000.0)


def tube_cost_index(E_GPa: ArrayLike, Cv_m3: ArrayLike) -> np.ndarray:
    """IM3 = E/C_v,R  [GPa / (kcurrency/m^3)] - cheapest tube for a prescribed flexural stiffness (C = C_m m)."""
    _check_positive(E_GPa=E_GPa, Cv_m3=Cv_m3)
    return _as_array(E_GPa) / (_as_array(Cv_m3) / 1000.0)


def tube_thickness_for_rigidity(E_GPa: float, EI_target_Nm2: float, R_m: float) -> float:
    """Wall thickness t [m] of a thin tube of mean radius R with flexural rigidity E*I = E*pi*R^3*t."""
    _check_positive(E_GPa=E_GPa, EI_target_Nm2=EI_target_Nm2, R_m=R_m)
    return float(EI_target_Nm2 / (E_GPa * 1e9 * np.pi * R_m**3))


def tube_mass_for_rigidity(E_GPa: float, rho_kg_m3: float, EI_target_Nm2: float, R_m: float, L_m: float) -> float:
    """Mass [kg] of a thin tube (mean radius R, length L) meeting the rigidity target E*I."""
    t = tube_thickness_for_rigidity(E_GPa, EI_target_Nm2, R_m)
    return rho_kg_m3 * 2.0 * np.pi * R_m * t * L_m


def tube_rigidity(E_GPa: float, t_m: float, R_m: float) -> float:
    """Flexural rigidity E*I = E*pi*R^3*t [N*m^2] of a thin tube."""
    _check_positive(E_GPa=E_GPa, t_m=t_m, R_m=R_m)
    return E_GPa * 1e9 * np.pi * R_m**3 * t_m


def panel_thickness_for_rigidity(E_GPa: float, D_per_width_Nm: float) -> float:
    """Thickness t [m] giving flexural rigidity per unit width D = E t^3 / 12."""
    _check_positive(E_GPa=E_GPa, D_per_width_Nm=D_per_width_Nm)
    return float((12.0 * D_per_width_Nm / (E_GPa * 1e9)) ** (1.0 / 3.0))


def panel_mass_for_rigidity(
    E_GPa: float,
    rho_kg_m3: float,
    D_per_width_Nm: float,
    length_m: float = 0.30,
    width_m: float = 0.15,
) -> float:
    """Mass [kg] of an L x w panel meeting the rigidity target D (per unit width)."""
    t = panel_thickness_for_rigidity(E_GPa, D_per_width_Nm)
    return rho_kg_m3 * length_m * width_m * t


def rigidity_of_panel(E_GPa: float, thickness_m: float) -> float:
    """Flexural rigidity per unit width D = E t^3 / 12 [N*m]."""
    _check_positive(E_GPa=E_GPa, thickness_m=thickness_m)
    return E_GPa * 1e9 * thickness_m**3 / 12.0


def performance_indices(E_GPa: ArrayLike, rho_kg_m3: ArrayLike, sigma_y_MPa: ArrayLike,
                        price_per_kg: ArrayLike) -> dict[str, np.ndarray]:
    """Minimisation form of the merit indices: P_k = 1/IM_k (the quantity to *minimise*).

    ``P1 = rho/E`` (tube mass), ``P2 = rho/sigma_y`` (tie mass), ``P3 = C_v,R/E`` (tube cost).
    Selecting the material with the smallest P is the same as selecting the largest IM; the symbolic
    derivation (``symbolic_derivations.py``) shows each P as the material group of a constrained
    minimisation problem  min m  s.t.  stiffness (or strength) >= requirement.
    """
    cv = volumetric_cost(price_per_kg, rho_kg_m3)
    return {
        "P1": 1.0 / tube_bending_index(E_GPa, rho_kg_m3),
        "P2": 1.0 / tensile_strength_index(sigma_y_MPa, rho_kg_m3),
        "P3": 1.0 / tube_cost_index(E_GPa, cv),
    }


def compute_all_indices(materials: Iterable[dict]) -> list[dict]:
    """Attach IM1 (E/rho), IM2 (sigma_y/rho), IM3 (E/C_v,R) and C_v,R to each material dict (returns copies)."""
    out = []
    for m in materials:
        cv = float(volumetric_cost(m["price_brl_kg"], m["density_kg_m3"]))
        out.append(
            {
                **m,
                "Cv_brl_m3": cv,
                "IM1": float(tube_bending_index(m["youngs_modulus_GPa"], m["density_kg_m3"])),
                "IM2": float(tensile_strength_index(m["yield_strength_MPa"], m["density_kg_m3"])),
                "IM3": float(tube_cost_index(m["youngs_modulus_GPa"], cv)),
            }
        )
    return out


if __name__ == "__main__":
    from src.analysis.export_tables import load_materials

    for row in compute_all_indices(load_materials()):
        print(f"{row['id']:<12} IM1={row['IM1']:.2f}  IM2={row['IM2']:.1f}  IM3={row['IM3']:.2f}")
