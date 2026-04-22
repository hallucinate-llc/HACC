from pathlib import Path
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


ROOT = Path("/home/barberb/HACC")
OUT_DIR = ROOT / "workspace"
OUT_DIR.mkdir(exist_ok=True)

LEAD_PDF = OUT_DIR / "motion_to_dismiss_failure_to_state_claim_26FE0586_court_style_lead.pdf"
APPENDIX_PDF = OUT_DIR / "motion_to_dismiss_failure_to_state_claim_26FE0586_authority_appendix.pdf"
FINAL_PDF = OUT_DIR / "motion_to_dismiss_failure_to_state_claim_26FE0586_READY_TO_FILE_PACKET.pdf"

COMPLAINT_PDF = ROOT / "complaint-generator/artifacts/eviction_docket_26fe0586/source_documents/evidence/Housing Authority Clackamas County Eviction.pdf"
JAN8_PDF = ROOT / "workspace/temporary-cli-session-migration/prior-research-results/emergency_motion_packet/exhibits/Exhibit G - HACC Jan 2026 blossom.pdf"
VOUCHER_PDF = ROOT / "workspace/temporary-cli-session-migration/prior-research-results/emergency_motion_packet/exhibits/Exhibit M - starworks5-ktilton-orientation-import/0004-RE-HCV-Orientation-384b5cd567d449f0b12b983bf00d576b-clackamas.us/attachments/VO---JC---03.19.2026.pdf"
ORIENTATION_PDF = ROOT / "workspace/temporary-cli-session-migration/prior-research-results/emergency_motion_packet/exhibits/Exhibit M - starworks5-ktilton-orientation-import/0007-RE-HCV-Orientation-f9ca224dab4a4487bb20b9f7ff33afbe-clackamas.us/attachments/Orientation---Required-Signatures-03.19.2026.pdf"


MOTION_PARAGRAPHS = [
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
        "ORCP 21 A(1)(h); ORS 105.123; ORS 105.124; 42 U.S.C. § 1437p; 24 C.F.R. §§ 970.21, 972.130",
    ]),
    ("body", "Defendants Jane Kay Cortez and Benjamin Jay Barber move to dismiss Plaintiff Housing Authority of Clackamas County's residential eviction complaint for failure to state ultimate facts sufficient to constitute a claim for possession."),
    ("body", "This motion is made under ORCP 21 A(1)(h), under Oregon FED pleading requirements, and under the federal relocation framework triggered by HACC's own attached demolition-based termination notice. The complaint does not plead ultimate facts showing HACC is presently entitled to possession."),
    ("body", "The complaint was signed April 1, 2026. HACC's attached notice seeks a March 31, 2026 vacate date because HACC says it will demolish the building. But the record attached to this motion shows that HACC was still administering the Tenant Protection Voucher and relocation path in March 2026. HACC has not pleaded that Defendants received voucher-based relocation assistance at least 90 days before displacement, nor that Defendants had actually relocated into comparable housing."),
    ("heading", "I. Relief Requested"),
    ("body", "Defendants request an order dismissing the residential eviction complaint without prejudice. Alternatively, Defendants request that possession be denied, stayed, or abated as premature until HACC pleads and proves compliance with the applicable federal relocation conditions precedent. Defendants also request costs and any other relief the Court finds just."),
    ("heading", "II. Facts Shown by the Pleading and Attached Record"),
    ("body", "HACC filed this residential eviction case as Case No. 26FE0586 in Clackamas County Justice Court. The summons is dated April 1, 2026 and set first appearance for April 16, 2026 at 3:30 p.m. See Exhibit 1."),
    ("body", "The complaint is dated April 1, 2026 and stamped April 2, 2026. It identifies the premises as 10043 SE 32nd Ave, Milwaukie, Oregon 97222 and seeks possession based on a 90-day notice. See Exhibit 1."),
    ("body", "The attached notice is titled '90 Day Lease Termination Notice without Cause,' dated December 23, 2025, and sets a lease termination and vacate date of March 31, 2026. See Exhibit 1."),
    ("body", "The notice states that HACC is terminating the lease because in or about May 2026 HACC will demolish the building in which Defendants' housing unit is located. See Exhibit 1."),
    ("body", "The notice also acknowledges that the tenancy is subsidized and that HACC will enforce termination only by judicial action. See Exhibit 1."),
    ("body", "HACC's January 8, 2026 Blossom / Tenant Protection Voucher notice told Jane Cortez she had to choose between moving forward with Blossom and Community Apartments or looking for a unit on the open market using a Tenant Protection Voucher. See Exhibit 2."),
    ("body", "The March 19, 2026 voucher materials show that HACC was still issuing voucher-related papers in March 2026. See Exhibits 3 and 4."),
    ("body", "The complaint does not plead that Defendants were actually relocated before HACC filed this FED. It does not plead that Defendants received voucher-based relocation assistance at least 90 days before displacement. It does not plead that voucher assistance had matured into comparable housing by actual relocation into such housing. It does not plead completion of relocation counseling, moving-expense support, comparable-housing placement, or related required relocation steps."),
    ("heading", "III. Statement of Authorities"),
    ("body", "ORCP 21 A(1)(h) allows a defendant to move to dismiss for failure to state ultimate facts sufficient to constitute a claim. The relevant Oregon FED pleading statutes require the complaint to state that the plaintiff is entitled to possession and require attachment of the notice relied on. See Authority Appendix A."),
    ("body", "The attached notice makes this a public-housing displacement tied to demolition, not a routine private holdover. Section 18 of the United States Housing Act, 42 U.S.C. § 1437p, and HUD's implementing regulation, 24 C.F.R. § 970.21, impose relocation duties before a public housing agency may treat displacement as complete. See Authority Appendix B."),
    ("body", "HUD's relocation rule treats tenant-based assistance differently from completed comparable housing: voucher assistance does not become comparable housing until actual relocation into that housing. See Authority Appendix B."),
    ("body", "If HACC relies on required-conversion rules, 24 C.F.R. § 972.130(b)(4) confirms that where voucher assistance is used for relocation, the family must be provided vouchers at least 90 days before displacement. See Authority Appendix B."),
    ("heading", "IV. Argument"),
    ("body", "HACC's complaint fails because it omits the ultimate facts needed to show present entitlement to possession. The attached notice pleads the federal trigger: demolition of the public-housing building. Once HACC chose that basis for displacement, HACC's entitlement to possession depended on more than the expiration of a state-law termination date."),
    ("body", "HACC had to plead facts showing satisfaction of the federal relocation protections that apply to the displacement. The complaint does not allege actual relocation into comparable housing. It does not allege voucher assistance provided at least 90 days before displacement. It does not allege completion of comparable-housing placement, counseling, relocation-expense support, or other relocation steps."),
    ("body", "Those omissions are not technical. They go to the core of HACC's possession theory. If HACC may not lawfully displace residents until relocation protections are satisfied, then a complaint seeking immediate possession without pleading those facts fails to state a present claim."),
    ("body", "The chronology also shows prematurity. The attached notice set March 31, 2026 as the vacate date and HACC filed the FED on April 1, 2026. Yet HACC's January 8, 2026 notice put Defendants into a Blossom-or-TPV choice, and HACC was still issuing voucher materials on March 19, 2026. A March 19 voucher process cannot satisfy a 90-day-before-displacement condition for a March 31 displacement date or an April 1 FED filing."),
    ("body", "The complaint also appears internally inconsistent about the notice theory. It seeks possession based on a 90-day notice, while the notice is expressly without stated cause and identifies demolition as the real reason. HACC cannot avoid federal relocation duties by treating a demolition-based public-housing displacement as an ordinary Oregon no-cause or stated-cause holdover."),
    ("heading", "V. Formatting and Source Appendix"),
    ("body", "This packet includes a court-format and authority appendix so the Court has the core procedural, legal, and record sources in one PDF. The lead motion is prepared on letter-size pages, with one-inch margins, numbered lines, first-page top spacing, footer identification, caption, title, and a statement of authorities. Exhibits are marked and indexed."),
    ("heading", "VI. Conclusion"),
    ("body", "HACC's complaint does not plead the ultimate facts required to show present entitlement to possession. The attached notice shows that HACC seeks displacement because of public-housing demolition. Federal law required HACC to complete relocation protections before treating displacement as complete or using an FED as an ordinary holdover mechanism. Defendants respectfully ask the Court to dismiss the complaint, or alternatively deny, stay, or abate possession as premature."),
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
]


ORDER_TEXT = [
    ("caption", [
        "IN THE CLACKAMAS COUNTY JUSTICE COURT",
        "STATE OF OREGON",
        "",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY, Plaintiff,",
        "v.",
        "JANE KAY CORTEZ, BENJAMIN JAY BARBER, and ALL OTHER OCCUPANTS, Defendants.",
        "",
        "Case No. 26FE0586",
        "",
        "ORDER ON DEFENDANTS' MOTION TO DISMISS",
    ]),
    ("body", "The Court has considered Defendants' Motion to Dismiss for Failure to State Ultimate Facts Sufficient to Constitute a Claim."),
    ("body", "IT IS ORDERED:"),
    ("body", "[ ] Defendants' motion is GRANTED. Plaintiff's residential eviction complaint is dismissed without prejudice."),
    ("body", "[ ] Defendants' motion is GRANTED IN PART. Plaintiff's request for possession is denied, stayed, or abated as premature pending a showing of compliance with applicable federal relocation requirements."),
    ("body", "[ ] Defendants' motion is DENIED."),
    ("body", "[ ] Other: ______________________________________________________________________"),
    ("signature", ["DATED: ____________________, 2026.", "", "____________________________________", "Judge"]),
]


SERVICE_TEXT = [
    ("heading", "CERTIFICATE OF SERVICE"),
    ("body", "I certify that on April ___, 2026, I served a true copy of this motion packet on Plaintiff Housing Authority of Clackamas County by the following method:"),
    ("body", "[ ] First-class mail addressed to: Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045."),
    ("body", "[ ] Email to: cskee@clackamas.us."),
    ("body", "[ ] Hand delivery."),
    ("body", "[ ] Other: ______________________________________________________________________"),
    ("signature", ["______________________________", "Benjamin Jay Barber", "", "______________________________", "Jane Kay Cortez"]),
]


APPENDIX_SECTIONS = [
    ("AUTHORITY AND FORMAT APPENDIX INDEX", [
        "Formatting sources: 2025 Oregon UTCR 2.010 and 5.020; Clackamas County Justice Court public information page.",
        "Oregon procedure: ORCP 21 A(1)(h); ORS 105.123; ORS 105.124; ORS 90.427.",
        "Federal relocation authorities: 42 U.S.C. § 1437p; 24 C.F.R. § 970.21; 24 C.F.R. § 972.130.",
        "Record exhibits: Plaintiff's summons/complaint/attached notice; HACC January 8, 2026 Blossom/TPV notice; March 19, 2026 voucher and orientation materials.",
    ]),
    ("FORMAT COMPLIANCE GUIDE USED FOR THIS PACKET", [
        "2025 Oregon UTCR source: https://www.courts.oregon.gov/rules/UTCR/2025_UTCR.pdf",
        "UTCR 2.010: pleadings and motions are prepared on letter-size pages, with one-inch margins, numbered lines, first-page top spacing, caption/title, signature/date, and footer identification.",
        "UTCR 5.020: a motion must include a memorandum of law or statement of authority explaining the authorities supporting the moving party.",
        "Clackamas County Justice Court source: https://www.clackamas.us/justice",
        "The Justice Court page identifies landlord-tenant eviction cases, required eviction appearances, and tenant eviction answer forms.",
        "Conservative formatting note: UTCR is written for Oregon circuit courts. This Justice Court packet follows those standards as a conservative filing format where not inconsistent with Justice Court forms or instructions.",
    ]),
    ("OREGON PROCEDURE AUTHORITIES", [
        "ORCP source: https://www.oregonlegislature.gov/bills_laws/SiteAssets/ORCP.html",
        "ORCP 21 A(1)(h) authorizes dismissal where a pleading fails to state ultimate facts sufficient to constitute a claim.",
        "ORCP 21 G(3) preserves the failure-to-state-ultimate-facts defense for later procedural presentation as specified in the rule.",
        "ORS 105.123 source: https://oregon.public.law/statutes/ors_105.123",
        "ORS 105.123 requires an FED complaint to state the premises, possession by defendant, and plaintiff's entitlement to possession.",
        "ORS 105.124 source: https://oregon.public.law/statutes/ors_105.124",
        "ORS 105.124 requires the Oregon residential eviction form and attachment of any notice relied upon.",
        "ORS 90.427 source: https://oregon.public.law/statutes/ors_90.427",
        "ORS 90.427(9) gives a tenant a defense to possession when a landlord termination violates listed provisions of that section.",
    ]),
    ("FEDERAL RELOCATION AUTHORITIES", [
        "42 U.S.C. § 1437p source: https://www.law.cornell.edu/uscode/text/42/1437p and https://www.govinfo.gov/link/uscode/42/1437p",
        "Section 1437p requires resident notice, comparable housing, relocation expenses, counseling, and no demolition or completed disposition until residents are relocated.",
        "24 C.F.R. § 970.21 source: https://www.ecfr.gov/current/title-24/section-970.21",
        "24 C.F.R. § 970.21 requires comparable housing for families displaced by demolition or disposition and says tenant-based assistance is not comparable housing until actual relocation into that housing.",
        "24 C.F.R. Part 972 Subpart A source: https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-972/subpart-A",
        "24 C.F.R. § 972.130(b)(4) requires written notice and, where Section 8 voucher assistance is used for relocation, vouchers at least 90 days before displacement.",
        "eCFR status checked April 20, 2026. eCFR displayed Title 24 as up to date through April 16, 2026.",
    ]),
    ("RECORD EXHIBIT INDEX", [
        "Exhibit 1: Plaintiff's eviction summons, complaint, and attached December 23, 2025 90-day notice. Source: Housing Authority Clackamas County Eviction.pdf, pages 1-8.",
        "Exhibit 2: HACC January 8, 2026 Blossom / Tenant Protection Voucher notice. Source: Exhibit G - HACC Jan 2026 blossom.pdf.",
        "Exhibit 3: March 19, 2026 voucher form. Source: VO---JC---03.19.2026.pdf.",
        "Exhibit 4: March 19, 2026 orientation / required signatures packet. Source: Orientation---Required-Signatures-03.19.2026.pdf.",
    ]),
]


def draw_line_numbers(c, page_num, title):
    c.setFont("Times-Roman", 8)
    c.setFillColor(colors.black)
    y = 10.0 * inch
    for i in range(1, 29):
        c.drawRightString(0.72 * inch, y, str(i))
        y -= 0.30 * inch
    c.setFont("Times-Roman", 9)
    c.drawString(1 * inch, 0.5 * inch, f"{title} - Page {page_num}")


def wrap_text(text, width, font="Times-Roman", size=12):
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


def render_pleading_pdf(path, sections, title):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    page = 1
    x = 1.0 * inch
    text_x = 1.05 * inch
    right = width - 1.0 * inch
    max_width = right - text_x
    y = height - 2.0 * inch
    line_h = 0.30 * inch
    para_no = 1

    def new_page():
        nonlocal page, y
        c.showPage()
        page += 1
        y = height - 1.0 * inch
        draw_line_numbers(c, page, title)

    draw_line_numbers(c, page, title)
    for kind, content in sections:
        if kind == "caption":
            c.setFont("Times-Roman", 12)
            for line in content:
                if y < 1.1 * inch:
                    new_page()
                if line:
                    is_all_caps = line == line.upper()
                    c.setFont("Times-Bold" if is_all_caps else "Times-Roman", 12)
                    centered_lines = wrap_text(line, max_width + 0.2 * inch, "Times-Bold" if is_all_caps else "Times-Roman", 12)
                    for centered_line in centered_lines:
                        if y < 1.1 * inch:
                            new_page()
                            c.setFont("Times-Bold" if is_all_caps else "Times-Roman", 12)
                        c.drawCentredString(width / 2, y, centered_line)
                        y -= line_h
                else:
                    y -= line_h
            y -= line_h
        elif kind == "heading":
            if y < 1.4 * inch:
                new_page()
            c.setFont("Times-Bold", 12)
            c.drawString(text_x, y, content)
            y -= line_h * 1.5
        elif kind == "signature":
            c.setFont("Times-Roman", 12)
            for line in content:
                if y < 1.0 * inch:
                    new_page()
                c.drawString(text_x, y, line)
                y -= line_h
            y -= line_h
        else:
            c.setFont("Times-Roman", 12)
            lines = wrap_text(content, max_width - 0.35 * inch)
            if y < 1.65 * inch:
                new_page()
            c.drawCentredString(width / 2, y, str(para_no))
            y -= line_h
            para_no += 1
            for line in lines:
                if y < 1.0 * inch:
                    new_page()
                c.drawString(text_x, y, line)
                y -= line_h
            y -= line_h
    c.save()


def render_appendix_pdf(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    page = 1
    y = height - inch
    left = inch
    max_width = width - 2 * inch

    def footer():
        c.setFont("Times-Roman", 9)
        c.drawString(inch, 0.5 * inch, f"Authority and Record Appendix - Page {page}")

    def new_page():
        nonlocal page, y
        footer()
        c.showPage()
        page += 1
        y = height - inch

    for heading, items in APPENDIX_SECTIONS:
        if y < 1.5 * inch:
            new_page()
        c.setFont("Times-Bold", 13)
        c.drawString(left, y, heading)
        y -= 0.35 * inch
        c.setFont("Times-Roman", 11)
        for item in items:
            wrapped = wrap_text(item, max_width - 0.25 * inch, size=11)
            for idx, line in enumerate(wrapped):
                if y < 0.9 * inch:
                    new_page()
                    c.setFont("Times-Roman", 11)
                prefix = "- " if idx == 0 else "  "
                c.drawString(left + 0.15 * inch, y, prefix + line)
                y -= 0.22 * inch
            y -= 0.05 * inch
        y -= 0.25 * inch
    footer()
    c.save()


def cover_page(title, source, note):
    from io import BytesIO

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Times-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.6 * inch, title)
    c.setFont("Times-Roman", 12)
    for i, line in enumerate(textwrap.wrap(source, 82)):
        c.drawCentredString(4.25 * inch, 5.8 * inch - i * 0.25 * inch, line)
    c.setFont("Times-Roman", 11)
    for i, line in enumerate(textwrap.wrap(note, 90)):
        c.drawCentredString(4.25 * inch, 4.7 * inch - i * 0.22 * inch, line)
    c.setFont("Times-Roman", 9)
    c.drawString(inch, 0.5 * inch, title)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def stamp_page(page, label, pageno):
    from io import BytesIO

    w = float(page.mediabox.width)
    h = float(page.mediabox.height)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFillColor(colors.white)
    c.rect(w - 1.85 * inch, 0.16 * inch, 1.65 * inch, 0.42 * inch, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Times-Roman", 9)
    c.drawRightString(w - 0.25 * inch, 0.42 * inch, label)
    c.drawRightString(w - 0.25 * inch, 0.25 * inch, f"Page {pageno}")
    c.save()
    buf.seek(0)
    overlay = PdfReader(buf).pages[0]
    page.merge_page(overlay)
    return page


def add_pdf_pages(writer, pdf_path, exhibit_label, pages=None):
    reader = PdfReader(str(pdf_path))
    selected = pages if pages is not None else range(len(reader.pages))
    total_note = f"Attached pages are from {pdf_path.relative_to(ROOT)}."
    writer.add_page(cover_page(exhibit_label, str(pdf_path.relative_to(ROOT)), total_note))
    out_no = 1
    for idx in selected:
        page = reader.pages[idx]
        writer.add_page(stamp_page(page, exhibit_label, out_no))
        out_no += 1


def build_final():
    render_pleading_pdf(LEAD_PDF, MOTION_PARAGRAPHS + ORDER_TEXT + SERVICE_TEXT, "DEFENDANTS' MOTION TO DISMISS")
    render_appendix_pdf(APPENDIX_PDF)

    writer = PdfWriter()
    for p in PdfReader(str(LEAD_PDF)).pages:
        writer.add_page(p)
    for p in PdfReader(str(APPENDIX_PDF)).pages:
        writer.add_page(p)

    add_pdf_pages(writer, COMPLAINT_PDF, "Exhibit 1", pages=range(0, 8))
    add_pdf_pages(writer, JAN8_PDF, "Exhibit 2")
    add_pdf_pages(writer, VOUCHER_PDF, "Exhibit 3")
    add_pdf_pages(writer, ORIENTATION_PDF, "Exhibit 4")

    with FINAL_PDF.open("wb") as f:
        writer.write(f)


if __name__ == "__main__":
    build_final()
    print(FINAL_PDF)
