"""Weighted decision matrix with hard-constraint screening.

Pipeline
--------
1. Hard filters (data/granta_filters.json): UV, water absorption, KIc, temperature, density, then the
   load-case filters (arm stiffness, arm and blade-root strength, ceramics in tension; premises in
   ``load_cases``, see src/math_modeling/load_case_screening.py).
2. Criterion scores in [0, 1]:
     * Mechanical performance = mean(IM1/max(IM1), IM2/max(IM2)), IM1 = E/rho (tube), IM2 = sigma_y/rho
     * Cost                   = IM3/max(IM3), IM3 = E/C_v,R
     * Manufacturability      = score/5   (qualitative, data/materials_db.json)
     * Environmental durability = score/5
3. Weighted sum with user-defined weights (normalised to sum to 1).

Usage (from repository root):
    python -m src.analysis.decision_matrix
    python -m src.analysis.decision_matrix --weights 0.5 0.2 0.15 0.15 --all
    (weight order: mechanical, cost, manufacturability, durability)
"""

from __future__ import annotations

import argparse

from src.analysis.export_tables import load_filters, load_materials, lower, upper
from src.math_modeling.load_case_screening import check_material
from src.math_modeling.merit_indices import compute_all_indices

CRITERIA = ["mechanical_performance", "cost", "manufacturability", "environmental_durability"]


def screen(materials: list[dict], filters: dict) -> tuple[list[dict], dict[str, list[str]]]:
    """Apply hard constraints; return (survivors, {id: [violated constraints]}).

    A constraint that cuts the Granta range of a material (its lowest value for a minimum, its highest for a maximum)
    discards it. A property that is not in the dataset (null) is not evaluated; see :func:`not_evaluated`.
    """
    scale = filters["uv_resistance_scale"]
    survivors, rejected = [], {}
    for m in materials:
        fails = []
        for c in filters["constraints"]:
            prop, kind, limit = c["property"], c["type"], c["value"]
            val = m.get(prop)
            if val is None:
                continue
            if kind == "min_category":
                ok = scale.index(val) >= scale.index(limit)
            elif kind == "min":
                ok = lower(m, prop) >= limit
            else:  # "max"
                ok = upper(m, prop) <= limit
            if not ok:
                fails.append(f"{prop}={val:g} violates {kind} {limit}" if isinstance(val, (int, float))
                             else f"{prop}={val} violates {kind} {limit}")
        if "load_cases" in filters:
            fails += check_material(m, filters["load_cases"])
        if fails:
            rejected[m["id"]] = fails
        else:
            survivors.append(m)
    return survivors, rejected


def not_evaluated(materials: list[dict], filters: dict) -> dict[str, list[str]]:
    """Constraint properties missing from the dataset, per material (the filter could not be applied)."""
    return {m["id"]: [c["property"] for c in filters["constraints"] if m.get(c["property"]) is None]
            for m in materials if any(m.get(c["property"]) is None for c in filters["constraints"])}


def normalise_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0 or any(w < 0 for w in weights.values()):
        raise ValueError("weights must be non-negative with a positive sum")
    return {k: v / total for k, v in weights.items()}


def score_materials(materials: list[dict], weights: dict[str, float]) -> list[dict]:
    """Return materials with per-criterion scores and a weighted total, sorted best-first."""
    if not materials:
        return []
    w = normalise_weights({k: weights[k] for k in CRITERIA})
    rows = compute_all_indices(materials)
    max1 = max(r["IM1"] for r in rows)
    max2 = max(r["IM2"] for r in rows)
    max3 = max(r["IM3"] for r in rows)
    out = []
    for r in rows:
        s = {
            "mechanical_performance": 0.5 * (r["IM1"] / max1 + r["IM2"] / max2),
            "cost": r["IM3"] / max3,
            "manufacturability": r["scores"]["manufacturability"] / 5.0,
            "environmental_durability": r["scores"]["environmental_durability"] / 5.0,
        }
        out.append({"id": r["id"], **s, "total": sum(w[k] * s[k] for k in CRITERIA)})
    return sorted(out, key=lambda x: x["total"], reverse=True)


def format_matrix(scored: list[dict], weights: dict[str, float]) -> str:
    w = normalise_weights({k: weights[k] for k in CRITERIA})
    head = ["Rank", "Material"] + [f"{c} ({w[c]:.2f})" for c in CRITERIA] + ["Total"]
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for i, r in enumerate(scored, 1):
        lines.append(f"| {i} | {r['id']} | " + " | ".join(f"{r[c]:.3f}" for c in CRITERIA) + f" | **{r['total']:.3f}** |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weights", type=float, nargs=4, metavar=("MECH", "COST", "MANUF", "DURAB"))
    ap.add_argument("--all", action="store_true", help="use every complete record instead of the shortlist")
    ap.add_argument("--no-filter", action="store_true", help="skip hard-constraint screening")
    args = ap.parse_args()

    filters = load_filters()
    weights = dict(zip(CRITERIA, args.weights)) if args.weights else filters["weights"]
    mats = load_materials(shortlist_only=not args.all)
    if args.no_filter:
        survivors, rejected = mats, {}
    else:
        survivors, rejected = screen(mats, filters)
    for mid, why in rejected.items():
        print(f"REJECTED {mid}: " + "; ".join(why))
    print(format_matrix(score_materials(survivors, weights), weights))


if __name__ == "__main__":
    main()
