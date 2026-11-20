"""Ashby charts with the constraint lines, discarded region, guide lines and numbered arrows drawn on them.

Two renderings of the same drawing code (axes are log10 of the property, so every merit-index line is straight):

* ``open``  - blank log-log axes plus the points of ``data/materials_db.json``. Reproducible, safe to publish
  (``docs/figures/ashby_*_blank.png``), for machines without the source PDFs.
* ``print`` - the same overlay drawn on top of the ORIGINAL charts (``assets/ashby_charts/*.pdf``: Ashby, Materials
  Selection in Mechanical Design, 4th ed., 2011, Granta MFA). The team decided to publish the annotated charts
  (``docs/figures/ashby_*_annotated.png``, with the source credited in the image); the source PDFs stay git-ignored.

The five steps of the reading (see ``.claude/skills/ashby-chart-selection``):
  1 constraint line, 2 materials discarded, 3 guide line of the merit index, 4 slide the ruler along the slope,
  5 keep the material whose bubble centre the guide line crosses.

Premises (arm, rotor, safety factor, steel reference) come from ``data/granta_filters.json`` -> ``load_cases``.

Usage (repository root):  python -m src.analysis.ashby_charts [--print | --open]   (default: --print if the PDFs exist)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.analysis.export_tables import ROOT, load_cases, load_materials
from src.analysis.figure_utils import declutter
from src.math_modeling.ashby_selection import GUIDE_SLOPES, excluded_in_tension, guide_line_log
from src.math_modeling.load_case_screening import derived_limits
from src.math_modeling.merit_indices import relative_volumetric_cost
from src.math_modeling.rotating_parts import blade_root_stress

CHART_DIR = ROOT / "assets" / "ashby_charts"
OUT_OPEN = ROOT / "docs" / "figures"
BLUE, RED, GREY, GREEN, PINK, BLACK = "#0072B2", "#D55E00", "#555555", "#009E73", "#CC79A7", "#111111"
WHITE_BOX = dict(fc="white", ec="none", alpha=0.88, pad=1.6)


@dataclass(frozen=True)
class Calib:
    """Pixel <-> log10 mapping of a printed chart: pixel of a known decade and pixels per decade."""

    x_px: float
    x_log: float
    x_dec: float
    y_px: float
    y_log: float
    y_dec: float

    def extent(self, width: int, height: int):
        left = self.x_log + (0 - self.x_px) / self.x_dec
        right = self.x_log + (width - self.x_px) / self.x_dec
        top = self.y_log + (self.y_px - 0) / self.y_dec
        bottom = self.y_log + (self.y_px - height) / self.y_dec
        return left, right, bottom, top


@dataclass(frozen=True)
class Guide:
    """A merit-index guide line: its key in GUIDE_SLOPES, colour and label."""

    index: str
    color: str
    label: str


@dataclass(frozen=True)
class ChartSpec:
    key: str
    x_prop: str                      # "density_kg_m3" or "Cv_R" (relative volumetric cost)
    y_prop: str
    xlabel: str
    ylabel: str
    guides: tuple[Guide, ...]
    pdf: str
    image_no: int
    calib: Calib
    open_xlim: tuple[float, float]
    open_ylim: tuple[float, float]


RHO = r"Density $\rho$ (kg/m$^3$)"
CVR = r"Relative cost per unit volume $C_{v,R}$"
CHARTS = (
    ChartSpec("E_rho", "density_kg_m3", "youngs_modulus_GPa", RHO, "Young's modulus $E$ (GPa)",
              (Guide("E/rho", BLUE, r"$E/\rho$ (tube)"),),
              "mapas_ashby", 1, Calib(407, 2, 288.5, 205, 2, 107.3), (2.8, 3.7), (-0.3, 2.4)),
    ChartSpec("sigma_rho", "density_kg_m3", "yield_strength_MPa", RHO, r"Strength $\sigma_f$ (MPa)",
              (Guide("sigma/rho", BLUE, r"$\sigma_f/\rho$"),),
              "mapas_ashby", 0, Calib(412, 2, 286.5, 277, 2, 133.2), (2.8, 3.7), (0.5, 3.3)),
    ChartSpec("E_cost", "Cv_R", "youngs_modulus_GPa", CVR, "Young's modulus $E$ (GPa)",
              (Guide("E/rho", BLUE, r"$E/C_{v,R}$ (tube)"),),
              "diagrama_custo", 0, Calib(550, 0, 212.5, 199, 2, 124.7), (-0.3, 2.0), (-0.3, 2.4)),
    ChartSpec("sigma_cost", "Cv_R", "yield_strength_MPa", CVR, r"Strength $\sigma_f$ (MPa)",
              (Guide("sigma/rho", BLUE, r"$\sigma_f/C_{v,R}$"),),
              "diagrama_custo", 1, Calib(574, 0, 220, 315, 2, 132.8), (-0.3, 2.0), (0.5, 3.3)),
)


def material_xy(m: dict, spec: ChartSpec, case: dict) -> tuple[float, float]:
    ref = case["reference_steel"]
    x = (relative_volumetric_cost(m["price_usd_kg"], m["density_kg_m3"], ref["price_usd_kg"], ref["density_kg_m3"])
         if spec.x_prop == "Cv_R" else m[spec.x_prop])
    return float(np.log10(x)), float(np.log10(m[spec.y_prop]))


def constraints_for(spec: ChartSpec, case: dict) -> list[dict]:
    """Constraint lines of the chart: horizontal (value) or sloped (the slope-1 blade-root line in log-log)."""
    lim, s = derived_limits(case), case["safety_factor"]
    if spec.y_prop == "youngs_modulus_GPa":
        return [dict(kind="h", value=lim["E_min_GPa"], color=RED,
                     label=rf"$E\geq{lim['E_min_GPa']:.2f}$ GPa (arm tip deflection)")]
    v = s * lim["sigma_mean_MPa"]
    cons = [dict(kind="h", value=v, color=RED, label=rf"$\sigma_y\geq{v:.1f}$ MPa (arm strength, $s={s:g}$)")]
    if spec.x_prop == "density_kg_m3":
        c = s * blade_root_stress(1.0, lim["omega_rad_s"], case["rotor"]["blade_length_m"]) / 1e6   # MPa per kg/m^3
        cons.append(dict(kind="line", slope=1.0, intercept=float(np.log10(c)), color=PINK,
                         label=r"$\sigma_y\geq s\rho\omega^{2}R_b^{2}/2$ (blade root)"))
    return cons


def fails_constraint(c: dict, xy: tuple[float, float]) -> bool:
    if c["kind"] == "h":
        return xy[1] < np.log10(c["value"])
    return xy[1] < c["intercept"] + c["slope"] * xy[0]


def _step(ax, n, target, offset, color, scale):
    """A numbered marker joined by a short arrow to ``target`` (data coordinates); ``offset`` in points."""
    ax.annotate(str(n), xy=target, xycoords="data", xytext=offset, textcoords="offset points", fontsize=10 * scale,
                color="white", ha="center", va="center", zorder=13,
                bbox=dict(boxstyle="circle,pad=0.25", fc=color, ec="white", lw=1.0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8 * scale, shrinkA=6, shrinkB=3))


def draw_overlay(ax, spec: ChartSpec, case: dict, xlim: tuple, ylim: tuple, scale: float = 1.0,
                 chart_bottom: float | None = None):
    """Draw steps 1-5 on ``ax`` (log10 coordinates). Returns (anchor per guide, discarded ids, legend lines)."""
    span_x, span_y = xlim[1] - xlim[0], ylim[1] - ylim[0]
    bottom = ylim[0] if chart_bottom is None else chart_bottom       # lines stop at the frame of the chart

    def line(xs, ys, **kw):
        keep = (ys >= bottom) & (ys <= ylim[1])
        ax.plot(xs[keep], ys[keep], **kw)

    xf = np.linspace(xlim[0], xlim[1], 400)
    mats = load_materials()
    pts = {m["id"]: material_xy(m, spec, case) for m in mats}
    cons = constraints_for(spec, case)
    dropped = {m["id"] for m in mats
               if excluded_in_tension(m) or any(fails_constraint(c, pts[m["id"]]) for c in cons)}
    kept = [m for m in mats if m["id"] not in dropped]
    legend = []
    # step 1: constraint lines and the shaded region they discard
    for k, c in enumerate(cons):
        if c["kind"] == "h":
            y0 = np.log10(c["value"])
            ax.axhline(y0, color=c["color"], lw=2.0 * scale, zorder=5)
            ax.axhspan(bottom, y0, facecolor=c["color"], alpha=0.07, hatch="///", edgecolor=c["color"], lw=0, zorder=4)
            tgt = (xlim[0] + ((0.20 if scale > 1 else 0.78) + 0.10 * k) * span_x, y0)
        else:
            line(xf, c["intercept"] + c["slope"] * xf, color=c["color"], lw=2.0 * scale, ls="-.", zorder=5)
            xt = xlim[0] + 0.30 * span_x
            tgt = (xt, c["intercept"] + c["slope"] * xt)
        _step(ax, 1, tgt, (0, -26 - 14 * k), c["color"], scale)
        legend.append((1, c["color"], "constraint line: " + c["label"]))
    # steps 3-5: one guide line per merit index, through the best surviving material
    anchors = {}
    for g in spec.guides:
        sl = GUIDE_SLOPES[g.index]
        best = max(kept, key=lambda m: pts[m["id"]][1] - sl * pts[m["id"]][0], default=None)
        anchors[g.index] = best
        if best is not None:
            line(xf, guide_line_log(sl, pts[best["id"]], xf), color=g.color, lw=2.0 * scale, zorder=6)
    texts, px, py = [], [], []
    selected = {a["id"] for a in anchors.values() if a is not None}
    for m in mats:
        p = pts[m["id"]]
        if m["id"] in dropped:
            ax.plot(*p, marker="x", color=GREY, ms=8 * scale, mew=2, zorder=8)
            texts.append(ax.text(*p, m["id"] + " (discarded)", fontsize=8 * scale, color=GREY, zorder=9))
        else:
            sel = m["id"] in selected
            ax.plot(*p, marker="o", ms=9 * scale, mfc=BLUE if sel else "white", mec=BLUE, mew=2, zorder=8)
            texts.append(ax.text(*p, m["id"] + (" (selected)" if sel else ""), fontsize=8.5 * scale, color=BLUE,
                                 zorder=9))
        px.append(p[0])
        py.append(p[1])
    declutter(ax, texts, points=(np.array(px), np.array(py)), leader=True)
    if dropped:
        _step(ax, 2, pts[sorted(dropped)[0]], (-30, -26), GREY, scale)
        legend.append((2, GREY, "materials discarded (x): " + ", ".join(sorted(dropped))
                       + "; cut by a constraint, and ceramics are never used in tension"))
    for n_, g in enumerate(spec.guides):
        a = anchors[g.index]
        if a is None:
            continue
        sl = GUIDE_SLOPES[g.index]
        xa = pts[a["id"]][0] + (0.22 if n_ == 0 else -0.16) * span_x
        _step(ax, 3, (xa, guide_line_log(sl, pts[a["id"]], np.array([xa]))[0]), (22 + 18 * n_, -26 - 12 * n_),
              g.color, scale)
        legend.append((3, g.color, f"guide line of the merit index {g.label}, slope {sl:g}"))
    first = anchors[spec.guides[0].index]
    if first is not None:
        sl = GUIDE_SLOPES[spec.guides[0].index]
        p = pts[first["id"]]
        x1, x2 = p[0] - 0.12 * span_x, p[0] + 0.12 * span_x
        y1, y2 = (guide_line_log(sl, p, np.array([v]))[0] for v in (x1, x2))
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<|-|>", color=BLACK, lw=2.2 * scale, mutation_scale=16 * scale), zorder=11)
        _step(ax, 4, ((x1 + x2) / 2, (y1 + y2) / 2), (28, -28), BLACK, scale)
        legend.append((4, BLACK, "black double arrow: slide the ruler along the slope of the guide line"))
        xs = p[0] - 0.05 * span_x
        ys = guide_line_log(sl, p, np.array([xs]))[0]
        ax.annotate("", xy=(xs - 0.07 * span_x, ys + 0.16 * span_y), xytext=(xs, ys),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.4 * scale, mutation_scale=18 * scale), zorder=11)
        legend.append((0, GREEN, "green arrow: direction of a higher merit index (up and to the left)"))
        _step(ax, 5, p, (-34, 30), BLUE, scale)
        legend.append((5, BLUE, "guide line through the centre of the material point: selected = "
                       + ", ".join(sorted(selected))))
    return anchors, dropped, legend


def _draw_legend(artist_text, legend, s, x, y, dy, fontsize, extra_line=None):
    """Colour-coded legend lines (same colours as the arrows), from the bottom ``y`` upwards in ``dy`` steps."""
    lines = ([(None, GREY, extra_line)] if extra_line else []) \
        + [(None, GREY, f"safety factor s = {s:g}; premises: data/granta_filters.json")] + list(reversed(legend))
    for k, (n, color, text) in enumerate(lines):
        label = (f"{n}  " if n else "") + text
        artist_text(x, y + k * dy, label, color=color, fontsize=fontsize, va="bottom")


def _tick_labels(ax, xlim, ylim) -> None:
    for axis, lim in ((ax.xaxis, xlim), (ax.yaxis, ylim)):
        ticks = np.arange(np.ceil(lim[0]), np.floor(lim[1]) + 1)
        axis.set_ticks(ticks)
        axis.set_ticklabels([f"$10^{{{int(t)}}}$" for t in ticks])


def build_open(spec: ChartSpec):
    case = load_cases()
    fig, ax = plt.subplots(figsize=(8.4, 7.4), dpi=170)
    ax.set_xlim(*spec.open_xlim)
    ax.set_ylim(*spec.open_ylim)
    ax.grid(True, ls=":", color="0.7")
    ax.set_xlabel(spec.xlabel)
    ax.set_ylabel(spec.ylabel)
    _tick_labels(ax, spec.open_xlim, spec.open_ylim)
    _, _, legend = draw_overlay(ax, spec, case, spec.open_xlim, spec.open_ylim)
    fig.subplots_adjust(bottom=0.34)
    _draw_legend(fig.text, legend, case["safety_factor"], 0.02, 0.012, 0.027, 7)
    what = "density" if spec.x_prop == "density_kg_m3" else "relative cost"
    ax.set_title(f"Ashby chart: {spec.ylabel.split(' (')[0]} against {what} (representative data)", fontsize=9.5)
    return fig


def build_print(spec: ChartSpec):
    import pymupdf
    from PIL import Image

    doc = pymupdf.open(CHART_DIR / f"{spec.pdf}.pdf")
    pm = pymupdf.Pixmap(doc, doc[0].get_images(full=True)[spec.image_no][0])
    if pm.n > 3:
        pm = pymupdf.Pixmap(pymupdf.csRGB, pm)
    img = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    left, right, bottom, top = spec.calib.extent(pm.width, pm.height)
    extra = 150                                  # white strip under the chart for the legend of the numbered arrows
    low = bottom - extra / spec.calib.y_dec
    fig = plt.figure(figsize=(pm.width / 110, (pm.height + extra) / 110), dpi=110)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, extent=(left, right, bottom, top), aspect="auto", zorder=0)
    ax.set_xlim(left, right)
    ax.set_ylim(low, top)
    ax.axis("off")
    case = load_cases()
    _, _, legend = draw_overlay(ax, spec, case, (left, right), (low, top), scale=1.25, chart_bottom=bottom)
    h = pm.height + extra
    _draw_legend(lambda x, y, t, **kw: ax.text(x, y, t, transform=ax.transAxes, **kw), legend, case["safety_factor"],
                 0.01, 0.008, 19.0 / h, 9,
                 extra_line="Original chart: Ashby, Materials Selection in Mechanical Design, 4th ed. (2011), Granta MFA.")
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--open", action="store_true", help="write the publishable charts to docs/figures")
    ap.add_argument("--print", dest="prints", action="store_true", help="annotate the original course charts (private)")
    ap.add_argument("--only", nargs="*", help="chart keys")
    a = ap.parse_args()
    if not (a.open or a.prints):
        a.prints = (CHART_DIR / "mapas_ashby.pdf").exists()
        a.open = not a.prints
    for spec in CHARTS:
        if a.only and spec.key not in a.only:
            continue
        if a.open and spec.x_prop == "density_kg_m3":
            OUT_OPEN.mkdir(parents=True, exist_ok=True)
            fig = build_open(spec)
            fig.savefig(OUT_OPEN / f"ashby_{spec.key}_blank.png")
            plt.close(fig)
            print("written", OUT_OPEN / f"ashby_{spec.key}_blank.png")
        if a.prints:
            OUT_OPEN.mkdir(parents=True, exist_ok=True)
            fig = build_print(spec)
            fig.savefig(OUT_OPEN / f"ashby_{spec.key}_annotated.png")
            plt.close(fig)
            print("written", OUT_OPEN / f"ashby_{spec.key}_annotated.png")


if __name__ == "__main__":
    main()
