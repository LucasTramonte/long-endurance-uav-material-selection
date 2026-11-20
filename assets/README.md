# assets/

Source material that is **inputs** to the project (not generated). Generated figures live in `docs/figures/` and `cad/figures/`.

**Everything in this folder except this file is git-ignored** (private, personal data or third-party copyright). The files stay on the authors' machines; the repository only cites them. To work with the project you do not need them: the numbers used from them are transcribed in `data/` and cited in the README.

| Folder | Content | Why it is not published | Where to get it |
|---|---|---|---|
| `brief/` | `projeto_selemat_2026-2.pdf` - professor's project brief (reference [14]) | course material | from the course (UNICAMP FCA, ER700/EU910) |
| `ashby_charts/` | `mapas_ashby.pdf`, `diagrama_custo.pdf` - the original Ashby property and cost charts | excerpts of a published book (reference [1]); no longer used for the figures, which are the Granta prints | Ashby, *Materials Selection in Mechanical Design* |
| `drafts/` | `relatorio_equipe_rascunho.docx` - team working draft (Portuguese) | lists student registration numbers (RA) | team members |
| `benchmark/` | `niero_jp_tcc_sjbv.PDF` - UNESP thesis (Niero, 2024), reference [20] | third-party thesis; redistribution terms of the institutional repository not verified | UNESP institutional repository (search the title in the reference) |
| `*.pdf` (top level) | course exercise solution and lecture notes used as models for figure and report style | course / third-party material | from the course |
| `courses/` | `Aula_*.pdf` - lecture slides, Prof. Dr. Jeferson A. Dias (reference [13]) | private course material | from the course |

## Notes

- Cite course material as "internal course material" (reference [13]); never link to it.
- The tables transcribed from the benchmark thesis are in `data/benchmark_niero2024.json` (published numerical values, cited); the comparison is in [`docs/benchmark.md`](../docs/benchmark.md). The tests do not need the PDF.
- Images used in the report were extracted from the draft into `cad/figures/` and `docs/figures/`; edit those copies, not the docx.
- If a file is needed in a public version, replace it with your own Granta screenshot, or obtain written permission first.
