#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import textwrap
from io import BytesIO
from email import policy
from email.parser import BytesParser
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path("/home/barberb/HACC")
WORKSPACE = ROOT / "workspace"
EXHIBIT_COVERS = WORKSPACE / "exhibit_cover_pages"
BUILD_DIR = WORKSPACE / "evidence_binder_full_build_2026-04-09"
GENERATED_DIR = BUILD_DIR / "generated_pdfs"
OUTPUT_PDF = WORKSPACE / "evidence_binder_full_2026-04-09.pdf"
LEAN_OUTPUT_PDF = WORKSPACE / "evidence_binder_full_lean_2026-04-09.pdf"
MANIFEST = BUILD_DIR / "manifest.txt"
COURT_READY_INDEX_PDF = WORKSPACE / "evidence_binder_exhibit_and_cover_sheet_index_court_ready_2026-04-09.pdf"
COURT_READY_INDEX_SCRIPT = WORKSPACE / "build_court_ready_binder_index_2026-04-09.py"
FAMILY_OUTPUTS = {
    "Shared Housing / State-Court Binder": WORKSPACE / "evidence_binder_shared_housing_state_court_2026-04-09.pdf",
    "Shared Motion / Probate / Sanctions Binder": WORKSPACE / "evidence_binder_shared_motion_probate_sanctions_2026-04-09.pdf",
    "Supplemental Background Appendix": WORKSPACE / "evidence_binder_supplemental_background_appendix_2026-04-09.pdf",
    "Housing Duty Appendix": WORKSPACE / "evidence_binder_housing_duty_appendix_2026-04-09.pdf",
}
LEAN_FAMILY_OUTPUTS = {
    "Shared Housing / State-Court Binder": WORKSPACE / "evidence_binder_shared_housing_state_court_lean_2026-04-09.pdf",
    "Shared Motion / Probate / Sanctions Binder": WORKSPACE / "evidence_binder_shared_motion_probate_sanctions_lean_2026-04-09.pdf",
    "Supplemental Background Appendix": WORKSPACE / "evidence_binder_supplemental_background_appendix_lean_2026-04-09.pdf",
    "Housing Duty Appendix": WORKSPACE / "evidence_binder_housing_duty_appendix_lean_2026-04-09.pdf",
}
COURT_LINES = [
    "IN THE CIRCUIT COURT OF THE STATE OF OREGON",
    "FOR THE COUNTY OF CLACKAMAS",
    "PROBATE DEPARTMENT",
]
CASE_NO = "Case No. 26PR00641"
MATTER_LINES = [
    "In the Matter of:",
    "Jane Kay Cortez,",
    "Protected Person.",
]


def run(cmd):
    subprocess.run(cmd, check=True)


def ensure_dirs():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def wrap_text(text, width_chars=100):
    out = []
    for para in text.splitlines():
        if not para.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width_chars, replace_whitespace=False, drop_whitespace=False))
    return out


def normalize_inline_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("`", "")
    return text.strip()


def paginate_wrapped_lines(lines, width_chars=105, body_lines_per_page=48):
    wrapped = []
    for raw in lines:
        block = wrap_text(raw, width_chars)
        if not block:
            block = [""]
        wrapped.extend(block)
    pages = []
    for i in range(0, len(wrapped), body_lines_per_page):
        pages.append(wrapped[i:i + body_lines_per_page])
    return pages or [[""]]


def draw_footer(c, width, label, page_num, total_pages):
    footer = f"{label} | Page {page_num} of {total_pages}"
    c.setFont("Times-Roman", 10)
    c.drawString(0.75 * inch, 0.42 * inch, footer)


def render_text_pdf(out_path: Path, title: str, lines, footer_label=None):
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 0.75 * inch
    top = height - 0.75 * inch
    bottom = 1.0 * inch
    line_height = 13
    footer_label = footer_label or title
    pages = paginate_wrapped_lines(lines, width_chars=105, body_lines_per_page=48)
    total_pages = len(pages)

    for page_num, page_lines in enumerate(pages, start=1):
        if page_num > 1:
            c.showPage()
        c.setFont("Times-Bold", 14)
        c.drawString(left, top, title)
        c.setFont("Times-Roman", 12)
        y = top - 0.35 * inch
        for line in page_lines:
            c.drawString(left, y, line)
            y -= line_height
            if y < bottom:
                break
        draw_footer(c, width, footer_label, page_num, total_pages)
    c.save()


def match_backtick_block(text: str, heading: str) -> str:
    pattern = rf"`{re.escape(heading)}`\s+`([^`]+)`"
    m = re.search(pattern, text, re.S)
    return normalize_inline_md(m.group(1)) if m else ""


def match_numbered_block(text: str, heading: str):
    pattern = rf"`{re.escape(heading)}`\s+(.*?)(?:\n`[A-Z][^`]*`|\Z)"
    m = re.search(pattern, text, re.S)
    if not m:
        return []
    body = m.group(1)
    items = []
    for line in body.splitlines():
        line = line.strip()
        if re.match(r"^\d+\.\s+", line):
            items.append(normalize_inline_md(re.sub(r"^\d+\.\s+", "", line)))
    return items


def centered_header(c, y, text, size=15):
    width, _ = letter
    c.setFont("Times-Bold", size)
    c.drawCentredString(width / 2, y, text)


def draw_case_caption(c, top_y):
    width, _ = letter
    left = 0.85 * inch
    right = width - 0.85 * inch
    split_x = width * 0.60
    y = top_y
    c.setLineWidth(1)
    c.line(left, y, right, y)
    c.setFont("Times-Bold", 11)
    c.drawCentredString(width / 2, y - 0.18 * inch, COURT_LINES[0])
    c.setFont("Times-Roman", 11)
    c.drawCentredString(width / 2, y - 0.38 * inch, COURT_LINES[1])
    c.drawCentredString(width / 2, y - 0.56 * inch, COURT_LINES[2])
    c.line(left, y - 0.72 * inch, right, y - 0.72 * inch)
    c.line(split_x, y - 0.72 * inch, split_x, y - 1.58 * inch)

    c.setFont("Times-Roman", 11)
    c.drawString(left + 0.08 * inch, y - 0.98 * inch, "EXHIBIT VOLUME")

    matter_y = y - 0.92 * inch
    for line in MATTER_LINES:
        c.drawString(split_x + 0.12 * inch, matter_y, line)
        matter_y -= 0.16 * inch
    c.drawString(split_x + 0.12 * inch, matter_y - 0.04 * inch, CASE_NO)

    c.line(left, y - 1.58 * inch, right, y - 1.58 * inch)
    return y - 1.84 * inch


def draw_labeled_block(c, x, y, width, label, lines, line_height=13, label_gap=0.18 * inch, bottom_gap=0.16 * inch):
    c.setFont("Times-Bold", 12)
    c.drawString(x, y, label)
    y -= label_gap
    c.setFont("Times-Roman", 12)
    width_chars = max(20, int(width / 5.4))
    for line in lines:
        wrapped = wrap_text(line, width_chars) or [""]
        for part in wrapped:
            c.drawString(x + 0.12 * inch, y, part)
            y -= line_height
    y -= bottom_gap
    return y


def render_binder_title_pdf(out_path: Path, lean_mode: bool):
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 1.0 * inch
    y = draw_case_caption(c, height - 0.95 * inch)
    centered_header(c, y, "EVIDENCE BINDER", 18)
    y -= 0.35 * inch
    centered_header(c, y, "LODGED EXHIBIT VOLUME", 13)
    y -= 0.55 * inch
    c.setLineWidth(1)
    c.line(left, y, width - left, y)
    y -= 0.55 * inch

    blocks = [
        ("Document", ["Lodged exhibit volume for the above-captioned matter."]),
        ("Print Set", ["Deduplicated exhibit print set." if lean_mode else "Full exhibit print set."]),
        ("Submitted By", ["Benjamin Barber, Pro Se"]),
        ("Contents", ["Exhibit schedule, divider pages, exhibit cover sheets, and underlying exhibit source pages."]),
    ]
    for label, lines in blocks:
        y = draw_labeled_block(c, left, y, width - (2 * left), label, lines)

    draw_footer(c, width, "Evidence Binder", 1, 1)
    c.save()


def render_family_divider_pdf(out_path: Path, family: str, labels):
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 0.95 * inch
    y = draw_case_caption(c, height - 0.95 * inch)
    centered_header(c, y, "EXHIBIT SECTION", 14)
    y -= 0.45 * inch
    centered_header(c, y, family.upper(), 16)
    y -= 0.55 * inch
    c.setLineWidth(1)
    c.line(left, y, width - left, y)
    y -= 0.55 * inch
    y = draw_labeled_block(c, left, y, width - (2 * left), "Included Exhibits", [", ".join(labels)])
    draw_footer(c, width, family, 1, 1)
    c.save()


def render_exhibit_tab_pdf(md_path: Path, out_path: Path):
    text = md_path.read_text(errors="replace")
    exhibit_label = match_backtick_block(text, "EXHIBIT LABEL") or "Exhibit"
    section = match_backtick_block(text, "SECTION")
    short_title = match_backtick_block(text, "SHORT TITLE")
    status = match_backtick_block(text, "STATUS")

    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 0.85 * inch
    y = draw_case_caption(c, height - 0.95 * inch)

    centered_header(c, y, "EXHIBIT", 15)
    y -= 0.38 * inch
    centered_header(c, y, exhibit_label.upper(), 20)
    y -= 0.5 * inch
    c.setLineWidth(1)
    c.line(left, y, width - left, y)
    y -= 0.75 * inch
    c.setFont("Times-Bold", 14)
    c.drawCentredString(width / 2, y, short_title)
    y -= 0.55 * inch
    c.setFont("Times-Italic", 11)
    c.drawCentredString(width / 2, y, section)
    y -= 0.3 * inch
    if status:
        c.setFont("Times-Roman", 11)
        c.drawCentredString(width / 2, y, status)
    draw_footer(c, width, exhibit_label, 1, 1)
    c.save()


def render_exhibit_cover_pdf(md_path: Path, out_path: Path):
    text = md_path.read_text(errors="replace")
    exhibit_label = match_backtick_block(text, "EXHIBIT LABEL") or "Exhibit"
    short_title = match_backtick_block(text, "SHORT TITLE")
    source = match_backtick_block(text, "SOURCE FILE")
    relied_on_by = match_numbered_block(text, "RELIED ON BY")
    propositions = match_numbered_block(text, "PROPOSITION(S) THIS EXHIBIT IS OFFERED TO SUPPORT")
    foundation = match_backtick_block(text, "AUTHENTICITY / FOUNDATION NOTE")
    limitation = match_backtick_block(text, "LIMITATION NOTE")

    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 0.75 * inch
    right = width - 0.75 * inch
    y = draw_case_caption(c, height - 0.95 * inch)

    centered_header(c, y, "EXHIBIT COVER SHEET", 15)
    y -= 0.3 * inch
    centered_header(c, y, exhibit_label.upper(), 17)
    y -= 0.35 * inch
    c.setLineWidth(1)
    c.line(left, y, right, y)
    y -= 0.32 * inch

    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "1. Exhibit Label",
        [exhibit_label],
        line_height=12,
    )
    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "2. Short Title",
        [short_title],
        line_height=12,
    )
    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "3. Primary Source Record",
        [source],
        line_height=11,
    )
    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "4. Filings Relying On This Exhibit",
        [f"{i + 1}. {item}" for i, item in enumerate(relied_on_by)] or ["None listed."],
        line_height=12,
    )
    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "5. Propositions This Exhibit Is Offered To Support",
        [f"{i + 1}. {item}" for i, item in enumerate(propositions)] or ["None listed."],
        line_height=12,
    )
    y = draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "6. Authenticity / Foundation Note",
        wrap_text(foundation, 95) or [""],
        line_height=12,
    )
    draw_labeled_block(
        c,
        left,
        y,
        right - left,
        "7. Limitation Note",
        wrap_text(limitation, 95) or [""],
        line_height=12,
    )
    draw_footer(c, width, exhibit_label, 1, 1)
    c.save()


def slugify(label: str) -> str:
    if label.startswith("Authority Exhibit "):
        s = label.replace("Authority Exhibit ", "authority_exhibit_")
        s = s.replace("-", "_").replace(" ", "_")
        return s.lower()
    s = label.replace("Exhibit ", "")
    s = s.replace("-", "_").replace(" ", "_")
    return f"exhibit_{s}"


def family_slug(family: str) -> str:
    return (
        family.lower()
        .replace(" / ", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


FAMILY_DIRS = {
    "Shared Housing / State-Court Binder": [
        "core_housing",
        "secondary_housing",
        "final_housing",
    ],
    "Shared Motion / Probate / Sanctions Binder": [
        "shared_motion_probate_batch1",
        "shared_motion_probate_batch2",
        "shared_motion_probate_batch3",
        "shared_motion_probate_batch4",
        "shared_motion_probate_batch5",
    ],
    "Supplemental Background Appendix": [
        "supplemental_background_appendix",
    ],
    "Housing Duty Appendix": [
        "housing_duty_appendix",
    ],
}


def find_cover_paths(label: str, family: str):
    slug = slugify(label)
    dirs = FAMILY_DIRS[family]
    tab = []
    cover = []
    for dirname in dirs:
        candidate_tab = EXHIBIT_COVERS / dirname / f"{slug}_tab_cover_page.md"
        candidate_cover = EXHIBIT_COVERS / dirname / f"{slug}_cover_page.md"
        if candidate_tab.exists():
            tab.append(candidate_tab)
        if candidate_cover.exists():
            cover.append(candidate_cover)
    if len(tab) != 1 or len(cover) != 1:
        raise FileNotFoundError(f"Could not uniquely locate cover pages for {label}: {tab} / {cover}")
    return tab[0], cover[0]


def convert_md_to_pdf(md_path: Path, output_name: str) -> Path:
    target = GENERATED_DIR / output_name
    if md_path.name.endswith("_tab_cover_page.md"):
        render_exhibit_tab_pdf(md_path, target)
        return target
    if md_path.name.endswith("_cover_page.md"):
        render_exhibit_cover_pdf(md_path, target)
        return target
    temp_input = GENERATED_DIR / f"{output_name}.md"
    shutil.copy2(md_path, temp_input)
    run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(GENERATED_DIR),
            str(temp_input),
        ]
    )
    produced = GENERATED_DIR / f"{temp_input.stem}.pdf"
    if produced != target:
        produced.rename(target)
    temp_input.unlink(missing_ok=True)
    return target


def image_to_pdf(image_path: Path, output_name: str) -> Path:
    out = GENERATED_DIR / output_name
    img = Image.open(image_path)
    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.save(out, "PDF", resolution=150.0)
    return out


def md_or_txt_to_pdf(source_path: Path, output_name: str) -> Path:
    if source_path.suffix.lower() == ".md":
        return convert_md_to_pdf(source_path, output_name)
    text = source_path.read_text(errors="replace").splitlines()
    out = GENERATED_DIR / output_name
    render_text_pdf(out, source_path.name, text, footer_label=source_path.stem)
    return out


def eml_to_pdf(source_path: Path, output_name: str) -> Path:
    with source_path.open("rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    lines = [
        f"File: {source_path}",
        f"Subject: {msg.get('subject', '')}",
        f"From: {msg.get('from', '')}",
        f"To: {msg.get('to', '')}",
        f"Cc: {msg.get('cc', '')}",
        f"Date: {msg.get('date', '')}",
        "",
        "Body:",
        "",
    ]
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    continue
    else:
        try:
            body = msg.get_content()
        except Exception:
            body = ""
    if not body:
        body = "[No plain-text body extracted. See original EML file.]"
    lines.extend(body.splitlines())
    out = GENERATED_DIR / output_name
    render_text_pdf(out, source_path.name, lines, footer_label=source_path.stem)
    return out


def note_pdf(output_name: str, title: str, body_lines) -> Path:
    out = GENERATED_DIR / output_name
    render_text_pdf(out, title, body_lines, footer_label=title)
    return out


def parse_source_from_cover(cover_md: Path) -> str:
    text = cover_md.read_text(errors="replace")
    m = re.search(r"`SOURCE FILE`\s+`([^`]+)`", text, re.S)
    if not m:
        return ""
    return m.group(1).strip()


def source_to_pdf(source: str, label: str, family: str, lean_mode: bool = False) -> Path:
    prefix = f"{family_slug(family)}_{slugify(label)}"
    if lean_mode and (family, label) in LEAN_REPLACEMENTS:
        return note_pdf(
            f"{prefix}_source.pdf",
            f"{label} lean cross-reference",
            LEAN_REPLACEMENTS[(family, label)],
        )
    if not source:
        return note_pdf(
            f"{prefix}_source_note.pdf",
            f"{label} source note",
            ["No source path was parsed from the exhibit cover page."],
        )

    if source.startswith("Not yet obtained.") or source.startswith("Reserved:"):
        return note_pdf(
            f"{prefix}_source_note.pdf",
            f"{label} source note",
            [
                f"Exhibit label: {label}",
                f"Source description: {source}",
                "",
                "This exhibit is a placeholder or reserved demonstrative.",
                "No underlying source file is currently attached in the repository.",
                "Use the tab cover page and exhibit cover page to preserve the slot and limitation note.",
            ],
        )

    source_path = Path(source)
    if not source_path.exists():
        return note_pdf(
            f"{prefix}_source_note.pdf",
            f"{label} source note",
            [
                f"Exhibit label: {label}",
                f"Expected source: {source}",
                "",
                "The referenced source file was not found at build time.",
                "Use the exhibit cover page for the current source and limitation statement.",
            ],
        )

    if source_path.is_dir():
        sample = sorted([p.name for p in source_path.iterdir()])[:20]
        return note_pdf(
            f"{prefix}_source_note.pdf",
            f"{label} directory source note",
            [
                f"Exhibit label: {label}",
                f"Directory source: {source}",
                "",
                "This exhibit source is a directory rather than a single file.",
                "Representative contents:",
                *sample,
            ],
        )

    suffix = source_path.suffix.lower()
    output_name = f"{prefix}_source.pdf"
    if suffix == ".pdf":
        target = GENERATED_DIR / output_name
        shutil.copy2(source_path, target)
        return target
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}:
        return image_to_pdf(source_path, output_name)
    if suffix in {".md", ".txt"}:
        return md_or_txt_to_pdf(source_path, output_name)
    if suffix == ".eml":
        return eml_to_pdf(source_path, output_name)

    return note_pdf(
        f"{prefix}_source_note.pdf",
        f"{label} source note",
        [
            f"Exhibit label: {label}",
            f"Source path: {source}",
            f"Source file type: {suffix or 'unknown'}",
            "",
            "No specialized renderer was configured for this source type.",
            "Use the original file path from the exhibit cover page.",
        ],
    )


ORDER = [
    ("Shared Housing / State-Court Binder", [
        "Exhibit B", "Exhibit C", "Exhibit D", "Exhibit E", "Exhibit G", "Exhibit H", "Exhibit M", "Exhibit O",
        "Exhibit P", "Exhibit R", "Exhibit T", "Exhibit V", "Exhibit W", "Exhibit X", "Exhibit Y", "Exhibit Z",
        "Exhibit AA",
    ]),
    ("Shared Motion / Probate / Sanctions Binder", [
        "Exhibit A", "Exhibit B", "Exhibit C", "Exhibit D", "Exhibit E", "Exhibit F", "Exhibit G", "Exhibit H",
        "Exhibit I", "Exhibit J", "Exhibit K", "Exhibit L", "Exhibit M", "Exhibit N", "Exhibit O", "Exhibit P",
        "Exhibit Q", "Exhibit R", "Exhibit S", "Exhibit T", "Exhibit U", "Exhibit V", "Exhibit W", "Exhibit X",
        "Exhibit Y", "Exhibit Z", "Exhibit AA", "Exhibit AB", "Exhibit AC", "Authority Exhibit 1", "Authority Exhibit 2",
    ]),
    ("Supplemental Background Appendix", [
        *[f"Exhibit A-{i}" for i in range(1, 21)],
        *[f"Exhibit B-{i}" for i in range(1, 15)],
    ]),
    ("Housing Duty Appendix", [f"Exhibit C-{i}" for i in range(1, 8)]),
]

LEAN_REPLACEMENTS = {
    ("Shared Motion / Probate / Sanctions Binder", "Exhibit D"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying November 17 Solomon text source already incorporated in the Shared Motion / Probate / Sanctions Binder at Exhibit C.",
        "",
        "Use Exhibit D cover page for the distinct proposition:",
        "The communication supports threshold notice and awareness arguments tied to Jane's asserted trust and authority situation.",
        "",
        "Incorporated by reference from:",
        "Shared Motion / Probate / Sanctions Binder - Exhibit C",
        "/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml",
    ],
    ("Shared Housing / State-Court Binder", "Exhibit X"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already incorporated in the Shared Housing / State-Court Binder at Exhibit V.",
        "",
        "Use Exhibit X cover page for the distinct proposition:",
        "The Waterleaf / port-out route was active and known to HACC across the January sequence.",
        "",
        "Incorporated by reference from:",
        "Shared Housing / State-Court Binder - Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Shared Housing / State-Court Binder", "Exhibit AA"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already incorporated in the Shared Housing / State-Court Binder at Exhibit V.",
        "",
        "Use Exhibit AA cover page for the distinct proposition:",
        "The March 26 three-option framework and April 30 completion demand remained active.",
        "",
        "Incorporated by reference from:",
        "Shared Housing / State-Court Binder - Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Shared Motion / Probate / Sanctions Binder", "Exhibit W"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already incorporated in the Shared Housing / State-Court Binder at Exhibit V.",
        "",
        "Use Exhibit W cover page for the distinct proposition:",
        "The earlier same-day household-member statement materially differed from the later January 12 removal-side position.",
        "",
        "Incorporated by reference from:",
        "Shared Housing / State-Court Binder - Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Supplemental Background Appendix", "Exhibit B-1"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same Waterleaf application artifact already incorporated in the Shared Housing / State-Court Binder at Exhibit W.",
        "",
        "Use Exhibit B-1 cover page for the distinct proposition:",
        "The Waterleaf relocation and backup-plan route existed.",
        "",
        "Incorporated by reference from:",
        "Shared Housing / State-Court Binder - Exhibit W",
        "/home/barberb/HACC/evidence/history/waterleaf_application.png",
    ],
}


def main():
    lean_mode = "--lean" in sys.argv
    output_pdf = LEAN_OUTPUT_PDF if lean_mode else OUTPUT_PDF
    family_outputs = LEAN_FAMILY_OUTPUTS if lean_mode else FAMILY_OUTPUTS
    ensure_dirs()
    merged_inputs = []
    manifest_lines = []
    family_inputs = {family: [] for family, _ in ORDER}
    manifest_lines.append(f"lean_mode={lean_mode}")
    manifest_lines.append("")

    title_pdf = GENERATED_DIR / "binder_title_page.pdf"
    render_binder_title_pdf(title_pdf, lean_mode)
    merged_inputs.append(str(title_pdf))
    manifest_lines.extend(["## Binder Front Matter", f"- title: {title_pdf}"])

    if COURT_READY_INDEX_SCRIPT.exists():
        run(["python3", str(COURT_READY_INDEX_SCRIPT)])
    if COURT_READY_INDEX_PDF.exists():
        merged_inputs.append(str(COURT_READY_INDEX_PDF))
        manifest_lines.append(f"- index: {COURT_READY_INDEX_PDF}")

    for family, labels in ORDER:
        divider_pdf = GENERATED_DIR / f"{family_slug(family)}_divider_page.pdf"
        render_family_divider_pdf(divider_pdf, family, labels)
        merged_inputs.append(str(divider_pdf))
        family_inputs[family].append(str(divider_pdf))
        manifest_lines.append(f"## {family}")
        manifest_lines.append(f"- divider: {divider_pdf}")
        for label in labels:
            tab_md, cover_md = find_cover_paths(label, family)
            slug = f"{family_slug(family)}_{slugify(label)}"
            tab_pdf = convert_md_to_pdf(tab_md, f"{slug}_tab_cover_page.pdf")
            cover_pdf = convert_md_to_pdf(cover_md, f"{slug}_cover_page.pdf")
            source = parse_source_from_cover(cover_md)
            source_pdf = source_to_pdf(source, label, family, lean_mode=lean_mode)
            merged_inputs.extend([str(tab_pdf), str(cover_pdf), str(source_pdf)])
            family_inputs[family].extend([str(tab_pdf), str(cover_pdf), str(source_pdf)])
            manifest_lines.extend(
                [
                    f"- {label}",
                    f"  tab: {tab_pdf}",
                    f"  cover: {cover_pdf}",
                    f"  source: {source_pdf}",
                ]
            )

    MANIFEST.write_text("\n".join(manifest_lines) + "\n")
    for family, out_path in family_outputs.items():
        if out_path.exists():
            out_path.unlink()
        run(["pdfunite", *family_inputs[family], str(out_path)])
    if output_pdf.exists():
        output_pdf.unlink()
    run(["pdfunite", *merged_inputs, str(output_pdf)])
    print(output_pdf)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise
