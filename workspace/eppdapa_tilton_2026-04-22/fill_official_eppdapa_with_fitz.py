from pathlib import Path
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
import re
import textwrap

import fitz


BASE = Path("/home/barberb/HACC/workspace/eppdapa_tilton_2026-04-22")
FORM = BASE / "EPPDAPA-ObtainingPacket.pdf"
OUTPUT = BASE / "official_filled_eppdapa_petition_barber_cortez_v_kati_tilton.pdf"
OUTPUT_WITH_EXHIBITS = BASE / "official_filled_eppdapa_petition_barber_cortez_v_kati_tilton_with_hacc_solomon_email_exhibits.pdf"


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data)

    def text(self):
        return " ".join(self.parts)


def mark(page, rect, fontsize=10):
    # Use the exact square geometry extracted from the source PDF.
    page.insert_text(
        (rect[0] + 1.6, rect[3] - 1.9),
        "X",
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),
    )


def text(page, x, y, value, fontsize=8.2):
    page.insert_text((x, y), value, fontsize=fontsize, fontname="helv", color=(0, 0, 0))


def textbox(page, rect, value, fontsize=7.4, align=0):
    page.insert_textbox(
        fitz.Rect(*rect),
        value,
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),
        align=align,
    )


def clear_textbox(page, rect, value, fontsize=7.4, align=0):
    page.draw_rect(fitz.Rect(*rect), color=None, fill=(1, 1, 1), overlay=True)
    textbox(page, rect, value, fontsize, align)


def plain_from_email(path):
    msg = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    part = msg.get_body(preferencelist=("plain", "html"))
    body = part.get_content() if part else ""
    if part and part.get_content_type() == "text/html":
        parser = HTMLTextExtractor()
        parser.feed(body)
        body = parser.text()
    body = re.sub(r"\r\n?", "\n", body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return msg, body.strip()


def excerpt_around(text_value, needles, before=1400, after=2600):
    lowered = text_value.lower()
    hits = [lowered.find(n.lower()) for n in needles if lowered.find(n.lower()) >= 0]
    if not hits:
        return text_value[: before + after]
    start = max(0, min(hits) - before)
    end = min(len(text_value), max(hits) + after)
    prefix = "[excerpt begins]\n" if start else ""
    suffix = "\n[excerpt ends]" if end < len(text_value) else ""
    return prefix + text_value[start:end].strip() + suffix


def add_wrapped_lines(page, x, y, lines, fontsize=8.6, width_chars=96, bottom=735):
    for line in lines:
        wrapped = textwrap.wrap(line, width=width_chars) or [""]
        for wrapped_line in wrapped:
            if y > bottom:
                page = page.parent.new_page(width=612, height=792)
                y = 54
            page.insert_text((x, y), wrapped_line, fontsize=fontsize, fontname="helv")
            y += fontsize + 3.2
    return page, y


def add_email_exhibits(doc):
    exhibits = [
        {
            "label": "EXHIBIT 1",
            "title": "February 2, 2026 HACC Email - Notice of Restraining-Order Documents",
            "path": Path("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml"),
            "note": "Included because the thread reflects Benjamin telling HACC that restraining-order documents and porting documents would be sent to HACC by priority mail.",
            "needles": ["restraining order documents", "court documentation showing"],
        },
        {
            "label": "EXHIBIT 2",
            "title": "January 12, 2026 HACC Email Chain - Household Composition and Court Documentation",
            "path": Path("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
            "note": "Included because HACC's household-composition thread states Benjamin was no longer listed as a household member based on internal review and court documentation currently on file.",
            "needles": ["no longer listed", "court documentation currently on file", "Violence Against Women Act"],
        },
        {
            "label": "EXHIBIT 3",
            "title": "March 17, 2026 HACC Email - Warning About Communication With Restrained Parties",
            "path": Path("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_2.eml"),
            "note": "Included because the email to Kati Tilton and B. Williams asks whether HACC was still communicating with parties who had restraining orders against them in the courts.",
            "needles": ["restraining orders against them", "communication with parties"],
        },
    ]

    for exhibit in exhibits:
        page = doc.new_page(width=612, height=792)
        y = 54
        page.insert_text((72, y), exhibit["label"], fontsize=13, fontname="helv")
        y += 20
        page.insert_textbox(fitz.Rect(72, y, 540, y + 38), exhibit["title"], fontsize=11, fontname="helv")
        y += 48
        page.insert_textbox(fitz.Rect(72, y, 540, y + 42), exhibit["note"], fontsize=8.5, fontname="helv")
        y += 54

        msg, body = plain_from_email(exhibit["path"])
        headers = [
            f"Source file: {exhibit['path']}",
            f"Date: {msg.get('Date', '')}",
            f"From: {msg.get('From', '')}",
            f"To: {msg.get('To', '')}",
            f"Cc: {msg.get('Cc', '')}",
            f"Subject: {msg.get('Subject', '')}",
            "",
            "Relevant email text:",
        ]
        page, y = add_wrapped_lines(page, 72, y, headers, fontsize=7.8, width_chars=100)
        y += 8
        excerpt = excerpt_around(body, exhibit["needles"])
        lines = [line.strip() for line in excerpt.splitlines()]
        page, y = add_wrapped_lines(page, 72, y, lines, fontsize=7.4, width_chars=108)


def fill_petition(doc):
    # Official packet pages 7-11 are the petition pages.
    p = doc[0]
    text(p, 300, 92, "CLACKAMAS", 8.2)
    textbox(p, (72, 106, 322, 127), "Jane Kay Cortez and Benjamin Jay Barber", 8.6, 1)
    textbox(p, (70, 213, 324, 232), "Kati Tilton, Housing Authority of Clackamas County", 8.0, 1)
    mark(p, (102.2, 418.1, 112.4, 428.3), 10)  # I am Petitioner
    text(p, 246, 474, "Clackamas County, Oregon", 8.0)
    text(p, 312, 498, "Clackamas County, Oregon / HACC", 7.6)
    mark(p, (91.1, 505.6, 101.3, 515.8), 10)  # incident occurred here
    text(p, 72, 548, "10043 SE 32nd Ave", 7.4)
    text(p, 222, 548, "Milwaukie, OR 97222", 7.4)
    text(p, 446, 548, "971-270-0855", 7.4)
    mark(p, (145.1, 602.2, 155.3, 612.4), 10)  # age 65+
    mark(p, (145.1, 614.6, 155.3, 624.8), 10)  # disability
    textbox(
        p,
        (312, 631, 535, 646),
        "Jane is 72 and disabled; Benjamin is disabled.",
        6.1,
    )
    mark(p, (109.1, 682.8, 119.3, 693.0), 10)  # not guardian/conservator

    p = doc[1]
    mark(p, (109.1, 92.4, 119.3, 102.6), 10)
    text(p, 197, 119, "Clackamas County, Oregon; see Attachment A", 7.2)
    text(p, 426, 119, "25PO11318; 26P000432/433; 26FE0586", 7.0)
    mark(p, (109.1, 315.1, 119.3, 325.3), 10)  # withholding services
    mark(p, (109.1, 352.6, 119.3, 362.8), 10)  # money/property
    mark(p, (109.1, 377.6, 119.3, 387.8), 10)  # fear harm
    mark(p, (145.1, 402.6, 155.3, 412.8), 10)  # threats/intimidation
    mark(p, (145.1, 427.6, 155.3, 437.8), 10)  # conduct/actions
    mark(p, (127.1, 577.6, 137.3, 587.8), 10)  # wrongful taking
    mark(p, (127.1, 590.0, 137.3, 600.2), 10)  # threat
    text(p, 136, 676, "April 2026", 7.0)
    text(p, 366, 676, "Clackamas County, Oregon", 7.0)
    clear_textbox(
        p,
        (108, 684, 540, 700),
        "Respondent participated in HACC actions to evict/displace Petitioners before federal relocation and voucher protections were complete. See Attachment A.",
        5.8,
    )

    p = doc[2]
    text(p, 136, 79, "March-April 2026", 7.2)
    text(p, 366, 79, "Clackamas County, Oregon", 7.2)
    clear_textbox(
        p,
        (108, 88, 540, 168),
        "HACC processed relocation/voucher matters through Kati Tilton while the household was trying to port to Multnomah County, but continued possession/eviction pressure. Petitioners believe this threatens wrongful loss of housing/voucher property.",
        6.6,
    )
    text(p, 136, 229, "Jan. 2026 and continuing", 7.2)
    text(p, 366, 229, "Clackamas County, Oregon", 7.2)
    clear_textbox(
        p,
        (108, 238, 540, 318),
        "After the Ashley Ferron petition was denied, Petitioners discovered Solomon Samuel Barber, who was subject to a protective order, caused or induced Benjamin's lease removal. See Attachment A.",
        6.6,
    )
    text(p, 136, 379, "Mar. 22, 2026 and continuing", 7.2)
    text(p, 366, 379, "Clackamas County, Oregon", 7.2)
    clear_textbox(
        p,
        (108, 388, 540, 478),
        "HACC seeks possession before at least 90 days after March 22, 2026 despite federal relocation and voucher protections under 42 U.S.C. 1437p, 24 C.F.R. 970.21, and 24 C.F.R. 972.130. See Attachment A.",
        6.6,
    )
    mark(p, (145.1, 504.4, 154.2, 513.5), 10)  # 180-day attachment
    mark(p, (127.1, 532.7, 137.3, 542.9), 10)  # older incidents
    clear_textbox(
        p,
        (126, 555, 540, 638),
        "Earlier events are included as context and pattern: the Ashley Ferron denial, Solomon lease-removal discovery, Julio VAWA dispute, essential-caregiver removal, and HACC's alleged disregard of federal housing protections.",
        6.6,
    )
    mark(p, (145.1, 689.0, 154.2, 698.2), 10)  # additional incidents attachment

    p = doc[3]
    mark(p, (105.5, 87.5, 115.7, 97.7), 10)  # immediate danger
    textbox(
        p,
        (72, 112, 540, 172),
        "Petitioners face imminent loss of home, collapse of relocation rights, forced one-bedroom placement despite essential-caregiver needs, dog-safety and emergency-access risks, and severe harm to Jane Cortez, age 72 and disabled. See Attachment A.",
        6.8,
    )

    p = doc[4]
    mark(p, (145, 76, 155, 86), 10)  # other relationship, continued from prior page
    text(p, 193, 83, "HACC operations manager / public-housing and voucher administrator", 7.0)
    mark(p, (147.0, 265.0, 157.2, 275.2), 10)  # submitted by petitioner
    text(p, 73, 308, "April ___, 2026", 7.6)
    text(p, 305, 308, "Jane Kay Cortez / Benjamin Jay Barber", 7.6)
    text(p, 73, 345, "starworks5@gmail.com", 7.6)
    text(p, 305, 345, "Jane Kay Cortez and Benjamin Jay Barber", 7.6)
    text(p, 73, 382, "10043 SE 32nd Ave", 7.4)
    text(p, 250, 382, "Milwaukie, OR 97222", 7.4)
    text(p, 452, 382, "971-270-0855", 7.4)


def fill_order(doc):
    # Official packet pages 12-15 are the proposed order.
    p = doc[5]
    text(p, 300, 92, "CLACKAMAS", 8.2)
    textbox(p, (72, 106, 322, 127), "Jane Kay Cortez and Benjamin Jay Barber", 8.6, 1)
    textbox(p, (72, 204, 313, 221), "Kati Tilton, Housing Authority of Clackamas County", 7.4, 0)
    p = doc[7]
    clear_textbox(
        p,
        (90, 344, 468, 400),
        "Respondent/HACC must not take possession of 10043 SE 32nd Ave, lock out Petitioners, or dispossess them before June 20, 2026, which is 90 days after March 22, 2026, and only after compliance with 42 U.S.C. 1437p, 24 C.F.R. 970.21, and 24 C.F.R. 972.130.",
        5.8,
    )


def fill_service_info(doc):
    p = doc[9]
    text(p, 147, 55, "Jane Kay Cortez and Benjamin Jay Barber", 7.8)
    text(p, 178, 180, "Jane Kay Cortez and Benjamin Jay Barber", 7.0)
    text(p, 176, 199, "10043 SE 32nd Ave", 6.5)
    text(p, 332, 199, "Milwaukie, OR", 6.5)
    text(p, 505, 199, "97222", 6.5)
    text(p, 178, 234, "971-270-0855", 7.0)
    text(p, 95, 258, "72", 6.8)
    text(p, 178, 307, "Kati Tilton", 7.3)
    text(p, 158, 330, "13930 S Gain St, Oregon City, OR 97045", 6.3)
    text(p, 142, 353, "503-655-8267 / HACC main office", 6.5)
    mark(p, (72, 479, 82, 489), 10)  # employment
    text(p, 212, 482, "HACC office / work hours", 6.8)
    text(p, 329, 482, "13930 S Gain St, Oregon City, OR 97045", 6.8)
    text(p, 384, 554, "Administrative displacement and loss of housing/voucher property.", 6.4)
    text(p, 72, 613, "No weapons information known to Petitioners.", 6.8)
    text(p, 72, 661, "No violent-crime information known to Petitioners.", 6.8)


def add_attachment(doc):
    # Insert a clean attachment after the petition pages and before the proposed order.
    attachment = fitz.open()
    page = attachment.new_page(width=612, height=792)
    y = 54
    page.insert_text((238, y), "ATTACHMENT A", fontsize=12, fontname="helv")
    y += 18
    page.insert_text((124, y), "INCIDENTS OF ABUSE, DANGER, AND REQUESTED RELIEF", fontsize=11, fontname="helv")
    y += 28

    sections = [
        ("Protected Persons", [
            "Jane Kay Cortez is 72 years old and disabled. Benjamin Jay Barber is disabled. Both seek protection.",
            "Petitioners live at 10043 SE 32nd Ave, Milwaukie, Oregon, in HACC-controlled public housing connected to a Tenant Protection Voucher and relocation process.",
        ]),
        ("Most Recent Abuse Within 180 Days", [
            "In March and April 2026, Respondent Kati Tilton handled or materially participated in HACC voucher, orientation, relocation, and housing-process communications while Petitioners were trying to port a Tenant Protection Voucher to Multnomah County.",
            "HACC nevertheless pursued or allowed eviction/possession before relocation and voucher protections were complete, threatening wrongful loss of housing, leasehold, voucher, relocation, subsidy, occupancy, and possessory rights.",
            "Jane Cortez is in imminent danger of significant physical and emotional harm if locked out before relocation is complete because she is 72, disabled, and depends on stable housing, disability accommodations, and Benjamin Barber's assistance.",
            "HACC removed or disregarded Benjamin Barber's designation and practical role as an essential family member / live-in caregiver for his elderly disabled mother. That designation and caregiving role would otherwise support a two-bedroom accommodation instead of forcing Jane and Benjamin into a one-bedroom arrangement.",
            "By treating the household as eligible only for a one-bedroom unit, HACC is creating forced-privacy and safety risks: Benjamin Barber is an adult who is sexually active, and the lack of a separate bedroom may expose household members, guests, emergency personnel, or service providers to avoidable privacy conflicts and potential legal risk, including the concerns reflected in ORS 163.467.",
            "The one-bedroom arrangement also increases the risk that guests or emergency personnel will be exposed to dog-bite hazards because there is no separate room to secure dogs while Benjamin cares for Jane or while others enter the home.",
            "The same loss of bedroom/workspace makes it materially harder or impossible for Benjamin Barber to work from home as a software engineer while also caring for Jane Cortez and maintaining safe separation of sleeping, caregiving, dogs, equipment, guests, and emergency access.",
        ]),
        ("VAWA / Lease-Removal Background", [
            "Petitioners raised abuse-related safety issues involving Julio Cortez and sought VAWA-related lease bifurcation or protection. Repository records reflect that a Julio-related protective order existed by November 2025 and that HACC was repeatedly placed on notice of household-composition and restraining-order issues.",
            "Petitioners allege that despite the restraining-order and VAWA context, HACC unlawfully removed Benjamin Barber from the lease and treated Julio Cortez as restored to or still part of the household, penalizing the protected side of the household rather than isolating the alleged perpetrator.",
            "Petitioners previously filed EPPDAPA/protective-order matters naming Ashley Ferron in her official HACC capacity. Repository materials reflect those petitions were denied. Petitioners reference those filings as background and pattern, not as proof that the prior petitions were granted.",
            "After the Ashley Ferron matter was denied, Petitioners discovered and allege that Benjamin's brother, Solomon Samuel Barber, against whom a protective order had been made, was the person who caused or induced HACC to remove Benjamin from the lease despite that protective order.",
            "Petitioners allege that Respondent Kati Tilton and HACC knew or should have known that relying on a restrained person's collateral communications or claimed authority to alter lease rights would endanger Petitioners and violate federal housing and abuse-protection safeguards.",
        ]),
        ("Requested Relief", [
            "Order Respondent not to abuse, intimidate, molest, interfere with, or menace Petitioners.",
            "Order Respondent not to cause, authorize, request, coordinate, or enforce displacement, lockout, eviction trespass, lease removal, loss of subsidy, loss of voucher, or loss of relocation rights while federal relocation/voucher issues remain unresolved except through lawful court proceedings after compliance with applicable federal protections.",
            "Order Respondent and HACC not to take possession of, lock out Petitioners from, or otherwise dispossess Petitioners from 10043 SE 32nd Ave before at least June 20, 2026, which is 90 days after March 22, 2026, and only after compliance with 42 U.S.C. 1437p, 24 C.F.R. 970.21, and 24 C.F.R. 972.130.",
            "Order Respondent to preserve all HACC records concerning Petitioners' lease composition, household status, VAWA/bifurcation requests, restraining-order documents, communications involving Solomon Samuel Barber or Julio Cortez, Tenant Protection Voucher, portability to Multnomah County, emergency-transfer issues, accommodations, and eviction/possession actions.",
        ]),
    ]
    left = 54
    width = 504
    n = 1
    for heading, paras in sections:
        if y > 700:
            page = attachment.new_page(width=612, height=792)
            y = 54
        page.insert_text((left, y), heading, fontsize=10, fontname="helv")
        y += 16
        for para in paras:
            lines = []
            line = ""
            for word in para.split():
                test = word if not line else f"{line} {word}"
                if fitz.get_text_length(test, fontname="helv", fontsize=8.6) <= width - 22:
                    line = test
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            if y + len(lines) * 12 > 735:
                page = attachment.new_page(width=612, height=792)
                y = 54
            page.insert_text((left, y), f"{n}.", fontsize=8.6, fontname="helv")
            for ln in lines:
                page.insert_text((left + 22, y), ln, fontsize=8.6, fontname="helv")
                y += 12
            y += 5
            n += 1
        y += 5
    doc.insert_pdf(attachment, start_at=5)


def main():
    doc = fitz.open(FORM)
    # Keep only the official forms section, not the instruction pages.
    keep = list(range(6, 23))
    new = fitz.open()
    for i in keep:
        new.insert_pdf(doc, from_page=i, to_page=i)
    fill_petition(new)
    fill_order(new)
    fill_service_info(new)
    add_attachment(new)
    new.save(OUTPUT)
    add_email_exhibits(new)
    new.save(OUTPUT_WITH_EXHIBITS)
    print(OUTPUT)
    print(OUTPUT_WITH_EXHIBITS)


if __name__ == "__main__":
    main()
