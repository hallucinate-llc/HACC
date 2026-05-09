from __future__ import annotations

import re
import textwrap
import tempfile
import json
from email import policy
from email.parser import BytesParser
from html import unescape
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "Collateral Estoppel" / "drafts" / "print_build_2026-04-27"
OUT = OUT_DIR / "probate_sanctions_exhibits_binder_with_source_documents_2026-04-28.pdf"
INDEX_MD = OUT_DIR / "probate_sanctions_exhibits_binder_with_source_documents_index_2026-04-28.md"

PAGE_W, PAGE_H = letter
LEFT = RIGHT = 0.85 * inch
TOP = 0.8 * inch
BOTTOM = 0.65 * inch
BODY_FONT = "Times-Roman"
BOLD_FONT = "Times-Bold"
SIZE = 11
LINE_H = 14


GV_DIR = "evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized"
BLUESTONE_DIR = "evidence/email_imports/starworks5-alex-bluestone-manual-imap-2026-04-25"


def existing_files(*paths: str) -> list[str]:
    return [p for p in paths if (ROOT / p).exists()]


def google_voice_source_files() -> list[str]:
    records = [
        "14159-solomon-gv-ed9289921a300dc7",
        "14160-Me-to-solomon-gv-7cb858000dea7723",
        "14161-Me-to-solomon-gv-b2df7cbf8706d9fe",
        "14163-Me-to-solomon-gv-7540e6c07566a84a",
        "14164-Me-to-solomon-gv-3f38fb3f900d4de1",
        "14165-Me-to-solomon-gv-e6594297d713efde",
        "14166-Me-to-solomon-gv-0eb16863d122188b",
    ]
    out: list[str] = []
    for record in records:
        base = ROOT / GV_DIR / record
        for name in ["transcript.txt", "event.json", "source.html"]:
            path = base / name
            if path.exists():
                out.append(str(path.relative_to(ROOT)))
        for subdir in ["enrichments", "attachments"]:
            folder = base / subdir
            if folder.exists():
                out.extend(str(p.relative_to(ROOT)) for p in sorted(folder.iterdir()) if p.is_file())
    return out


def bluestone_source_files() -> list[str]:
    records = [
        "2026-04-15_753379_Re-Barber-Cortez---Mailing-received",
        "2026-04-15_753380_Re-Barber-Cortez---Mailing-received",
        "2026-04-15_753391_Re-Barber-Cortez---Mailing-received",
        "2026-04-20_755066_Re-Barber-Cortez---Mailing-received",
    ]
    out: list[str] = []
    for record in records:
        base = ROOT / BLUESTONE_DIR / record
        for name in ["message.json", "message.eml"]:
            path = base / name
            if path.exists():
                out.append(str(path.relative_to(ROOT)))
        attach = base / "attachments"
        if attach.exists():
            out.extend(str(p.relative_to(ROOT)) for p in sorted(attach.iterdir()) if p.is_file())
    return out


EXHIBITS = [
    {
        "label": "Exhibit 1",
        "title": "First Amended Guardianship Petition",
        "purpose": "Source pleading challenged by the objection and ORCP 17 sanctions motion.",
        "files": [
            "evidence/history/Solomon Motion for Guardianship.pdf",
            "Collateral Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt",
        ],
    },
    {
        "label": "Exhibit 2",
        "title": "Writ of Assistance Materials",
        "purpose": "Shows the coercive relief requested or obtained through the probate proceeding.",
        "files": [
            "evidence/paper documents/writ of assistance solomon barber.pdf",
            "workspace/writ_of_assistance_solomon_barber_ocr.txt",
        ],
    },
    {
        "label": "Exhibit 3",
        "title": "Restraining Order Materials, Case No. 25PO11530",
        "purpose": "Shows the protective-order context omitted from the probate petition.",
        "files": [
            "evidence/history/sam barber restraining order.pdf",
            "Collateral Estoppel/evidence_notes/solomon_order_digest.md",
        ],
    },
    {
        "label": "Exhibit 4",
        "title": "Probate Petition False-Allegation Matrix",
        "purpose": "Maps petition allegations to contested proof issues and impeachment categories.",
        "files": [
            "Collateral Estoppel/drafts/motion_3_probate_petition_false_allegation_matrix_2026-04-26.md",
        ],
    },
    {
        "label": "Exhibit 5",
        "title": "Google Voice / Google Takeout Impeachment Materials",
        "purpose": "Summarizes and attaches source records for Solomon's own statements relevant to notice, service, compliance, motive, and collateral attack.",
        "files": [
            "Collateral Estoppel/evidence_notes/solomon_google_voice_text_impeachment_exhibit_matrix_2026-04-26.md",
            "Collateral Estoppel/evidence_notes/solomon_probate_allegations_vs_google_voice_knowledge_comparison_2026-04-26.md",
        ] + google_voice_source_files(),
    },
    {
        "label": "Exhibit 6",
        "title": "HACC / Quantum and Household-Composition Materials",
        "purpose": "Supports the disputed housing-causation and lease-removal issues, with available HACC paper-document sources included.",
        "files": [
            "Collateral Estoppel/evidence_notes/delay_apportionment_timeline_solomon_vs_quantum_2026-04-07.md",
            "Collateral Estoppel/evidence_notes/jc_household_chain_household_composition_findings_2026-04-07.md",
            "Collateral Estoppel/evidence_notes/household_submission_and_participation_chronology_2026-04-09.md",
        ] + existing_files(
            "evidence/paper documents/HACC add to lease.pdf",
            "evidence/paper documents/HACC financial requests.pdf",
            "evidence/paper documents/HACC inspection.pdf",
            "evidence/paper documents/HACC 90 day notice.pdf",
            "evidence/paper documents/HACC 90 day notice 2.pdf",
            "evidence/paper documents/HACC 90 day notice 3.pdf",
            "evidence/paper documents/HACC Jan 2026 blossom.pdf",
            "evidence/paper documents/HACC 2024 relocation.pdf",
            "evidence/paper documents/HACC phase2 2024.pdf",
            "evidence/paper documents/HACC first amendment.pdf",
        ),
    },
    {
        "label": "Exhibit 7",
        "title": "Jane and Benjamin Declaration Materials",
        "purpose": "Supports residence history, relationship, inspection, lease-removal, and Jane's position.",
        "files": [
            "Collateral Estoppel/drafts/final_filing_set/04_declaration_of_benjamin_barber_in_support_of_motions_final.md",
            "Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/04_declaration_of_benjamin_barber_in_support_of_motions_final.pdf",
            "Collateral Estoppel/evidence_notes/jane_cortez_declaration_april_8_2026_ocr.txt",
            "evidence/paper documents/Declaration of Jane Cortez April 8th 2026.pdf",
            "workspace/declaration_of_jane_cortez_march_23_2026_inspection_court_ready.md",
            "workspace/declaration_of_benjamin_barber_march_23_2026_inspection_court_ready.md",
        ],
    },
    {
        "label": "Exhibit 8",
        "title": "Trust / Inheritance Materials",
        "purpose": "Supports the objection that no-alternative and estate-value allegations require source proof.",
        "files": [
            "evidence/paper documents/Gerald miller jane cortez trust.pdf",
        ],
    },
    {
        "label": "Exhibit 9",
        "title": "Sanctions Exhibit Readiness Review",
        "purpose": "Identifies which allegations are ready for proof and which require supplementation.",
        "files": [
            "Collateral Estoppel/evidence_notes/motion_3_sanctions_exhibit_readiness_review_2026-04-26.md",
        ],
    },
    {
        "label": "Exhibit 10",
        "title": "University Place Hotel Reservation",
        "purpose": "Supports a concrete less-restrictive short-term housing alternative.",
        "files": [
            "evidence/paper documents/Gmail - Reservation Confirmation for Benjamin Barber Checking In_ 2026-04-30.pdf",
        ],
    },
    {
        "label": "Exhibit 11",
        "title": "Alex Bluestone Notice And Production-Demand Source Emails",
        "purpose": "Attaches source email records showing counsel notice, the demand for court-ordered production, counsel's response, and the April 20 follow-up.",
        "files": bluestone_source_files(),
    },
]


def clean_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2610", "[ ]")
    return text


def html_to_text(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>|</div>|</li>|</tr>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def json_to_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if isinstance(data, dict) and {"date", "from", "to", "subject"} & set(data):
        headers = [
            f"Date: {data.get('date', '')}",
            f"From: {data.get('from', '')}",
            f"To: {data.get('to', '')}",
            f"Cc: {data.get('cc', '')}",
            f"Subject: {data.get('subject', '')}",
            "",
            "Body text:",
            data.get("body_text") or data.get("text") or "",
        ]
        return "\n".join(headers)
    return json.dumps(data, indent=2, ensure_ascii=False)


def eml_to_text(path: Path) -> str:
    msg = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    headers = [
        f"Date: {msg.get('date', '')}",
        f"From: {msg.get('from', '')}",
        f"To: {msg.get('to', '')}",
        f"Cc: {msg.get('cc', '')}",
        f"Subject: {msg.get('subject', '')}",
        "",
        "Body:",
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
                    body = html_to_text(part.get_content())
                    break
    else:
        body = msg.get_content()
        if msg.get_content_type() == "text/html":
            body = html_to_text(body)
    return "\n".join(headers) + "\n" + str(body)


def wrap_line(line: str, width: float, font: str = BODY_FONT, size: int = SIZE) -> list[str]:
    if not line:
        return [""]
    words = line.split()
    out: list[str] = []
    cur = ""
    for word in words:
        test = word if not cur else f"{cur} {word}"
        if stringWidth(test, font, size) <= width:
            cur = test
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out or [""]


def draw_footer(c: canvas.Canvas, label: str, page_no: int) -> None:
    c.setFont(BODY_FONT, 8)
    c.drawString(LEFT, 0.38 * inch, label[:80])
    c.drawRightString(PAGE_W - RIGHT, 0.38 * inch, f"Page {page_no}")


def render_text_pdf(dest: Path, title: str, body: str, footer: str) -> None:
    c = canvas.Canvas(str(dest), pagesize=letter)
    y = PAGE_H - TOP
    page_no = 1
    draw_footer(c, footer, page_no)

    def new_page() -> None:
        nonlocal y, page_no
        c.showPage()
        page_no += 1
        y = PAGE_H - TOP
        draw_footer(c, footer, page_no)

    def line(text: str = "", font: str = BODY_FONT, size: int = SIZE, leading: int = LINE_H) -> None:
        nonlocal y
        if y < BOTTOM + leading:
            new_page()
        c.setFont(font, size)
        c.drawString(LEFT, y, text)
        y -= leading

    for part in wrap_line(title.upper(), PAGE_W - LEFT - RIGHT, BOLD_FONT, 13):
        line(part, BOLD_FONT, 13, 18)
    line()

    for raw in clean_md(body).splitlines():
        stripped = raw.strip()
        if not stripped:
            y -= 6
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip().upper()
            y -= 4
            for part in wrap_line(heading, PAGE_W - LEFT - RIGHT, BOLD_FONT, 11):
                line(part, BOLD_FONT, 11, 15)
            continue
        indent = 0.2 * inch if stripped.startswith(("-", ">", "*")) else 0
        prefix = ""
        if stripped.startswith(">"):
            stripped = stripped.lstrip("> ").strip()
            prefix = '"'
        for i, part in enumerate(wrap_line(stripped, PAGE_W - LEFT - RIGHT - indent)):
            if y < BOTTOM + LINE_H:
                new_page()
            c.setFont(BODY_FONT, SIZE)
            c.drawString(LEFT + indent, y, (prefix if i == 0 else "") + part)
            y -= LINE_H
    c.save()


def render_image_pdf(dest: Path, source: Path, footer: str) -> None:
    c = canvas.Canvas(str(dest), pagesize=letter)
    draw_footer(c, footer, 1)
    c.setFont(BOLD_FONT, 12)
    c.drawString(LEFT, PAGE_H - TOP, source.name[:85])
    image = ImageReader(str(source))
    iw, ih = image.getSize()
    max_w = PAGE_W - LEFT - RIGHT
    max_h = PAGE_H - TOP - BOTTOM - 0.45 * inch
    scale = min(max_w / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    x = (PAGE_W - w) / 2
    y = BOTTOM + (max_h - h) / 2
    c.drawImage(image, x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")
    c.save()


def render_source_pdf(dest: Path, path: Path, footer: str) -> None:
    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        render_image_pdf(dest, path, footer)
        return
    if suffix == ".json":
        body = json_to_text(path)
    elif suffix == ".eml":
        body = eml_to_text(path)
    elif suffix in {".html", ".htm"}:
        body = html_to_text(path.read_text(encoding="utf-8", errors="replace"))
    else:
        body = path.read_text(encoding="utf-8", errors="replace")
    render_text_pdf(dest, path.name, body, footer)


def cover_pdf(dest: Path, label: str, title: str, purpose: str, files: list[str]) -> None:
    body = "\n".join(
        [
            f"{label}",
            "",
            title,
            "",
            "Purpose:",
            purpose,
            "",
            "Source files included:",
            *[f"- {f}" for f in files],
        ]
    )
    render_text_pdf(dest, f"{label}: {title}", body, label)


def append_pdf(writer: PdfWriter, path: Path) -> int:
    reader = PdfReader(str(path))
    for page in reader.pages:
        writer.add_page(page)
    return len(reader.pages)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    manifest: list[tuple[str, str, int, str]] = []
    missing: list[str] = []

    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)

        index_lines = [
            "# Exhibit Binder Index",
            "",
            "Case No. 26PR00641",
            "In the Matter of Jane Kay Cortez",
            "Objector Benjamin Barber",
            "Prepared April 27, 2026",
            "",
        ]
        for ex in EXHIBITS:
            index_lines.append(f"- {ex['label']}: {ex['title']}")
        index = tmp / "00_index.pdf"
        render_text_pdf(index, "Exhibit Binder Index", "\n".join(index_lines), "EXHIBIT BINDER INDEX - 26PR00641")
        append_pdf(writer, index)

        for ex in EXHIBITS:
            cover = tmp / f"{ex['label'].replace(' ', '_')}_cover.pdf"
            cover_pdf(cover, ex["label"], ex["title"], ex["purpose"], ex["files"])
            added = append_pdf(writer, cover)
            page_count = added
            for rel in ex["files"]:
                path = ROOT / rel
                if not path.exists():
                    missing.append(rel)
                    continue
                if path.suffix.lower() == ".pdf":
                    page_count += append_pdf(writer, path)
                else:
                    rendered = tmp / f"{ex['label'].replace(' ', '_')}_{len(manifest)}.pdf"
                    render_source_pdf(rendered, path, f"{ex['label']} - {path.name}")
                    page_count += append_pdf(writer, rendered)
            manifest.append((ex["label"], ex["title"], page_count, "; ".join(ex["files"])))

    with OUT.open("wb") as f:
        writer.write(f)

    lines = [
        "# Probate Sanctions Exhibits Binder Index With Source Documents",
        "",
        "Case No. 26PR00641",
        "In the Matter of Jane Kay Cortez",
        "Objector Benjamin Barber",
        "Prepared April 28, 2026",
        "",
        "| Exhibit | Title | Binder pages | Source files |",
        "|---|---:|---:|---|".replace("---:", "---"),
    ]
    for label, title, pages, files in manifest:
        lines.append(f"| {label} | {title} | {pages} | {files} |")
    if missing:
        lines.extend(["", "## Missing source files", "", *[f"- {m}" for m in missing]])
    INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
