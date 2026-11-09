from copy import deepcopy
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


BASE = Path("/Users/**********/Downloads")

REPORTS = [
    {
        "input": BASE / "地震模拟实验" / "地震模拟实验报告_***_含现场图片_代码截图修正版.docx",
        "template": BASE / "地震模拟实验" / "地震模拟实验报告模板.docx",
        "output": BASE / "地震模拟实验" / "地震模拟实验报告_***_含现场图片_代码截图修正版_统一排版版.docx",
    },
    {
        "input": BASE / "重磁电综合实验" / "重磁电综合实验报告_插图版.docx",
        "template": BASE / "重磁电综合实验" / "重磁电综合实验实验报告模板.docx",
        "output": BASE / "重磁电综合实验" / "重磁电综合实验报告_插图版_统一排版版.docx",
    },
]


EXPERIMENT_RE = re.compile(r"^实验\s*\d+\s+")
SECTION_RE = re.compile(r"^[一二三四五六七八九十]+、")
CAPTION_RE = re.compile(r"^(图|照片|表)\s*\d|^实验\d+现场照片")
NUMBERED_ITEM_RE = re.compile(r"^\d+\.\s")


def set_font(run_or_style, latin="Times New Roman", east_asia="宋体", size=None, bold=None):
    font = run_or_style.font
    font.name = latin
    if size is not None:
        font.size = Pt(size)
    if bold is not None:
        font.bold = bold
    rpr = getattr(run_or_style, "_element", None)
    if rpr is not None:
        if rpr.rPr is None:
            rpr.get_or_add_rPr()
        rpr.rPr.rFonts.set(qn("w:eastAsia"), east_asia)


def set_style_font(style, latin="Times New Roman", east_asia="宋体", size=None, bold=None):
    style.font.name = latin
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    style._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)


def set_cell_margins(cell, top=90, start=120, bottom=90, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in {"top": top, "start": start, "bottom": bottom, "end": end}.items():
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "808080")


def copy_section_layout(doc, template):
    source = Document(template).sections[0]
    for section in doc.sections:
        section.page_width = source.page_width
        section.page_height = source.page_height
        section.top_margin = source.top_margin
        section.bottom_margin = source.bottom_margin
        section.left_margin = source.left_margin
        section.right_margin = source.right_margin
        section.header_distance = source.header_distance
        section.footer_distance = source.footer_distance
        section.orientation = source.orientation
        section.start_type = WD_SECTION.NEW_PAGE


def configure_styles(doc):
    styles = doc.styles
    normal = styles["Normal"]
    set_style_font(normal, size=11, bold=False)
    normal.paragraph_format.first_line_indent = Pt(22)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(5)

    title = styles["Title"]
    set_style_font(title, size=18, bold=True)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.first_line_indent = Pt(0)
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(12)

    for name, size, before, after in [
        ("Heading 1", 14, 12, 6),
        ("Heading 2", 12, 8, 4),
        ("Heading 3", 11, 6, 2),
    ]:
        st = styles[name]
        set_style_font(st, size=size, bold=True)
        st.paragraph_format.first_line_indent = Pt(0)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.line_spacing = 1.2
        st.paragraph_format.keep_with_next = True

    if "Caption" in styles:
        cap = styles["Caption"]
        set_style_font(cap, size=9.5, bold=False)
        cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.first_line_indent = Pt(0)
        cap.paragraph_format.space_before = Pt(3)
        cap.paragraph_format.space_after = Pt(7)
        cap.paragraph_format.line_spacing = 1.15


def paragraph_has_drawing(paragraph):
    return bool(paragraph._p.xpath(".//w:drawing | .//w:pict"))


def clear_page_break_before(paragraph):
    ppr = paragraph._p.get_or_add_pPr()
    node = ppr.find(qn("w:pageBreakBefore"))
    if node is not None:
        ppr.remove(node)


def delete_paragraph(paragraph):
    element = paragraph._element
    element.getparent().remove(element)
    paragraph._p = paragraph._element = None


def remove_front_matter_empty_paragraphs(doc):
    for para in list(doc.paragraphs):
        text = para.text.strip()
        if EXPERIMENT_RE.match(text):
            break
        if not text and not paragraph_has_drawing(para):
            delete_paragraph(para)


def style_paragraphs(doc):
    seen_title = False
    for para in doc.paragraphs:
        text = para.text.strip()
        pf = para.paragraph_format

        if not text and not paragraph_has_drawing(para):
            clear_page_break_before(para)
            pf.space_after = Pt(0)
            continue

        clear_page_break_before(para)
        run_size = 11
        run_bold = None

        if paragraph_has_drawing(para):
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.first_line_indent = Pt(0)
            pf.space_before = Pt(4)
            pf.space_after = Pt(3)
            continue

        if not seen_title and "实验报告" in text and len(text) <= 24:
            para.style = doc.styles["Title"]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            seen_title = True
            run_size = 18
            run_bold = True
        elif EXPERIMENT_RE.match(text):
            para.style = doc.styles["Heading 1"]
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_size = 14
            run_bold = True
        elif SECTION_RE.match(text):
            para.style = doc.styles["Heading 2"]
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_size = 12
            run_bold = True
        elif CAPTION_RE.match(text):
            para.style = doc.styles["Caption"]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_size = 9.5
        else:
            para.style = doc.styles["Normal"]
            if text.startswith(("姓名", "指导老师", "班", "学", "姓", "组", "重力勘探")) and len(text) < 80:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER if "  " in text or "·" in text else WD_ALIGN_PARAGRAPH.LEFT
                pf.first_line_indent = Pt(0)
                run_size = 10.5 if "·" in text else 11
            elif NUMBERED_ITEM_RE.match(text):
                para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                pf.first_line_indent = Pt(0)
                pf.left_indent = Pt(18)
                pf.space_after = Pt(2)
            else:
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        for run in para.runs:
            set_font(run, size=run_size, bold=run_bold)


def resize_inline_shapes(doc):
    usable_width = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin
    max_width = int(usable_width * 0.96)
    for shape in doc.inline_shapes:
        if shape.width and shape.width > max_width:
            ratio = max_width / shape.width
            shape.width = max_width
            shape.height = int(shape.height * ratio)


def style_tables(doc):
    for table in doc.tables:
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_borders(table)
        for row in table.rows:
            for cell in row.cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                set_cell_margins(cell)
                for para in cell.paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.paragraph_format.first_line_indent = Pt(0)
                    para.paragraph_format.space_before = Pt(0)
                    para.paragraph_format.space_after = Pt(0)
                    para.paragraph_format.line_spacing = 1.15
                    for run in para.runs:
                        set_font(run, size=10.5)


def preserve_template_headers(doc, template):
    src_doc = Document(template)
    src_sec = src_doc.sections[0]
    if not src_sec.header.paragraphs and not src_sec.footer.paragraphs:
        return
    for sec in doc.sections:
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        for part_name in ["header", "footer"]:
            dst = getattr(sec, part_name)
            src = getattr(src_sec, part_name)
            for p in list(dst._element):
                dst._element.remove(p)
            for p in src._element:
                dst._element.append(deepcopy(p))


def normalize_report(input_path, template_path, output_path):
    doc = Document(input_path)
    remove_front_matter_empty_paragraphs(doc)
    copy_section_layout(doc, template_path)
    configure_styles(doc)
    preserve_template_headers(doc, template_path)
    style_paragraphs(doc)
    style_tables(doc)
    resize_inline_shapes(doc)
    doc.core_properties.comments = "Layout normalized against the original experiment report template."
    doc.save(output_path)
    return output_path


def main():
    for spec in REPORTS:
        out = normalize_report(spec["input"], spec["template"], spec["output"])
        print(out)


if __name__ == "__main__":
    main()
