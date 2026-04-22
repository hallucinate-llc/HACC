from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


ROOT = Path("/home/barberb/HACC")
OUT_DIR = ROOT / "workspace"
AUTH_DIR = OUT_DIR / "controlling_authorities_26FE0586"

LEAD_PDF = OUT_DIR / "justice_court_motion_to_dismiss_26FE0586_lead.pdf"
FINAL_PDF = OUT_DIR / "justice_court_ready_motion_to_dismiss_with_authorities_26FE0586.pdf"

AUTHORITY_PDFS = [
    (
        "Appendix A",
        "42 U.S.C. § 1437p - Demolition and disposition of public housing",
        AUTH_DIR / "42_USC_1437p_govinfo.pdf",
        "Section 18 demolition/disposition authority. This is the controlling statute for demolition/disposition displacement and relocation.",
    ),
    (
        "Appendix B",
        "42 U.S.C. § 1437z-5 - Required conversion to tenant-based assistance",
        AUTH_DIR / "42_USC_1437z-5_govinfo.pdf",
        "Required-conversion authority. Included because 24 C.F.R. Part 972 Subpart A implements required conversion.",
    ),
    (
        "Appendix C",
        "42 U.S.C. § 1437t - Voluntary conversion to tenant-based assistance",
        AUTH_DIR / "42_USC_1437t_govinfo.pdf",
        "Voluntary-conversion authority. Included because 24 C.F.R. Part 972 also cites this authority.",
    ),
    (
        "Appendix D",
        "24 C.F.R. Part 970 - Demolition or Disposition of Public Housing Projects",
        AUTH_DIR / "24_CFR_part_970_govinfo_2025.pdf",
        "HUD demolition/disposition regulation. Section 970.21 is the key relocation provision.",
    ),
    (
        "Appendix E",
        "24 C.F.R. Part 972 - Conversion of Public Housing to Tenant-Based Assistance",
        AUTH_DIR / "24_CFR_part_972_govinfo_2025.pdf",
        "HUD conversion regulation. Section 972.130(b)(4) includes the voucher-at-least-90-days-before-displacement requirement.",
    ),
]


PARAGRAPHS = [
    ("intro", "Defendants Jane Kay Cortez and Benjamin Jay Barber move to dismiss Plaintiff Housing Authority of Clackamas County's residential eviction complaint for failure to state ultimate facts sufficient to constitute a claim for possession."),
    ("intro", "Defendants file this motion in the style used for Oregon residential eviction filings in Justice Court. The summons, complaint, and any notice relied on by Plaintiff are already part of the court file. This combined filing attaches the controlling federal statutes and regulations the Court may need to decide the motion."),
    ("heading", "Request"),
    ("numbered", "Dismiss the residential eviction complaint without prejudice for failure to plead present entitlement to possession."),
    ("numbered", "Alternatively, deny, stay, or abate possession as premature unless and until Plaintiff pleads and proves compliance with the applicable federal public-housing relocation requirements."),
    ("numbered", "Award Defendants costs, disbursements, and any further relief the Court finds just."),
    ("heading", "Grounds for Motion"),
    ("numbered", "Plaintiff is a public housing agency seeking possession in connection with public-housing displacement tied to demolition, disposition, or conversion to tenant-based assistance."),
    ("numbered", "In that setting, present entitlement to possession is controlled by federal relocation law, not only by the expiration of a state-law termination date."),
    ("numbered", "The controlling federal authorities require relocation protections before displacement is treated as complete. Those protections include comparable housing, relocation assistance, notice, counseling, and special rules when voucher assistance is used for relocation."),
    ("numbered", "The complaint does not plead ultimate facts showing that those federal relocation prerequisites were satisfied before Plaintiff filed this FED."),
    ("numbered", "The complaint therefore fails to plead Plaintiff's present entitlement to possession and should be dismissed or, at minimum, abated as premature."),
    ("heading", "Controlling Federal Authorities Attached"),
    ("bullet", "Appendix A: 42 U.S.C. § 1437p, demolition and disposition of public housing."),
    ("bullet", "Appendix B: 42 U.S.C. § 1437z-5, required conversion to tenant-based assistance."),
    ("bullet", "Appendix C: 42 U.S.C. § 1437t, voluntary conversion to tenant-based assistance."),
    ("bullet", "Appendix D: 24 C.F.R. Part 970, including § 970.21."),
    ("bullet", "Appendix E: 24 C.F.R. Part 972, including § 972.130."),
    ("heading", "Why the Federal Authorities Matter"),
    ("numbered", "42 U.S.C. § 1437p controls demolition and disposition of public housing. It requires resident notice 90 days before displacement, comparable housing, relocation expenses, counseling, and no demolition or completed disposition until residents are relocated."),
    ("numbered", "24 C.F.R. § 970.21 implements those relocation protections. It states that tenant-based assistance, including Housing Choice Voucher assistance, is not comparable housing until the family is actually relocated into such housing."),
    ("numbered", "42 U.S.C. § 1437z-5 and 24 C.F.R. Part 972 control required conversion to tenant-based assistance. Section 972.130(b)(4) requires the relocation plan to include written notice and, where Section 8 voucher assistance is used for relocation, to provide the vouchers at least 90 days before displacement."),
    ("numbered", "The legal consequence is straightforward: voucher paperwork, a termination date, or a future move-out deadline is not the same thing as completed federal relocation compliance."),
    ("heading", "Conclusion"),
    ("intro", "Because Plaintiff's possession claim depends on federal public-housing relocation law and the complaint does not plead ultimate facts showing compliance with those controlling prerequisites, Defendants respectfully ask the Court to dismiss the complaint, or alternatively deny, stay, or abate possession as premature."),
]


def wrap(text, width, font="Helvetica", size=11):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if stringWidth(test, font, size) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def footer(c, page, title):
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, f"FED - {title}")
    c.drawRightString(7.75 * inch, 0.45 * inch, f"Page {page}")


def new_page(c, page, title):
    footer(c, page, title)
    c.showPage()
    return page + 1


def render_lead_pdf(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    title = "Motion to Dismiss"
    page = 1
    left = 0.75 * inch
    right = width - 0.75 * inch
    y = height - 0.7 * inch

    def ensure(space):
        nonlocal page, y
        if y - space < 0.8 * inch:
            page = new_page(c, page, title)
            y = height - 0.75 * inch

    # OJD/FED-style court heading.
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "IN THE JUSTICE COURT OF THE STATE OF OREGON")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "FOR THE COUNTY OF CLACKAMAS")
    y -= 0.38 * inch

    # Simple caption table.
    table_top = y
    table_bottom = y - 1.7 * inch
    mid = width / 2
    c.setLineWidth(0.75)
    c.line(left, table_top, right, table_top)
    c.line(left, table_bottom, right, table_bottom)
    c.line(mid, table_top, mid, table_bottom)
    c.setFont("Helvetica", 10)
    c.drawString(left + 0.1 * inch, table_top - 0.25 * inch, "Housing Authority of Clackamas County")
    c.drawString(left + 0.1 * inch, table_top - 0.48 * inch, "Plaintiff (Landlord or Agent)")
    c.drawString(left + 0.1 * inch, table_top - 0.78 * inch, "v.")
    c.drawString(left + 0.1 * inch, table_top - 1.08 * inch, "Jane Kay Cortez, Benjamin Jay Barber,")
    c.drawString(left + 0.1 * inch, table_top - 1.31 * inch, "and All Other Occupants")
    c.drawString(left + 0.1 * inch, table_top - 1.54 * inch, "Defendants (Tenants or Occupants)")
    c.setFont("Helvetica", 10)
    c.drawString(mid + 0.1 * inch, table_top - 0.25 * inch, "Case No: 26FE0586")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(mid + 0.1 * inch, table_top - 0.72 * inch, "MOTION TO DISMISS")
    c.setFont("Helvetica", 9.5)
    c.drawString(mid + 0.1 * inch, table_top - 1.05 * inch, "Failure to State Ultimate Facts")
    c.drawString(mid + 0.1 * inch, table_top - 1.28 * inch, "ORCP 21 A(1)(h)")
    y = table_bottom - 0.35 * inch

    c.setFont("Helvetica", 10.5)
    c.drawString(left, y, "Filed by: Jane Kay Cortez and Benjamin Jay Barber, Defendants pro se")
    y -= 0.22 * inch
    c.drawString(left, y, "Property: 10043 SE 32nd Ave, Milwaukie, OR 97222")
    y -= 0.35 * inch

    para_no = 1
    for kind, text in PARAGRAPHS:
        if kind == "heading":
            ensure(0.55 * inch)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(left, y, text)
            y -= 0.28 * inch
            continue
        if kind == "numbered":
            prefix = f"{para_no}. "
            para_no += 1
            body_left = left + 0.25 * inch
            first_width = right - body_left
            c.setFont("Helvetica", 10.5)
            lines = wrap(text, first_width, "Helvetica", 10.5)
            ensure((len(lines) + 1) * 0.20 * inch)
            c.drawString(left, y, prefix)
            for i, line in enumerate(lines):
                c.drawString(body_left, y, line)
                y -= 0.20 * inch
            y -= 0.08 * inch
            continue
        if kind == "bullet":
            body_left = left + 0.25 * inch
            c.setFont("Helvetica", 10.5)
            lines = wrap(text, right - body_left, "Helvetica", 10.5)
            ensure((len(lines) + 1) * 0.20 * inch)
            c.drawString(left + 0.05 * inch, y, "•")
            for line in lines:
                c.drawString(body_left, y, line)
                y -= 0.20 * inch
            y -= 0.06 * inch
            continue
        c.setFont("Helvetica", 10.5)
        lines = wrap(text, right - left, "Helvetica", 10.5)
        ensure((len(lines) + 1) * 0.20 * inch)
        for line in lines:
            c.drawString(left, y, line)
            y -= 0.20 * inch
        y -= 0.08 * inch

    # Signature.
    ensure(1.7 * inch)
    y -= 0.10 * inch
    c.setFont("Helvetica", 10.5)
    c.drawString(left, y, "DATED: April ___, 2026.")
    y -= 0.45 * inch
    c.drawString(left, y, "Respectfully submitted,")
    y -= 0.42 * inch
    c.drawString(left, y, "__________________________________")
    c.drawString(mid + 0.1 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(left, y, "Benjamin Jay Barber, Defendant pro se")
    c.drawString(mid + 0.1 * inch, y, "Jane Kay Cortez, Defendant pro se")

    # Proposed order.
    page = new_page(c, page, title)
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "IN THE JUSTICE COURT OF THE STATE OF OREGON")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "FOR THE COUNTY OF CLACKAMAS")
    y -= 0.50 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "ORDER ON DEFENDANTS' MOTION TO DISMISS")
    y -= 0.45 * inch
    c.setFont("Helvetica", 10.5)
    for line in [
        "Case No: 26FE0586",
        "The Court has considered Defendants' Motion to Dismiss and the attached controlling federal authorities.",
        "",
        "IT IS ORDERED:",
        "[ ] Defendants' motion is GRANTED. Plaintiff's residential eviction complaint is dismissed without prejudice.",
        "[ ] Defendants' motion is GRANTED IN PART. Possession is denied, stayed, or abated as premature pending a showing of compliance with applicable federal relocation requirements.",
        "[ ] Defendants' motion is DENIED.",
        "[ ] Other: ________________________________________________________________________________",
        "",
        "DATED: ____________________, 2026.",
        "",
        "__________________________________",
        "Judge",
    ]:
        if not line:
            y -= 0.18 * inch
            continue
        for wrapped in wrap(line, right - left, "Helvetica", 10.5):
            c.drawString(left, y, wrapped)
            y -= 0.22 * inch
        y -= 0.04 * inch

    # Certificate of service.
    page = new_page(c, page, title)
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "CERTIFICATE OF SERVICE")
    y -= 0.45 * inch
    c.setFont("Helvetica", 10.5)
    service = [
        "I certify that on April ___, 2026, I served a true copy of this Motion to Dismiss and attached federal authorities on Plaintiff Housing Authority of Clackamas County.",
        "[ ] First-class mail to: Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045.",
        "[ ] Email to: cskee@clackamas.us.",
        "[ ] Hand delivery.",
        "[ ] Other: ________________________________________________________________________________",
        "",
        "__________________________________        __________________________________",
        "Benjamin Jay Barber                         Jane Kay Cortez",
    ]
    for line in service:
        if not line:
            y -= 0.25 * inch
            continue
        for wrapped in wrap(line, right - left, "Helvetica", 10.5):
            c.drawString(left, y, wrapped)
            y -= 0.24 * inch

    footer(c, page, title)
    c.save()


def cover_page(label, title, note, pages):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.9 * inch, label)
    c.setFont("Helvetica-Bold", 13)
    y = 6.35 * inch
    for line in wrap(title, 6.4 * inch, "Helvetica-Bold", 13):
        c.drawCentredString(4.25 * inch, y, line)
        y -= 0.25 * inch
    y -= 0.25 * inch
    c.setFont("Helvetica", 11)
    for line in wrap(note, 6.6 * inch, "Helvetica", 11):
        c.drawCentredString(4.25 * inch, y, line)
        y -= 0.22 * inch
    c.setFont("Helvetica", 10)
    c.drawCentredString(4.25 * inch, 3.7 * inch, f"Official source PDF attached ({pages} pages).")
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, f"FED - Authority Appendix Cover - {label}")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def stamp_page(page, label, page_no):
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFillColor(colors.white)
    c.rect(w - 1.95 * inch, 0.16 * inch, 1.75 * inch, 0.42 * inch, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8.5)
    c.drawRightString(w - 0.25 * inch, 0.42 * inch, label)
    c.drawRightString(w - 0.25 * inch, 0.25 * inch, f"Authority page {page_no}")
    c.save()
    buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])
    return page


def build():
    render_lead_pdf(LEAD_PDF)
    writer = PdfWriter()
    for page in PdfReader(str(LEAD_PDF)).pages:
        writer.add_page(page)
    for label, title, path, note in AUTHORITY_PDFS:
        reader = PdfReader(str(path))
        writer.add_page(cover_page(label, title, note, len(reader.pages)))
        for idx, page in enumerate(reader.pages, 1):
            writer.add_page(stamp_page(page, label, idx))
    with FINAL_PDF.open("wb") as fh:
        writer.write(fh)
    print(FINAL_PDF)


if __name__ == "__main__":
    build()
