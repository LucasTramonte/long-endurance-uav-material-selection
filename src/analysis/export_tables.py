"""Format material property tables as Markdown and CSV.

Usage (from the repository root):
    python -m src.analysis.export_tables                 # print Markdown to stdout
    python -m src.analysis.export_tables --out outputs   # also write CSV + MD files
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def _geometric_mean(lo: float, hi: float) -> float:
    """Centre of a Granta bubble in log space."""
    return (lo * hi) ** 0.5


def expand_ranges(material: dict) -> dict:
    """Add the representative value (geometric mean of the Granta range) as the plain key, plus ``<key>_min`` and ``<key>_max``."""
    out = dict(material)
    for key, (lo, hi) in material.get("granta", {}).items():
        out[key] = _geometric_mean(lo, hi)
        out[f"{key}_min"], out[f"{key}_max"] = lo, hi
    return out


def lower(m: dict, prop: str) -> float:
    """Lowest value of the Granta range (conservative for a minimum requirement); the plain value if no range."""
    return m.get(f"{prop}_min", m[prop])


def upper(m: dict, prop: str) -> float:
    """Highest value of the Granta range (conservative for a maximum requirement)."""
    return m.get(f"{prop}_max", m[prop])


def load_materials(path: Path | None = None, shortlist_only: bool = False, include_incomplete: bool = False) -> list[dict]:
    """Load materials from JSON (default: data/materials_db.json), with the Granta ranges expanded.

    Records without the mechanical properties (``complete`` false) are left out unless ``include_incomplete``.
    """
    with open(path or DATA_DIR / "materials_db.json", encoding="utf-8") as fh:
        mats = [expand_ranges(m) for m in json.load(fh)["materials"]]
    if not include_incomplete:
        mats = [m for m in mats if m.get("complete", True)]
    return [m for m in mats if m.get("shortlist")] if shortlist_only else mats


def load_cases(path: Path | None = None) -> dict:
    """Load-case premises (arm, rotor, safety factor) of data/granta_filters.json."""
    return load_filters(path)["load_cases"]


def load_filters(path: Path | None = None) -> dict:
    with open(path or DATA_DIR / "granta_filters.json", encoding="utf-8") as fh:
        return json.load(fh)


def reference_cv() -> float:
    """Volumetric cost C_v [BRL/m^3] of the steel reference record (centre of the Granta ranges)."""
    ref = load_filters()["reference_steel"]
    return _geometric_mean(*ref["price_brl_kg"]) * _geometric_mean(*ref["density_kg_m3"])


def properties_dataframe(materials: list[dict]) -> pd.DataFrame:
    """Flat table of core properties (representative values and Granta ranges) plus derived indices."""
    from src.math_modeling.merit_indices import compute_all_indices

    rows = []
    for m in compute_all_indices(materials):
        rows.append({
            "Material": m["id"],
            "rho (kg/m3)": f"{m['density_kg_m3_min']:g}-{m['density_kg_m3_max']:g}",
            "E (GPa)": f"{m['youngs_modulus_GPa_min']:g}-{m['youngs_modulus_GPa_max']:g}",
            "sigma_y (MPa)": f"{m['yield_strength_MPa_min']:g}-{m['yield_strength_MPa_max']:g}",
            "KIc (MPa.m^0.5)": f"{m['fracture_toughness_MPa_m05_min']:g}-{m['fracture_toughness_MPa_m05_max']:g}",
            "Price (BRL/kg)": f"{m['price_brl_kg_min']:g}-{m['price_brl_kg_max']:g}",
            "Cv (BRL/m3)": round(m["Cv_brl_m3"]),
            "Cv/Cv,steel": round(m["Cv_brl_m3"] / reference_cv(), 2),
            "IM1": round(m["IM1"], 1),
            "IM2": round(m["IM2"], 1),
            "IM3": round(m["IM3"], 2),
        })
    return pd.DataFrame(rows)


def tube_table(materials: list[dict]) -> pd.DataFrame:
    """Wall, mass and material cost of the reference tube at equal flexural rigidity (README Section 3.2).

    The rigidity target is that of a wall of ``reference_thickness_m`` of the reference material; a wall thicker than the
    radius is a formal value (the thin-walled model does not hold).
    """
    from src.math_modeling.merit_indices import tube_mass_for_rigidity, tube_rigidity, tube_thickness_for_rigidity

    ref = load_filters()["reference_tube"]
    r, length = ref["mean_radius_m"], ref["length_m"]
    ref_mat = next(m for m in load_materials(include_incomplete=True) if m["id"] == ref["reference_material"])
    ei = tube_rigidity(ref_mat["youngs_modulus_GPa"], ref["reference_thickness_m"], r)
    rows = []
    for m in materials:
        wall = tube_thickness_for_rigidity(m["youngs_modulus_GPa"], ei, r)
        mass = tube_mass_for_rigidity(m["youngs_modulus_GPa"], m["density_kg_m3"], ei, r, length)
        rows.append({"Material": m["id"], "Wall (mm)": round(wall * 1e3, 2) if wall <= r else f"{wall * 1e3:.1f} (> radius)",
                     "Mass (g)": round(mass * 1e3, 1), "Cost (BRL)": round(mass * m["price_brl_kg"], 2)})
    return pd.DataFrame(rows)


def to_markdown(df: pd.DataFrame) -> str:
    """GitHub-flavoured Markdown pipe table (no external dependency)."""
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, help="directory for materials.csv / materials.md")
    ap.add_argument("--shortlist", action="store_true", help="only the shortlisted materials")
    ap.add_argument("--tube", action="store_true", help="wall, mass and cost of the reference tube instead of the properties")
    args = ap.parse_args()

    mats = load_materials(shortlist_only=args.shortlist)
    df = tube_table(mats) if args.tube else properties_dataframe(mats)
    md = to_markdown(df)
    print(md)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out / "materials.csv", index=False)
        (args.out / "materials.md").write_text(md + "\n", encoding="utf-8")
        print(f"\nWrote {args.out / 'materials.csv'} and {args.out / 'materials.md'}")


if __name__ == "__main__":
    main()
