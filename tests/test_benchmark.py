"""Cross-validation of the merit-index code against the benchmark thesis (Niero, 2024).

The thesis (assets/benchmark/niero_jp_tcc_sjbv.PDF) tabulates E, rho and the indices
IM_L = E^(1/2)/rho (spar, beam in bending) and IM_N = E^(1/3)/rho (rib, plate in bending)
for 19 materials. Our IM1 (E^(1/3)/rho) must reproduce IM_N, and bending_beam_index must
reproduce IM_L, to within the rounding of the published tables.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.math_modeling.merit_indices import bending_beam_index, bending_panel_index  # noqa: E402

with open(ROOT / "data" / "benchmark_niero2024.json", encoding="utf-8") as fh:
    BENCH = json.load(fh)["materials"]


@pytest.mark.parametrize("m", BENCH, ids=[m["name"] for m in BENCH])
def test_plate_index_matches_thesis(m):
    ours = float(bending_panel_index(m["E"], m["rho"] * 1000.0))
    assert ours == pytest.approx(m["IM_N"], rel=0.005)


@pytest.mark.parametrize("m", BENCH, ids=[m["name"] for m in BENCH])
def test_beam_index_matches_thesis(m):
    ours = float(bending_beam_index(m["E"], m["rho"] * 1000.0))
    assert ours == pytest.approx(m["IM_L"], rel=0.005)


def test_benchmark_qualitative_conclusions():
    """Thesis conclusion: carbon/epoxy has the highest index, steels and cast iron the lowest."""
    ranked = sorted(BENCH, key=lambda m: bending_panel_index(m["E"], m["rho"] * 1000.0), reverse=True)
    assert ranked[0]["name"].startswith("Carbon epoxy")
    assert all(m["name"].split()[0] in {"ASTM", "AISI", "304"} for m in ranked[-4:])
