"""Shared helpers for the physics figures: label de-cluttering and an automatic overlap check.

Libraries
---------
* ``adjustText`` (Flyamer, https://github.com/Phlya/adjustText): iterative repulsion of text labels from
  each other and from chosen objects, with leader lines (same idea as ``ggrepel`` in R).
* ``matplotlib.patheffects``: a white halo around each label so it stays readable over thin lines.

The automatic check (:func:`text_overlaps`) is used by ``tests/test_figures.py`` so that a future edit
cannot silently reintroduce overlapping labels.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import combinations

import matplotlib.patheffects as pe
from adjustText import adjust_text
from matplotlib.figure import Figure
from matplotlib.text import Text

HALO = [pe.withStroke(linewidth=3.0, foreground="white")]
LEADER = dict(arrowstyle="-", color="0.45", lw=0.6, shrinkA=0, shrinkB=2)


def halo(text: Text) -> Text:
    """White outline around a label (readability over lines and arrows)."""
    text.set_path_effects(HALO)
    return text


def declutter(ax, texts: Sequence[Text], avoid: Iterable | None = None, leader: bool = True,
              points: tuple | None = None, **kwargs) -> None:
    """Move ``texts`` apart (and away from ``avoid`` artists and ``points`` = (x, y) data coordinates).

    Leader lines are drawn when ``leader`` is true. Use ``points`` for markers on log axes."""
    if not texts:
        return
    for t in texts:
        halo(t)
    adjust_text(
        list(texts),
        ax=ax,
        objects=list(avoid) if avoid else None,
        x=None if points is None else points[0],
        y=None if points is None else points[1],
        arrowprops=LEADER if leader else None,
        expand=kwargs.pop("expand", (1.15, 1.35)),
        force_text=kwargs.pop("force_text", (0.25, 0.4)),
        force_static=kwargs.pop("force_static", (0.2, 0.4)),
        ensure_inside_axes=False,
        **kwargs,
    )


def _visible_texts(fig: Figure) -> list[Text]:
    hidden = set()
    for ax in fig.axes:
        if not ax.axison:                     # tick labels of axes switched off with axis("off") are not drawn
            hidden.update(ax.xaxis.get_ticklabels() + ax.yaxis.get_ticklabels())
            continue
        for axis, (lo, hi) in ((ax.xaxis, sorted(ax.get_xlim())), (ax.yaxis, sorted(ax.get_ylim()))):
            for tick in axis.get_major_ticks():   # ticks outside the view limits are kept by matplotlib, not drawn
                if not lo <= tick.get_loc() <= hi:
                    hidden.add(tick.label1)
                    hidden.add(tick.label2)
    return [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and t not in hidden]


def text_overlaps(fig: Figure, tolerance_px: float = 1.0) -> list[tuple[str, str]]:
    """Pairs of visible text objects whose bounding boxes intersect by more than ``tolerance_px``.

    Tick labels, axis titles that are empty and the axes' own bookkeeping texts are ignored.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = []
    for t in _visible_texts(fig):
        if getattr(t, "_is_tick_label", False):
            continue
        try:
            bb = t.get_window_extent(renderer)
        except Exception:  # pragma: no cover - artists without extent
            continue
        if bb.width > 0 and bb.height > 0:
            boxes.append((t.get_text(), bb))
    bad = []
    for (ta, a), (tb, b) in combinations(boxes, 2):
        w = min(a.x1, b.x1) - max(a.x0, b.x0)
        h = min(a.y1, b.y1) - max(a.y0, b.y0)
        if w > tolerance_px and h > tolerance_px:
            bad.append((ta, tb))
    return bad
