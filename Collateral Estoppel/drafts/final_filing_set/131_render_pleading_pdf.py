#!/usr/bin/env python3
from __future__ import annotations

import copy
import html
import re
import sys
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def usage() -> None:
    print("Usage: 131_render_pleading_pdf.py <input_text_file> <output_pdf> [title]")


def clean_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    return text


def _parse_legal_header(lines: list[str]) -> tuple[dict[str, object] | None, int]:
    """Parse common Oregon pleading header components if present."""
    idx = 0
    n = len(lines)

    # Skip leading empties.
    while idx < n and not lines[idx].strip():
        idx += 1

    if idx >= n or not lines[idx].strip().startswith("IN THE "):
        return None, 0

    court_lines: list[str] = []
    while idx < n and lines[idx].strip():
        court_lines.append(lines[idx].strip())
        idx += 1

    while idx < n and not lines[idx].strip():
        idx += 1

    case_no = ""
    if idx < n and lines[idx].strip().startswith("Case No."):
        case_no = lines[idx].strip()
        idx += 1
        while idx < n and not lines[idx].strip():
            idx += 1

    party_lines: list[str] = []
    while idx < n and lines[idx].strip():
        party_lines.append(lines[idx].strip())
        idx += 1

    while idx < n and not lines[idx].strip():
        idx += 1

    title_lines: list[str] = []
    while idx < n and lines[idx].strip():
        title_lines.append(lines[idx].strip())
        idx += 1

    while idx < n and not lines[idx].strip():
        idx += 1

    header = {
        "court_lines": court_lines,
        "case_no": case_no,
        "party_lines": party_lines,
        "title_lines": title_lines,
    }
    return header, idx


def footer(canvas, doc):
    canvas.saveState()
    page_x_left = doc.leftMargin
    page_x_right = letter[0] - doc.rightMargin
    rule_y = 0.74 * inch
    text_y = 0.48 * inch

    # Footer divider line for cleaner page framing.
    canvas.setLineWidth(0.8)
    canvas.line(page_x_left, rule_y, page_x_right, rule_y)

    page_label = f"Page {canvas.getPageNumber()} of {doc.page_count}"
    canvas.setFont("Times-Roman", 9)
    canvas.drawRightString(page_x_right, text_y, page_label)

    left_label = getattr(doc, "footer_left_label", "") or ""
    center_label = getattr(doc, "footer_center_label", "") or doc.title

    if left_label:
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(page_x_left, text_y, left_label[:52])

    if center_label:
        center_x = (page_x_left + page_x_right) / 2
        canvas.setFont("Times-Italic", 8.3)
        canvas.drawCentredString(center_x, text_y, center_label[:68])
    canvas.restoreState()


def pleading_paper(canvas, doc):
    # Match court-order styling baseline from the signed source order:
    # clean page body, no pleading line-number gutter.
    footer(canvas, doc)


def render_text(input_path: Path, output_path: Path, title: str) -> None:
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "base",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11.5,
        leading=15,
        spaceAfter=3,
    )
    h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=12.3, leading=15.2, spaceBefore=2, spaceAfter=7, alignment=1)
    h2 = ParagraphStyle("h2", parent=base, fontName="Times-Bold", fontSize=12.4, leading=15.8, spaceBefore=9, spaceAfter=5)
    h3 = ParagraphStyle("h3", parent=base, fontName="Times-BoldItalic", fontSize=11.4, leading=13.8, spaceBefore=5, spaceAfter=3)
    h4 = ParagraphStyle("h4", parent=base, fontName="Times-Bold", fontSize=11.2, leading=13.8, spaceBefore=5, spaceAfter=3)
    h5 = ParagraphStyle("h5", parent=base, fontName="Times-Italic", fontSize=11, leading=13.5, spaceBefore=4, spaceAfter=2)
    quote = ParagraphStyle("quote", parent=base, leftIndent=18, fontName="Courier", fontSize=9.8, leading=12)
    bodynum = ParagraphStyle("bodynum", parent=base, leftIndent=12, firstLineIndent=-12)
    bodynum_sub = ParagraphStyle("bodynum_sub", parent=base, leftIndent=22, firstLineIndent=-12)
    centered = ParagraphStyle("centered", parent=base, alignment=1, fontName="Times-Roman", fontSize=12, leading=14)
    cap = ParagraphStyle("cap", parent=base, fontSize=11, leading=13)

    raw = input_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    story = []
    header, body_start = _parse_legal_header(lines)

    parsed_case_no = ""
    if header:
        court_lines = header["court_lines"]
        case_no = str(header["case_no"])
        parsed_case_no = case_no
        party_lines = header["party_lines"]
        title_lines = header["title_lines"]

        for c in court_lines:
            story.append(Paragraph(clean_inline(c), centered))
        story.append(Spacer(1, 0.08 * inch))

        if party_lines or case_no:
            left_text = "<br/>".join(clean_inline(x) for x in party_lines) if party_lines else ""
            right_text = clean_inline(case_no) if case_no else ""
            caption_table = Table(
                [[Paragraph(left_text, cap), Paragraph(right_text, cap)]],
                colWidths=[4.1 * inch, 2.0 * inch],
            )
            caption_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LINEBEFORE", (1, 0), (1, 0), 0.8, "black"),
                        ("LEFTPADDING", (1, 0), (1, 0), 10),
                    ]
                )
            )
            story.append(caption_table)
            story.append(Spacer(1, 0.10 * inch))

        if title_lines:
            title_html = "<br/>".join(clean_inline(t) for t in title_lines)
            story.append(Paragraph(title_html, h1))
            story.append(Spacer(1, 0.04 * inch))
    in_code = False
    code_lines: list[str] = []

    for raw_line in lines[body_start:]:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                story.append(Paragraph("<br/>".join(clean_inline(x) for x in code_lines), quote))
                story.append(Spacer(1, 0.06 * inch))
                in_code = False
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            continue

        if stripped == "---":
            story.append(Spacer(1, 0.08 * inch))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(clean_inline(stripped[2:]), h1))
            continue

        if stripped.startswith("## "):
            story.append(HRFlowable(width="100%", thickness=0.9, color="black"))
            story.append(Spacer(1, 0.03 * inch))
            story.append(Paragraph(clean_inline(stripped[3:]), h2))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(clean_inline(stripped[4:]), h3))
            continue

        if stripped.startswith("#### "):
            story.append(Paragraph(clean_inline(stripped[5:]), h4))
            continue

        # Roman numeral section headers common in motions.
        if re.match(r"^[IVXLC]+\.\s+[A-Z].*$", stripped):
            story.append(Spacer(1, 0.03 * inch))
            story.append(HRFlowable(width="100%", thickness=0.9, color="black"))
            story.append(Spacer(1, 0.03 * inch))
            story.append(Paragraph(clean_inline(stripped), h2))
            continue

        # Lettered legal subheadings like "A. STANDARD" or "B. FACTS".
        if re.match(r"^[A-Z]\.\s+[A-Z].*$", stripped):
            story.append(Paragraph(clean_inline(stripped), h4))
            continue

        # Compact sub-subheadings like "(1) ...", "(a) ...".
        if re.match(r"^\([0-9a-zA-Z]+\)\s+.*$", stripped):
            story.append(Paragraph(clean_inline(stripped), h5))
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            n, text = numbered.groups()
            story.append(Paragraph(f"<b>{n}.</b> {clean_inline(text)}", bodynum))
            continue

        lettered = re.match(r"^([a-z])\.\s+(.*)$", stripped)
        if lettered:
            a, text = lettered.groups()
            story.append(Paragraph(f"<b>{a}.</b> {clean_inline(text)}", bodynum_sub))
            continue

        dashed = re.match(r"^-\s+(.*)$", stripped)
        if dashed:
            story.append(Paragraph(f"&#8226; {clean_inline(dashed.group(1))}", base))
            continue

        # Preserve all-caps headings found in legal drafts.
        if re.fullmatch(r"[A-Z0-9 ,.'&()\[\]/:-]{8,}", stripped):
            story.append(Paragraph(clean_inline(stripped), h2))
            continue

        story.append(Paragraph(clean_inline(stripped), base))

    doc_kwargs = dict(
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.85 * inch,
        title=title,
    )

    count_doc = SimpleDocTemplate(str(output_path), **doc_kwargs)
    story_for_count = copy.deepcopy(story)
    page_counter = []

    def _capture_page_count(canvas, _doc):
        page_counter.append(canvas.getPageNumber())

    count_doc.build(story_for_count, onFirstPage=_capture_page_count, onLaterPages=_capture_page_count)

    doc = SimpleDocTemplate(str(output_path), **doc_kwargs)
    doc.page_count = len(page_counter)
    doc.footer_left_label = parsed_case_no
    doc.footer_center_label = title
    doc.build(story, onFirstPage=pleading_paper, onLaterPages=pleading_paper)


def main() -> int:
    if len(sys.argv) < 3:
        usage()
        return 2

    input_path = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]).expanduser().resolve()
    title = sys.argv[3] if len(sys.argv) >= 4 else input_path.stem.replace("_", " ")

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    render_text(input_path, output_path, title)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
