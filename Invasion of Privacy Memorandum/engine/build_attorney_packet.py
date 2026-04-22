#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs" / "attorney_packet"
COMBINED_PACKET = OUTPUT_DIR / "combined_attorney_packet_live_in_aide_2br.pdf"
LEGACY_EXHIBIT_B = OUTPUT_DIR / "exhibit_b_reasonable_accommodation_record.pdf"

MARKDOWN_OUTPUTS = [
    {
        "source": ROOT / "docs" / "attorney_cover_note_live_in_aide_2br.md",
        "pdf": OUTPUT_DIR / "attorney_cover_note_live_in_aide_2br.pdf",
        "txt": OUTPUT_DIR / "attorney_cover_note_live_in_aide_2br.txt",
    },
    {
        "source": ROOT / "docs" / "formal_section_504_memorandum_of_law.md",
        "pdf": OUTPUT_DIR / "formal_section_504_memorandum_of_law.pdf",
        "txt": OUTPUT_DIR / "formal_section_504_memorandum_of_law.txt",
    },
    {
        "source": ROOT / "docs" / "oregon_article_i_section_9_privacy_research_note.md",
        "pdf": OUTPUT_DIR / "oregon_article_i_section_9_privacy_research_note.pdf",
        "txt": OUTPUT_DIR / "oregon_article_i_section_9_privacy_research_note.txt",
    },
]

SOURCE_EXHIBITS = {
    "exhibit_a_privacy_slides.pdf": ROOT.parent / "evidence" / "history" / "privacy slides portrait.pdf",
    "exhibit_b_doctor_verification_and_accommodation_record.pdf": ROOT.parent / "evidence" / "history" / "Reasonable accomidation.pdf",
}

PACKET_ORDER = [
    OUTPUT_DIR / "attorney_cover_note_live_in_aide_2br.pdf",
    OUTPUT_DIR / "formal_section_504_memorandum_of_law.pdf",
    OUTPUT_DIR / "exhibit_a_privacy_slides.pdf",
    OUTPUT_DIR / "exhibit_b_doctor_verification_and_accommodation_record.pdf",
    OUTPUT_DIR / "exhibit_c_affordability_range_record.pdf",
    OUTPUT_DIR / "oregon_article_i_section_9_privacy_research_note.pdf",
]


def _normalize_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    return escape(text)


def _markdown_blocks(text: str) -> list[tuple[str, int | list[str] | str]]:
    blocks: list[tuple[str, int | list[str] | str]] = []
    paragraph_lines: list[str] = []
    bullet_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            blocks.append(("paragraph", " ".join(line.strip() for line in paragraph_lines)))
            paragraph_lines = []

    def flush_bullets() -> None:
        nonlocal bullet_lines
        if bullet_lines:
            blocks.append(("bullets", bullet_lines[:]))
            bullet_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue
        if stripped.startswith("#"):
            flush_paragraph()
            flush_bullets()
            level = len(stripped) - len(stripped.lstrip("#"))
            blocks.append(("heading", level, stripped[level:].strip()))
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            bullet_lines.append(stripped[2:].strip())
            continue
        if bullet_lines:
            bullet_lines[-1] = f"{bullet_lines[-1]} {stripped}"
            continue
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_bullets()
    return blocks


def _render_markdown_pdf(source_path: Path, pdf_path: Path, txt_path: Path) -> None:
    _require_file(source_path)
    text = source_path.read_text()
    txt_path.write_text(text)

    styles = getSampleStyleSheet()
    heading_styles = {
        1: styles["Title"],
        2: styles["Heading1"],
        3: styles["Heading2"],
        4: styles["Heading3"],
    }
    body_style = styles["BodyText"]
    bullet_style = ParagraphStyle(
        "PacketBullet",
        parent=body_style,
        leftIndent=18,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    story = []
    for block in _markdown_blocks(text):
        kind = block[0]
        if kind == "heading":
            _, level, heading_text = block
            style = heading_styles.get(level, styles["Heading4"])
            story.append(Paragraph(_normalize_inline(str(heading_text)), style))
            story.append(Spacer(1, 8))
        elif kind == "paragraph":
            _, paragraph_text = block
            story.append(Paragraph(_normalize_inline(str(paragraph_text)), body_style))
            story.append(Spacer(1, 6))
        elif kind == "bullets":
            _, items = block
            for item in items:
                story.append(Paragraph(f"• {_normalize_inline(item)}", bullet_style))
            story.append(Spacer(1, 4))

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    doc.build(story)


def _refresh_rendered_documents() -> None:
    for item in MARKDOWN_OUTPUTS:
        _render_markdown_pdf(item["source"], item["pdf"], item["txt"])


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required PDF: {path}")


def _refresh_source_exhibits() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_EXHIBIT_B.exists():
        LEGACY_EXHIBIT_B.unlink()
    for output_name, source_path in SOURCE_EXHIBITS.items():
        _require_file(source_path)
        shutil.copy2(source_path, OUTPUT_DIR / output_name)


def _build_combined_packet() -> None:
    writer = PdfWriter()
    for pdf_path in PACKET_ORDER:
        _require_file(pdf_path)
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            writer.add_page(page)
    with COMBINED_PACKET.open("wb") as handle:
        writer.write(handle)


def main() -> None:
    _refresh_rendered_documents()
    _refresh_source_exhibits()
    _build_combined_packet()
    print(COMBINED_PACKET)


if __name__ == "__main__":
    main()