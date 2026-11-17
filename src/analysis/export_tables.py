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


def load_materials(path: Path | None = None, shortlist_only: bool = False) -> list[dict]:
    """Load materials from JSON (default: data/materials_db.json)."""
    with open(path or DATA_DIR / "materials_db.json", encoding="utf-8") as fh:
        mats = json.load(fh)["materials"]
    return [m for m in mats if m.get("shortlist")] if shortlist_only else mats


def load_cases(path: Path | None = None) -> dict:
    """Load-case premises (arm, rotor, safety factor, fatigue ratio, steel reference) of data/granta_filters.json."""
    return load_filters(path)["load_cases"]


def load_filters(path: Path | None = None) -> dict:
    with open(path or DATA_DIR / "granta_filters.json", encoding="utf-8") as fh:
        return json.load(fh)


def properties_dataframe(materials: list[dict]) -> pd.DataFrame:
    """Flat table of core properties plus derived indices."""
    from src.math_modeling.merit_indices import compute_all_indices

    rows = []
    for m in compute_all_indices(materials):
        rows.append({
            "Material": m["id"],
            "rho (kg/m3)": m["density_kg_m3"],
            "E (GPa)": m["youngs_modulus_GPa"],
            "sigma_y (MPa)": m["yield_strength_MPa"],
            "KIc (MPa.m^0.5)": m["fracture_toughness_MPa_m05"],
            "Water 24h (%)": m["water_absorption_24h_pct"],
            "UV": m["uv_resistance"],
            "Price (USD/kg)": m["price_usd_kg"],
            "Cv,R (USD/m3)": round(m["Cv_usd_m3"]),
            "IM1": round(m["IM1"], 2),
            "IM2": round(m["IM2"], 1),
            "IM3": round(m["IM3"], 2),
        })
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
    ap.add_argument("--shortlist", action="store_true", help="only the four shortlisted materials")
    args = ap.parse_args()

    df = properties_dataframe(load_materials(shortlist_only=args.shortlist))
    md = to_markdown(df)
    print(md)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out / "materials.csv", index=False)
        (args.out / "materials.md").write_text(md + "\n", encoding="utf-8")
        print(f"\nWrote {args.out / 'materials.csv'} and {args.out / 'materials.md'}")


if __name__ == "__main__":
    main()
