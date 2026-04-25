from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


BASE = Path("/home/barberb/HACC/workspace/eppdapa_tilton_2026-04-22")
FORM = BASE / "EPPDAPA-ObtainingPacket.pdf"
OUTPUT = BASE / "clean_eppdapa_petition_barber_cortez_v_kati_tilton.pdf"

BODY = "Helvetica"
BOLD = "Helvetica-Bold"
SIZE = 9.2
LEAD = 0.18 * inch
LEFT = 0.78 * inch
RIGHT = 0.78 * inch
BOTTOM = 0.72 * inch


def wrap(text, width, font=BODY, size=SIZE):
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


class Doc:
    def __init__(self):
        self.buf = BytesIO()
        self.c = canvas.Canvas(self.buf, pagesize=letter)
        self.w, self.h = letter
        self.y = self.h - 0.72 * inch
        self.page = 1

    def footer(self):
        self.c.setFont(BODY, 8)
        self.c.drawString(LEFT, 0.42 * inch, "EPPDAPA Typed Petition Supplement")
        self.c.drawRightString(self.w - RIGHT, 0.42 * inch, f"Page {self.page}")

    def new_page(self):
        self.footer()
        self.c.showPage()
        self.page += 1
        self.y = self.h - 0.72 * inch

    def heading(self, text, size=12):
        if self.y < 1.2 * inch:
            self.new_page()
        self.c.setFont(BOLD, size)
        self.c.drawString(LEFT, self.y, text)
        self.y -= 0.26 * inch

    def centered(self, text, size=12, font=BOLD):
        self.c.setFont(font, size)
        self.c.drawCentredString(self.w / 2, self.y, text)
        self.y -= 0.24 * inch

    def para(self, text, no=None, size=SIZE):
        body_left = LEFT + (0.28 * inch if no is not None else 0)
        lines = wrap(text, self.w - RIGHT - body_left, BODY, size)
        if self.y - len(lines) * LEAD < BOTTOM:
            self.new_page()
        self.c.setFont(BODY, size)
        if no is not None:
            self.c.drawString(LEFT, self.y, f"{no}.")
        for line in lines:
            self.c.drawString(body_left, self.y, line)
            self.y -= LEAD
        self.y -= 0.06 * inch

    def row(self, label, value):
        if self.y < 1.0 * inch:
            self.new_page()
        self.c.setFont(BOLD, SIZE)
        self.c.drawString(LEFT, self.y, f"{label}:")
        self.c.setFont(BODY, SIZE)
        x = LEFT + 2.05 * inch
        for line in wrap(value, self.w - RIGHT - x, BODY, SIZE):
            self.c.drawString(x, self.y, line)
            self.y -= LEAD
        self.y -= 0.035 * inch

    def finish(self):
        self.footer()
        self.c.save()
        self.buf.seek(0)
        return PdfReader(self.buf)


def typed_supplement():
    d = Doc()
    d.centered("IN THE CIRCUIT COURT OF THE STATE OF OREGON", 11)
    d.centered("FOR THE COUNTY OF CLACKAMAS", 11)
    d.y -= 0.10 * inch
    d.centered("TYPED EPPDAPA PETITION SUPPLEMENT", 13)
    d.centered("Jane Kay Cortez and Benjamin Jay Barber v. Kati Tilton", 10, BODY)
    d.y -= 0.12 * inch

    d.heading("Official Form Use")
    d.para(
        "This supplement is intended to accompany the official OJD EPPDAPA Petition for Restraining Order to Prevent Abuse and proposed Restraining Order forms attached after this supplement. The official OJD forms use singular petitioner language; Petitioners ask the Court to protect both Jane Kay Cortez and Benjamin Jay Barber, or to accept this same supplement with separate official petitions if the clerk requires separate filings."
    )

    d.heading("Form Information")
    rows = [
        ("County", "Clackamas County"),
        ("Petitioners", "Jane Kay Cortez and Benjamin Jay Barber"),
        ("Respondent", "Kati Tilton, Housing Authority of Clackamas County"),
        ("Contact address", "10043 SE 32nd Ave, Milwaukie, OR 97222"),
        ("Contact phone", "971-270-0855"),
        ("Petitioners live in", "Clackamas County, Oregon"),
        ("Respondent lives/works in", "Clackamas County, Oregon / Housing Authority of Clackamas County"),
        ("Filing basis", "Incidents of abuse occurred in Clackamas County."),
        ("Protected status", "Jane Cortez is 72 and disabled. Benjamin Barber is disabled."),
        ("Respondent is not", "a court-appointed guardian or conservator for Petitioners."),
    ]
    for label, value in rows:
        d.row(label, value)

    d.heading("Boxes Requested On Official Petition")
    boxes = [
        "Petitioner: is age 65 or older",
        "Petitioner: is a person with a disability",
        "Other cases: There is a restraining order or stalking order",
        "Abuse within 180 days: caused physical harm by withholding services needed for health and well-being",
        "Abuse within 180 days: wrongfully took or used money or property, or threatened to",
        "Abuse within 180 days: made Petitioners fear significant physical or emotional harm by harassment, threats, intimidation, conduct, or actions",
        "Specific acts re money or property: Respondent wrongfully took or used Petitioners' money or property, or knowingly alarmed Petitioners by threatening to do so",
        "Additional page attached labeled Incidents of Abuse - 180 Days",
        "Additional page attached labeled Additional Incidents of Abuse",
    ]
    for box in boxes:
        d.para(f"[X] {box}")

    d.heading("Other Related Cases")
    d.para(
        "Related Clackamas County matters include the Julio Cortez protective-order / VAWA lease-bifurcation dispute, prior EPPDAPA/protective-order filings involving Ashley Ferron in her official HACC capacity, and Clackamas County Justice Court eviction case 26FE0586. Petitioners understand prior Ashley Ferron petitions were denied and reference them only as background and pattern."
    )

    d.heading("Incidents Of Abuse Within 180 Days")
    facts = [
        "In March and April 2026, while Petitioners were trying to complete relocation and port a Tenant Protection Voucher to Multnomah County, Respondent Kati Tilton handled or materially participated in HACC communications and administration of the voucher, orientation, relocation paperwork, and housing process.",
        "HACC nevertheless pursued or allowed an eviction/possession process before Petitioners' relocation and voucher process was complete. Petitioners contend this threatens wrongful taking or loss of housing, leasehold, voucher, relocation, subsidy, occupancy, and possessory rights.",
        "Jane Cortez is in imminent danger of significant physical and emotional harm if locked out or displaced before relocation is complete. She is 72, disabled, and depends on stable housing, disability accommodations, and Benjamin Barber's assistance.",
        "Federal relocation law and HUD rules require actual relocation protections, comparable housing, and voucher timing protections before displacement. Petitioners contend HACC is treating unfinished voucher paperwork or an unfinished housing search as completed relocation.",
        "Petitioners allege that Respondent's conduct, in her official HACC role, is part of a continuing policy or practice of willful disregard of federal housing law, including VAWA protections, disability accommodation duties, and federal relocation/voucher duties.",
    ]
    n = 1
    for fact in facts:
        d.para(fact, n)
        n += 1

    d.heading("VAWA / Lease-Removal Background")
    background = [
        "In late 2025 and early 2026, Petitioners raised abuse-related safety issues involving Julio Cortez and sought VAWA-related lease bifurcation or protection. Repository records reflect that a Julio-related protective order existed by November 2025 and that HACC was repeatedly placed on notice of household-composition and restraining-order issues.",
        "Petitioners allege that despite the restraining-order and VAWA context, HACC unlawfully removed Benjamin Barber from the lease and treated Julio Cortez as restored to or still part of the household. Petitioners contend that this penalized the protected side of the household rather than isolating the alleged perpetrator, contrary to VAWA's anti-penalization and lease-bifurcation protections.",
        "HACC records and repository timelines reflect that HACC generated or relied on lease-side paperwork effective January 1, 2026; on January 12, 2026 HACC still wrote that Julio was a household member unless court documentation was submitted; and by January 27, 2026 HACC treated the household as reduced to one-bedroom voucher eligibility.",
        "Jane Cortez has declared that during the March 23, 2026 HUD NSPIRE inspection she heard HACC staff state, in substance, that Benjamin had been taken off the lease because Benjamin's brother and stepfather had been emailing documents to HACC and that HACC associated the delay or non-move with sorting through those materials.",
        "Petitioners previously filed EPPDAPA/protective-order matters naming Ashley Ferron in her official HACC capacity. Repository materials reflect those petitions were denied, and contemporaneous notes indicate the court may have viewed the housing-administration issues as better addressed elsewhere. Petitioners reference those filings here as background and pattern, not as proof that the prior petitions were granted.",
    ]
    for fact in background:
        d.para(fact, n)
        n += 1

    d.heading("Immediate And Present Danger")
    danger = [
        "The danger is immediate because eviction, lockout, or loss of possession would occur before the federal relocation and voucher process is adjudicated or completed.",
        "If Petitioners are displaced now, Jane Cortez may lose stable housing, access to necessary disability accommodations, access to caregiver support, and the practical ability to complete the Multnomah County voucher port. The resulting harm is not only economic; it threatens significant physical and emotional harm to an elderly disabled person.",
        "Respondent should be restrained from abusing, intimidating, interfering with, menacing, or causing displacement of Petitioners through HACC actions that wrongfully take or threaten Petitioners' housing, voucher, relocation, subsidy, occupancy, or possessory property rights.",
    ]
    for fact in danger:
        d.para(fact, n)
        n += 1

    d.heading("Requested Relief")
    relief = [
        "Order Respondent not to abuse, intimidate, molest, interfere with, or menace Petitioners.",
        "Order Respondent not to cause, authorize, request, coordinate, or enforce displacement, lockout, eviction trespass, lease removal, loss of subsidy, loss of voucher, or loss of relocation rights against Petitioners while the federal relocation/voucher issues remain unresolved, except through lawful court proceedings after compliance with all applicable federal protections.",
        "Order Respondent not to exercise control over Petitioners' housing, lease, voucher, relocation, subsidy, occupancy, or possessory rights in a manner inconsistent with federal relocation law, VAWA, disability-accommodation requirements, or any court stay or protective order.",
        "Order Respondent to preserve all HACC records concerning Petitioners' lease composition, household status, VAWA/bifurcation requests, restraining-order documents, Tenant Protection Voucher, portability to Multnomah County, emergency-transfer issues, reasonable accommodations, and eviction/possession actions.",
        "Grant any other relief necessary for the safety and welfare of Jane Cortez and Benjamin Barber under ORS 124.020.",
    ]
    for fact in relief:
        d.para(fact, n)
        n += 1

    d.heading("Service Information")
    service_rows = [
        ("Respondent", "Kati Tilton, Housing Authority of Clackamas County"),
        ("Likely service location", "Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045"),
        ("Phone", "HACC main office: 503-655-8267"),
        ("Likely availability", "HACC office / work hours"),
        ("Weapons information", "Petitioners do not know of firearms or weapons information for Respondent."),
        ("Danger note", "The alleged danger is administrative displacement, loss of housing/voucher property, and resulting physical/emotional harm to elderly/disabled Petitioners."),
    ]
    for label, value in service_rows:
        d.row(label, value)

    d.heading("Signature")
    d.para("Petitioners declare that the above statements are true to the best of their knowledge and belief.")
    d.y -= 0.25 * inch
    if d.y < 2.1 * inch:
        d.new_page()
    d.c.setFont(BODY, SIZE)
    d.c.drawString(LEFT, d.y, "DATED: April ___, 2026.")
    d.y -= 0.45 * inch
    d.c.drawString(LEFT, d.y, "__________________________________")
    d.c.drawString(4.35 * inch, d.y, "__________________________________")
    d.y -= 0.2 * inch
    d.c.drawString(LEFT, d.y, "Jane Kay Cortez")
    d.c.drawString(4.35 * inch, d.y, "Benjamin Jay Barber")
    return d.finish()


def build():
    writer = PdfWriter()
    for page in typed_supplement().pages:
        writer.add_page(page)

    source = PdfReader(str(FORM))
    # Reuse the official OJD form pages without text overlays:
    # petition, proposed order, service info, certificate, notice, request for hearing.
    for page_no in range(7, 24):
        writer.add_page(source.pages[page_no - 1])

    with OUTPUT.open("wb") as fh:
        writer.write(fh)
    print(OUTPUT)


if __name__ == "__main__":
    build()
