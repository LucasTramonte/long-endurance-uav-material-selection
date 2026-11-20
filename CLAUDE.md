# CLAUDE.md

Instructions for AI agents working in this repository. Humans: the README is the entry point.

## What this project is

Long-endurance UAV fuselage (ducted quadcopter) material selection for UNICAMP ER700/EU910: Python models
(`src/`), tests (`tests/`), an English technical report (README, built to PDF) and the **official deliverable in
Portuguese** (`docs/unicamp_deliverable/`, .docx + .pdf). README, code and commit messages are English.

## Commands

| Task | Command |
| --- | --- |
| Tests | `python -m pytest` |
| Lint | `ruff check src tests` |
| Redraw physics figures | `python -m src.analysis.forces_on_drone`; TikZ figures (`docs/tikz/`): `python -m src.analysis.build_tikz_figures` (MiKTeX installed with winget; stanli and tikz-3dplot cannot be loaded together) |
| English report PDF | `python docs/build_english_report.py` (Edge/Chrome, internet for MathJax) |
| Portuguese .docx + .pdf | `python docs/unicamp_deliverable/build_docx_report.py` (Word or LibreOffice) |

## Rules that come from real mistakes

| Mistake | Rule | Guard |
| --- | --- | --- |
| Inline Python in the shell turned `\v` into a control character (`\vec` became `ec`) and `\rho` into CR + `ho` | Write scripts with the Write tool, or use raw strings in files; never put LaTeX in a shell heredoc | `tests/test_readme.py` (no control characters) |
| README math written as `$$...$$` / bare `$...$` is fragile on GitHub | Display math in ```math fences, inline as `` $`...`$ ``; use `\lbrace` if a brace is lost | `tests/test_readme.py` |
| Labels and vectors overlapped in the force figures and were only noticed by eye | Place labels with `adjustText` (`src/analysis/figure_utils.py`); look at the PNG | `tests/test_figures.py` |
| README formulas drifted from the code | Derive indices symbolically (SymPy) and compare with the numeric functions | `tests/test_symbolic.py` |
| Backslash inside an f-string expression is valid on 3.12, a SyntaxError on 3.10/3.11 | Build the string first, then interpolate | `tests/test_python_compatibility.py` |
| A figure showed forces but nothing proved the equations were solved correctly | Add analytic-vs-numeric, convergence and energy-error panels (`verification_figure.py`) with a test per number | `tests/test_verification.py` |
| Material chosen without the chart procedure, or a safety factor picked to make a material pass | Follow `.claude/skills/ashby-chart-selection` and `.claude/skills/safety-factor-selection`: constraint line, discard cut bubbles, guide line, ceramics never in tension, `s` from cited literature | `tests/test_ashby.py` |
| Static strength used for a cyclic load, or merit indices that do not describe the drone (flywheel, extra premises) | Follow `.claude/skills/fatigue-assessment` (and `rotating-parts-merit-indices` for spinning parts); keep IM1 = E/rho (tube, fixed radius), IM2, IM3 as reviewed by the course monitor; cost and selection text follow `cost-merit-indices` and `selection-method-and-decision-matrix` | `tests/test_rotating_fatigue.py`, `tests/test_symbolic.py` |
| Claimed numbers or sources that were not checked | Cite only what was read; say what could not be verified | review |

## Privacy and redistribution

Everything in `assets/` except its README is git-ignored (slides, brief, drafts with student RA numbers, benchmark thesis). Never `git add -f` them and never link to them from published documents; cite instead. Exception decided by the team: the
annotated Ashby charts in `docs/figures/ashby_*_annotated.png` are published (source credited in the image); the source PDFs in
`assets/ashby_charts/` stay git-ignored. Material data in `data/materials_db.json` are representative placeholders until replaced by
Granta/MatWeb exports.

Skills in `.claude/skills/` are never deleted because the current report does not use them: they are the team's reusable method.

## Do not commit or push unless the user asks.
