"""Multi-objective optimisation: mass vs. cost vs. fracture toughness.

Objectives (for a panel of prescribed bending rigidity, see merit_indices.py):
  1. minimise panel mass          m    = rho * L * w * t,  t = (12 D / E)^(1/3)
  2. minimise material cost       cost = C_m * m
  3. maximise fracture toughness  KIc  (converted to -KIc so that all objectives are minimised)

A candidate is Pareto-optimal if no other candidate is at least as good in every
objective and strictly better in at least one.

Usage:
    python -m src.math_modeling.pareto_optimization [--all] [--plot docs/figures/pareto.png]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.analysis.export_tables import ROOT, load_filters, load_materials
from src.math_modeling.merit_indices import panel_mass_for_rigidity, rigidity_of_panel


def pareto_mask(objectives: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated rows; every column is MINIMISED."""
    obj = np.asarray(objectives, dtype=float)
    n = obj.shape[0]
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        dominated = np.all(obj <= obj[i], axis=1) & np.any(obj < obj[i], axis=1)
        if dominated.any():
            mask[i] = False
    return mask


def evaluate_candidates(materials: list[dict], D_target: float | None = None,
                        length_m: float | None = None, width_m: float | None = None) -> list[dict]:
    """Compute panel mass [kg], material cost [USD] and KIc for each material.

    Defaults (panel size and rigidity target) come from "reference_panel" in
    data/granta_filters.json.
    """
    ref = load_filters()["reference_panel"]
    length_m = ref["length_m"] if length_m is None else length_m
    width_m = ref["width_m"] if width_m is None else width_m
    if D_target is None:
        ref_mat = next(m for m in load_materials() if m["id"] == ref["reference_material"])
        D_target = rigidity_of_panel(ref_mat["youngs_modulus_GPa"], ref["reference_thickness_m"])
    rows = []
    for m in materials:
        mass = panel_mass_for_rigidity(m["youngs_modulus_GPa"], m["density_kg_m3"], D_target,
                                       length_m, width_m)
        rows.append({
            "id": m["id"],
            "mass_g": mass * 1000.0,
            "cost_usd": mass * m["price_usd_kg"],
            "KIc": m["fracture_toughness_MPa_m05"],
        })
    return rows


def pareto_front(rows: list[dict]) -> list[dict]:
    """Return rows annotated with a boolean 'pareto' flag."""
    obj = np.array([[r["mass_g"], r["cost_usd"], -r["KIc"]] for r in rows])
    mask = pareto_mask(obj)
    return [{**r, "pareto": bool(k)} for r, k in zip(rows, mask)]


def dominated_by(rows: list[dict]) -> dict[str, list[str]]:
    """For every dominated row, the ids of the rows that dominate it (mass, cost minimised; KIc maximised)."""
    obj = np.array([[r["mass_g"], r["cost_usd"], -r["KIc"]] for r in rows])
    out: dict[str, list[str]] = {}
    for i, r in enumerate(rows):
        dom = [rows[j]["id"] for j in range(len(rows))
               if j != i and np.all(obj[j] <= obj[i]) and np.any(obj[j] < obj[i])]
        if dom:
            out[r["id"]] = dom
    return out


def _front_2d(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Non-dominated points of two objectives that are both minimised, sorted by x."""
    keep = pareto_mask(np.column_stack([x, y]))
    order = np.argsort(x[keep])
    return x[keep][order], y[keep][order]


def build_front_figure(rows: list[dict]):
    """Two projections of the three-objective problem, with the 2D fronts and the dominance relations."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter, NullFormatter

    from src.analysis.figure_utils import declutter

    blue, grey, vermilion = "#0072B2", "#666666", "#D55E00"
    mass = np.array([r["mass_g"] for r in rows])
    cost = np.array([r["cost_usd"] for r in rows])
    kic = np.array([r["KIc"] for r in rows])
    optimal = np.array([r["pareto"] for r in rows])

    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.6))
    fig.subplots_adjust(left=0.07, right=0.98, top=0.86, bottom=0.2, wspace=0.22)
    panels = (
        (axs[0], cost, "Material cost of the panel (USD, log scale)", _front_2d(mass, cost), "lower left"),
        (axs[1], kic, r"Fracture toughness $K_{Ic}$ (MPa$\cdot$m$^{1/2}$, log scale)", None, "upper left"),
    )
    labelled = []
    for ax, y, ylabel, front, corner in panels:
        if front is None:                                   # mass minimised, K_Ic maximised
            fx, fneg = _front_2d(mass, -kic)
            front = (fx, -fneg)
        ax.step(front[0], front[1], where="post", color=blue, lw=1.4, ls="--", alpha=0.7, zorder=1)
        ax.scatter(mass[~optimal], y[~optimal], s=80, facecolor="white", edgecolor=grey, lw=1.6, zorder=3)
        ax.scatter(mass[optimal], y[optimal], s=90, color=blue, zorder=4)
        texts = [ax.text(m, v, r["id"].replace("_", " "), fontsize=9, color=blue if r["pareto"] else grey)
                 for r, m, v in zip(rows, mass, y)]
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_yticks([t for t in (0.03, 0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 50)
                       if 0.8 * y.min() <= t <= 1.25 * y.max()])
        ax.set_xlabel("Panel mass at equal bending rigidity (g)")
        ax.set_ylabel(ylabel)
        ax.grid(True, which="major", alpha=0.25)
        ax.margins(x=0.12, y=0.18)
        ideal = (0.05, 0.08) if corner == "lower left" else (0.05, 0.66)
        away = (0.17, 0.30) if corner == "lower left" else (0.17, 0.50)
        ax.annotate("better", xy=ideal, xytext=away, xycoords="axes fraction", textcoords="axes fraction",
                    fontsize=9, color=vermilion, ha="center",
                    arrowprops=dict(arrowstyle="-|>", color=vermilion, lw=1.4))
        labelled.append((ax, texts, (mass, y)))
    fig.canvas.draw()                                       # extents are needed before the labels are placed
    for ax, texts, pts in labelled:
        declutter(ax, texts, points=pts, leader=False)
    axs[0].set_title("(a) Mass vs cost", loc="left", fontsize=11)
    axs[1].set_title(r"(b) Mass vs toughness", loc="left", fontsize=11)

    fig.suptitle("Pareto analysis of the candidate materials: minimise mass and cost, maximise toughness",
                 fontsize=12, y=0.97)
    fig.legend(handles=[
        Line2D([0], [0], marker="o", ls="", color=blue, label="non-dominated in all three objectives"),
        Line2D([0], [0], marker="o", ls="", mfc="white", mec=grey, mew=1.6, color=grey, label="dominated"),
        Line2D([0], [0], color=blue, ls="--", lw=1.4, label="front of the two objectives shown"),
    ], loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.075))
    dom = dominated_by(rows)
    pretty = {k: ", ".join(v).replace("_", " ") for k, v in dom.items()}
    note = "Dominated: " + "; ".join(f"{k.replace('_', ' ')} by {v}" for k, v in pretty.items())
    fig.text(0.5, 0.025, note, ha="center", fontsize=8.5, color=grey, wrap=True)
    return fig


def plot_front(rows: list[dict], path: Path) -> None:
    fig = build_front_figure(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="use the full screening pool, not only the shortlist")
    ap.add_argument("--plot", type=Path, help="save scatter plot to this path")
    args = ap.parse_args()

    mats = load_materials(shortlist_only=not args.all)
    rows = pareto_front(evaluate_candidates(mats))
    print(f"{'Material':<12}{'mass (g)':>10}{'cost (USD)':>12}{'KIc':>8}  Pareto")
    for r in sorted(rows, key=lambda r: r["mass_g"]):
        print(f"{r['id']:<12}{r['mass_g']:>10.1f}{r['cost_usd']:>12.3f}{r['KIc']:>8.1f}  {'*' if r['pareto'] else ''}")
    if args.plot:
        plot_front(rows, args.plot if args.plot.is_absolute() else ROOT / args.plot)
        print(f"Saved {args.plot}")


if __name__ == "__main__":
    main()
