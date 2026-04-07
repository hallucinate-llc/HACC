from __future__ import annotations

import email
from email import policy
from pathlib import Path
import re
from textwrap import wrap

from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import subprocess


ROOT = Path("/home/barberb/HACC/workspace/exhibit-binder-court-ready")
COVERS = ROOT / "covers"
EXHIBITS = ROOT / "exhibits"
COMPILED = ROOT / "compiled"
WORKING = ROOT / "working"
CASE_NO = "26FE0586"

EXHIBIT_ORDER = ["B", "C", "D", "E", "G", "H", "M", "O", "P", "R", "T", "V", "W", "X", "Y", "Z", "AA"]
EXHIBIT_TITLES = {
    "B": "Hillside Park Apartments Phase II General Information Notice",
    "C": "December 31, 2025 30-Day Lease Termination Notice",
    "D": "December 23, 2025 90-Day Lease Termination Notice Without Cause",
    "E": "December 2025 Notice of Eligibility for Relocation Assistance as a Displaced Resident",
    "G": "HACC January 8, 2026 Blossom / TPV Notice",
    "H": "February 4, 2026 For-Cause Notice With Option to Cure or Vacate",
    "M": "HCV Orientation / Voucher / Waterleaf March 2026 Thread",
    "O": "Reasonable Accommodation Provider Verification",
    "P": "HACC March 26, 2026 Reasonable Accommodation Denial / One-Bedroom Position",
    "R": "Gmail Preserved Sent-Mail Headers and Body Snippets",
    "T": "February 2, 2026 Comparator Email to Ashley Ferron and Blossom",
    "V": "HACC Email Acknowledging Packet Was Left With Quantum But Did Not Reach HACC",
    "W": "Waterleaf Application Record",
    "X": "HACC / Waterleaf / Port-Out Email Thread",
    "Y": "Blossom and Community Apartments Lease-Up Page Excerpt",
    "Z": "HACC Administrative Plan Excerpts on Hillside Manor, Waiting Lists, and Quantum",
    "AA": "March 26, 2026 HACC Housing Options Email",
}


def shorten_display_paths(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        path = Path(match.group(0))
        parts = path.parts
        if len(parts) >= 2:
            return "/".join(parts[-2:])
        return path.name

    return re.sub(r"/home/barberb/HACC/[^\s)]+", repl, text)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    page_label = f"Page {canvas.getPageNumber()} of {doc.page_count}"
    page_x = letter[0] - doc.rightMargin
    page_y = 0.55 * inch
    canvas.drawRightString(page_x, page_y, page_label)
    max_chars = 70
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


def binder_page(canvas, doc):
    footer(canvas, doc)


def render_markdown(md_path: Path, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    base = ParagraphStyle("base", parent=styles["Normal"], fontName="Times-Roman", fontSize=11.5, leading=15, spaceAfter=3)
    h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=12.5, leading=16, alignment=1, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=base, fontName="Times-Bold", fontSize=12, leading=15, spaceBefore=7, spaceAfter=4)
    bullet = ParagraphStyle("bullet", parent=base, leftIndent=12, firstLineIndent=-12)

    def clean(text: str) -> str:
        text = shorten_display_paths(text)
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("`", "")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = []
    title = md_path.stem.replace("_", " ")
    started = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(clean(stripped[2:]), h1))
            title = stripped[2:]
            started = True
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(clean(stripped[3:]), h2))
            started = True
            continue
        if stripped.startswith("- "):
            story.append(Paragraph(f"&#8226; {clean(stripped[2:])}", bullet))
            started = True
            continue
        if stripped[:2].isdigit() and stripped[1] == ".":
            story.append(Paragraph(clean(stripped), bullet))
            started = True
            continue
        story.append(Paragraph(clean(stripped), base))
        started = True

    count_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    counter = []

    def count_pages(canvas, _doc):
        counter.append(canvas.getPageNumber())

    import copy
    count_doc.build(copy.deepcopy(story), onFirstPage=count_pages, onLaterPages=count_pages)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    doc.page_count = len(counter)
    doc.build(story, onFirstPage=binder_page, onLaterPages=binder_page)


def render_front_sheet(md_path: Path, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    base = ParagraphStyle("base", parent=styles["Normal"], fontName="Times-Roman", fontSize=11.5, leading=15, spaceAfter=3)
    small = ParagraphStyle("small", parent=base, fontSize=10.2, leading=13)
    centered = ParagraphStyle("centered", parent=base, alignment=1, fontName="Times-Bold", fontSize=11.5, leading=14)
    cap = ParagraphStyle("cap", parent=base, fontSize=11, leading=13)
    h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=12.5, leading=15.5, spaceBefore=2, spaceAfter=8, alignment=1)

    def clean(text: str) -> str:
        text = shorten_display_paths(text)
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("`", "")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    body_lines: list[str] = []
    title = "Defendants' Exhibit Binder"
    body_started = False
    for raw in lines:
        stripped = raw.strip()
        if not body_started and (
            not stripped
            or stripped.startswith("IN THE ")
            or stripped == "STATE OF OREGON"
            or stripped == "HOUSING AUTHORITY OF CLACKAMAS COUNTY,"
            or stripped == "Plaintiff,"
            or stripped == "v."
            or stripped == "BENJAMIN JAY BARBER and JANE KAY CORTEZ,"
            or stripped == "Defendants."
            or stripped.startswith("Case No.")
        ):
            continue
        body_started = True
        if stripped.startswith("## "):
            title = stripped[3:].strip()
            continue
        body_lines.append(raw)

    story = []
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
    right = Paragraph(f"Case No. {CASE_NO}", cap)
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
    story.append(Paragraph(clean(title), h1))
    story.append(Spacer(1, 0.06 * inch))

    for raw in body_lines:
        stripped = raw.strip()
        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            continue
        if stripped.startswith("- "):
            story.append(Paragraph(f"&#8226; {clean(stripped[2:])}", base))
            continue
        if stripped[:2].isdigit() and stripped[1] == ".":
            story.append(Paragraph(clean(stripped), base))
            continue
        story.append(Paragraph(clean(stripped), base))

    count_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    counter = []

    def count_pages(canvas, _doc):
        counter.append(canvas.getPageNumber())

    import copy
    count_doc.build(copy.deepcopy(story), onFirstPage=count_pages, onLaterPages=count_pages)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    doc.page_count = len(counter)
    doc.build(story, onFirstPage=binder_page, onLaterPages=binder_page)


def extract_eml_text(eml_path: Path) -> str:
    msg = email.message_from_binary_file(eml_path.open("rb"), policy=policy.default)
    headers = [
        f"From: {msg.get('From', '')}",
        f"To: {msg.get('To', '')}",
        f"Cc: {msg.get('Cc', '')}",
        f"Date: {msg.get('Date', '')}",
        f"Subject: {msg.get('Subject', '')}",
        "",
    ]
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = part.get_content()
                    body = body.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
                    break
    else:
        body = msg.get_content()
    return "\n".join(headers) + (body or "")


def render_text_exhibit(title: str, text: str, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    base = ParagraphStyle("base", parent=styles["Normal"], fontName="Courier", fontSize=9.5, leading=12, spaceAfter=2)
    heading = ParagraphStyle("heading", parent=styles["Normal"], fontName="Times-Bold", fontSize=12, leading=14, alignment=1, spaceAfter=8)
    story = [Paragraph(title.replace("&", "&amp;"), heading)]
    for line in text.splitlines():
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if not safe:
            story.append(Spacer(1, 0.03 * inch))
        else:
            story.append(Paragraph(safe, base))

    count_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    import copy
    counter = []

    def count_pages(canvas, _doc):
        counter.append(canvas.getPageNumber())

    count_doc.build(copy.deepcopy(story), onFirstPage=count_pages, onLaterPages=count_pages)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch, title=title)
    doc.page_count = len(counter)
    doc.build(story, onFirstPage=binder_page, onLaterPages=binder_page)


def convert_image_to_pdf(img_path: Path, pdf_path: Path) -> None:
    with Image.open(img_path) as im:
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        im.save(pdf_path, "PDF", resolution=150.0)


def merge_pdfs(output_pdf: Path, pdfs: list[Path]) -> None:
    subprocess.run(["pdfunite", *map(str, pdfs), str(output_pdf)], check=True)


def pdf_pages(pdf_path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not determine page count for {pdf_path}")


def build_exhibit_pdf(letter_code: str) -> Path:
    matches = list(EXHIBITS.glob(f"Exhibit_{letter_code}_*"))
    if not matches:
        raise FileNotFoundError(f"Missing exhibit file for {letter_code}")
    exhibit = matches[0]
    if exhibit.suffix.lower() == ".pdf":
        return exhibit
    if exhibit.suffix.lower() == ".eml":
        exhibit_pdf = WORKING / f"{exhibit.stem}.pdf"
        render_text_exhibit(exhibit.stem.replace("_", " "), extract_eml_text(exhibit), exhibit_pdf)
        return exhibit_pdf
    if exhibit.suffix.lower() in {".txt", ".md"}:
        exhibit_pdf = WORKING / f"{exhibit.stem}.pdf"
        render_text_exhibit(exhibit.stem.replace("_", " "), exhibit.read_text(encoding="utf-8"), exhibit_pdf)
        return exhibit_pdf
    if exhibit.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        exhibit_pdf = WORKING / f"{exhibit.stem}.pdf"
        convert_image_to_pdf(exhibit, exhibit_pdf)
        return exhibit_pdf
    raise RuntimeError(f"Unsupported exhibit type: {exhibit}")


def write_table_of_exhibits(starts: dict[str, int]) -> None:
    lines = [
        "# Table Of Exhibits",
        "",
        "IN THE CLACKAMAS COUNTY JUSTICE COURT",
        "STATE OF OREGON",
        "",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY,",
        "Plaintiff,",
        "",
        "v.",
        "",
        "BENJAMIN JAY BARBER and JANE KAY CORTEZ,",
        "Defendants.",
        "",
        f"Case No. {CASE_NO}",
        "",
        "## Core Exhibit Index",
        "",
    ]
    for letter_code in EXHIBIT_ORDER:
        title = EXHIBIT_TITLES[letter_code]
        lines.append(
            f"- `Exhibit {letter_code}` — {title} — begins at binder page `{starts[letter_code]}`"
        )
    lines.extend(
        [
            "",
            "## Note",
            "",
            "Each exhibit is preceded by a tab divider and a cover sheet describing:",
            "",
            "1. the source file;",
            "2. the source page or key record location;",
            "3. the factual assertion supported; and",
            "4. where that assertion is used in the filings.",
        ]
    )
    (COVERS / "TABLE_OF_EXHIBITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_table_of_exhibits_pdf(pdf_path: Path, starts: dict[str, int], counts: dict[str, int]) -> None:
    styles = getSampleStyleSheet()
    base = ParagraphStyle("base", parent=styles["Normal"], fontName="Times-Roman", fontSize=10.3, leading=12.5, spaceAfter=2)
    small = ParagraphStyle("small", parent=base, fontSize=9.5, leading=11.5)
    h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=12.5, leading=15.5, alignment=1, spaceAfter=8)
    centered = ParagraphStyle("centered", parent=base, alignment=1, fontName="Times-Bold", fontSize=11.2, leading=13.5)
    cap = ParagraphStyle("cap", parent=base, fontSize=10.8, leading=12.5)

    story = [
        Paragraph("IN THE CLACKAMAS COUNTY JUSTICE COURT", centered),
        Paragraph("STATE OF OREGON", centered),
        Spacer(1, 0.10 * inch),
    ]

    left = Paragraph(
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY,<br/>Plaintiff,<br/><br/>v.<br/><br/>"
        "BENJAMIN JAY BARBER and JANE KAY CORTEZ,<br/>Defendants.",
        cap,
    )
    right = Paragraph(f"Case No. {CASE_NO}", cap)
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
    story.extend([caption_table, Spacer(1, 0.14 * inch), Paragraph("Table Of Exhibits", h1)])
    story.append(
        Paragraph(
            "Binder page references correspond to the compiled master volume beginning with the binder front sheet as page 1.",
            base,
        )
    )
    story.append(Spacer(1, 0.08 * inch))

    rows = [[
        Paragraph("<b>Exhibit</b>", small),
        Paragraph("<b>Title</b>", small),
        Paragraph("<b>Start</b>", small),
        Paragraph("<b>Range</b>", small),
    ]]
    for letter_code in EXHIBIT_ORDER:
        start = starts[letter_code]
        page_count = counts[letter_code]
        end = start + page_count - 1
        page_range = f"{start}-{end}" if end != start else f"{start}"
        rows.append([
            Paragraph(f"Exhibit {letter_code}", small),
            Paragraph(EXHIBIT_TITLES[letter_code], small),
            Paragraph(str(start), small),
            Paragraph(page_range, small),
        ])

    toc_table = Table(rows, colWidths=[1.0 * inch, 4.2 * inch, 0.6 * inch, 0.8 * inch], repeatRows=1)
    toc_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, "black"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, 0), "#EDEDED"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(toc_table)
    story.append(Spacer(1, 0.10 * inch))
    story.append(
        Paragraph(
            "Each exhibit is preceded by a tab divider and a cover sheet identifying the source file, key source location, supported assertion, and where that assertion appears in the filing papers.",
            base,
        )
    )

    doc_kwargs = dict(
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.85 * inch,
        title="Table Of Exhibits",
    )
    count_doc = SimpleDocTemplate(str(pdf_path), **doc_kwargs)
    import copy
    counter = []

    def count_pages(canvas, _doc):
        counter.append(canvas.getPageNumber())

    count_doc.build(copy.deepcopy(story), onFirstPage=count_pages, onLaterPages=count_pages)
    doc = SimpleDocTemplate(str(pdf_path), **doc_kwargs)
    doc.page_count = len(counter)
    doc.build(story, onFirstPage=binder_page, onLaterPages=binder_page)


def main() -> None:
    COMPILED.mkdir(parents=True, exist_ok=True)
    WORKING.mkdir(parents=True, exist_ok=True)

    front_pdf = COMPILED / "0000_Exhibit_Binder_Front_Sheet.pdf"
    render_front_sheet(COVERS / "EXHIBIT_BINDER_FRONT_SHEET.md", front_pdf)

    packet_paths = []
    packet_starts = {}
    packet_counts = {}
    current_page = pdf_pages(front_pdf) + 1
    current_page += 1  # reserve the table of exhibits page, which is rendered after starts are calculated
    for letter_code in EXHIBIT_ORDER:
        divider_md = COVERS / f"Exhibit_{letter_code}_tab_divider.md"
        divider_pdf = WORKING / f"Exhibit_{letter_code}_tab_divider.pdf"
        render_markdown(divider_md, divider_pdf)

        cover_md = COVERS / f"Exhibit_{letter_code}_cover_sheet.md"
        cover_pdf = WORKING / f"Exhibit_{letter_code}_cover_sheet.pdf"
        render_markdown(cover_md, cover_pdf)

        exhibit_pdf = build_exhibit_pdf(letter_code)

        packet_starts[letter_code] = current_page
        packet_counts[letter_code] = pdf_pages(divider_pdf) + pdf_pages(cover_pdf) + pdf_pages(exhibit_pdf)
        current_page += packet_counts[letter_code]

        merged = COMPILED / f"Exhibit_{letter_code}_packet.pdf"
        merge_pdfs(merged, [divider_pdf, cover_pdf, exhibit_pdf])
        packet_paths.append(merged)
        print(merged)

    write_table_of_exhibits(packet_starts)
    table_pdf = COMPILED / "0001_Table_Of_Exhibits.pdf"
    render_table_of_exhibits_pdf(table_pdf, packet_starts, packet_counts)
    merge_pdfs(
        COMPILED / "MASTER_Exhibit_Binder_Core_Set.pdf",
        [front_pdf, table_pdf, *packet_paths],
    )


if __name__ == "__main__":
    main()
