"""Compile the Portuguese Markdown draft into an ABNT-style .docx (UNICAMP deliverable).

Usage (from repository root):
    python docs/unicamp_deliverable/build_docx_report.py            # writes .docx and .pdf
    python docs/unicamp_deliverable/build_docx_report.py -i docs/unicamp_deliverable/relatorio_pt_template.md \
        -o docs/unicamp_deliverable/relatorio_final.docx   # also writes relatorio_final.pdf

Supported Markdown subset: YAML-like front matter (--- ... ---) for the cover page,
# / ## / ### headings (numbered by the author), paragraphs, **bold**, *italic*, `code`,
-/* bullets, 1. numbered lists, pipe tables, ![caption](path) images, > block quotes
(rendered as ABNT long quotation), and the line "\\pagebreak".

ABNT NBR 14724 formatting applied: A4; margins 3 cm (top/left) and 2 cm (bottom/right);
Times New Roman 12 pt; 1.5 line spacing; justified text with 1.25 cm first-line indent;
page numbers at top right from the first text page; long quotations and captions at
10 pt with single spacing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from latex_to_omml import M_NS, latex_to_omml, split_lines  # noqa: E402

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FONT = "Times New Roman"
INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


# ----------------------------------------------------------------------------- helpers
def set_font(run, size: float = 12, bold=None, italic=None, name: str = FONT) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


SCRIPT = re.compile(r"([_^])\{([^}]*)\}")


def emit(par, text: str, size: float, bold=None, italic=None, name: str = FONT) -> None:
    """Add ``text`` to ``par``; ``x_{abc}`` becomes a subscript and ``x^{abc}`` a superscript."""
    pos = 0
    for m in SCRIPT.finditer(text):
        if m.start() > pos:
            set_font(par.add_run(text[pos:m.start()]), size, bold=bold, italic=italic, name=name)
        run = par.add_run(m.group(2))
        set_font(run, size, bold=bold, italic=False if italic else italic, name=name)
        if m.group(1) == "_":
            run.font.subscript = True
        else:
            run.font.superscript = True
        pos = m.end()
    if pos < len(text):
        set_font(par.add_run(text[pos:]), size, bold=bold, italic=italic, name=name)


def add_runs(par, text: str, size: float = 12) -> None:
    """Add text to a paragraph, honouring **bold**, *italic* and `code` spans and sub/superscripts."""
    for chunk in INLINE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            emit(par, chunk[2:-2], size, bold=True)
        elif chunk.startswith("`") and chunk.endswith("`"):
            set_font(par.add_run(chunk[1:-1]), size - 1, name="Courier New")
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            emit(par, chunk[1:-1], size, italic=True)
        else:
            emit(par, chunk, size)


def fmt(par, align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.5, indent_first=True, left=0.0,
        before=0, after=0) -> None:
    pf = par.paragraph_format
    par.alignment = align
    pf.line_spacing = spacing
    pf.first_line_indent = Cm(1.25) if indent_first else Cm(0)
    pf.left_indent = Cm(left)
    pf.space_before, pf.space_after = Pt(before), Pt(after)


def add_page_number_field(par) -> None:
    run = par.add_run()
    set_font(run, 10)
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def set_cell_borders(table) -> None:
    """Open table style (ABNT/IBGE): horizontal rules only."""
    tbl = table._tbl
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tbl.tblPr.append(borders)


# ----------------------------------------------------------------------------- document setup
def setup_document() -> Document:
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin, sec.left_margin = Cm(3.0), Cm(3.0)
    sec.bottom_margin, sec.right_margin = Cm(2.0), Cm(2.0)
    sec.header_distance = Cm(1.25)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    for name, size in (("Heading 1", 12), ("Heading 2", 12), ("Heading 3", 12)):
        st = doc.styles[name]
        st.font.name, st.font.size, st.font.color.rgb = FONT, Pt(size), None
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        st.font.bold = name != "Heading 3"
        st.font.italic = name == "Heading 3"
    return doc


def parse_front_matter(lines: list[str]) -> tuple[dict, list[str]]:
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                meta = {}
                for ln in lines[1:i]:
                    if ":" in ln:
                        k, v = ln.split(":", 1)
                        meta[k.strip()] = v.strip().strip('"')
                return meta, lines[i + 1:]
    return {}, lines


def add_cover(doc: Document, meta: dict) -> None:
    def centered(text, size=12, bold=False, before=0, after=0):
        p = doc.add_paragraph()
        fmt(p, WD_ALIGN_PARAGRAPH.CENTER, 1.5, False, before=before, after=after)
        set_font(p.add_run(text), size, bold=bold)

    centered(meta.get("instituicao", "UNIVERSIDADE ESTADUAL DE CAMPINAS").upper(), bold=True)
    centered(meta.get("unidade", "Faculdade de Engenharia Mecânica").upper(), bold=True)
    centered(meta.get("disciplina", "ER700/EU910 – Seleção de Materiais para Engenharia"))
    centered(meta.get("professor", "Prof. Dr. Jeferson Almeida Dias"), after=60)
    for member in [m.strip() for m in meta.get("autores", "").split(";") if m.strip()]:
        centered(member.upper())
    centered(meta.get("titulo", "TÍTULO DO TRABALHO").upper(), size=14, bold=True, before=110, after=6)
    if meta.get("subtitulo"):
        centered(meta["subtitulo"], size=12, after=6)
    centered(meta.get("local", "Campinas"), before=150)
    centered(meta.get("ano", ""))
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ----------------------------------------------------------------------------- blocks
def add_table(doc: Document, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_cell_borders(table)
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            cell = table.cell(r, c)
            par = cell.paragraphs[0]
            fmt(par, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False)
            add_runs(par, f"**{text}**" if r == 0 and not text.startswith("**") else text, size=10)
    doc.add_paragraph()


def image_width_cm(path: Path, src: str) -> float:
    """Text width is 16 cm: Ashby charts and wide screenshots use it all, tall panels are narrower."""
    with Image.open(path) as im:
        w, h = im.size
    if "ashby" in src or w > 1000:
        return 16.0
    return 9.0 if h > 400 else 13.0


def add_image(doc: Document, alt: str, src: str, base: Path) -> None:
    path = (base / src).resolve()
    p = doc.add_paragraph()
    fmt(p, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False, before=6)
    if path.exists():
        p.add_run().add_picture(str(path), width=Cm(image_width_cm(path, src)))
    else:
        set_font(p.add_run(f"[Figura não encontrada: {src}]"), 10, italic=True)
    cap = doc.add_paragraph()
    fmt(cap, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False, after=10)
    add_runs(cap, alt, size=10)


def add_image_row(doc: Document, items: list[tuple[str, str]], base: Path) -> None:
    """Several figures side by side (one table row, no borders), each with its caption below."""
    n = len(items)
    table = doc.add_table(rows=1, cols=n)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_cm = 16.0 / n
    for cell, (alt, src) in zip(table.rows[0].cells, items, strict=True):
        cell.width = Cm(col_cm)
        path = (base / src).resolve()
        p = cell.paragraphs[0]
        fmt(p, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False, before=4)
        if path.exists():
            p.add_run().add_picture(str(path), width=Cm(col_cm - 0.4))
        else:
            set_font(p.add_run(f"[Figura não encontrada: {src}]"), 10, italic=True)
        cap = cell.add_paragraph()
        fmt(cap, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False, after=6)
        add_runs(cap, alt, size=9)
    doc.add_paragraph()


def add_equation(doc: Document, latex: str, number: int) -> None:
    r"""Native Word equation (OMML) centred, number in parentheses at the right margin (ABNT NBR 14724).

    Long equations are split at ``\qquad`` into several centred lines so they never overflow the text width.
    """
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = (Cm(0.5), Cm(14.0), Cm(1.5))
    for cell, w in zip(table.rows[0].cells, widths, strict=True):
        cell.width = w
    mid = table.cell(0, 1)
    for k, line in enumerate(split_lines(latex)):
        par = mid.paragraphs[0] if k == 0 else mid.add_paragraph()
        fmt(par, WD_ALIGN_PARAGRAPH.CENTER, 1.0, False, before=4, after=4)
        par._p.append(parse_xml(f'<m:oMathPara xmlns:m="{M_NS}" xmlns:w="{W_NS}">{latex_to_omml(line)}</m:oMathPara>'))
    num = table.cell(0, 2).paragraphs[0]
    fmt(num, WD_ALIGN_PARAGRAPH.RIGHT, 1.0, False, before=10)
    set_font(num.add_run(f"({number})"), 12)


def build(md_text: str, out_path: Path, base: Path) -> None:
    doc = setup_document()
    meta, lines = parse_front_matter(md_text.splitlines())
    if meta:
        add_cover(doc, meta)

    # page numbers: top right, 10 pt
    header = doc.sections[0].header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_page_number_field(header)

    eq_count = 0
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            i += 1
        elif s == "$$":                                  # display equation block
            i += 1
            block = []
            while lines[i].strip() != "$$":
                block.append(lines[i].strip())
                i += 1
            i += 1
            eq_count += 1
            add_equation(doc, " ".join(block), eq_count)
        elif s == r"\pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            i += 1
        elif s.startswith("<!--"):                       # skip HTML comments (authoring notes)
            while "-->" not in lines[i]:
                i += 1
            i += 1
        elif re.match(r"^#{1,3}\s", s):
            level = len(s) - len(s.lstrip("#"))
            text = s[level:].strip()
            h = doc.add_heading(level=level)
            text = text.upper() if level == 1 else text
            set_font(h.add_run(text), 12, bold=level != 3, italic=level == 3)
            fmt(h, WD_ALIGN_PARAGRAPH.LEFT, 1.5, False, before=12, after=6)
            h.paragraph_format.keep_with_next = True
            i += 1
        elif s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [[c.strip() for c in r.strip("|").split("|")] for r in block
                    if not re.match(r"^\|[\s:\-|]+\|$", r)]
            add_table(doc, rows)
        elif s.startswith("![") and len(re.findall(r"!\[(.*?)\]\((.*?)\)", s)) > 1:        # figures side by side
            add_image_row(doc, [(m_[0], m_[1]) for m_ in re.findall(r"!\[(.*?)\]\((.*?)\)", s)], base)
            i += 1
        elif (m := re.match(r"^!\[(.*?)\]\((.*?)\)", s)):
            add_image(doc, m.group(1), m.group(2), base)
            i += 1
        elif s.startswith(">"):
            p = doc.add_paragraph()
            fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.0, False, left=4.0, before=6, after=6)
            add_runs(p, s.lstrip("> ").strip(), size=10)
            i += 1
        elif re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            numbered = bool(re.match(r"^\d+\.\s+", s))
            n = 0
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                n += 1
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                p = doc.add_paragraph()
                fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, False, left=1.9)
                p.paragraph_format.first_line_indent = Cm(-0.65)
                add_runs(p, (f"{n}. " if numbered else "– ") + item)
                i += 1
        else:
            para = [s]
            i += 1
            block_start = r"^(#{1,3}\s|\||!\[|>|[-*]\s|\d+\.\s|\\pagebreak|<!--|\$\$)"
            while i < len(lines) and lines[i].strip() and not re.match(block_start, lines[i].strip()):
                para.append(lines[i].strip())
                i += 1
            p = doc.add_paragraph()
            fmt(p)
            add_runs(p, " ".join(para))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)


def export_pdf(docx_path: Path) -> Path | None:
    """Convert the .docx to PDF next to it. Tries Microsoft Word (docx2pdf), then LibreOffice.

    Returns the PDF path, or None (with a warning) if no converter is available.
    """
    import shutil
    import subprocess

    pdf_path = docx_path.with_suffix(".pdf")
    try:
        from docx2pdf import convert  # drives Microsoft Word (Windows / macOS)

        convert(str(docx_path), str(pdf_path))
        if pdf_path.exists():
            return pdf_path
    except Exception as exc:  # noqa: BLE001 - fall through to the next converter
        print(f"[aviso] docx2pdf falhou ({exc.__class__.__name__}); tentando LibreOffice...")
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent),
                        str(docx_path)], check=True)
        if pdf_path.exists():
            return pdf_path
    print("[aviso] Nenhum conversor de PDF disponível (instale o Word + docx2pdf ou o LibreOffice).")
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--input", type=Path, default=HERE / "relatorio_pt_template.md")
    ap.add_argument("-o", "--output", type=Path, default=HERE / "relatorio_final.docx")
    ap.add_argument("--no-pdf", action="store_true", help="do not export a PDF copy")
    args = ap.parse_args()
    build(args.input.read_text(encoding="utf-8"), args.output, args.input.resolve().parent)
    print(f"Relatório gerado: {args.output}")
    if not args.no_pdf:
        pdf = export_pdf(args.output.resolve())
        if pdf:
            print(f"PDF gerado: {pdf}")


if __name__ == "__main__":
    main()
