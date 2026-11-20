"""Report equations are native Word equations (OMML), not images."""

import re
import sys
import zipfile
from pathlib import Path
from xml.dom import minidom

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docs" / "unicamp_deliverable"))

from latex_to_omml import M_NS, latex_to_omml, split_lines  # noqa: E402

TEMPLATE = ROOT / "docs" / "unicamp_deliverable" / "relatorio_pt_template.md"


def _equations() -> list[str]:
    blocks = re.findall(r"^\$\$\n(.*?)\n\$\$$", TEMPLATE.read_text(encoding="utf-8"), re.S | re.M)
    return [" ".join(b.split("\n")) for b in blocks]


def test_every_report_equation_converts_to_wellformed_omml():
    eqs = _equations()
    assert len(eqs) >= 10
    for eq in eqs:
        for line in split_lines(eq):
            xml = latex_to_omml(line)
            minidom.parseString(f'<root xmlns:m="{M_NS}">{xml}</root>')
            assert "\\" not in re.sub(r"<[^>]+>", "", xml)           # no unconverted LaTeX command


def test_fraction_and_scripts_use_native_structures():
    xml = latex_to_omml(r"m^{*}=\frac{S_{\mathrm{req}}\,L^{4}}{24\,R^{2}}")
    for tag in ("<m:f>", "<m:sSub>", "<m:sSup>"):
        assert tag in xml


def test_built_docx_has_no_equation_images():
    docx = ROOT / "docs" / "unicamp_deliverable" / "relatorio_final.docx"
    if not docx.exists():
        return
    with zipfile.ZipFile(docx) as z:
        document = z.read("word/document.xml").decode("utf-8")
        assert document.count("<m:oMathPara") >= len(_equations())
        assert not [n for n in z.namelist() if n.startswith("word/media/") and "eq" in Path(n).stem.lower()]
