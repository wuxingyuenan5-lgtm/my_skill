# -*- coding: utf-8 -*-
"""Generate meeting minutes .docx per meeting-minutes skill v2.0 spec (python-docx).

Spec mapping (from SKILL.md + MeetingMinutesFormatter.bas):
  H1  : Heading 1  -> 微软雅黑 18pt bold RGB(0,32,96), centered
  H2  : Heading 2  -> 微软雅黑 14pt bold RGB(0,32,96), with blue "▌ " prefix RGB(0,112,192)
  H3  : Heading 3  -> 微软雅黑 12pt bold RGB(64,64,64)
  body: 微软雅黑 11pt black, line spacing 1.5
  **bold** -> orange RGB(192,80,0) bold
  bullets "- " -> list bullets
  tables -> header row dark blue fill RGB(0,32,96) white bold centered;
            zebra rows RGB(242,242,242)/white; borders 0.5pt gray
  Q:/A: paragraphs -> light gray shading RGB(242,242,242), left indent 18pt
  margins: top/bottom 2.54cm, left/right 3.17cm
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DARK_BLUE  = RGBColor(0, 32, 96)
BLUE_LINE  = RGBColor(0, 112, 192)
ORANGE     = RGBColor(192, 80, 0)
DARK_GRAY  = RGBColor(64, 64, 64)
LIGHT_GRAY = "F2F2F2"
GRAY_TEXT  = RGBColor(128, 128, 128)
FONT       = "微软雅黑"

def set_font(run, size, color=None, bold=False, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    r = run._element.rPr
    if r is None:
        r = run._element.get_or_add_rPr()
    rFonts = r.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        r.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name)

def add_runs_with_bold(p, text, size, color=None, base_bold=False):
    """Handle **bold** inline markers -> orange bold."""
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(part[2:-2])
            set_font(run, size, ORANGE, True)
        else:
            run = p.add_run(part)
            set_font(run, size, color, base_bold)

def set_shading(el, color_hex):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    el.append(shd)

def para_shading(p, color_hex):
    pPr = p._p.get_or_add_pPr()
    set_shading(pPr, color_hex)

def cell_shading(cell, color_hex):
    set_shading(cell._tc.get_or_add_tcPr(), color_hex)

def add_h1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(16)
    add_runs_with_bold(p, text, 18, DARK_BLUE, True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run("▌ ")
    set_font(run, 14, BLUE_LINE, True)
    add_runs_with_bold(p, text, 14, DARK_BLUE, True)
    return p

def add_h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    add_runs_with_bold(p, text, 12, DARK_GRAY, True)
    return p

def add_body(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    add_runs_with_bold(p, text, 11)
    return p

def add_bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    add_runs_with_bold(p, text, 11)
    return p

def add_qa(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(4)
    pf.left_indent = Pt(18)
    para_shading(p, LIGHT_GRAY)
    add_runs_with_bold(p, text, 11)
    return p

def set_cell_text(cell, text, size=10.5, bold=False, color=None, center=True):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs_with_bold(p, text, size, color, bold)

def add_table(doc, header, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = 'Table Grid'
    # header
    for j, h in enumerate(header):
        cell = t.rows[0].cells[j]
        set_cell_text(cell, h, bold=True, color=RGBColor(255, 255, 255))
        cell_shading(cell, "002060")
    # body
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.rows[i + 1].cells[j]
            set_cell_text(cell, val)
            if (i + 1) % 2 == 0:
                cell_shading(cell, LIGHT_GRAY)
    # borders gray 0.5pt
    tbl = t._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement('w:' + edge)
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')   # 0.5pt
        el.set(qn('w:color'), '808080')
        borders.append(el)
    tblPr.append(borders)
    return t

def build(md_lines, out_path):
    doc = Document()
    # default style font
    style = doc.styles['Normal']
    style.font.name = FONT
    style.font.size = Pt(11)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    # margins
    for sec in doc.sections:
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(3.17)
        sec.right_margin = Cm(3.17)

    i = 0
    n = len(md_lines)
    while i < n:
        line = md_lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        s = line.strip()
        if s.startswith('### '):
            add_h3(doc, s[4:])
        elif s.startswith('## '):
            add_h2(doc, s[3:])
        elif s.startswith('# '):
            add_h1(doc, s[2:])
        elif s.startswith('- '):
            add_bullet(doc, s[2:])
        elif s.startswith('Q：') or s.startswith('Q:'):
            add_qa(doc, s)
        elif s.startswith('A：') or s.startswith('A:'):
            add_qa(doc, s)
        elif s.startswith('|'):
            # gather table
            header = [c.strip() for c in s.strip('|').split('|')]
            rows = []
            j = i + 1
            while j < n and md_lines[j].strip().startswith('|'):
                row = [c.strip() for c in md_lines[j].strip().strip('|').split('|')]
                if not all(c == '---' or set(c) <= set('-: ') for c in row):
                    rows.append(row)
                j += 1
            add_table(doc, header, rows)
            i = j - 1
        else:
            add_body(doc, s)
        i += 1

    doc.save(out_path)
    print('SAVED:', out_path)

if __name__ == '__main__':
    md_file = sys.argv[1]
    out_file = sys.argv[2]
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    build(lines, out_file)
