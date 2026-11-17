"""The README renders on GitHub: guard the math syntax and the characters that broke it before."""

from __future__ import annotations

import re
from pathlib import Path

README = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")


def _outside_fences(text: str) -> list[str]:
    lines, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            lines.append(line)
    return lines


def test_no_control_characters():
    bad = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", README)
    assert bad == []                                  # e.g. a mangled \v or \r inside a formula


def test_math_uses_github_safe_syntax():
    for line in _outside_fences(README):
        assert "$$" not in line, line[:80]            # use ```math fences
        bare = re.sub(r"\$`.+?`\$", "", line)
        assert "$" not in bare, line[:80]             # inline math must be $`...`$


def test_math_fences_are_balanced():
    fence_lines = [ln for ln in README.splitlines() if ln.lstrip().startswith("```")]
    assert sum(ln.strip() == "```math" for ln in fence_lines) >= 10
    assert len(fence_lines) % 2 == 0


def test_formulas_do_not_break_on_github():
    blocks = re.findall(r"```math\n(.*?)\n```", README, flags=re.S)
    assert blocks
    for b in blocks:
        assert "%" not in re.sub(r"\%", "", b), b[:60]    # an unescaped % starts a LaTeX comment
        assert b.count("{") == b.count("}"), b[:60]


def test_merit_indices_are_written_as_minimisation_problems():
    for token in (r"\min_{t>0}", r"\min_{A>0}", "P_1", "P_2", "P_3", r"\arg\min"):
        assert token in README, token
