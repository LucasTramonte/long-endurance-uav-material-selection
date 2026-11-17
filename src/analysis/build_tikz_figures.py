"""Compile the TikZ figures in docs/tikz/ and export them as PDF (vector) and PNG (README) in docs/figures/.

Requires a LaTeX distribution (MiKTeX or TeX Live) with TikZ and stanli; MiKTeX installs missing packages on demand.

Usage (repository root):  python -m src.analysis.build_tikz_figures [name ...]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from src.analysis.export_tables import ROOT

TIKZ_DIR = ROOT / "docs" / "tikz"
OUT_DIR = ROOT / "docs" / "figures"
MIKTEX_BIN = Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64"


def find_pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    candidate = MIKTEX_BIN / "pdflatex.exe"
    if candidate.exists():
        return str(candidate)
    raise SystemExit("pdflatex not found: install MiKTeX or TeX Live")


def build(name: str, dpi: int = 220) -> Path:
    import pymupdf

    source = TIKZ_DIR / f"{name}.tex"
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run([find_pdflatex(), "-interaction=nonstopmode", "-halt-on-error",
                                 f"-output-directory={tmp}", str(source)], capture_output=True, text=True,
                                cwd=TIKZ_DIR)
        pdf = Path(tmp) / f"{name}.pdf"
        if result.returncode != 0 or not pdf.exists():
            print(result.stdout[-2500:], file=sys.stderr)
            raise SystemExit(f"LaTeX failed for {name}")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf, OUT_DIR / f"{name}.pdf")
        png = OUT_DIR / f"{name}.png"
        with pymupdf.open(pdf) as doc:                   # closed before the temp folder is removed (Windows locks)
            doc[0].get_pixmap(dpi=dpi, alpha=False).save(png)
    return png


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="figure names (default: every .tex in docs/tikz)")
    args = ap.parse_args()
    names = args.names or [p.stem for p in sorted(TIKZ_DIR.glob("*.tex"))]
    for name in names:
        print(f"Saved {build(name)}")


if __name__ == "__main__":
    main()
