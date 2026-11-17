"""Build the English technical report (PDF) from README.md.

The README is the single source of truth. This script takes the report content
(Executive Summary, Technical Report Sections 1-6, Project Management, References), renders it
to HTML (Markdown + MathJax for the equations) and prints it to PDF with headless Microsoft Edge
or Google Chrome. The official UNICAMP deliverable stays in Portuguese
(docs/unicamp_deliverable/); this PDF is a convenience copy for English readers.

Usage (repository root):
    python docs/build_english_report.py
Output:
    docs/english_report/technical_report_en.pdf   (and a standalone .html next to it)

Requirements: markdown, pymdown-extensions (requirements.txt); Edge or Chrome installed;
internet access on first run to load MathJax from a CDN.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "english_report"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge", "google-chrome", "chromium", "chromium-browser",
]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10.2pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #1f5fa8; padding-bottom: 4px; margin-top: 26px; page-break-after: avoid; }
h2 { font-size: 15pt; margin-top: 22px; color: #1f3d6b; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin-top: 16px; page-break-after: avoid; }
h4 { font-size: 11pt; margin-top: 12px; page-break-after: avoid; }
table { border-collapse: collapse; margin: 8px 0; font-size: 9pt; width: auto; max-width: 100%; page-break-inside: avoid; }
th, td { border: 1px solid #b8c1cc; padding: 3px 7px; vertical-align: top; }
th { background: #eaf0f7; }
img { max-width: 100%; height: auto; display: block; margin: 8px auto; page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f3f4f6; padding: 0 3px; }
pre { background: #f3f4f6; padding: 8px; font-size: 8.5pt; overflow-x: auto; page-break-inside: avoid; }
blockquote { border-left: 4px solid #d35400; margin: 8px 0; padding: 2px 12px; background: #fdf3ea; }
.title { text-align: center; margin: 30px 0 18px; }
.title h1 { border: 0; font-size: 24pt; margin: 0; }
.title p { margin: 4px 0; color: #444; }
mjx-container[display="true"] { margin: 0.7em 0 !important; }
a { color: #1f5fa8; text-decoration: none; }
* { font-weight: normal !important; }   /* no bold anywhere: headings and table heads are told apart by size, colour and shading */
"""

MATHJAX = """
<script>window.MathJax = { tex: { inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] },
  svg: { fontCache: 'global' } };</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"></script>
"""


def extract_report(readme: str) -> str:
    """Executive summary ... project management + open points, then the references."""
    a = readme.index("## Executive Summary")
    b = readme.index("# Repository Structure")
    body = readme[a:b].rstrip().rstrip("-").rstrip()
    c = readme.index("## References")
    d = readme.index("## License")
    return body + "\n\n---\n\n" + readme[c:d].rstrip() + "\n"


def no_bold_math(text: str) -> str:
    """The PDF has no bold: bold math (\\mathbf, \\boldsymbol) is typeset upright instead."""
    return text.replace("\\mathbf", "\\mathrm").replace("\\boldsymbol", "")


def github_math_to_arithmatex(text: str) -> str:
    """README uses GitHub math syntax (```math fences, $`...`$ inline); convert it to $$...$$ and $...$."""
    fence = re.compile(r"```math\n(.*?)\n```", re.S)
    text = fence.sub(lambda m: "\n$$\n" + m.group(1) + "\n$$\n", text)
    return re.sub(r"\$`(.+?)`\$", lambda m: "$" + m.group(1) + "$", text)


def to_html(md_text: str) -> str:
    md_text = no_bold_math(github_math_to_arithmatex(md_text))
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "pymdownx.arithmatex"],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
    )
    body = md.convert(md_text)
    title = """<div class="title"><h1>Long-Endurance UAV Fuselage:<br>Material Selection &amp; Manufacturing Design</h1>
<p>Technical report (English) - UNICAMP FCA, ER700/EU910 - Materials Selection for Engineering</p>
<p>Prof. Dr. Jeferson Almeida Dias - Group 2, 2026/2</p>
<p><i>Convenience copy generated from README.md. The official deliverable is in Portuguese
(docs/unicamp_deliverable/).</i></p></div>"""
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Technical report (EN)</title>"
            f"<base href='{ROOT.as_uri()}/'><style>{CSS}</style>{MATHJAX}</head><body>{title}{body}</body></html>")


def find_browser() -> str | None:
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_DIR / "technical_report_en.pdf")
    ap.add_argument("--wait-ms", type=int, default=40000, help="virtual time budget for MathJax/network")
    args = ap.parse_args()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    html_text = to_html(extract_report(readme))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    html_path = args.out.with_suffix(".html")
    html_path.write_text(html_text, encoding="utf-8")

    browser = find_browser()
    if not browser:
        print(f"No Edge/Chrome found; open {html_path} in a browser and print to PDF.", file=sys.stderr)
        return 1
    cmd = [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--virtual-time-budget={args.wait_ms}", f"--print-to-pdf={args.out}", html_path.as_uri()]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    print(f"PDF written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
