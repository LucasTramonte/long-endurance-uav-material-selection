"""The TikZ figures in docs/tikz must compile (skipped when no LaTeX distribution is installed)."""

from __future__ import annotations

import shutil

import pytest

from src.analysis import build_tikz_figures as bt

HAS_LATEX = shutil.which("pdflatex") is not None or (bt.MIKTEX_BIN / "pdflatex.exe").exists()


@pytest.mark.skipif(not HAS_LATEX, reason="no LaTeX distribution installed")
def test_load_paths_figure_compiles(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "OUT_DIR", tmp_path)
    png = bt.build("load_paths", dpi=60)
    assert png.exists() and png.stat().st_size > 5_000
    assert (tmp_path / "load_paths.pdf").exists()
