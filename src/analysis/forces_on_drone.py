"""3D free-body schematic of the quad-duct airframe with all force vectors drawn on the drone.

Geometry from the team's CAD (drawing sheet Y): motor axes at (+-30, +-30) mm
(pitch circle D = 84.85 mm), duct outer diameter 52.08 mm, duct height 9 mm, body about
19 x 19 mm, motor pods 21 mm long.

Formalism: repere R_G = (G; x, y, z), z upward; rotors i = 1..4 at (+,+), (-,+), (-,-), (+,-);
spin sign eps_i = +1 (counter-clockwise seen from +z) / -1. Vectors:
  T_i  thrust (green)          Q_i  aerodynamic reaction torque on the airframe (orange)
  P    weight at G (grey)      F_c  blade centrifugal force (red)
  F_u  unbalance force rotating in the plane of the rotor (purple)

Usage (repository root):  python -m src.analysis.forces_on_drone
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.analysis.export_tables import ROOT
from src.analysis.figure_utils import declutter

GREEN, GREY, ORANGE, RED, PURPLE, BLUE = "#1e8449", "#444444", "#d35400", "#c0392b", "#7d3c98", "#1f5fa8"
A = 30.0          # mm, motor offset on x and y
R_DUCT = 26.04    # mm, duct outer radius
H_DUCT = 9.0      # mm
ROTORS = [(+A, +A, +1), (-A, +A, -1), (-A, -A, +1), (+A, -A, -1)]  # (x, y, eps)


def circle(cx, cy, z, r, n=120):
    t = np.linspace(0, 2 * np.pi, n)
    return cx + r * np.cos(t), cy + r * np.sin(t), np.full_like(t, z)


def vec(ax, p, d, color, lw=2.4, ratio=0.22):
    ax.quiver(*p, *d, color=color, linewidth=lw, arrow_length_ratio=ratio, normalize=False)


def draw_airframe(ax):
    # body
    for z in (0, H_DUCT * 0.5):
        xs = np.array([-9.5, 9.5, 9.5, -9.5, -9.5])
        ys = np.array([-9.5, -9.5, 9.5, 9.5, -9.5])
        ax.plot(xs, ys, z, color="#7f8c8d", lw=1.2)
    for x, y in [(-9.5, -9.5), (9.5, -9.5), (9.5, 9.5), (-9.5, 9.5)]:
        ax.plot([x, x], [y, y], [0, H_DUCT * 0.5], color="#7f8c8d", lw=1.2)
    for x, y, _ in ROTORS:
        for z in (0, H_DUCT):
            ax.plot(*circle(x, y, z, R_DUCT), color="#2c3e50", lw=1.2)
        for th in (90, 210, 330):                      # three spokes
            c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
            ax.plot([x, x + 24 * c], [y, y + 24 * s], [H_DUCT * 0.5] * 2, color="#95a5a6", lw=1.0)
        ax.plot([x, x], [y, y], [-21, H_DUCT * 0.5], color="#34495e", lw=5, solid_capstyle="round")  # motor pod
        # arm to the body
        ax.plot([x * 0.32, x * 0.78], [y * 0.32, y * 0.78], [H_DUCT * 0.5] * 2, color="#95a5a6", lw=2.0)


LABELS: list[tuple] = []   # (xyz anchor, text, colour, (dx, dy) initial offset in px, fontsize)


def label(xyz, text, color, offset=(0, 14), size=13):
    LABELS.append((xyz, text, color, offset, size))


TEXT = {
    "en": {"each": "(each blade)", "thrust": "thrust", "torque": "reaction torque", "weight": "weight", "at": "at",
           "cf": "centrifugal force", "per": "(per blade)", "unb": "unbalance",
           "title": r"Free-body diagram of the airframe, frame $\mathcal{R}_G=(G;\vec{x},\vec{y},\vec{z})$, hover",
           "sub": "CAD dimensions: motor axes at (±30, ±30) mm; duct Ø52.08 x 9 mm; motor pods 21 mm. "
                  r"$\vec{F}_c$ and $\vec{F}_u$ are drawn on rotor 1 only."},
    "pt": {"each": "(cada pá)", "thrust": "empuxo", "torque": "torque de reação", "weight": "peso", "at": "em",
           "cf": "força centrífuga", "per": "(por pá)", "unb": "desbalanceamento",
           "title": r"Diagrama de corpo livre da estrutura, referencial $\mathcal{R}_G=(G;\vec{x},\vec{y},\vec{z})$, voo pairado",
           "sub": "Dimensões do CAD: eixos dos motores em (±30, ±30) mm; duto Ø52,08 × 9 mm; nacelas de 21 mm. "
                  r"$\vec{F}_c$ e $\vec{F}_u$ são desenhadas apenas no rotor 1."},
}


def build_figure(lang: str = "en"):
    """Draw the airframe + vectors, then place every label on a 2D overlay with adjustText."""
    from matplotlib.lines import Line2D
    from mpl_toolkits.mplot3d import proj3d

    LABELS.clear()
    tx = TEXT[lang]
    fig = plt.figure(figsize=(12.5, 8.8))
    ax = fig.add_axes([0.0, 0.07, 1.0, 0.88], projection="3d")
    draw_airframe(ax)

    zr = H_DUCT * 0.5
    for i, (x, y, eps) in enumerate(ROTORS, 1):
        for sgn in (-1, 1):                                   # two blades in the duct mid-plane
            ax.plot([x, x + sgn * 22], [y, y], [zr + 2] * 2, color=BLUE, lw=2.6)
        vec(ax, (x, y, zr + 2), (0, 0, 30), GREEN, 3.0)       # thrust T_i
        label((x, y, zr + 32), rf"$\vec{{T}}_{i}$", GREEN, (30 if i == 4 else 0, 4 if i == 4 else 16))
        # reaction torque Q_i: arc in a plane below the duct, sense = -eps (reaction on the airframe)
        th = np.linspace(np.radians(35), np.radians(305), 60)
        if -eps < 0:
            th = th[::-1]
        r_arc = 10.5
        ax.plot(x + r_arc * np.cos(th), y + r_arc * np.sin(th), np.full_like(th, -8), color=ORANGE, lw=2.4)
        d = np.array([r_arc * (np.cos(th[-1]) - np.cos(th[-4])), r_arc * (np.sin(th[-1]) - np.sin(th[-4])), 0])
        vec(ax, (x + r_arc * np.cos(th[-4]), y + r_arc * np.sin(th[-4]), -8), tuple(d * 1.6), ORANGE, 2.4, 0.9)
        label((x + r_arc, y, -8), rf"$\vec{{Q}}_{i}$", ORANGE, ((66 if x > 0 else 96) * np.sign(x), -6), 13)
        label((x, y, -21), rf"$M_{i}$", "#2c3e50", 30.0, 11)
        # spin sense of the rotor, written next to the blade tip
        label((x, y + 22 * np.sign(y), zr + 2), r"$\circlearrowleft$" if eps > 0 else r"$\circlearrowright$",
              BLUE, 26.0, 16)

    # detailed vectors of rotor 1 only (the three others are identical): centrifugal force and unbalance
    x1, y1, _ = ROTORS[0]
    for sgn in (-1, 1):
        vec(ax, (x1 + sgn * 11, y1, zr + 2), (sgn * 11, 0, 0), RED, 1.8, 0.35)
    label((x1 + 22, y1, zr + 2), rf"$\vec{{F}}_c$ {tx['each']}", RED, (70, 40), 12)
    vec(ax, (x1, y1, zr - 3.5), (0, 12, 0), PURPLE, 1.6, 0.4)
    label((x1, y1 + 12, zr - 3.5), r"$\vec{F}_u(t)$", PURPLE, (-30, 58), 12)

    # weight at G and frame
    vec(ax, (0, 0, zr), (0, 0, -26), GREY, 3.2)
    label((0, 0, zr - 26), r"$\vec{P}$", GREY, (-14, -14), 14)
    ax.plot([0], [0], [zr], "ko", ms=7)
    label((0, 0, zr), "G", "k", (-16, 10), 13)
    for d_, lab in (((22, 0, 0), r"$\vec{x}$"), ((0, 22, 0), r"$\vec{y}$"), ((0, 0, 22), r"$\vec{z}$")):
        vec(ax, (0, 0, zr), d_, "k", 1.4, 0.25)
        label((d_[0], d_[1], d_[2] + zr), lab, "k", (8, 8), 13)

    ax.set_xlim(-60, 60)
    ax.set_ylim(-60, 60)
    ax.set_zlim(-30, 45)
    ax.set_box_aspect((1, 1, 0.62), zoom=1.28)
    ax.view_init(elev=24, azim=-58)
    ax.set_axis_off()

    # ---- 2D overlay: anchors projected to pixels, labels repelled with adjustText -------------------------
    fig.canvas.draw()
    W, H = fig.canvas.get_width_height()
    ov = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ov.set_xlim(0, W)
    ov.set_ylim(0, H)
    ov.axis("off")
    proj = ax.get_proj()
    texts, anchors = [], []
    gx, gy, _ = proj3d.proj_transform(0, 0, H_DUCT * 0.5, proj)
    g_px = np.array(ax.transData.transform((gx, gy)))
    for xyz, txt, col, off, size in LABELS:
        x2, y2, _ = proj3d.proj_transform(*xyz, proj)
        px, py = ax.transData.transform((x2, y2))
        if isinstance(off, float):                      # radial push away from G on the screen
            v = np.array([px, py]) - g_px
            dx, dy = off * v / (np.linalg.norm(v) + 1e-9)
        else:
            dx, dy = off
        anchors.append(ov.plot(px, py, ".", color=col, ms=2, alpha=0.0)[0])
        texts.append(ov.text(px + dx, py + dy, txt, color=col, fontsize=size, ha="center", va="center"))
    declutter(ov, texts, avoid=anchors, leader=False)

    fig.legend(handles=[
        Line2D([0], [0], color=GREEN, lw=3, label=rf"{tx['thrust']} $\vec{{T}}_i=k_T\,\omega_i^{{2}}\,\vec{{z}}$"),
        Line2D([0], [0], color=ORANGE, lw=3, label=rf"{tx['torque']} $\vec{{Q}}_i=-\varepsilon_i\,k_Q\,\omega_i^{{2}}\,\vec{{z}}$"),
        Line2D([0], [0], color=GREY, lw=3, label=rf"{tx['weight']} $\vec{{P}}=-mg\,\vec{{z}}$ {tx['at']} $G$"),
        Line2D([0], [0], color=RED, lw=3, label=rf"{tx['cf']} $\vec{{F}}_c=m_p\,\omega^{{2}}\,r_G\,\vec{{e}}_r$ {tx['per']}"),
        Line2D([0], [0], color=PURPLE, lw=3, label=rf"{tx['unb']} $\vec{{F}}_u(t)=m_u\,e\,\omega^{{2}}\,\vec{{e}}_r(\omega t)$"),
    ], loc="lower center", ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, 0.975, tx["title"], ha="center", fontsize=12)
    fig.text(0.5, 0.945, tx["sub"], ha="center", fontsize=8.5, color="#555")
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "figures" / "forces_on_drone.png")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for lang, out in (("en", args.out), ("pt", args.out.with_name(args.out.stem + "_pt.png"))):
        build_figure(lang).savefig(out, dpi=170, facecolor="white")
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
