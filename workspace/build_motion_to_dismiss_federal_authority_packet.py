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

LEAD_PDF = OUT_DIR / "motion_to_dismiss_failure_to_state_claim_26FE0586_federal_authority_lead.pdf"
FINAL_PDF = OUT_DIR / "motion_to_dismiss_failure_to_state_claim_26FE0586_FEDERAL_AUTHORITY_PACKET.pdf"

AUTHORITY_PDFS = [
    (
        "Appendix A",
        "42 U.S.C. § 1437p - Demolition and disposition of public housing",
        AUTH_DIR / "42_USC_1437p_govinfo.pdf",
        "Controls Section 18 demolition/disposition displacement, including 90-day notice, comparable housing, relocation expenses, counseling, and no demolition or completed disposition until residents are relocated.",
    ),
    (
        "Appendix B",
        "42 U.S.C. § 1437z-5 - Required conversion of distressed public housing to tenant-based assistance",
        AUTH_DIR / "42_USC_1437z-5_govinfo.pdf",
        "Statutory authority for required conversion to tenant-based assistance; included because Defendants rely on 24 C.F.R. Part 972 Subpart A.",
    ),
    (
        "Appendix C",
        "42 U.S.C. § 1437t - Voluntary conversion of public housing to tenant-based assistance",
        AUTH_DIR / "42_USC_1437t_govinfo.pdf",
        "Included because 24 C.F.R. Part 972's authority also includes voluntary conversion; useful if HACC characterizes the project under a non-required conversion pathway.",
    ),
    (
        "Appendix D",
        "24 C.F.R. Part 970 - Public Housing Program, Demolition or Disposition of Public Housing Projects",
        AUTH_DIR / "24_CFR_part_970_govinfo_2025.pdf",
        "Implementing regulations for Section 18 demolition/disposition. Section 970.21 is the key relocation rule.",
    ),
    (
        "Appendix E",
        "24 C.F.R. Part 972 - Conversion of Public Housing to Tenant-Based Assistance",
        AUTH_DIR / "24_CFR_part_972_govinfo_2025.pdf",
        "Conversion regulations. Subpart A and section 972.130(b)(4) contain the 90-day voucher-before-displacement provision.",
    ),
]


SECTIONS = [
    ("caption", [
        "Benjamin Jay Barber, pro se",
        "Jane Kay Cortez, pro se",
        "10043 SE 32nd Ave",
        "Milwaukie, OR 97222",
        "971-270-0855",
        "starworks5@gmail.com",
        "",
        "Defendants",
        "",
        "IN THE CLACKAMAS COUNTY JUSTICE COURT",
        "STATE OF OREGON",
        "",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY,",
        "Plaintiff,",
        "",
        "v.",
        "",
        "JANE KAY CORTEZ, BENJAMIN JAY BARBER, and ALL OTHER OCCUPANTS,",
        "Defendants.",
        "",
        "Case No. 26FE0586",
        "",
        "DEFENDANTS' MOTION TO DISMISS FOR FAILURE TO STATE ULTIMATE FACTS SUFFICIENT TO CONSTITUTE A CLAIM",
        "ORCP 21 A(1)(h); 42 U.S.C. §§ 1437p, 1437t, 1437z-5; 24 C.F.R. Parts 970 and 972",
    ]),
    ("body", "Defendants Jane Kay Cortez and Benjamin Jay Barber move to dismiss Plaintiff Housing Authority of Clackamas County's residential eviction complaint for failure to state ultimate facts sufficient to constitute a claim for possession."),
    ("body", "This version of the packet is intentionally focused on the federal authorities controlling disposition of the case. It does not attach the summons, complaint, or 90-day notice because those materials are already part of the court file. Instead, it attaches the controlling U.S. Code and CFR materials the Court may need to decide whether HACC pleaded a present entitlement to possession."),
    ("body", "The central point is legal: where public-housing displacement is tied to demolition, disposition, or conversion to tenant-based assistance, the public housing agency may not treat relocation as complete merely because a termination date has passed or voucher paperwork has been started. The governing federal law requires relocation protections, comparable housing, and, for voucher-based relocation, timing and actual-relocation safeguards."),
    ("heading", "I. Relief Requested"),
    ("body", "Defendants request dismissal without prejudice. Alternatively, Defendants request that possession be denied, stayed, or abated as premature unless and until HACC pleads and proves compliance with the federal relocation prerequisites controlling demolition, disposition, or conversion displacement."),
    ("heading", "II. Controlling Federal Law"),
    ("body", "Section 18 of the United States Housing Act, 42 U.S.C. § 1437p, controls demolition and disposition of public housing. It requires resident notice 90 days before displacement, comparable housing, relocation expenses, counseling, and no demolition or completed disposition until residents are relocated. See Appendix A."),
    ("body", "For required conversion to tenant-based assistance, 42 U.S.C. § 1437z-5 controls. It requires notice 90 days before displacement and comparable-housing protections, with tenant-based assistance satisfying the comparable-housing requirement only upon relocation into such housing. See Appendix B."),
    ("body", "For voluntary conversion to tenant-based assistance, 42 U.S.C. § 1437t is included because Part 972's authority includes it. See Appendix C."),
    ("body", "HUD's Section 18 regulation, 24 C.F.R. Part 970, implements demolition/disposition. Section 970.21 is the key relocation rule: it requires comparable housing, states that tenant-based assistance such as a Housing Choice Voucher is not comparable housing until the family is actually relocated into such housing, prohibits completion of disposition before relocation, and requires notice, expenses, and counseling. See Appendix D."),
    ("body", "HUD's conversion regulation, 24 C.F.R. Part 972, implements conversion to tenant-based assistance. Section 972.130(b)(4) requires a relocation notice and expressly states that where Section 8 voucher assistance is being used for relocation, the family will be provided the vouchers at least 90 days before displacement. See Appendix E."),
    ("heading", "III. Why These Authorities Control the Pleading"),
    ("body", "A residential eviction complaint must plead facts showing present entitlement to possession. Where the plaintiff is a public housing agency using demolition, disposition, or conversion displacement as the basis for possession, present entitlement depends on federal relocation compliance, not merely expiration of a state-law termination date."),
    ("body", "The attached federal authorities make the omitted facts material. HACC needed to plead ultimate facts showing that the required relocation protections had been satisfied, including comparable housing and the federally required treatment of tenant-based voucher assistance. The complaint does not plead those federal prerequisites."),
    ("body", "If HACC relies on voucher-based relocation, the controlling law is especially direct: under 24 C.F.R. § 970.21 and the parallel statutory language, tenant-based assistance does not fulfill comparable housing until the family is actually relocated into such housing; under 24 C.F.R. § 972.130(b)(4)(ii)(F), voucher assistance used for relocation must be provided at least 90 days before displacement."),
    ("heading", "IV. Source and Currency Note"),
    ("body", "The U.S. Code appendices are official govinfo section PDFs for the 2024 edition of Title 42. The CFR appendices are official govinfo PDFs for the 2025 edition of Title 24, Volume 4. The eCFR pages for 24 C.F.R. § 970.21 and Part 972 Subpart A were checked on April 20, 2026, and eCFR displayed Title 24 as up to date through April 16, 2026. The eCFR timeline for the relevant Part 970 and Part 972 materials showed no changes after January 3, 2017."),
    ("heading", "V. Conclusion"),
    ("body", "Because HACC's possession claim depends on federal public-housing relocation law and the complaint does not plead ultimate facts showing compliance with those controlling federal prerequisites, the Court should dismiss the complaint or, at minimum, deny, stay, or abate possession as premature."),
    ("signature", [
        "DATED: April ___, 2026.",
        "",
        "Respectfully submitted,",
        "",
        "______________________________",
        "Benjamin Jay Barber, Defendant pro se",
        "",
        "______________________________",
        "Jane Kay Cortez, Defendant pro se",
    ]),
    ("heading", "PROPOSED ORDER"),
    ("body", "The Court has considered Defendants' Motion to Dismiss for Failure to State Ultimate Facts Sufficient to Constitute a Claim and the attached controlling federal authorities."),
    ("body", "[ ] Defendants' motion is GRANTED. Plaintiff's residential eviction complaint is dismissed without prejudice."),
    ("body", "[ ] Defendants' motion is GRANTED IN PART. Plaintiff's request for possession is denied, stayed, or abated as premature pending a showing of compliance with applicable federal relocation requirements."),
    ("body", "[ ] Defendants' motion is DENIED."),
    ("body", "[ ] Other: ______________________________________________________________________"),
    ("signature", ["DATED: ____________________, 2026.", "", "____________________________________", "Judge"]),
    ("heading", "CERTIFICATE OF SERVICE"),
    ("body", "I certify that on April ___, 2026, I served a true copy of this motion packet on Plaintiff Housing Authority of Clackamas County by first-class mail, email, hand delivery, or other legally permitted method."),
    ("signature", ["______________________________", "Benjamin Jay Barber", "", "______________________________", "Jane Kay Cortez"]),
]


def wrap_text(text, max_width, font="Times-Roman", size=12):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_line_numbers(c, page, title):
    c.setFont("Times-Roman", 8)
    y = 10.0 * inch
    for i in range(1, 29):
        c.drawRightString(0.72 * inch, y, str(i))
        y -= 0.30 * inch
    c.setFont("Times-Roman", 9)
    c.drawString(inch, 0.5 * inch, f"{title} - Page {page}")


def render_lead_pdf(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    title = "DEFENDANTS' MOTION TO DISMISS"
    page = 1
    y = height - 2 * inch
    x = 1.05 * inch
    max_width = width - 2.05 * inch
    line_h = 0.30 * inch
    para = 1

    def new_page():
        nonlocal page, y
        c.showPage()
        page += 1
        y = height - inch
        draw_line_numbers(c, page, title)

    draw_line_numbers(c, page, title)
    for kind, content in SECTIONS:
        if kind == "caption":
            for line in content:
                if not line:
                    y -= line_h
                    continue
                is_bold = line == line.upper() or line.startswith("ORCP")
                c.setFont("Times-Bold" if is_bold else "Times-Roman", 12)
                font = "Times-Bold" if is_bold else "Times-Roman"
                for subline in wrap_text(line, max_width + 0.1 * inch, font, 12):
                    if y < inch:
                        new_page()
                        c.setFont(font, 12)
                    c.drawCentredString(width / 2, y, subline)
                    y -= line_h
            y -= line_h
            continue
        if kind == "heading":
            if y < 1.4 * inch:
                new_page()
            c.setFont("Times-Bold", 12)
            c.drawString(x, y, content)
            y -= line_h * 1.5
            continue
        if kind == "signature":
            c.setFont("Times-Roman", 12)
            for line in content:
                if y < inch:
                    new_page()
                c.drawString(x, y, line)
                y -= line_h
            y -= line_h
            continue
        if y < 1.65 * inch:
            new_page()
        c.setFont("Times-Roman", 12)
        c.drawCentredString(width / 2, y, str(para))
        y -= line_h
        para += 1
        for line in wrap_text(content, max_width):
            if y < inch:
                new_page()
            c.drawString(x, y, line)
            y -= line_h
        y -= line_h
    c.save()


def cover_page(label, title, note, pages):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Times-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.9 * inch, label)
    c.setFont("Times-Bold", 13)
    for i, line in enumerate(wrap_text(title, 6.4 * inch, "Times-Bold", 13)):
        c.drawCentredString(4.25 * inch, 6.25 * inch - i * 0.25 * inch, line)
    c.setFont("Times-Roman", 11)
    y = 5.2 * inch
    for line in wrap_text(note, 6.6 * inch, "Times-Roman", 11):
        c.drawCentredString(4.25 * inch, y, line)
        y -= 0.22 * inch
    c.setFont("Times-Roman", 10)
    c.drawCentredString(4.25 * inch, 3.7 * inch, f"Official source PDF attached ({pages} pages).")
    c.drawString(inch, 0.5 * inch, f"{label} Cover")
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
    c.setFont("Times-Roman", 9)
    c.drawRightString(w - 0.25 * inch, 0.42 * inch, label)
    c.drawRightString(w - 0.25 * inch, 0.25 * inch, f"Authority page {page_no}")
    c.save()
    buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])
    return page


def build_packet():
    render_lead_pdf(LEAD_PDF)
    writer = PdfWriter()
    for p in PdfReader(str(LEAD_PDF)).pages:
        writer.add_page(p)

    for label, title, pdf_path, note in AUTHORITY_PDFS:
        reader = PdfReader(str(pdf_path))
        writer.add_page(cover_page(label, title, note, len(reader.pages)))
        for i, page in enumerate(reader.pages, start=1):
            writer.add_page(stamp_page(page, label, i))

    with FINAL_PDF.open("wb") as fh:
        writer.write(fh)
    print(FINAL_PDF)


if __name__ == "__main__":
    build_packet()
