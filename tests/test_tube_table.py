"""Reference tube of README Section 3.2."""

import pytest

from src.analysis.export_tables import load_materials, tube_table


def test_tube_table_reproduces_the_readme_values():
    rows = {r["Material"]: r for r in tube_table(load_materials(shortlist_only=True)).to_dict("records")}
    assert rows["AL_ALLOYS"]["Wall (mm)"] == pytest.approx(1.0)               # the reference wall
    assert rows["AL_ALLOYS"]["Mass (g)"] == pytest.approx(9.2, abs=0.05)
    assert rows["CFRP_QI"]["Mass (g)"] == pytest.approx(3.7, abs=0.05)
    assert rows["CFRP_QI"]["Wall (mm)"] == pytest.approx(0.71, abs=0.005)
    # a wall thicker than the 18 mm radius is a formal value
    assert "radius" in rows["PC"]["Wall (mm)"]
