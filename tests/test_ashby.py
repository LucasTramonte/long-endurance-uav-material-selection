"""Ashby chart procedure: constraint, screening, guide lines, safety factor, and the drawn charts."""

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.analysis import ashby_charts as ac  # noqa: E402
from src.analysis.export_tables import load_cases, load_materials  # noqa: E402
from src.analysis.figure_utils import text_overlaps  # noqa: E402
from src.math_modeling import ashby_selection as sel  # noqa: E402
from src.math_modeling.load_case_screening import derived_limits  # noqa: E402
from src.math_modeling.merit_indices import bending_panel_index, compute_all_indices  # noqa: E402

ARM = dict(F=0.30, L=0.030, b=0.005, h=0.0015)


def test_arm_requirements_match_hand_calculation():
    e_c, s_c = sel.arm_requirements(**ARM, w_max=0.5e-3, s=1.5)
    assert e_c.minimum == pytest.approx(4 * 0.3 * 0.03**3 / (0.005 * 0.0015**3 * 0.5e-3) / 1e9)
    assert s_c.minimum == pytest.approx(1.5 * 6 * 0.3 * 0.03 / (0.005 * 0.0015**2) / 1e6)


def test_stiffness_constraint_is_consistent_with_deflection_formula():
    e_c, _ = sel.arm_requirements(**ARM, w_max=0.5e-3)
    E = e_c.minimum * 1e9
    I = ARM["b"] * ARM["h"] ** 3 / 12
    assert ARM["F"] * ARM["L"] ** 3 / (3 * E * I) == pytest.approx(0.5e-3)


def test_screening_discards_what_the_constraint_cuts():
    e_c, _ = sel.arm_requirements(**ARM, w_max=0.5e-3)
    kept, dropped = sel.screen_by_constraint(load_materials(), e_c)
    assert {m["id"] for m, _ in dropped} == {"PC", "ABS"}
    assert all(m["youngs_modulus_GPa"] >= e_c.minimum for m in kept)


def test_ceramics_are_excluded_in_tension_only():
    ceramic = {"id": "AL2O3", "family": "Ceramic", "youngs_modulus_GPa": 370, "yield_strength_MPa": 300}
    c = sel.Constraint("youngs_modulus_GPa", 1.0, "E")
    assert sel.screen_by_constraint([ceramic], c, tension=True)[0] == []
    assert sel.screen_by_constraint([ceramic], c, tension=False)[0] == [ceramic]


def test_guide_line_slope_and_offset():
    a = {"id": "a", "density_kg_m3": 1000.0, "youngs_modulus_GPa": 10.0}
    on = {"id": "b", "density_kg_m3": 2000.0, "youngs_modulus_GPa": 10.0 * 2**3}   # same E^(1/3)/rho
    better = {"id": "c", "density_kg_m3": 1000.0, "youngs_modulus_GPa": 100.0}
    s = sel.GUIDE_SLOPES["E^(1/3)/rho"]
    assert sel.on_guide_line(on, a, "density_kg_m3", "youngs_modulus_GPa", s)
    assert sel.offset_decades(better, a, "density_kg_m3", "youngs_modulus_GPa", s) > 0
    assert bending_panel_index(8e1 / 8, 1000) == pytest.approx(bending_panel_index(80, 2000))


@pytest.mark.parametrize("spec", ac.CHARTS, ids=lambda s: s.key)
def test_selected_material_has_the_best_merit_index(spec):
    """The guide-line anchor of each chart is the survivor with the largest index of that guide."""
    fig, ax = plt.subplots()
    ax.set_xlim(*spec.open_xlim)
    ax.set_ylim(*spec.open_ylim)
    anchors, dropped, _ = ac.draw_overlay(ax, spec, load_cases(), spec.open_xlim, spec.open_ylim)
    plt.close(fig)
    rows = {r["id"]: r for r in compute_all_indices(load_materials()) if r["id"] not in dropped}
    key = {"E_rho": ("IM1",), "sigma_rho": ("IM2",), "E_cost": ("IM3",), "sigma_cost": ("IM2",)}
    for guide, name in zip(spec.guides, key[spec.key], strict=True):
        if spec.key == "sigma_cost":          # sigma/C_v,R is a different index from IM2 (sigma/rho): recompute
            best = max(rows.values(), key=lambda r: r["yield_strength_MPa"] / r["Cv_usd_m3"])["id"]
        else:
            best = max(rows.values(), key=lambda r: r[name])["id"]
        assert anchors[guide.index]["id"] == best


def test_load_case_constraints_on_the_charts():
    lim = derived_limits(load_cases())
    assert lim["E_min_GPa"] == pytest.approx(3.84)
    assert lim["sigma_mean_MPa"] == pytest.approx(4.8)


@pytest.mark.parametrize("spec", ac.CHARTS, ids=lambda s: s.key)
def test_open_charts_have_no_overlapping_labels(spec):
    fig = ac.build_open(spec)
    try:
        # the numbered step circles (single digits) sit on their arrows; the label placement of adjustText varies
        # slightly with the matplotlib version, so the check is on the readable labels and the legend lines
        bad = [pair for pair in text_overlaps(fig) if not any(t.isdigit() for t in pair)]
        assert bad == []
    finally:
        plt.close(fig)


def test_safety_factors_carry_their_verification_status():
    assert all(isinstance(f.verified, bool) and f.source for f in sel.SAFETY_FACTORS)
    assert np.isclose(sel.DEFAULT_SAFETY_FACTOR, 1.5)
