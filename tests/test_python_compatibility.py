"""The CI runs Python 3.10-3.13; a backslash inside an f-string expression is only valid from 3.12."""

from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [p for d in ("src", "tests", "docs") for p in (ROOT / d).rglob("*.py")]


def test_sources_parse_with_the_oldest_supported_grammar():
    for path in SOURCES:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 10))


def test_no_backslash_in_fstring_expressions():
    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        text = path.read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if isinstance(node, ast.FormattedValue):
                segment = ast.get_source_segment(text, node.value) or ""
                assert "\\" not in segment, f"{path.name}:{node.lineno}: {segment}"
    assert tokenize and io  # imported for readability of failures
