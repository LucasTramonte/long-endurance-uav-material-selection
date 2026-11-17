# Contributing

1. Branch from `main`; keep changes focused.
2. Write or update tests first (`tests/`); numerical claims need a test or a cited source.
3. Run the checks before opening a pull request:

   ```bash
   ruff check src tests
   python -m pytest
   ```
4. Regenerate derived files when their inputs change: `python -m src.analysis.forces_on_drone`,
   `python -m src.analysis.build_tikz_figures` (needs LaTeX), `python docs/build_english_report.py`,
   `python docs/unicamp_deliverable/build_docx_report.py`.
5. Look at every figure and PDF page you changed. Label overlap is also checked automatically
   (`tests/test_figures.py`).

## Conventions

- **Language:** README, code, comments and commit messages in English; the official deliverable
  (`docs/unicamp_deliverable/`) in Portuguese.
- **Equations in the README:** GitHub math syntax only - display math in ```` ```math ```` fences, inline math as
  `` $`...`$ ``; never `$$` or bare `$...$` (guarded by `tests/test_readme.py`). Merit indices are written as
  minimisation problems (README Section 2); SymPy checks them (`src/math_modeling/symbolic_derivations.py`).
- **Units:** keep them explicit in names and docstrings (GPa, MPa, kg/m^3, USD/kg).
- **Figures:** drawn at near-final size; labels placed with `adjustText` through `src/analysis/figure_utils.py`.
- **Physics figures** (rules from Rougier et al. [25] and from the course notes on numerical orbits and the two-mass
  exercise): (1) draw a labelled schematic first, then the equations, then the numerical scheme; (2) plot analytic and
  numerical results on the same axes; (3) show the error against the step size with its order of accuracy, and the
  energy (or another invariant) error for several steps; (4) compare with a literature value and give the relative
  error; (5) write the parameters and assumptions inside the plot; (6) keep equal axis scales for geometry and say
  so; (7) label axes with units, label curves directly or with a legend, and use the colour-blind-safe Okabe-Ito
  palette; (8) every figure has a caption that explains how to read it; (9) a figure that shows a result has a test
  behind the number (`tests/test_verification.py`).
- **References:** every claim, formula or dataset is cited with the numbered list in the README.
- **Python:** 3.10 or newer; no backslash inside f-string expressions (invalid before 3.12).
