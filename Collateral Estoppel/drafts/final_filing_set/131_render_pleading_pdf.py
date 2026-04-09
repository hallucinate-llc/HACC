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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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
    canvas.setFont("Times-Roman", 10)
    page_label = f"Page {canvas.getPageNumber()} of {doc.page_count}"
    page_x = letter[0] - doc.rightMargin
    page_y = 0.55 * inch
    canvas.drawRightString(page_x, page_y, page_label)

    available_width = page_x - doc.leftMargin - 0.7 * inch
    avg_char_width = 5.1
    max_chars = max(20, int(available_width / avg_char_width))
    wrapped_title = wrap(doc.title, width=max_chars)[:2]

    text = canvas.beginText()
    text.setTextOrigin(doc.leftMargin, 0.68 * inch if len(wrapped_title) > 1 else page_y)
    text.setFont("Times-Roman", 10)
    for line in wrapped_title:
        text.textLine(line)
    canvas.drawText(text)
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
    h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=12.5, leading=15.5, spaceBefore=2, spaceAfter=8, alignment=1)
    h2 = ParagraphStyle("h2", parent=base, fontName="Times-Bold", fontSize=12, leading=15, spaceBefore=8, spaceAfter=5)
    h3 = ParagraphStyle("h3", parent=base, fontName="Times-BoldItalic", fontSize=11.5, leading=14, spaceBefore=6, spaceAfter=3)
    quote = ParagraphStyle("quote", parent=base, leftIndent=18, fontName="Courier", fontSize=9.8, leading=12)
    bodynum = ParagraphStyle("bodynum", parent=base, leftIndent=12, firstLineIndent=-12)
    centered = ParagraphStyle("centered", parent=base, alignment=1, fontName="Times-Roman", fontSize=12, leading=14)
    cap = ParagraphStyle("cap", parent=base, fontSize=11, leading=13)

    raw = input_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    story = []
    header, body_start = _parse_legal_header(lines)

    if header:
        court_lines = header["court_lines"]
        case_no = str(header["case_no"])
        party_lines = header["party_lines"]
        title_lines = header["title_lines"]

        for c in court_lines:
            story.append(Paragraph(clean_inline(c), centered))
        story.append(Spacer(1, 0.12 * inch))

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
            story.append(Spacer(1, 0.16 * inch))

        if title_lines:
            title_html = "<br/>".join(clean_inline(t) for t in title_lines)
            story.append(Paragraph(title_html, h1))
            story.append(Spacer(1, 0.06 * inch))
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
            story.append(Paragraph(clean_inline(stripped[3:]), h2))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(clean_inline(stripped[4:]), h3))
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            n, text = numbered.groups()
            story.append(Paragraph(f"<b>{n}.</b> {clean_inline(text)}", bodynum))
            continue

        lettered = re.match(r"^([a-z])\.\s+(.*)$", stripped)
        if lettered:
            a, text = lettered.groups()
            story.append(Paragraph(f"<b>{a}.</b> {clean_inline(text)}", bodynum))
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
