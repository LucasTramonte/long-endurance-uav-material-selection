"""Ashby performance (merit) indices for the UAV fuselage.

Derivations are given in README.md, Section 2. Summary
------------------------------------------------------
* IM1 = E^(1/3) / rho      - minimum-mass panel, prescribed bending stiffness
* IM2 = sigma_y / rho      - minimum-mass tie/skin, prescribed tensile strength
* IM3 = E^(1/3) / C_v,R    - minimum-cost panel, prescribed bending stiffness,
                             with C_v,R = C_m * rho (volumetric cost, USD/m^3)

Assumptions: Hookean (linear-elastic) regime, small-deflection (Euler-Bernoulli /
Kirchhoff) theory, isotropic (or quasi-isotropic) material, fixed length and width
with free thickness. Larger index = better material.

Unit convention (kept explicit to avoid silent errors)
------------------------------------------------------
* E          : GPa
* sigma_y    : MPa
* rho        : kg/m^3  (converted internally to Mg/m^3, the Ashby convention)
* price      : USD/kg  ->  C_v,R in USD/m^3 (converted to kUSD/m^3 inside IM3)
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


def volumetric_cost(price_usd_kg: ArrayLike, rho_kg_m3: ArrayLike) -> np.ndarray:
    """Volumetric cost C_v,R = C_m * rho  [USD/m^3]."""
    _check_positive(price_usd_kg=price_usd_kg, rho_kg_m3=rho_kg_m3)
    return _as_array(price_usd_kg) * _as_array(rho_kg_m3)


def relative_volumetric_cost(price_per_kg: float, rho_kg_m3: float, ref_price_per_kg: float,
                             ref_rho_kg_m3: float) -> float:
    """C_v,R = (C_m rho) / (C_m,ref rho_ref): cost per unit volume relative to a reference material.

    Comparing relative cost removes the currency and the inflation of the price list. Ashby's charts use a
    reference material (course notes: steel; confirm the exact reference before mixing with USD/m^3).
    """
    _check_positive(price=price_per_kg, rho=rho_kg_m3, ref_price=ref_price_per_kg, ref_rho=ref_rho_kg_m3)
    return (price_per_kg * rho_kg_m3) / (ref_price_per_kg * ref_rho_kg_m3)


def cost_index(E_GPa: ArrayLike, Cv_usd_m3: ArrayLike) -> np.ndarray:
    """IM3 = E^(1/3)/C_v,R  [GPa^(1/3) / (kUSD/m^3)].

    Minimum-cost panel for prescribed bending stiffness: cost = C_m * m =
    C_v,R * L * w * t with t ~ E^(-1/3), so cost scales as C_v,R / E^(1/3).
    """
    _check_positive(E_GPa=E_GPa, Cv_usd_m3=Cv_usd_m3)
    return np.cbrt(_as_array(E_GPa)) / (_as_array(Cv_usd_m3) / 1000.0)


def beam_cost_index(E_GPa: ArrayLike, Cv_usd_m3: ArrayLike) -> np.ndarray:
    """Minimum-cost beam in bending (square section free): IM = E^(1/2)/(C_m rho) = E^(1/2)/C_v,R.

    Cost C = C_m m with m = (12 S / C_1)^(1/2) L^(5/2) rho / E^(1/2), so the material group to minimise is
    C_m rho / E^(1/2). Units: GPa^(1/2) / (kUSD/m^3).
    """
    _check_positive(E_GPa=E_GPa, Cv_usd_m3=Cv_usd_m3)
    return np.sqrt(_as_array(E_GPa)) / (_as_array(Cv_usd_m3) / 1000.0)


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
                        price_usd_kg: ArrayLike) -> dict[str, np.ndarray]:
    """Minimisation form of the merit indices: P_k = 1/IM_k (the quantity to *minimise*).

    ``P1 = rho/E^(1/3)`` (panel mass), ``P2 = rho/sigma_y`` (tie mass), ``P3 = C_v,R/E^(1/3)`` (panel cost).
    Selecting the material with the smallest P is the same as selecting the largest IM; the symbolic
    derivation (``symbolic_derivations.py``) shows each P as the material group of a constrained
    minimisation problem  min m  s.t.  stiffness (or strength) >= requirement.
    """
    cv = volumetric_cost(price_usd_kg, rho_kg_m3)
    return {
        "P1": 1.0 / bending_panel_index(E_GPa, rho_kg_m3),
        "P2": 1.0 / tensile_strength_index(sigma_y_MPa, rho_kg_m3),
        "P3": 1.0 / cost_index(E_GPa, cv),
    }


def compute_all_indices(materials: Iterable[dict]) -> list[dict]:
    """Attach IM1, IM2, IM3, the beam indices IM_beam, IM3_beam and C_v,R to each material dict (returns copies)."""
    out = []
    for m in materials:
        cv = float(volumetric_cost(m["price_usd_kg"], m["density_kg_m3"]))
        out.append(
            {
                **m,
                "Cv_usd_m3": cv,
                "IM1": float(bending_panel_index(m["youngs_modulus_GPa"], m["density_kg_m3"])),
                "IM2": float(tensile_strength_index(m["yield_strength_MPa"], m["density_kg_m3"])),
                "IM3": float(cost_index(m["youngs_modulus_GPa"], cv)),
                "IM_beam": float(bending_beam_index(m["youngs_modulus_GPa"], m["density_kg_m3"])),
                "IM3_beam": float(beam_cost_index(m["youngs_modulus_GPa"], cv)),
            }
        )
    return out


if __name__ == "__main__":
    from src.analysis.export_tables import load_materials

    for row in compute_all_indices(load_materials()):
        print(f"{row['id']:<12} IM1={row['IM1']:.2f}  IM2={row['IM2']:.1f}  IM3={row['IM3']:.2f}")
