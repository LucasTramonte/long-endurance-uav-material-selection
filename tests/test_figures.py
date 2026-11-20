"""Figures must not have overlapping labels (checked with real text extents, not by eye)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from src.analysis import forces_on_drone, verification_figure
from src.analysis.figure_utils import text_overlaps

BUILDERS = [forces_on_drone.build_figure, verification_figure.build_figure]


@pytest.mark.parametrize("build", BUILDERS)
def test_no_overlapping_labels(build):
    fig = build()
    try:
        assert text_overlaps(fig) == []
    finally:
        plt.close(fig)


def test_overlap_checker_detects_a_collision():
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "alpha")
    ax.text(0.5, 0.5, "beta")
    assert text_overlaps(fig) == [("alpha", "beta")]
    plt.close(fig)
