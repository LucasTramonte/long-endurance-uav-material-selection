"""Convert the small LaTeX subset used in the report equations to native Word equations (OMML).

Word and Google Docs import OMML as editable equations, so they stay sharp at any size
(images came out cropped and blurry in Google Docs). Supported: letters, digits, Greek letters,
``_`` and ``^`` (with groups), ``\\frac``, ``\\sqrt``, ``\\sum``, ``\\min``/``\\max``, ``\\mathrm``,
spacing commands and a few relation symbols.
"""

from __future__ import annotations

import re
from xml.sax.saxutils import escape

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "varepsilon": "ε", "epsilon": "ε", "zeta": "ζ",
    "eta": "η", "theta": "θ", "lambda": "λ", "mu": "μ", "nu": "ν", "pi": "π", "rho": "ρ", "sigma": "σ",
    "tau": "τ", "phi": "φ", "varphi": "φ", "omega": "ω", "Delta": "Δ", "Omega": "Ω", "Sigma": "Σ", "Phi": "Φ",
    "Gamma": "Γ",
}
SYMBOLS = {"leq": "≤", "geq": "≥", "Rightarrow": "⇒", "cdot": "·", "in": "∈", "dots": "…", "ldots": "…",
           "times": "×", "approx": "≈", "propto": "∝", "ll": "≪", "infty": "∞", "pm": "±", "neq": "≠"}
SPACES = {",": " ", ";": " ", ":": " ", " ": " ", "quad": " ", "qquad": "  ",
          "!": ""}
OPERATORS = {"min", "max", "sin", "cos", "log", "ln", "exp"}


def _run(text: str, upright: bool = False) -> str:
    props = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
    return f'<m:r>{props}<m:t xml:space="preserve">{escape(text)}</m:t></m:r>'


class _Parser:
    def __init__(self, src: str) -> None:
        self.s = src
        self.i = 0

    # ---- low level
    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def command(self) -> str:
        """Read a control sequence after the backslash."""
        j = self.i
        if self.s[j].isalpha():
            while j < len(self.s) and self.s[j].isalpha():
                j += 1
        else:
            j += 1
        name = self.s[self.i:j]
        self.i = j
        return name

    def group(self) -> str:
        """Parse ``{...}`` (or a single token) and return its OMML content."""
        if self.peek() == "{":
            self.i += 1
            body = self.sequence(stop="}")
            self.i += 1
            return body
        if self.peek() == "\\":
            self.i += 1
            return self.command_node(self.command())
        ch = self.peek()
        self.i += 1
        return _run(ch)

    def text_group(self) -> str:
        """Content of ``\\mathrm{...}`` as upright text."""
        assert self.peek() == "{"
        self.i += 1
        out = []
        while self.peek() != "}":
            if self.peek() == "\\":
                self.i += 1
                name = self.command()
                out.append(SPACES.get(name, ""))
            else:
                out.append(self.peek())
                self.i += 1
        self.i += 1
        return "".join(out)

    # ---- nodes
    def command_node(self, name: str) -> str:
        if name in GREEK:
            return _run(GREEK[name])
        if name in SYMBOLS:
            return _run(SYMBOLS[name])
        if name in SPACES:
            return _run(SPACES[name]) if SPACES[name] else ""
        if name in OPERATORS:
            return _run(name, upright=True)
        if name == "mathrm":
            return _run(self.text_group(), upright=True)
        if name == "frac":
            num, den = self.group(), self.group()
            return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"
        if name == "sqrt":
            return f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{self.group()}</m:e></m:rad>'
        if name == "sum":
            return self.nary("∑")
        raise ValueError(f"unsupported LaTeX command: \\{name}")

    def nary(self, char: str) -> str:
        sub = sup = ""
        while self.peek() in ("_", "^"):
            kind = self.peek()
            self.i += 1
            if kind == "_":
                sub = self.group()
            else:
                sup = self.group()
        body = self.sequence(stop="=")          # the summand runs up to the next relation
        return (f'<m:nary><m:naryPr><m:chr m:val="{char}"/><m:limLoc m:val="undOvr"/></m:naryPr>'
                f"<m:sub>{sub}</m:sub><m:sup>{sup}</m:sup><m:e>{body}</m:e></m:nary>")

    def atom(self) -> str:
        ch = self.peek()
        if ch == "{":
            base = self.group()
        elif ch == "\\":
            self.i += 1
            name = self.command()
            if name == "sum":
                return self.nary("∑")
            base = self.command_node(name)
            if name in OPERATORS:
                return self.scripts(base, limits=True)
        else:
            self.i += 1
            base = _run(ch)
        return self.scripts(base)

    def scripts(self, base: str, limits: bool = False) -> str:
        sub = sup = ""
        while self.peek() in ("_", "^"):
            kind = self.peek()
            self.i += 1
            if kind == "_":
                sub = self.group()
            else:
                sup = self.group()
        if not sub and not sup:
            return base
        if limits and sub and not sup:
            return f"<m:limLow><m:e>{base}</m:e><m:lim>{sub}</m:lim></m:limLow>"
        if sub and sup:
            return f"<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>"
        if sub:
            return f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>"
        return f"<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>"

    def sequence(self, stop: str = "") -> str:
        out = []
        while self.i < len(self.s) and self.peek() != stop:
            if self.peek() == "}" and stop != "}":
                break
            if self.peek().isspace():            # LaTeX ignores plain spaces in math
                self.i += 1
                continue
            out.append(self.atom())
        return "".join(out)


def latex_to_omml(latex: str) -> str:
    """Return the ``<m:oMath>`` element (without namespace declaration) for ``latex``."""
    latex = latex.replace("arg\\,min", "arg min")
    parser = _Parser(latex.strip())
    body = parser.sequence()
    if parser.i != len(parser.s):
        raise ValueError(f"unparsed LaTeX tail: {parser.s[parser.i:]!r}")
    return f"<m:oMath>{body}</m:oMath>"


def split_lines(latex: str, budget: int = 78) -> list[str]:
    r"""Split a long equation at ``\qquad`` into lines of at most ``budget`` LaTeX characters."""
    parts = [p.strip() for p in re.split(r"\\qquad", latex) if p.strip()]
    merged: list[str] = []
    for part in parts:                           # an implication arrow stays with what follows it
        if merged and merged[-1] == r"\Rightarrow":
            merged[-1] += r"\ " + part
        else:
            merged.append(part)
    lines: list[str] = []
    for part in merged:
        if lines and len(lines[-1]) + len(part) + 8 <= budget and not part.startswith(r"\Rightarrow"):
            lines[-1] += r"\qquad " + part
        else:
            lines.append(part)
    return lines
