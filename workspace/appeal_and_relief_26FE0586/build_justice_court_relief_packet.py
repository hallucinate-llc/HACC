from io import BytesIO
from pathlib import Path
from email import policy
from email.parser import BytesParser

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


ROOT = Path("/home/barberb/HACC")
BASE = ROOT / "workspace/appeal_and_relief_26FE0586"
EXHIBIT_A = ROOT / "evidence/paper documents/Gmail - Orientation Registration - Cortez - 04_22_2026 @10AM.pdf"
EXHIBIT_VOUCHER = ROOT / "workspace/imap-confirmed-messages/extracted-attachments/2026-03-26_hcv-orientation_living-room_3__Voucher 3.20.26.pdf"
PORT_THREAD_SOURCE = ROOT / "workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml"
EXHIBIT_B_SOURCE = ROOT / "evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB9270F53EFF04DC797564CE209450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Request-for-additional-information-Cortez---DUE-04-15-2026/message.eml"

LEAD = BASE / "justice_court_motion_for_relief_26FE0586_lead.pdf"
FINAL = BASE / "justice_court_emergency_motion_for_relief_packet_26FE0586.pdf"
NOTICE = BASE / "notice_of_appeal_26FE0586.pdf"
STAY_LEAD = BASE / "motion_to_stay_pending_appeal_and_supersedeas_undertaking_26FE0586.pdf"
STAY_PACKET = BASE / "stay_pending_appeal_packet_26FE0586.pdf"

BODY_FONT = "Helvetica"
BODY_SIZE = 9.2
HEADING_SIZE = 10.5
LINE_STEP = 0.18 * inch
PARA_GAP = 0.065 * inch
BOTTOM_SAFE = 1.45 * inch
LEFT_MARGIN = 0.8 * inch
RIGHT_MARGIN = 0.95 * inch


MOTION_ITEMS = [
    ("intro", "Defendants Jane Kay Cortez and Benjamin Jay Barber move for emergency relief from any default judgment, judgment for possession, judgment of restitution, order of default, writ-related order, or other adverse judgment entered after Defendants missed the April 22, 2026 court appearance at 8:15 a.m."),
    ("heading", "Request"),
    ("numbered", "Vacate and set aside any default or possession judgment entered on April 22, 2026."),
    ("numbered", "Recall, stay, quash, or suspend any notice of restitution, writ of execution, lockout process, or eviction trespass notice."),
    ("numbered", "Reset the first appearance or set an emergency hearing on this motion."),
    ("numbered", "Accept Defendants' answer, motion to dismiss, and federal relocation defenses for hearing on the merits."),
    ("numbered", "Alternatively, stay enforcement long enough for Defendants to pursue appeal and any undertaking, waiver, reduction, or other relief the Court finds just."),
    ("numbered", "Grant any other relief necessary to prevent manifest injustice."),
    ("heading", "Why Relief Is Needed Now"),
    ("numbered", "Defendants file this motion immediately after discovering that they missed the 8:15 a.m. court appearance."),
    ("numbered", "The missed appearance was not intentional. It resulted from a good-faith calendar/time confusion involving a separate housing-related meeting titled \"Gmail - Orientation Registration - Cortez - 04_22_2026 @10AM.\""),
    ("numbered", "Both events concerned the same housing crisis, the same household, the same relocation/voucher process, and the same date, April 22, 2026. Defendants were not ignoring the Court; they were attempting to attend to the housing and relocation process intertwined with this eviction."),
    ("heading", "Legal Basis"),
    ("numbered", "ORCP 71 B authorizes relief from judgment for mistake, inadvertence, surprise, or excusable neglect; voidness; and circumstances where prospective enforcement is no longer equitable."),
    ("numbered", "Defendants invoke ORCP 71 B(1)(a), (d), and (e), ORS 105.137, and the Court's equitable authority to prevent manifest injustice."),
    ("numbered", "Even on default, a court should not enforce a judgment unsupported by a legally sufficient present claim for possession."),
    ("heading", "Federal Possession Bar"),
    ("numbered", "This case is not a routine private holdover. Plaintiff is the Housing Authority of Clackamas County, and the eviction arises from public-housing displacement tied to demolition, disposition, relocation, and Tenant Protection Voucher administration."),
    ("numbered", "Federal law controls key conditions precedent to displacement and possession. Under 42 U.S.C. § 1437p and 24 C.F.R. § 970.21, residents displaced by public-housing demolition or disposition must receive comparable housing, relocation expenses, counseling, and actual relocation protections."),
    ("numbered", "Tenant-based assistance is not comparable housing until the family is actually relocated into such housing. Under 24 C.F.R. § 972.130(b)(4), where Section 8 voucher assistance is used for relocation, the family must be provided vouchers at least 90 days before displacement."),
    ("numbered", "Those rules are not merely background defenses. They bar Plaintiff from obtaining or enforcing possession as though relocation were complete unless the federal relocation prerequisites have actually been satisfied."),
    ("numbered", "HACC could not treat Tenant Protection Voucher paperwork or an unfinished housing search as completed comparable housing. HACC also could not use voucher-based relocation as a basis for displacement unless the voucher assistance was provided at least 90 days before displacement where 24 C.F.R. § 972.130 applies."),
    ("numbered", "A default judgment entered without adjudicating those defenses rests on a legally insufficient premise: that Plaintiff was presently entitled to possession despite unresolved federal relocation conditions and despite federal law barring displacement before those conditions were satisfied."),
    ("heading", "Meritorious Defenses"),
    ("numbered", "Plaintiff failed to plead or prove present entitlement to possession."),
    ("numbered", "Plaintiff pursued possession before completing federal relocation duties under 42 U.S.C. § 1437p and 24 C.F.R. § 970.21."),
    ("numbered", "Plaintiff did not provide voucher-based relocation assistance at least 90 days before displacement as required where 24 C.F.R. § 972.130 applies."),
    ("numbered", "Tenant-based assistance does not count as comparable housing until actual relocation into such housing."),
    ("numbered", "Plaintiff's own records show the relocation/voucher path was active and unresolved in March and April 2026."),
    ("numbered", "Plaintiff's process also implicates reasonable-accommodation, live-in-aide, disability, and emergency-transfer issues that were not resolved before the possession request."),
    ("heading", "Manifest Injustice"),
    ("numbered", "Allowing the judgment to stand would cause manifest injustice: loss of home, loss of possession, possible lockout, loss or collapse of relocation and voucher rights, and possible destruction of the subject matter before the Court reaches the merits."),
    ("numbered", "The prejudice to Defendants is extreme. Plaintiff can still litigate possession on the merits if default is set aside."),
    ("heading", "Conclusion"),
    ("intro", "Defendants respectfully ask the Court to set aside any default or judgment, stay enforcement immediately, reset the matter for hearing on the merits, and grant all relief necessary to preserve the tenancy, relocation process, voucher rights, and the Court's ability to decide the case lawfully."),
]


DECL_ITEMS = [
    ("intro", "I, Benjamin Jay Barber, declare:"),
    ("numbered", "I am a Defendant in this case. I make this declaration from my own personal knowledge unless otherwise stated."),
    ("numbered", "The court appearance in this eviction matter was scheduled for April 22, 2026 at 8:15 a.m."),
    ("numbered", "I missed that appearance by mistake. I did not intentionally fail to appear, and I did not intend to abandon any defense."),
    ("numbered", "I confused the 8:15 a.m. court appearance with a separate housing-related meeting on the same date. The separate meeting was reflected in a document/email titled \"Gmail - Orientation Registration - Cortez - 04_22_2026 @10AM.\""),
    ("numbered", "I understood that 10:00 a.m. meeting to be connected to Multnomah County / housing orientation and the same relocation/voucher process intertwined with this eviction case."),
    ("numbered", "Because both events concerned the same housing crisis and occurred on the same date, I conflated the times in good faith."),
    ("numbered", "I have actively tried to defend this case. Before the missed appearance, I had prepared or caused to be prepared a motion to dismiss, a federal authority packet, and arguments concerning HACC's unresolved relocation and Tenant Protection Voucher duties."),
    ("numbered", "My household has substantial defenses to possession, including that HACC had not completed the relocation/voucher process before pursuing possession and that federal law required comparable housing and actual relocation protections."),
    ("numbered", "Allowing a default or possession judgment to stand would cause severe prejudice, including loss of home, possible lockout, disruption of relocation rights, and possible loss or collapse of voucher/subsidy protections before the merits are heard."),
    ("numbered", "I acted promptly once I realized the mistake and ask the Court to set aside any default or judgment and allow the matter to be heard on the merits."),
    ("numbered", "Attached as Exhibit A is the document titled \"Gmail - Orientation Registration - Cortez - 04_22_2026 @10AM,\" which reflects the separate 10:00 a.m. housing-related orientation that contributed to the confusion."),
]


JANE_DECL_ITEMS = [
    ("intro", "I, Jane Kay Cortez, declare:"),
    ("numbered", "I am a Defendant in this case."),
    ("numbered", "I understand that the April 22, 2026 8:15 a.m. court appearance was missed because of confusion with a separate 10:00 a.m. housing-related orientation meeting on the same date."),
    ("numbered", "I did not intend to abandon my defenses or consent to eviction."),
    ("numbered", "I ask the Court to set aside any default or possession judgment and allow the case to be heard on the merits."),
    ("numbered", "I face serious prejudice and manifest injustice if a default judgment results in loss of my home, loss of relocation rights, or loss of voucher/subsidy protections before my defenses are heard."),
]


NOTICE_ITEMS = [
    ("intro", "Defendants Jane Kay Cortez and Benjamin Jay Barber give notice that they appeal from any default judgment, judgment of restitution, judgment for possession, order of default, writ-related order, or other appealable judgment entered against them on or about April 22, 2026 in this residential eviction case."),
    ("heading", "Preservation of Appellate Rights"),
    ("numbered", "This notice is filed to preserve Defendants' rights under ORS 53.010 to 53.125 and related Justice Court appeal procedures, and under ORS 19.245 to the extent any default judgment is void or appealable after disposition of a motion to set aside default."),
    ("numbered", "Defendants are also filing, or have filed contemporaneously, a motion for relief from judgment, to set aside default, and to stay enforcement in the Justice Court. If that motion is granted, this appeal may become unnecessary. If it is denied, Defendants intend this notice to preserve all available appellate rights."),
    ("heading", "Grounds and Defenses Preserved"),
    ("numbered", "Defendants' failure to appear at the April 22, 2026 8:15 a.m. court appearance resulted from mistake, inadvertence, surprise, or excusable neglect, not intentional disregard of the Court."),
    ("numbered", "Defendants confused the 8:15 a.m. court appearance with a separate housing-related meeting on the same date titled \"Gmail - Orientation Registration - Cortez - 04_22_2026 @10AM,\" connected to housing orientation and the same relocation/voucher process involved in this case."),
    ("numbered", "Defendants have substantial meritorious defenses to possession. Plaintiff is the Housing Authority of Clackamas County, and the case arises from public-housing displacement tied to demolition, disposition, relocation, and Tenant Protection Voucher administration."),
    ("numbered", "Federal law controls key conditions precedent to displacement and possession. Under 42 U.S.C. § 1437p and 24 C.F.R. § 970.21, residents displaced by public-housing demolition or disposition must receive comparable housing, relocation expenses, counseling, and actual relocation protections."),
    ("numbered", "Tenant-based assistance is not comparable housing until the family is actually relocated into such housing. Under 24 C.F.R. § 972.130(b)(4), where Section 8 voucher assistance is used for relocation, the family must be provided vouchers at least 90 days before displacement."),
    ("numbered", "Plaintiff could not obtain or enforce possession as though relocation were complete unless the federal relocation prerequisites were satisfied. A default possession judgment entered without adjudicating those defenses rests on a legally insufficient premise of present entitlement to possession."),
    ("numbered", "Plaintiff's own relocation/voucher process remained active and unresolved in March and April 2026, and the case also implicates reasonable-accommodation, live-in-aide, disability, and emergency-transfer issues that were not resolved before Plaintiff sought possession."),
    ("numbered", "Allowing a default possession judgment to stand would cause manifest injustice, including loss of home, possible lockout, disruption of relocation rights, and possible loss or collapse of voucher/subsidy protections before the merits are heard."),
    ("heading", "Request for Stay"),
    ("numbered", "Defendants request that enforcement of any judgment for possession, notice of restitution, writ, lockout, or eviction trespass notice be stayed pending resolution of the motion for relief from judgment and/or appeal, subject to any undertaking, waiver, reduction, or other terms the Court finds just."),
]


STAY_ITEMS = [
    ("intro", "Defendants / Appellants Jane Kay Cortez and Benjamin Jay Barber move the Circuit Court, as the appellate court on appeal from Justice Court, for an order staying enforcement of any judgment for possession, judgment of restitution, notice of restitution, writ of execution, lockout, or eviction trespass notice pending appeal, and ask the Court to approve, waive, reduce, limit, or set the undertaking terms necessary to preserve possession while appellate review proceeds."),
    ("heading", "Relief Requested"),
    ("numbered", "Stay all enforcement of any April 22, 2026 possession judgment pending appeal."),
    ("numbered", "Approve the attached undertaking, or waive, reduce, limit, or set the amount and terms of the undertaking under ORS 53.040."),
    ("numbered", "If the Court requires a cash deposit, bond, or registry payment to perfect the stay, set the amount expressly, identify where it must be deposited, and allow a reasonable time after entry of the stay order for Defendants to make that deposit."),
    ("numbered", "Alternatively, enter temporary appellate stay relief while the undertaking amount and terms are set."),
    ("numbered", "Order that no writ, notice of restitution, lockout, or transfer of possession be enforced while the stay is in effect."),
    ("heading", "Stay Authority"),
    ("numbered", "This is an appeal from a civil judgment in Justice Court. Under ORS 53.020, the appeal lies to Clackamas County Circuit Court."),
    ("numbered", "Under ORS 53.030, the notice of appeal is served on the adverse party and filed with the Justice Court, and when the notice has been served and filed the appellate court has jurisdiction of the cause."),
    ("numbered", "Under ORS 53.040, the undertaking is filed with the justice within five days after the notice of appeal is given or filed, and the justice or the appellate court may waive, reduce, or limit the undertaking for good cause, including indigency, on just and equitable terms."),
    ("numbered", "Under ORS 53.060, when an appeal is taken the justice states whether proceedings are stayed. The Justice Court denied stay relief, so Defendants now request that the Circuit Court, as the appellate court, grant stay relief and set equitable undertaking terms."),
    ("numbered", "Under ORS 53.090, once the transcript and papers are filed with the clerk of the appellate court the appeal is perfected, and the action is then pending in circuit court for further proceedings."),
    ("numbered", "Clackamas County Justice Court's current appeal instructions direct litigants to file the notice of appeal with the Justice Court, which then notifies the Circuit Court."),
    ("heading", "Why A Stay Should Enter"),
    ("numbered", "This appeal is taken in good faith, not for delay. Defendants immediately prepared post-judgment filings after discovering the missed April 22, 2026 hearing."),
    ("numbered", "The underlying possession judgment is challenged as void or unenforceable because it awarded present possession in conflict with controlling federal law governing HACC's displacement and relocation duties."),
    ("numbered", "Under 42 U.S.C. 1437p(a)(4) and 24 C.F.R. 970.21, HACC may not complete a disposition-driven displacement process until residents are relocated, must provide comparable housing, must provide counseling and relocation expenses, and tenant-based assistance does not count as comparable housing until the family is actually relocated into such housing."),
    ("numbered", "24 C.F.R. 972.130 requires a conversion plan to describe, among other things, how residents will be assisted through tenant-based assistance and related relocation components; where voucher assistance is the chosen path, Defendants contend federal law required voucher assistance to be provided at least 90 days before displacement or transfer of possession."),
    ("numbered", "Exhibit A is the voucher provided by HACC. The voucher form lists an issue date of March 19, 2026 and shows signatures dated March 20, 2026. On Defendants' calculation, any displacement or transfer of possession before at least June 17, 2026 from the issue date, or before at least June 18, 2026 from the signed/provided date, would be inconsistent with the 90-day federal relocation timetable."),
    ("numbered", "As a matter of law and fact, HACC should not have been pursuing state-court eviction while the voucher-porting relocation process was still underway, and should not have sought possession only about 10 days after granting the voucher."),
    ("numbered", "Exhibit B, the April 22, 2026 orientation registration record, further shows that the household was still engaged in relocation-related orientation and porting activity on the same date as the missed court appearance, not at the end of a completed relocation process."),
    ("numbered", "The federal relocation rules require actual relocation protections and time for voucher-based relocation to occur. A housing authority cannot short-circuit that process by issuing a voucher, leaving the family in the middle of porting and housing search activity, and then almost immediately pursuing restitution in state court."),
    ("numbered", "Irreparable injury will occur if stay relief is denied. Defendant Jane Cortez is elderly at 73 years old, approximately four feet six inches tall, has cognitive disorder, and has mobility impairment. Abrupt eviction or lockout before the voucher can be ported and before she has enough time to move safely to Multnomah County would create a serious risk of immediate physical dislocation, medical destabilization, and loss of the very relocation opportunity federal law was intended to protect."),
    ("numbered", "Because the judgment is challenged as void or unenforceable and because Defendants are disabled occupants facing immediate loss of housing, the Court should not require an undefined immediate deposit before entering temporary stay relief. If a deposit is required, the amount should be set in a specific order and payment should be due only after notice of the amount and a reasonable compliance period."),
    ("numbered", "The harm from denying a stay is extraordinary: loss of home, lockout, disruption of relocation and voucher rights, and destruction of the status quo before appellate review of the federal-preemption and void-judgment issues can occur."),
    ("numbered", "The harm to Plaintiff from a stay can be addressed by undertaking terms preserving the premises and securing the value of use and occupation during the appeal."),
    ("heading", "Conclusion"),
    ("intro", "Defendants respectfully request that the Circuit Court enter an immediate stay pending appeal, approve or promptly set equitable undertaking terms, and grant any further order necessary to preserve possession until the appeal and the federal defenses can be resolved lawfully."),
]


SUPERS_ITEMS = [
    ("intro", "Defendants / Appellants Jane Kay Cortez and Benjamin Jay Barber submit this proposed undertaking under ORS 53.040, subject to approval, waiver, reduction, limitation, or modification by the Circuit Court."),
    ("numbered", "Appellants will not commit waste or allow waste to be committed on the premises located at 10043 SE 32nd Ave, Milwaukie, OR 97222 while they remain in possession during appeal."),
    ("numbered", "If the judgment is affirmed, Appellants will pay the value of use and occupation of the premises during the period of possession in the amount stated below, or in such amount as the Court sets by order."),
    ("numbered", "Stated value of use and occupation for purposes of appellate stay terms: $________________ per month, subject to the Court's approval, reduction, limitation, or modification."),
    ("numbered", "If the Court requires deposit of money into the court registry or filing of a bond, Appellants request that the order specify the exact amount, payee or registry, deadline, and any installment or other payment terms."),
    ("numbered", "Appellants request that the Court approve this undertaking as filed or set a different amount and temporary stay terms that preserve the status quo pending appeal."),
]


def wrap(text, width, font=BODY_FONT, size=BODY_SIZE):
    words = []
    # ReportLab will happily draw a single long token past the margin. Break
    # long tokens here so quoted filenames, dates, and email-style strings
    # cannot overflow the right edge.
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


def load_exhibit_b_email():
    with EXHIBIT_B_SOURCE.open("rb") as fh:
        msg = BytesParser(policy=policy.default).parse(fh)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and part.get_content_disposition() != "attachment":
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    headers = [
        ("From", str(msg.get("From", ""))),
        ("To", str(msg.get("To", ""))),
        ("Subject", str(msg.get("Subject", ""))),
        ("Date", str(msg.get("Date", ""))),
        ("Message-ID", str(msg.get("Message-ID", ""))),
        ("Preserved file", str(EXHIBIT_B_SOURCE)),
    ]
    return headers, body.replace("\r\n", "\n").replace("\r", "\n")


def footer(c, page, title):
    c.setFont("Helvetica", 8.5)
    c.drawString(LEFT_MARGIN, 0.45 * inch, f"FED - {title}")
    c.drawRightString(letter[0] - RIGHT_MARGIN, 0.45 * inch, f"Page {page}")


def caption(c, y, motion_title, subtitle):
    width, _ = letter
    left = LEFT_MARGIN
    right = width - RIGHT_MARGIN
    mid = width / 2
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "IN THE JUSTICE COURT OF THE STATE OF OREGON")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "FOR THE COUNTY OF CLACKAMAS")
    y -= 0.38 * inch
    top = y
    bottom = y - 1.72 * inch
    c.setLineWidth(0.75)
    c.line(left, top, right, top)
    c.line(left, bottom, right, bottom)
    c.line(mid, top, mid, bottom)
    c.setFont("Helvetica", 9.5)
    c.drawString(left + 0.1 * inch, top - 0.25 * inch, "Housing Authority of Clackamas County")
    c.drawString(left + 0.1 * inch, top - 0.48 * inch, "Plaintiff (Landlord or Agent)")
    c.drawString(left + 0.1 * inch, top - 0.78 * inch, "v.")
    c.drawString(left + 0.1 * inch, top - 1.08 * inch, "Jane Kay Cortez, Benjamin Jay Barber,")
    c.drawString(left + 0.1 * inch, top - 1.31 * inch, "and All Other Occupants")
    c.drawString(left + 0.1 * inch, top - 1.54 * inch, "Defendants (Tenants or Occupants)")
    c.drawString(mid + 0.1 * inch, top - 0.25 * inch, "Case No: 26FE0586")
    c.setFont("Helvetica-Bold", 11)
    title_y = top - 0.70 * inch
    for line in wrap(motion_title, 2.55 * inch, "Helvetica-Bold", 11):
        c.drawString(mid + 0.1 * inch, title_y, line)
        title_y -= 0.18 * inch
    c.setFont("Helvetica", 9.5)
    for line in wrap(subtitle, 2.55 * inch, "Helvetica", 9.2):
        c.drawString(mid + 0.1 * inch, title_y - 0.05 * inch, line)
        title_y -= 0.18 * inch
    return bottom - 0.35 * inch


def circuit_stay_caption(c, y, motion_title, subtitle):
    width, _ = letter
    left = LEFT_MARGIN
    right = width - RIGHT_MARGIN
    mid = width / 2
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "IN THE CIRCUIT COURT OF THE STATE OF OREGON")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "FOR THE COUNTY OF CLACKAMAS")
    y -= 0.38 * inch
    top = y
    bottom = y - 1.90 * inch
    c.setLineWidth(0.75)
    c.line(left, top, right, top)
    c.line(left, bottom, right, bottom)
    c.line(mid, top, mid, bottom)
    c.setFont("Helvetica", 9.5)
    c.drawString(left + 0.1 * inch, top - 0.25 * inch, "Housing Authority of Clackamas County")
    c.drawString(left + 0.1 * inch, top - 0.48 * inch, "Plaintiff / Respondent")
    c.drawString(left + 0.1 * inch, top - 0.78 * inch, "v.")
    c.drawString(left + 0.1 * inch, top - 1.08 * inch, "Jane Kay Cortez, Benjamin Jay Barber,")
    c.drawString(left + 0.1 * inch, top - 1.31 * inch, "and All Other Occupants")
    c.drawString(left + 0.1 * inch, top - 1.54 * inch, "Defendants / Appellants")
    c.drawString(mid + 0.1 * inch, top - 0.25 * inch, "Circuit Court Case No: ________________")
    c.drawString(mid + 0.1 * inch, top - 0.48 * inch, "Justice Court Case No: 26FE0586")
    c.setFont("Helvetica-Bold", 11)
    title_y = top - 0.86 * inch
    for line in wrap(motion_title, 2.55 * inch, "Helvetica-Bold", 11):
        c.drawString(mid + 0.1 * inch, title_y, line)
        title_y -= 0.18 * inch
    c.setFont("Helvetica", 9.5)
    for line in wrap(subtitle, 2.55 * inch, "Helvetica", 9.2):
        c.drawString(mid + 0.1 * inch, title_y - 0.05 * inch, line)
        title_y -= 0.18 * inch
    return bottom - 0.35 * inch


def render_items(c, items, y, page, title, start_no=1):
    width, height = letter
    left = LEFT_MARGIN
    right = width - RIGHT_MARGIN
    para_no = start_no

    def new_page():
        nonlocal page, y
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch

    def ensure(space):
        if y - space < BOTTOM_SAFE:
            new_page()

    for kind, text in items:
        if kind == "heading":
            ensure(0.45 * inch)
            c.setFont("Helvetica-Bold", HEADING_SIZE)
            c.drawString(left, y, text)
            y -= 0.28 * inch
        elif kind == "numbered":
            body_left = left + 0.25 * inch
            lines = wrap(text, right - body_left, BODY_FONT, BODY_SIZE)
            ensure(len(lines) * LINE_STEP + 0.34 * inch)
            c.setFont(BODY_FONT, BODY_SIZE)
            c.drawString(left, y, f"{para_no}.")
            for line in lines:
                c.setFont(BODY_FONT, BODY_SIZE)
                c.drawString(body_left, y, line)
                y -= LINE_STEP
            y -= PARA_GAP
            para_no += 1
        else:
            lines = wrap(text, right - left, BODY_FONT, BODY_SIZE)
            ensure(len(lines) * LINE_STEP + 0.25 * inch)
            c.setFont(BODY_FONT, BODY_SIZE)
            for line in lines:
                c.setFont(BODY_FONT, BODY_SIZE)
                c.drawString(left, y, line)
                y -= LINE_STEP
            y -= PARA_GAP
    return y, page, para_no


def render_lead():
    c = canvas.Canvas(str(LEAD), pagesize=letter)
    width, height = letter
    title = "Emergency Motion for Relief"
    page = 1
    y = height - 0.7 * inch
    y = caption(c, y, "EMERGENCY MOTION FOR RELIEF FROM JUDGMENT", "Set Aside Default and Stay Enforcement")
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "Filed by: Jane Kay Cortez and Benjamin Jay Barber, Defendants pro se")
    y -= 0.22 * inch
    c.drawString(LEFT_MARGIN, y, "Property: 10043 SE 32nd Ave, Milwaukie, OR 97222")
    y -= 0.35 * inch
    y, page, _ = render_items(c, MOTION_ITEMS, y, page, title)
    y -= 0.08 * inch
    if y < 1.8 * inch:
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026.")
    y -= 0.45 * inch
    c.drawString(LEFT_MARGIN, y, "Respectfully submitted,")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber, Defendant pro se")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez, Defendant pro se")
    footer(c, page, title)

    # Proposed order
    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "IN THE JUSTICE COURT OF THE STATE OF OREGON")
    y -= 0.22 * inch
    c.drawCentredString(width / 2, y, "FOR THE COUNTY OF CLACKAMAS")
    y -= 0.50 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "ORDER ON DEFENDANTS' EMERGENCY MOTION FOR RELIEF")
    y -= 0.42 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    order_lines = [
        "Case No: 26FE0586",
        "The Court has considered Defendants' Emergency Motion for Relief from Judgment, to Set Aside Default, and to Stay Enforcement.",
        "",
        "IT IS ORDERED:",
        "[ ] Defendants' motion is GRANTED. Any default, judgment for possession, judgment of restitution, or related order entered on or about April 22, 2026 is vacated and set aside.",
        "[ ] Enforcement of any judgment, notice of restitution, writ, lockout, or eviction trespass notice is stayed immediately pending further order.",
        "[ ] Any issued writ, restitution process, lockout process, or eviction trespass notice is recalled, quashed, or suspended.",
        "[ ] The matter is reset for hearing on ____________________, 2026 at ____________.",
        "[ ] Defendants may file or present their answer, motion to dismiss, and federal relocation defenses.",
        "[ ] Defendants' request for relief is denied.",
        "[ ] Other: ________________________________________________________________________________",
        "",
        "DATED: ____________________, 2026.",
        "",
        "__________________________________",
        "Judge",
    ]
    for line in order_lines:
        if not line:
            y -= 0.18 * inch
            continue
        for wrapped in wrap(line, width - LEFT_MARGIN - RIGHT_MARGIN, BODY_FONT, BODY_SIZE):
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.22 * inch
        y -= 0.04 * inch
    footer(c, page, title)

    # Certificate
    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "CERTIFICATE OF SERVICE")
    y -= 0.45 * inch
    service_lines = [
        "I certify that on April ___, 2026, I served a true copy of this Emergency Motion for Relief and attached declaration/exhibit on Plaintiff Housing Authority of Clackamas County.",
        "[ ] First-class mail to: Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045.",
        "[ ] Email to: cskee@clackamas.us.",
        "[ ] Hand delivery.",
        "[ ] Other: ________________________________________________________________________________",
        "",
        "__________________________________        __________________________________",
        "Benjamin Jay Barber                         Jane Kay Cortez",
    ]
    c.setFont(BODY_FONT, BODY_SIZE)
    for line in service_lines:
        if not line:
            y -= 0.22 * inch
            continue
        for wrapped in wrap(line, width - LEFT_MARGIN - RIGHT_MARGIN, BODY_FONT, BODY_SIZE):
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.24 * inch
    footer(c, page, title)

    # Declarations
    c.showPage()
    page += 1
    y = height - 0.75 * inch
    y = caption(c, y, "DECLARATION IN SUPPORT OF EMERGENCY MOTION", "Benjamin Jay Barber and Jane Kay Cortez")
    y, page, _ = render_items(c, DECL_ITEMS[:-1], y, page, title, start_no=1)
    # Keep paragraph 11, the penalty-of-perjury language, and Benjamin's
    # signature block together. This prevents the final declaration fact from
    # sitting at the page edge or visually running into the footer.
    if y < 3.05 * inch:
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch
    y, page, _ = render_items(c, DECL_ITEMS[-1:], y, page, title, start_no=11)
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "I declare under penalty of perjury that the foregoing is true and correct.")
    y -= 0.35 * inch
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026, at Milwaukie, Oregon.")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber")
    y -= 0.50 * inch
    y, page, _ = render_items(c, JANE_DECL_ITEMS, y, page, title, start_no=1)
    if y < 1.6 * inch:
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "I declare under penalty of perjury that the foregoing is true and correct.")
    y -= 0.35 * inch
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026, at Milwaukie, Oregon.")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Jane Kay Cortez")
    footer(c, page, title)
    c.save()


def render_notice_of_appeal():
    c = canvas.Canvas(str(NOTICE), pagesize=letter)
    width, height = letter
    title = "Notice of Appeal"
    page = 1
    y = height - 0.7 * inch
    y = caption(c, y, "NOTICE OF APPEAL", "Default Judgment / FED Possession")
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "Filed by: Jane Kay Cortez and Benjamin Jay Barber, Defendants/Appellants pro se")
    y -= 0.22 * inch
    c.drawString(LEFT_MARGIN, y, "Property: 10043 SE 32nd Ave, Milwaukie, OR 97222")
    y -= 0.35 * inch
    y, page, _ = render_items(c, NOTICE_ITEMS, y, page, title)

    if y < 1.95 * inch:
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026.")
    y -= 0.45 * inch
    c.drawString(LEFT_MARGIN, y, "Respectfully submitted,")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber, Defendant/Appellant pro se")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez, Defendant/Appellant pro se")
    footer(c, page, title)

    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "CERTIFICATE OF SERVICE")
    y -= 0.45 * inch
    service_lines = [
        "I certify that on April ___, 2026, I served a true copy of this Notice of Appeal on Plaintiff Housing Authority of Clackamas County.",
        "[ ] First-class mail to: Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045.",
        "[ ] Email to: cskee@clackamas.us.",
        "[ ] Hand delivery.",
        "[ ] Other: ________________________________________________________________________________",
    ]
    c.setFont(BODY_FONT, BODY_SIZE)
    for line in service_lines:
        for wrapped in wrap(line, width - LEFT_MARGIN - RIGHT_MARGIN, BODY_FONT, BODY_SIZE):
            c.setFont(BODY_FONT, BODY_SIZE)
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.24 * inch
    y -= 0.30 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez")
    footer(c, page, title)
    c.save()


def exhibit_cover():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.5 * inch, "EXHIBIT A")
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(4.25 * inch, 5.95 * inch, "Gmail - Orientation Registration - Cortez - 04/22/2026 @ 10AM")
    c.setFont("Helvetica", 11)
    c.drawCentredString(4.25 * inch, 5.35 * inch, "Separate housing-related orientation document referenced in the declaration.")
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, "FED - Exhibit A Cover")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def voucher_exhibit_cover():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.5 * inch, "EXHIBIT A")
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(4.25 * inch, 5.95 * inch, "HACC Voucher Issued 03/19/2026 and Signed 03/20/2026")
    c.setFont("Helvetica", 11)
    c.drawCentredString(4.25 * inch, 5.35 * inch, "Voucher exhibit relied on for the 90-day displacement argument.")
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, "FED - Stay Exhibit A Cover")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def orientation_exhibit_cover():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.5 * inch, "EXHIBIT B")
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(4.25 * inch, 5.95 * inch, "April 22, 2026 Orientation Registration Email / PDF")
    c.setFont("Helvetica", 11)
    c.drawCentredString(4.25 * inch, 5.35 * inch, "Orientation record supporting the April 22 timing-confusion and housing-process context.")
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, "FED - Stay Exhibit B Cover")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def authority_exhibit_cover(label, title_text, subtitle_text):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25 * inch, 6.5 * inch, label)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(4.25 * inch, 5.95 * inch, title_text)
    c.setFont("Helvetica", 11)
    c.drawCentredString(4.25 * inch, 5.35 * inch, subtitle_text)
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, 0.45 * inch, f"FED - Stay {label} Cover")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def render_authority_exhibit(label, title_text, source_text, body_lines):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    page = 1
    title = f"Stay {label}"
    y = height - 0.8 * inch
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2, y, label)
    y -= 0.32 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, title_text)
    y -= 0.35 * inch
    c.setFont("Helvetica", 8.9)
    for line in wrap(source_text, letter[0] - LEFT_MARGIN - RIGHT_MARGIN, "Helvetica", 8.9):
        c.drawString(LEFT_MARGIN, y, line)
        y -= 0.18 * inch
    y -= 0.08 * inch
    c.setLineWidth(0.5)
    c.line(LEFT_MARGIN, y, letter[0] - RIGHT_MARGIN, y)
    y -= 0.2 * inch
    c.setFont("Courier", 8.4)
    for raw in body_lines:
        if not raw:
            if y - 0.14 * inch < BOTTOM_SAFE:
                footer(c, page, title)
                c.showPage()
                page += 1
                y = height - 0.75 * inch
                c.setFont("Courier", 8.4)
            y -= 0.14 * inch
            continue
        wrapped_lines = wrap(raw, letter[0] - LEFT_MARGIN - RIGHT_MARGIN, "Courier", 8.4)
        needed = len(wrapped_lines) * 0.15 * inch + 0.01 * inch
        if y - needed < BOTTOM_SAFE:
            footer(c, page, title)
            c.showPage()
            page += 1
            y = height - 0.75 * inch
            c.setFont("Courier", 8.4)
        for wrapped in wrapped_lines:
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.15 * inch
    footer(c, page, title)
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def build():
    render_notice_of_appeal()
    render_lead()
    writer = PdfWriter()
    for page in PdfReader(str(LEAD)).pages:
        writer.add_page(page)
    writer.add_page(exhibit_cover())
    for page in PdfReader(str(EXHIBIT_A)).pages:
        writer.add_page(page)
    with FINAL.open("wb") as fh:
        writer.write(fh)
    print(FINAL)


def build_stay_packet():
    c = canvas.Canvas(str(STAY_LEAD), pagesize=letter)
    width, height = letter
    title = "Stay Pending Appeal"
    page = 1
    y = height - 0.7 * inch
    y = circuit_stay_caption(c, y, "MOTION TO STAY JUDGMENT PENDING APPEAL", "Circuit Court Appellate Stay and Undertaking Relief")
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "Filed by: Jane Kay Cortez and Benjamin Jay Barber, Defendants/Appellants pro se")
    y -= 0.22 * inch
    c.drawString(LEFT_MARGIN, y, "Property: 10043 SE 32nd Ave, Milwaukie, OR 97222")
    y -= 0.35 * inch
    y, page, _ = render_items(c, STAY_ITEMS, y, page, title)
    if y < 2.3 * inch:
        footer(c, page, title)
        c.showPage()
        page += 1
        y = height - 0.75 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026.")
    y -= 0.45 * inch
    c.drawString(LEFT_MARGIN, y, "Respectfully submitted,")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber, Defendant/Appellant pro se")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez, Defendant/Appellant pro se")
    footer(c, page, title)

    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "PROPOSED SUPERSEDEAS UNDERTAKING")
    y -= 0.45 * inch
    y, page, _ = render_items(c, SUPERS_ITEMS, y, page, title)
    y -= 0.1 * inch
    c.setFont(BODY_FONT, BODY_SIZE)
    c.drawString(LEFT_MARGIN, y, "DATED: April ___, 2026.")
    y -= 0.42 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber, Appellant")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez, Appellant")
    footer(c, page, title)

    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "PROPOSED CIRCUIT COURT ORDER STAYING JUDGMENT PENDING APPEAL")
    y -= 0.48 * inch
    order_lines = [
        "Circuit Court Case No: ____________________    Justice Court Case No: 26FE0586",
        "The Court has considered Defendants' Motion to Stay Judgment Pending Appeal after Justice Court denial of stay relief, together with the proposed undertaking.",
        "",
        "IT IS ORDERED:",
        "[ ] Enforcement of any judgment for possession, notice of restitution, writ of execution, lockout, or eviction trespass notice is stayed pending appeal.",
        "[ ] The undertaking is approved as filed.",
        "[ ] The value of use and occupation for purposes of ORS 19.335(2) is set at $________________ per month.",
        "[ ] Any required deposit into the court registry / bond amount is set at $________________ and shall be deposited by ____________________, 2026.",
        "[ ] Appellants shall not commit or allow waste while they remain in possession during appeal.",
        "[ ] The Circuit Court waives / reduces / limits the undertaking under ORS 53.040 on the terms stated above.",
        "[ ] Other: ________________________________________________________________________________",
        "",
        "DATED: ____________________, 2026.",
        "",
        "__________________________________",
        "Judge",
    ]
    c.setFont(BODY_FONT, BODY_SIZE)
    for line in order_lines:
        if not line:
            y -= 0.18 * inch
            continue
        for wrapped in wrap(line, width - LEFT_MARGIN - RIGHT_MARGIN, BODY_FONT, BODY_SIZE):
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.22 * inch
        y -= 0.04 * inch
    footer(c, page, title)

    c.showPage()
    page += 1
    y = height - 0.75 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "CERTIFICATE OF SERVICE")
    y -= 0.45 * inch
    service_lines = [
        "I certify that on April ___, 2026, I served a true copy of this Motion to Stay Judgment Pending Appeal, proposed supersedeas undertaking, and exhibits on Plaintiff Housing Authority of Clackamas County.",
        "[ ] First-class mail to: Housing Authority of Clackamas County, 13930 S Gain St, Oregon City, OR 97045.",
        "[ ] Email to: cskee@clackamas.us.",
        "[ ] Hand delivery.",
        "[ ] Other: ________________________________________________________________________________",
    ]
    c.setFont(BODY_FONT, BODY_SIZE)
    for line in service_lines:
        for wrapped in wrap(line, width - LEFT_MARGIN - RIGHT_MARGIN, BODY_FONT, BODY_SIZE):
            c.drawString(LEFT_MARGIN, y, wrapped)
            y -= 0.24 * inch
    y -= 0.30 * inch
    c.drawString(LEFT_MARGIN, y, "__________________________________")
    c.drawString(4.45 * inch, y, "__________________________________")
    y -= 0.20 * inch
    c.drawString(LEFT_MARGIN, y, "Benjamin Jay Barber")
    c.drawString(4.45 * inch, y, "Jane Kay Cortez")
    footer(c, page, title)
    c.save()

    writer = PdfWriter()
    for page in PdfReader(str(STAY_LEAD)).pages:
        writer.add_page(page)
    writer.add_page(voucher_exhibit_cover())
    for page in PdfReader(str(EXHIBIT_VOUCHER)).pages:
        writer.add_page(page)
    writer.add_page(orientation_exhibit_cover())
    for page in PdfReader(str(EXHIBIT_A)).pages:
        writer.add_page(page)
    writer.add_page(
        authority_exhibit_cover(
            "EXHIBIT C",
            "42 U.S.C. 1437p",
            "Official statutory authority on demolition/disposition, displacement notice, comparable housing, and relocation.",
        )
    )
    for page in render_authority_exhibit(
        "EXHIBIT C",
        "42 U.S.C. 1437p - Demolition and disposition of public housing",
        "Source: U.S. House Office of the Law Revision Counsel, https://uscode.house.gov/view.xhtml?req=(title:42 section:1437p edition:prelim)",
        [
            "42 U.S.C. 1437p(a)(4) provides, in relevant part:",
            "",
            "(A) the public housing agency will notify each family residing in a project subject to demolition or disposition 90 days prior to the displacement date;",
            "(ii) the demolition of the building in which the family resides will not commence until each resident of the building is relocated; and",
            "(iii) each family displaced by such action will be offered comparable housing;",
            "(III)(aa) tenant-based assistance, except that the comparable housing requirement is fulfilled by tenant-based assistance only upon the relocation of such family into such housing;",
            "(B) the agency will provide for the payment of the actual and reasonable relocation expenses of each resident to be displaced;",
            "(C) the agency will ensure that each displaced resident is offered comparable housing in accordance with the notice;",
            "(D) the agency will provide any necessary counseling for residents who are displaced; and",
            "(E) the agency will not commence demolition or complete disposition until all residents residing in the building are relocated.",
        ],
    ).pages:
        writer.add_page(page)
    writer.add_page(
        authority_exhibit_cover(
            "EXHIBIT D",
            "24 C.F.R. 970.21",
            "Official regulation on relocation of residents in demolition/disposition cases.",
        )
    )
    for page in render_authority_exhibit(
        "EXHIBIT D",
        "24 C.F.R. 970.21 - Relocation of residents",
        "Source: eCFR, current text, and govinfo published CFR reference, https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-970/section-970.21",
        [
            "24 C.F.R. 970.21(a) provides, in relevant part:",
            "A PHA must offer each family displaced by demolition or disposition comparable housing that meets housing quality standards and is located in an area generally not less desirable than the location of the displaced persons.",
            "Tenant-based assistance will not be considered comparable housing until the family is actually relocated into such housing.",
            "A PHA may not complete disposition of a building until all tenants residing in the building are relocated.",
            "",
            "24 C.F.R. 970.21(e) provides, in relevant part:",
            "The PHA is responsible for notifying each family residing in the development 90 days prior to the displacement date.",
            "The notice must state that demolition of the building will not commence until each resident has been relocated.",
            "The notice must state that each family displaced by such action will be provided comparable housing.",
            "The PHA must provide for payment of actual and reasonable relocation expenses.",
            "The PHA must ensure each displaced resident is offered comparable replacement housing and provide any necessary counseling for residents that are displaced.",
        ],
    ).pages:
        writer.add_page(page)
    writer.add_page(
        authority_exhibit_cover(
            "EXHIBIT E",
            "24 C.F.R. 972.130",
            "Official regulation excerpt concerning voucher timing and notice in conversion/relocation context.",
        )
    )
    for page in render_authority_exhibit(
        "EXHIBIT E",
        "24 C.F.R. 972.130(b)(4) - Written notice and voucher timing",
        "Source: govinfo published CFR, Title 24 Part 972 (most recent official PDF), https://www.govinfo.gov/link/cfr/24/972?link-type=pdf&year=mostrecent",
        [
            "24 C.F.R. 972.130(b)(4) provides, in relevant part:",
            "(i) Timing of notice. If the required conversion is not subject to the URA, the notice shall be provided to families at least 90 days before displacement.",
            "(ii) Contents of notice. The written notice shall include all of the following:",
            "(B) The family will be offered comparable housing, which may include tenant-based or project-based assistance, or occupancy in a unit operated or assisted by the PHA, and if tenant-based assistance is used, the comparable housing requirement is fulfilled only upon relocation of the family into such housing.",
            "(C) Any necessary counseling with respect to the relocation will be provided.",
            "(D) Such families will be relocated to other decent, safe, sanitary, and affordable housing that is, to the maximum extent possible, housing of their choice.",
            "(F) Where Section 8 voucher assistance is being used for relocation, the family will be provided with the vouchers at least 90 days before displacement.",
        ],
    ).pages:
        writer.add_page(page)
    with STAY_PACKET.open("wb") as fh:
        writer.write(fh)
    print(STAY_PACKET)


if __name__ == "__main__":
    build()
    build_stay_packet()
