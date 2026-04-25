from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


BASE = Path("/home/barberb/HACC/workspace/eppdapa_tilton_2026-04-22")
FORM = BASE / "EPPDAPA-ObtainingPacket.pdf"
OUTPUT = BASE / "completed_eppdapa_petition_barber_cortez_v_kati_tilton.pdf"

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
SIZE = 8.3
SMALL = 7.2
LEAD = 0.145 * inch


def wrap(text, width, font=FONT, size=SIZE):
    words = []
    for token in text.split():
        if stringWidth(token, font, size) <= width:
            words.append(token)
            continue
        current = ""
        for ch in token:
            test = current + ch
            if current and stringWidth(test, font, size) > width:
                words.append(current)
                current = ch
            else:
                current = test
        if current:
            words.append(current)
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


def make_overlay(page_no):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont(FONT, SIZE)

    def txt(x, y, s, size=SIZE, font=FONT):
        c.setFont(font, size)
        c.drawString(x, y, s)

    def box(x, y):
        c.setFont(FONT_BOLD, 10)
        c.drawString(x, y, "X")

    def lines(x, y, text, width, size=SIZE, lead=LEAD, max_lines=None):
        c.setFont(FONT, size)
        drawn = 0
        for line in wrap(text, width, FONT, size):
            if max_lines is not None and drawn >= max_lines:
                break
            c.drawString(x, y, line)
            y -= lead
            drawn += 1
        return y

    # Original OJD packet pages:
    # 7-11 = petition; 12-15 = proposed order; 16 = service info; 17 = certificate.
    if page_no == 7:
        txt(303, 743, "CLACKAMAS", 9)
        txt(169, 686, "Jane Kay Cortez and Benjamin Jay Barber", 9)
        txt(164, 558, "Kati Tilton, Housing Authority of Clackamas County", 8.6)
        # Page 1 of the official form is cramped and contains the court's
        # notice box. The detailed eligibility/contact facts are stated on the
        # clean attachment and service-information page to avoid obscuring the
        # official form text.

    elif page_no == 8:
        box(112, 692)  # There is a restraining order
        txt(191, 675, "Related Clackamas County matters; see Attachment A", 7.5)
        txt(419, 675, "25PO11318; 26P000432/433; 26FE0586", 7.2)
        box(113, 469)  # withholding services
        box(113, 425)  # wrongfully took/used property
        box(113, 405)  # made fear
        box(151, 376)  # threats/intimidation
        box(151, 346)  # conduct/actions
        box(132, 205)  # money/property wrongfully took
        box(132, 184)  # threatened to wrongfully take/use
        txt(79, 111, "April 2026", 8)
        txt(277, 111, "Clackamas County, Oregon", 8)
        lines(
            72,
            92,
            "Respondent, as HACC operations manager, is part of the continuing effort to evict and displace Petitioners before federal relocation and voucher protections are complete. See Attachment A.",
            458,
            size=7.5,
            lead=0.13 * inch,
            max_lines=4,
        )

    elif page_no == 9:
        txt(79, 701, "March-April 2026", 8)
        txt(277, 701, "Clackamas County, Oregon", 8)
        lines(
            72,
            682,
            "HACC processed relocation/voucher matters through Kati Tilton while the household was trying to port to Multnomah County, but continued possession/eviction pressure. Petitioners believe this threatens wrongful loss of housing/voucher property.",
            458,
            size=7.5,
            lead=0.13 * inch,
            max_lines=5,
        )
        txt(79, 585, "Jan. 2026 and continuing", 8)
        txt(277, 585, "Clackamas County, Oregon", 8)
        lines(
            72,
            566,
            "After earlier VAWA/restraining-order issues involving Julio Cortez, HACC removed Benjamin from the lease and treated Julio as back in the household, despite abuse-protection concerns. See Attachment A.",
            458,
            size=7.5,
            lead=0.13 * inch,
            max_lines=5,
        )
        box(113, 465)  # Additional page attached incidents
        box(113, 413)  # Additional incidents older than 180 days
        lines(
            72,
            387,
            "Earlier events are included only as context and pattern: the prior Ashley Ferron EPPDAPA filings, the Julio Cortez restraining-order/VAWA lease-bifurcation dispute, and HACC's alleged policy or practice of disregarding federal housing protections.",
            458,
            size=7.5,
            lead=0.13 * inch,
            max_lines=7,
        )

    elif page_no == 10:
        lines(
            72,
            693,
            "Petitioners face imminent loss of home, possible lockout, collapse of relocation rights, disruption of a Tenant Protection Voucher port to Multnomah County, and severe emotional/physical harm to Jane Cortez, age 72 and disabled. Respondent controls or materially participates in HACC actions that can continue or stop the displacement. See Attachment A.",
            468,
            size=7.7,
            lead=0.132 * inch,
            max_lines=8,
        )

    elif page_no == 11:
        # Leave the official signature/contact page clean for wet signatures.
        pass

    elif page_no == 12:
        txt(252, 735, "CLACKAMAS", 9)
        txt(164, 689, "Jane Kay Cortez and Benjamin Jay Barber", 9)
        txt(164, 624, "Kati Tilton, Housing Authority of Clackamas County", 9)
        box(66, 504)  # Petitioner is elderly/disabled
        # Desired order terms are marked for judge's consideration; judge initials at right.
        box(54, 355)  # prohibit entering residence
        txt(181, 333, "10043 SE 32nd Ave, Milwaukie, OR 97222", 8)

    elif page_no == 13:
        box(76, 708)  # contact prohibition
        txt(392, 677, "150", 8)
        box(76, 296)  # property control restraint
        lines(
            82,
            199,
            "Housing, lease, voucher, relocation, subsidy, occupancy, and possessory rights of Jane Cortez and Benjamin Barber, including the pending Tenant Protection Voucher and port to Multnomah County.",
            413,
            size=7.4,
            lead=0.13 * inch,
            max_lines=5,
        )

    elif page_no == 14:
        lines(
            72,
            465,
            "Respondent must not cause, request, authorize, coordinate, or enforce displacement, lockout, lease removal, loss of voucher/subsidy, or interference with Petitioners' relocation/portability process unless and until a court with jurisdiction determines that HACC has complied with federal relocation, VAWA, disability-accommodation, and voucher requirements. Respondent must preserve Petitioners' housing/voucher records and communicate only through lawful, non-abusive channels necessary for court proceedings or benefit administration.",
            468,
            size=7.3,
            lead=0.122 * inch,
            max_lines=9,
        )
        txt(97, 118, "X", 9)  # Certificate readiness petitioner
        txt(72, 84, "April ___, 2026", 8)
        txt(283, 84, "Jane Kay Cortez / Benjamin Jay Barber", 8)

    elif page_no == 15:
        txt(97, 118, "X", 9)
        txt(72, 84, "April ___, 2026", 8)
        txt(283, 84, "Jane Kay Cortez / Benjamin Jay Barber", 8)
        txt(72, 46, "10043 SE 32nd Ave", 8)
        txt(252, 46, "Milwaukie, OR 97222", 8)
        txt(449, 46, "971-270-0855", 8)

    elif page_no == 16:
        txt(147, 729, "Jane Kay Cortez and Benjamin Jay Barber", 8)
        txt(486, 729, "X", 9)  # Nonbinary? leave no gender? Avoid wrong gender. This is imperfect for two petitioners.
        txt(76, 695, "10043 SE 32nd Ave", 8)
        txt(276, 695, "Milwaukie, OR", 8)
        txt(449, 695, "97222", 8)
        txt(180, 669, "971-270-0855", 8)
        txt(72, 643, "Jane: 72; Benjamin: [fill age]", 8)
        txt(71, 560, "Kati Tilton", 8)
        txt(74, 526, "Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045", 7.6)
        txt(178, 502, "503-655-8267 / HACC main office", 7.4)
        txt(83, 398, "HACC office / work hours", 7.6)
        txt(212, 398, "13930 S Gain St, Oregon City, OR 97045", 7.6)
        lines(
            72,
            301,
            "The present danger is administrative displacement and loss of housing/voucher property. Petitioners do not allege personal weapons knowledge.",
            465,
            size=7.5,
            lead=0.13 * inch,
            max_lines=4,
        )
        lines(
            72,
            245,
            "No weapons information known to Petitioners.",
            465,
            size=7.5,
            lead=0.13 * inch,
            max_lines=2,
        )
        lines(
            72,
            190,
            "No violent-crime information known to Petitioners.",
            465,
            size=7.5,
            lead=0.13 * inch,
            max_lines=2,
        )

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def supplemental_pages():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    left = 0.75 * inch
    right = width - 0.75 * inch
    y = height - 0.72 * inch
    page = 1

    def footer():
        c.setFont(FONT, 8)
        c.drawString(left, 0.45 * inch, "EPPDAPA Attachment A - Incidents, Danger, and Requested Relief")
        c.drawRightString(right, 0.45 * inch, f"Page {page}")

    def new_page():
        nonlocal y, page
        footer()
        c.showPage()
        page += 1
        y = height - 0.72 * inch

    def heading(text):
        nonlocal y
        if y < 1.15 * inch:
            new_page()
        c.setFont(FONT_BOLD, 11)
        c.drawString(left, y, text)
        y -= 0.24 * inch

    def para(text, no=None):
        nonlocal y
        prefix = f"{no}. " if no is not None else ""
        x = left
        body_x = left + (0.25 * inch if no is not None else 0)
        max_width = right - body_x
        lines = wrap(text, max_width, FONT, 9.2)
        if y - len(lines) * 0.18 * inch < 0.9 * inch:
            new_page()
        c.setFont(FONT, 9.2)
        if no is not None:
            c.drawString(x, y, f"{no}.")
        for line in lines:
            c.drawString(body_x, y, line if not prefix else line)
            y -= 0.18 * inch
        y -= 0.065 * inch

    c.setFont(FONT_BOLD, 12)
    c.drawCentredString(width / 2, y, "ATTACHMENT A")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "INCIDENTS OF ABUSE, IMMEDIATE DANGER, AND REQUESTED RELIEF")
    y -= 0.34 * inch
    c.setFont(FONT, 9)
    c.drawString(left, y, "Petitioners: Jane Kay Cortez and Benjamin Jay Barber")
    y -= 0.18 * inch
    c.drawString(left, y, "Respondent: Kati Tilton, Housing Authority of Clackamas County")
    y -= 0.30 * inch

    heading("A. Protected Persons")
    items = [
        "Jane Kay Cortez is 72 years old and disabled. She is the primary elderly/disabled protected person facing immediate harm from displacement.",
        "Benjamin Jay Barber is disabled and seeks protection as a protected person and household member/caregiver whose housing, lease, and relocation rights are intertwined with Jane Cortez's safety.",
        "Petitioners live at 10043 SE 32nd Ave, Milwaukie, Oregon, in HACC-controlled public housing connected to a Tenant Protection Voucher and relocation process.",
    ]
    n = 1
    for item in items:
        para(item, n)
        n += 1

    heading("B. Most Recent Abuse Within 180 Days")
    recent = [
        "In March and April 2026, while Petitioners were trying to complete relocation and port a Tenant Protection Voucher to Multnomah County, Respondent Kati Tilton handled or materially participated in HACC communications and administration of the voucher, orientation, relocation paperwork, and housing process.",
        "HACC has nevertheless pursued or allowed an eviction/possession process before Petitioners' relocation and voucher process was complete. Petitioners contend this threatens wrongful taking or loss of their housing, leasehold, voucher, relocation, subsidy, and possessory rights.",
        "Jane Cortez is in imminent danger of significant physical and emotional harm if locked out or displaced before relocation is complete. She is 72, disabled, and depends on stable housing, disability accommodations, and Benjamin Barber's assistance. Loss of the home would disrupt the voucher port, medical/disability stability, and the subject matter of the relocation process.",
        "Federal relocation law and HUD rules require actual relocation protections, comparable housing, and voucher timing protections before displacement. Petitioners contend HACC is treating unfinished voucher paperwork or an unfinished housing search as if it were completed relocation.",
        "Petitioners allege that Respondent's conduct, in her official HACC role, is part of a continuing policy or practice of willful disregard of federal housing law, including VAWA protections, disability accommodation duties, and federal relocation/voucher duties.",
    ]
    for item in recent:
        para(item, n)
        n += 1

    heading("C. VAWA / Lease-Removal Background")
    background = [
        "In late 2025 and early 2026, Petitioners raised abuse-related safety issues involving Julio Cortez and sought VAWA-related lease bifurcation or protection. Repository records reflect that a Julio-related protective order existed by November 2025 and that HACC was repeatedly placed on notice of household-composition and restraining-order issues.",
        "Petitioners allege that despite the restraining-order and VAWA context, HACC unlawfully removed Benjamin Barber from the lease and treated Julio Cortez as restored to or still part of the household. Petitioners contend that this penalized the protected side of the household rather than isolating the alleged perpetrator, contrary to VAWA's anti-penalization and lease-bifurcation protections.",
        "HACC records and repository timelines reflect that HACC generated or relied on lease-side paperwork effective January 1, 2026; on January 12, 2026 HACC still wrote that Julio was a household member unless court documentation was submitted; and by January 27, 2026 HACC treated the household as reduced to one-bedroom voucher eligibility.",
        "Jane Cortez has declared that during the March 23, 2026 HUD NSPIRE inspection she heard HACC staff state, in substance, that Benjamin had been taken off the lease because Benjamin's brother and stepfather had been emailing documents to HACC and that HACC associated the delay or non-move with sorting through those materials.",
        "Petitioners previously filed EPPDAPA/protective-order matters naming Ashley Ferron in her official HACC capacity. Repository materials reflect those petitions were denied, and contemporaneous notes indicate the court may have viewed the housing-administration issues as better addressed elsewhere. Petitioners reference those filings here as background and pattern, not as proof that the prior petitions were granted.",
    ]
    for item in background:
        para(item, n)
        n += 1

    heading("D. Why Immediate Protection Is Needed")
    danger = [
        "The danger is immediate because eviction, lockout, or loss of possession would occur before the federal relocation and voucher process is adjudicated or completed.",
        "If Petitioners are displaced now, Jane Cortez may lose stable housing, access to necessary disability accommodations, access to her caregiver support, and the practical ability to complete the Multnomah County voucher port. The resulting harm is not only economic; it threatens significant physical and emotional harm to an elderly disabled person.",
        "Respondent should be restrained from abusing, intimidating, interfering with, menacing, or causing displacement of Petitioners through HACC actions that wrongfully take or threaten Petitioners' housing, voucher, relocation, subsidy, occupancy, or possessory property rights.",
    ]
    for item in danger:
        para(item, n)
        n += 1

    heading("E. Requested Relief")
    relief = [
        "Order Respondent not to abuse, intimidate, molest, interfere with, or menace Petitioners.",
        "Order Respondent not to cause, authorize, request, coordinate, or enforce displacement, lockout, eviction trespass, lease removal, loss of subsidy, loss of voucher, or loss of relocation rights against Petitioners while the federal relocation/voucher issues remain unresolved, except through lawful court proceedings after compliance with all applicable federal protections.",
        "Order Respondent not to exercise control over Petitioners' housing, lease, voucher, relocation, subsidy, occupancy, or possessory rights in a manner inconsistent with federal relocation law, VAWA, disability-accommodation requirements, or any court stay or protective order.",
        "Order Respondent to preserve all HACC records concerning Petitioners' lease composition, household status, VAWA/bifurcation requests, restraining-order documents, Tenant Protection Voucher, portability to Multnomah County, emergency-transfer issues, reasonable accommodations, and eviction/possession actions.",
        "Grant any other relief necessary for the safety and welfare of Jane Cortez and Benjamin Barber under ORS 124.020.",
    ]
    for item in relief:
        para(item, n)
        n += 1

    footer()
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def service_supplement_page():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    left = 0.75 * inch
    right = width - 0.75 * inch
    y = height - 0.78 * inch
    c.setFont(FONT_BOLD, 12)
    c.drawCentredString(width / 2, y, "SERVICE INFORMATION SUPPLEMENT")
    y -= 0.35 * inch
    c.setFont(FONT, 9.4)
    rows = [
        ("Petitioners", "Jane Kay Cortez and Benjamin Jay Barber"),
        ("Petitioners' contact address", "10043 SE 32nd Ave, Milwaukie, OR 97222"),
        ("Contact phone", "971-270-0855"),
        ("Respondent", "Kati Tilton, Housing Authority of Clackamas County"),
        ("Likely service location", "Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045"),
        ("Phone", "HACC main office: 503-655-8267"),
        ("Likely availability", "HACC office / work hours"),
        ("Weapons information", "Petitioners do not know of firearms or weapons information for Respondent."),
        ("Danger note", "The alleged danger is administrative displacement, loss of housing/voucher property, and resulting physical/emotional harm to elderly/disabled Petitioners."),
    ]
    for label, text in rows:
        if y < 1.1 * inch:
            c.showPage()
            y = height - 0.78 * inch
        c.setFont(FONT_BOLD, 9.4)
        c.drawString(left, y, f"{label}:")
        c.setFont(FONT, 9.4)
        tx = left + 1.85 * inch
        for line in wrap(text, right - tx, FONT, 9.4):
            c.drawString(tx, y, line)
            y -= 0.18 * inch
        y -= 0.08 * inch
    c.setFont(FONT, 8)
    c.drawString(left, 0.45 * inch, "EPPDAPA Service Information Supplement")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def build():
    source = PdfReader(str(FORM))
    writer = PdfWriter()

    # Petition pages from the official packet.
    for page_no in range(7, 12):
        page = source.pages[page_no - 1]
        page.merge_page(make_overlay(page_no))
        writer.add_page(page)

    # Attachment A gives the narrative the official form cannot hold.
    for page in supplemental_pages().pages:
        writer.add_page(page)

    # Proposed order, service information, and blank certificate of service.
    # Leave the official proposed-order pages visually clean; Attachment A
    # states the requested terms for the judge to incorporate.
    for page_no in range(12, 18):
        page = source.pages[page_no - 1]
        writer.add_page(page)
        if page_no == 16:
            writer.add_page(service_supplement_page())

    # Include the statutory notice/request-for-hearing pages the court packet requires
    # after an order is granted.
    for page_no in range(18, 24):
        writer.add_page(source.pages[page_no - 1])

    with OUTPUT.open("wb") as fh:
        writer.write(fh)
    print(OUTPUT)


if __name__ == "__main__":
    build()
