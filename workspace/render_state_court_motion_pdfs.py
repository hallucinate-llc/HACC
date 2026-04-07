from __future__ import annotations

import copy
import re
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path("/home/barberb/HACC/workspace")
OUTDIR = ROOT / "pdf-filings-court-ready"
FILED_DATE = "April 6, 2026"

DOCS = [
    "combined_state_court_packet_cover_sheet.md",
    "court_ready_packet_index.md",
    "filing_specific_exhibit_schedule.md",
    "court_facing_exhibit_reference_sheet.md",
    "response_to_eviction_motion_and_cross_motion_for_injunctive_relief.md",
    "memorandum_in_support_of_response_to_eviction_and_cross_motion.md",
    "polished_motion_for_joinder_quantum.md",
    "polished_memorandum_in_support_of_joinder_quantum.md",
    "motion_to_show_cause_quantum_application_nonprocessing.md",
    "memorandum_in_support_of_motion_to_show_cause_quantum_application_nonprocessing.md",
    "proposed_order_on_eviction_response_and_interim_relief.md",
    "proposed_order_on_motion_for_joinder_quantum.md",
    "proposed_order_to_show_cause_quantum_application_nonprocessing.md",
    "declaration_of_benjamin_barber_in_support_of_preliminary_injunction.md",
    "declaration_of_jane_cortez_in_support_of_preliminary_injunction.md",
    "certificate_of_service_combined_state_court_packet.md",
    "certificate_of_service_quantum_joinder_and_show_cause_packet.md",
]

SIGNATURE_DOC_KEYWORDS = (
    "motion",
    "memorandum",
    "response_to_eviction",
    "certificate_of_service",
)

DECLARATION_DOC_KEYWORDS = (
    "declaration_of_benjamin_barber_in_support",
    "declaration_of_jane_cortez_in_support",
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    page_label = f"Page {canvas.getPageNumber()} of {doc.page_count}"
    page_x = letter[0] - doc.rightMargin
    page_y = 0.55 * inch
    canvas.drawRightString(page_x, page_y, page_label)

    available_width = page_x - doc.leftMargin - 0.7 * inch
    avg_char_width = 5.1  # rough Times-Roman 10pt average
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
    footer(canvas, doc)
    canvas.saveState()
    canvas.setFont("Times-Roman", 8)
    top = letter[1] - 0.9 * inch
    step = 24
    for i in range(1, 29):
        y = top - (i - 1) * step
        if y < 0.95 * inch:
            break
        canvas.drawRightString(0.62 * inch, y, str(i))
    canvas.setLineWidth(0.3)
    canvas.line(0.7 * inch, 0.9 * inch, 0.7 * inch, letter[1] - 0.82 * inch)
    canvas.restoreState()


def humanize_label(text: str) -> str:
    text = text.replace(".md", "").replace(".pdf", "")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", lambda m: humanize_label(m.group(1)), text)
    text = text.replace("  ", " ")
    return text


def build_pdf(md_path: Path, pdf_path: Path) -> None:
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
    small = ParagraphStyle("small", parent=base, fontSize=10.2, leading=13)
    quote = ParagraphStyle("quote", parent=base, leftIndent=18, fontName="Courier", fontSize=9.8, leading=12)
    centered = ParagraphStyle("centered", parent=base, alignment=1, fontName="Times-Bold", fontSize=11.5, leading=14)
    cap = ParagraphStyle("cap", parent=base, fontSize=11, leading=13)
    bodynum = ParagraphStyle("bodynum", parent=base, leftIndent=12, firstLineIndent=-12)

    story = []
    lines = md_path.read_text(encoding="utf-8").splitlines()
    title_line = ""
    case_no = "Case No. __________________"
    body_start = 0
    first_heading_idx = None
    case_idx = None
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("# ") and first_heading_idx is None:
            first_heading_idx = i
            title_line = s[2:].strip()
        if s.startswith("Case No."):
            case_idx = i
            case_no = s
            break
    if case_idx is not None:
        body_start = case_idx + 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
        if body_start < len(lines):
            first_after = lines[body_start].strip()
            if first_after.isupper() or first_after.startswith("DEFENDANTS'") or first_after.startswith("[Proposed]"):
                title_line = first_after
                body_start += 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
    elif first_heading_idx is not None:
        body_start = first_heading_idx + 1

    # Court-style header block
    contact = Paragraph(
        "Benjamin Jay Barber, pro se<br/>Jane Kay Cortez, pro se<br/>10043 SE 32nd Ave<br/>Milwaukie, OR 97222<br/>971-270-0855<br/>starworks5@gmail.com<br/>Defendants",
        small,
    )
    story.append(contact)
    story.append(Spacer(1, 0.14 * inch))
    story.append(Paragraph("IN THE CLACKAMAS COUNTY JUSTICE COURT", centered))
    story.append(Paragraph("STATE OF OREGON", centered))
    story.append(Spacer(1, 0.12 * inch))

    left = Paragraph(
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY,<br/>Plaintiff,<br/><br/>v.<br/><br/>"
        "BENJAMIN JAY BARBER and JANE KAY CORTEZ,<br/>Defendants.",
        cap,
    )
    right = Paragraph(f"{clean_inline(case_no)}", cap)
    caption_table = Table([[left, right]], colWidths=[4.1 * inch, 2.0 * inch])
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

    if title_line:
        story.append(Paragraph(clean_inline(title_line), h1))
        story.append(Spacer(1, 0.06 * inch))

    in_code = False
    code_lines: list[str] = []

    for raw in lines[body_start:]:
        line = raw.rstrip()

        if line.strip().startswith("```"):
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

        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            continue

        if stripped == "---":
            story.append(Spacer(1, 0.08 * inch))
            continue

        if stripped.startswith("## "):
            story.append(Paragraph(clean_inline(stripped[3:]), h2))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(clean_inline(stripped[4:]), h3))
            continue

        if re.fullmatch(r"[A-Z0-9 ,.'&()\\[\\]/-]{8,}", stripped):
            story.append(Paragraph(clean_inline(stripped), h2))
            continue

        bullet_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if bullet_match:
            n, text = bullet_match.groups()
            story.append(Paragraph(f"<b>{n}.</b> {clean_inline(text)}", bodynum))
            continue

        dash_match = re.match(r"^-\s+(.*)$", stripped)
        if dash_match:
            story.append(Paragraph(f"&#8226; {clean_inline(dash_match.group(1))}", base))
            continue

        story.append(Paragraph(clean_inline(stripped), small if "Case No." in stripped else base))

    stem = md_path.stem.lower()
    if any(key in stem for key in SIGNATURE_DOC_KEYWORDS) and not stem.startswith("proposed_order"):
        sig_block = [
            Spacer(1, 0.22 * inch),
            Paragraph(f"Dated: {FILED_DATE}", base),
            Spacer(1, 0.08 * inch),
            Paragraph("Respectfully submitted,", base),
            Spacer(1, 0.16 * inch),
            Paragraph("Submitted by Defendants:", base),
            Spacer(1, 0.20 * inch),
            Paragraph("__________________________________", base),
            Paragraph("Signature", small),
            Spacer(1, 0.12 * inch),
            Paragraph("Benjamin Jay Barber, pro se", base),
            Spacer(1, 0.22 * inch),
            Paragraph("__________________________________", base),
            Paragraph("Signature", small),
            Spacer(1, 0.12 * inch),
            Paragraph("Jane Kay Cortez, pro se", base),
        ]
        story.append(KeepTogether(sig_block))
    elif any(key in stem for key in DECLARATION_DOC_KEYWORDS):
        decl_block = [
            Spacer(1, 0.22 * inch),
            Paragraph(f"Dated: {FILED_DATE}", base),
            Spacer(1, 0.24 * inch),
            Paragraph("__________________________________", base),
            Paragraph("Signature", small),
            Spacer(1, 0.12 * inch),
        ]
        if "benjamin" in stem:
            decl_block.append(Paragraph("Benjamin Jay Barber, Declarant", base))
        else:
            decl_block.append(Paragraph("Jane Kay Cortez, Declarant", base))
        story.append(KeepTogether(decl_block))
    doc_title = humanize_label(title_line) if title_line else humanize_label(md_path.stem)
    doc_kwargs = dict(
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.85 * inch,
        title=doc_title,
    )
    count_doc = SimpleDocTemplate(str(pdf_path), **doc_kwargs)
    story_for_count = copy.deepcopy(story)
    page_counter = []

    def _capture_page_count(canvas, _doc):
        page_counter.append(canvas.getPageNumber())

    count_doc.build(story_for_count, onFirstPage=_capture_page_count, onLaterPages=_capture_page_count)
    doc = SimpleDocTemplate(str(pdf_path), **doc_kwargs)
    doc.page_count = len(page_counter)
    doc.build(story, onFirstPage=pleading_paper, onLaterPages=pleading_paper)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        md_path = ROOT / name
        pdf_path = OUTDIR / f"{md_path.stem}.pdf"
        build_pdf(md_path, pdf_path)
        print(pdf_path)


if __name__ == "__main__":
    main()
