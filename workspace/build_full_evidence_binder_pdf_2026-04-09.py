#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import textwrap
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


def render_text_pdf(out_path: Path, title: str, lines):
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    left = 0.75 * inch
    top = height - 0.75 * inch
    bottom = 0.75 * inch
    line_height = 12

    def new_page():
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left, top, title)
        c.setFont("Helvetica", 10)
        return top - 0.35 * inch

    y = new_page()
    for raw in lines:
        for line in wrap_text(raw, 105):
            if y < bottom:
                y = new_page()
            c.drawString(left, y, line)
            y -= line_height
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
    render_text_pdf(out, source_path.name, text)
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
    render_text_pdf(out, source_path.name, lines)
    return out


def note_pdf(output_name: str, title: str, body_lines) -> Path:
    out = GENERATED_DIR / output_name
    render_text_pdf(out, title, body_lines)
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
    ("Shared Housing / State-Court Binder", "Exhibit X"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already printed in full at Exhibit V.",
        "",
        "Use Exhibit X cover page for the distinct proposition:",
        "The Waterleaf / port-out route was active and known to HACC across the January sequence.",
        "",
        "Master printed source:",
        "Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Shared Housing / State-Court Binder", "Exhibit AA"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already printed in full at Exhibit V.",
        "",
        "Use Exhibit AA cover page for the distinct proposition:",
        "The March 26 three-option framework and April 30 completion demand remained active.",
        "",
        "Master printed source:",
        "Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Shared Motion / Probate / Sanctions Binder", "Exhibit W"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same underlying JC Household chain already printed in full at Exhibit V in the shared housing binder.",
        "",
        "Use Exhibit W cover page for the distinct proposition:",
        "The earlier same-day household-member statement materially differed from the later January 12 removal-side position.",
        "",
        "Master printed source:",
        "Shared Housing / State-Court Binder - Exhibit V",
        "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml",
    ],
    ("Supplemental Background Appendix", "Exhibit B-1"): [
        "Lean binder replacement page.",
        "",
        "This exhibit uses the same Waterleaf application artifact already printed in full at Exhibit W in the shared housing binder.",
        "",
        "Use Exhibit B-1 cover page for the distinct proposition:",
        "The Waterleaf relocation and backup-plan route existed.",
        "",
        "Master printed source:",
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

    for family, labels in ORDER:
        manifest_lines.append(f"## {family}")
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
