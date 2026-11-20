"""Render the project Gantt chart (PNG) and a Markdown table from data/schedule.json.

Usage (repository root):
    python -m src.analysis.gantt_chart                       # writes docs/figures/gantt.png
    python -m src.analysis.gantt_chart --table               # also prints the Markdown table
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from src.analysis.export_tables import DATA_DIR, ROOT


def load_schedule(path: Path | None = None) -> dict:
    with open(path or DATA_DIR / "schedule.json", encoding="utf-8") as fh:
        return json.load(fh)


def _d(s: str) -> date:
    return date.fromisoformat(s)


def markdown_table(sched: dict) -> str:
    lines = ["| # | Activity | Owner(s) | Start | End | Days |", "|:-:|:--|:--|:-:|:-:|:-:|"]
    for t in sched["tasks"]:
        s, e = _d(t["start"]), _d(t["end"])
        lines.append(f"| {t['id']} | {t['name']} | {t['owner']} | {s:%d/%m} | {e:%d/%m} | {(e - s).days + 1} |")
    for m in sched["milestones"]:
        lines.append(f"| M | **{m['name']}** | all | {_d(m['date']):%d/%m} | {_d(m['date']):%d/%m} | - |")
    return "\n".join(lines)


def plot_gantt(sched: dict, out: Path, lang: str = "en") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    pt = lang == "pt"
    tasks = sched["tasks"]
    name = (lambda t: t["name_pt"]) if pt else (lambda t: t["name"])
    start, end = _d(sched["start"]), _d(sched["end"]) + timedelta(days=1)
    fig, ax = plt.subplots(figsize=(11, 0.62 * (len(tasks) + len(sched['milestones'])) + 1.6))
    colours = ["#1f77b4", "#1f77b4", "#2ca02c", "#d95f02", "#d95f02"]
    n = len(tasks)
    for i, t in enumerate(tasks):
        s, e = _d(t["start"]), _d(t["end"]) + timedelta(days=1)
        y = n - i
        ax.barh(y, (e - s).days, left=mdates.date2num(s), height=0.5, color=colours[i % len(colours)], zorder=3)
        ax.text(mdates.date2num(s) + 0.15, y, f"{s:%d/%m}–{_d(t['end']):%d/%m}", va="center", ha="left",
                fontsize=8.5, color="white", zorder=4)
    ms = sched["milestones"]
    for j, m in enumerate(ms):
        y = -j
        x = mdates.date2num(_d(m["date"])) + 0.5
        ax.plot(x, y, marker="D", color="#c0392b", markersize=10, zorder=5)
        ax.text(x - 0.35, y, f"{name(m)} - {_d(m['date']):%d/%m}", ha="right", va="center", fontsize=8.5)
    ax.set_yticks(list(range(n, 0, -1)) + [-j for j in range(len(ms))])
    ax.set_yticklabels([f"{t['id']}. {name(t)}" for t in tasks] + ["Marco" if pt else "Milestone"] * len(ms), fontsize=9)
    ax.set_ylim(-len(ms) + 0.4, n + 0.7)
    ax.set_xlim(mdates.date2num(start), mdates.date2num(end))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_minor_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.tick_top()
    ax.grid(axis="x", which="major", color="#888", alpha=0.5, zorder=0)
    ax.grid(axis="x", which="minor", color="#ccc", alpha=0.4, zorder=0)
    for s_ in ("right", "bottom"):
        ax.spines[s_].set_visible(False)
    title = (sched["project_pt"] + f" — {start:%d/%m/%Y} a {_d(sched['end']):%d/%m/%Y}") if pt else (
        sched["project"] + f" — {start:%d/%m/%Y} to {_d(sched['end']):%d/%m/%Y}")
    ax.set_title(title, fontsize=11, pad=28, loc="left")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "figures" / "gantt.png")
    ap.add_argument("--table", action="store_true")
    args = ap.parse_args()
    sched = load_schedule()
    plot_gantt(sched, args.out)
    plot_gantt(sched, args.out.with_name(args.out.stem + "_pt.png"), lang="pt")      # Portuguese version for the report
    print(f"Saved {args.out} and the _pt version")
    if args.table:
        print(markdown_table(sched))


if __name__ == "__main__":
    main()
