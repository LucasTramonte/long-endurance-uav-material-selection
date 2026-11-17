"""Unit tests for merit indices, laminate model, vibration/fatigue, Pareto and decision matrix.

Run from the repository root:  pytest -q
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.decision_matrix import CRITERIA, normalise_weights, score_materials, screen  # noqa: E402
from src.analysis.export_tables import load_filters, load_materials, properties_dataframe, to_markdown  # noqa: E402
from src.math_modeling import composite_anisotropy as ca  # noqa: E402
from src.math_modeling import merit_indices as mi  # noqa: E402
from src.math_modeling import pareto_optimization as po  # noqa: E402
from src.math_modeling import vibration_fatigue as vf  # noqa: E402


# ---------------------------------------------------------------- merit indices
def test_im1_known_value():
    # Al 7075: E = 71.7 GPa, rho = 2.81 Mg/m3 -> 71.7^(1/3)/2.81
    assert mi.bending_panel_index(71.7, 2810) == pytest.approx(71.7 ** (1 / 3) / 2.81)


def test_im2_known_value():
    assert mi.tensile_strength_index(503, 2810) == pytest.approx(503 / 2.81)


def test_volumetric_cost_and_im3():
    cv = mi.volumetric_cost(4.5, 2810)
    assert cv == pytest.approx(12645.0)
    assert mi.cost_index(71.7, cv) == pytest.approx(71.7 ** (1 / 3) / 12.645)


def test_im1_predicts_panel_mass_ratio():
    """Derivation check: at equal rigidity the mass ratio equals the IM1 inverse ratio."""
    D = mi.rigidity_of_panel(71.7, 1.5e-3)
    m_al = mi.panel_mass_for_rigidity(71.7, 2810, D)
    m_cf = mi.panel_mass_for_rigidity(48.0, 1550, D)
    expected = mi.bending_panel_index(71.7, 2810) / mi.bending_panel_index(48.0, 1550)
    assert m_cf / m_al == pytest.approx(expected, rel=1e-9)


def test_thickness_scaling_cube_root():
    """t ~ E^(-1/3): doubling E at fixed D shrinks t by 2^(1/3)."""
    t1 = mi.panel_thickness_for_rigidity(10.0, 5.0)
    t2 = mi.panel_thickness_for_rigidity(20.0, 5.0)
    assert t1 / t2 == pytest.approx(2 ** (1 / 3))


def test_rigidity_roundtrip():
    D = mi.rigidity_of_panel(71.7, 1.5e-3)
    assert mi.panel_thickness_for_rigidity(71.7, D) == pytest.approx(1.5e-3)


def test_vectorised_and_validation():
    out = mi.bending_panel_index([10, 20], [1000, 2000])
    assert out.shape == (2,)
    with pytest.raises(ValueError):
        mi.bending_panel_index(-1, 1000)
    with pytest.raises(ValueError):
        mi.tensile_strength_index(100, 0)


# ---------------------------------------------------------------- laminate model
def test_unidirectional_matches_rule_of_mixtures():
    r = ca.effective_modulus([0.0] * 4, Vf=0.6)
    k = ca.ply_engineering_constants(0.6)
    # Poisson coupling makes Ex marginally different from E1 only in the 3rd digit
    assert r["Ex"] == pytest.approx(k["E1"], rel=1e-3)
    assert r["Ey"] == pytest.approx(k["E2"], rel=1e-3)


def test_quasi_isotropic_is_isotropic_in_plane():
    r = ca.effective_modulus(ca.quasi_isotropic_layup(), Vf=0.55)
    assert r["Ex"] == pytest.approx(r["Ey"], rel=1e-9)
    # isotropy: G = E / (2 (1 + nu))
    assert r["Gxy"] == pytest.approx(r["Ex"] / (2 * (1 + r["nuxy"])), rel=1e-6)


def test_rotation_by_90_swaps_axes():
    a = ca.effective_modulus([0.0] * 4, Vf=0.55)
    b = ca.effective_modulus([90.0] * 4, Vf=0.55)
    assert a["Ex"] == pytest.approx(b["Ey"], rel=1e-9)


def test_modulus_increases_with_vf():
    lo = ca.effective_modulus(ca.quasi_isotropic_layup(), Vf=0.4)["Ex"]
    hi = ca.effective_modulus(ca.quasi_isotropic_layup(), Vf=0.6)["Ex"]
    assert hi > lo


def test_invalid_vf():
    with pytest.raises(ValueError):
        ca.ply_engineering_constants(1.2)


# ---------------------------------------------------------------- vibration / fatigue
def test_motor_frequency():
    assert vf.rpm_to_hz(40_000) == pytest.approx(666.6667, rel=1e-6)


def test_transmissibility_properties():
    assert vf.transmissibility(100.0, 100.0, 0.05) > 5            # resonance amplifies
    assert vf.transmissibility(math.sqrt(2) * 50, 50, 0.3) == pytest.approx(1.0, rel=1e-9)  # r = sqrt(2) -> T = 1
    assert vf.transmissibility(666.7, 100, 0.1) < 1                # isolation region
    assert vf.transmissibility(1e-6, 100, 0.1) == pytest.approx(1.0, rel=1e-6)  # quasi-static


def test_required_isolator_frequency_meets_target():
    f = vf.rpm_to_hz(40_000)
    fn = vf.required_isolator_natural_frequency(f, 0.1, 0.1)
    assert vf.transmissibility(f, fn, 0.1) == pytest.approx(0.1, rel=1e-3)
    with pytest.raises(ValueError):
        vf.required_isolator_natural_frequency(f, 1.5, 0.1)


def test_isolator_stiffness():
    assert vf.isolator_stiffness(1.0, 1 / (2 * math.pi)) == pytest.approx(1.0)


def test_plate_frequency_scales_with_thickness():
    f1 = vf.plate_natural_frequency_ss(71.7, 2810, 1e-3, 0.3, 0.15)
    f2 = vf.plate_natural_frequency_ss(71.7, 2810, 2e-3, 0.3, 0.15)
    assert f2 / f1 == pytest.approx(2.0, rel=1e-9)


def test_basquin_and_miner():
    N = vf.basquin_cycles(300.0, 900.0, -0.1)
    assert N == pytest.approx(0.5 * 3.0 ** 10)
    assert vf.miner_damage([1e5, 1e5], [2e5, 4e5]) == pytest.approx(0.75)
    with pytest.raises(ValueError):
        vf.basquin_cycles(100.0, 900.0, 0.1)


# ---------------------------------------------------------------- Pareto
def test_pareto_mask_simple():
    pts = np.array([[1, 5], [2, 4], [3, 3], [3, 5], [4, 4]])
    assert po.pareto_mask(pts).tolist() == [True, True, True, False, False]


def test_pareto_duplicates_are_both_kept():
    assert po.pareto_mask(np.array([[1, 1], [1, 1]])).tolist() == [True, True]


def test_pareto_on_database_contains_lightest_and_cheapest():
    rows = po.pareto_front(po.evaluate_candidates(load_materials()))
    flagged = {r["id"] for r in rows if r["pareto"]}
    lightest = min(rows, key=lambda r: r["mass_g"])["id"]
    cheapest = min(rows, key=lambda r: r["cost_usd"])["id"]
    assert lightest in flagged and cheapest in flagged


# ---------------------------------------------------------------- decision matrix / data
def test_database_integrity():
    mats = load_materials()
    assert len(mats) >= 4
    assert {m["id"] for m in mats if m["shortlist"]} == {"CFRP_QI", "PEEK_CF30", "PC", "AL_7075_T6"}
    for m in mats:
        assert m["density_kg_m3"] > 0 and m["youngs_modulus_GPa"] > 0


def test_screening_rejects_abs_and_keeps_shortlist():
    survivors, rejected = screen(load_materials(), load_filters())
    assert "ABS" in rejected
    assert {m["id"] for m in survivors} >= {"CFRP_QI", "PEEK_CF30", "AL_7075_T6"}
    assert "PC" in rejected                               # arm stiffness E >= 3.84 GPa and fatigue premise


def test_weights_normalised_and_ranking_responds():
    w = normalise_weights({"a": 2, "b": 2})
    assert sum(w.values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        normalise_weights({"a": 0})
    surv, _ = screen(load_materials(shortlist_only=True), load_filters())
    mech_only = dict.fromkeys(CRITERIA, 0.0) | {"mechanical_performance": 1.0}
    cost_only = dict.fromkeys(CRITERIA, 0.0) | {"cost": 1.0}
    assert score_materials(surv, mech_only)[0]["id"] == "CFRP_QI"
    assert score_materials(surv, cost_only)[0]["id"] == "AL_7075_T6"


def test_scores_bounded():
    surv, _ = screen(load_materials(shortlist_only=True), load_filters())
    for r in score_materials(surv, load_filters()["weights"]):
        assert 0.0 <= r["total"] <= 1.0


def test_markdown_table_shape():
    md = to_markdown(properties_dataframe(load_materials(shortlist_only=True))).splitlines()
    assert len(md) == 2 + 4


def test_dominance_relations_of_the_pareto_analysis():
    from src.analysis.export_tables import load_materials
    from src.math_modeling.pareto_optimization import dominated_by, evaluate_candidates, pareto_front

    rows = pareto_front(evaluate_candidates(load_materials(shortlist_only=False)))
    dom = dominated_by(rows)
    assert set(dom) == {r["id"] for r in rows if not r["pareto"]}     # exactly the non-Pareto rows are dominated
    optimal = {r["id"] for r in rows if r["pareto"]}
    assert all(optimal & set(v) for v in dom.values())          # each dominated row has a Pareto-optimal dominator
