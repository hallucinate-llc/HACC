#!/usr/bin/env python3
"""Collect Solomon-related evidence events into a structured graph feed.

Discovery mode:
- scans all Solomon SMS EML files in workspace/solomon-sms-eml-2026-04-04
- scans all Google Voice transcript files in email_imports matching *-to-solomon-*
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Dict, List, Tuple


OUT = Path("/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_evidence_graph_feed.json")

EML_ROOT = Path("/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04")
GV_ROOT = Path("/home/barberb/HACC/evidence/email_imports")
HACC_NOTICE_SOURCES = [
    Path("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_3.eml"),
    Path("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json"),
]


TRANSCRIPT_PATTERNS = [
    {
        "event_id": "ev_msg_claim_restraining_order_filed",
        "predicate": "MessageClaimOrderFiled",
        "phrase": "restraining order filed",
        "actor": "me",
        "target": "person:solomon",
    },
    {
        "event_id": "ev_msg_claim_restraining_order_granted",
        "predicate": "MessageClaimOrderGranted",
        "phrase": "the restraining order is granted",
        "actor": "me",
        "target": "person:solomon",
    },
    {
        "event_id": "ev_msg_request_service_address",
        "predicate": "MessageRequestServiceAddress",
        "phrase": "provide an address where you can be served",
        "actor": "me",
        "target": "person:solomon",
    },
    {
        "event_id": "ev_solomon_not_incentivized_statement",
        "predicate": "StatementNotIncentivizedToCooperate",
        "phrase": "not incentivized to cooperate",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
    },
    {
        "event_id": "ev_solomon_wait_for_service_statement",
        "predicate": "StatementWaitForServiceBeforeCompliance",
        "phrase": "once i get served and it goes into effect",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
    },
    {
        "event_id": "ev_solomon_judge_overturn_statement",
        "predicate": "StatementWillHaveJudgeOverturn",
        "phrase": "i'd just have the judge overturn anyway",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
    },
    {
        "event_id": "ev_solomon_order_not_in_effect_statement",
        "predicate": "StatementOrderNotInEffect",
        "phrase": "it is not in effect",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
    },
]

EML_PATTERNS = [
    {
        "event_id": "ev_solomon_ack_heard_restraining_order",
        "predicate": "StatementHeardAboutRestrainingOrder",
        "phrase": "i heard about the restraining order",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "I heard about the restraining order.",
    },
    {
        "event_id": "ev_solomon_ack_already_have_order",
        "predicate": "StatementAlreadyHaveRestrainingOrder",
        "phrase": "don't you already have the restraining order",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "Don't you already have the restraining order?",
    },
    {
        "event_id": "ev_solomon_not_incentivized_eml",
        "predicate": "StatementNotIncentivizedToCooperate",
        "phrase": "not incentivized to cooperate",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "I'm just not incentivized to cooperate.",
    },
    {
        "event_id": "ev_solomon_pickup_plan_for_jane",
        "predicate": "StatementPlannedPickupOfJane",
        "phrase": "jane has an appointment tomorrow with adult protective services tomorrow at 12pm. i will be coming by at 11:30pm to pick her up.",
        "actor": "person:solomon",
        "target": "person:jane_cortez",
        "text": "Jane has an appointment tomorrow with Adult Protective Services tomorrow at 12pm. I will be coming by at 11:30pm to pick her up.",
    },
    {
        "event_id": "ev_solomon_identified_aps_contact",
        "predicate": "StatementProvidedApsContact",
        "phrase": "juliet sutherland apss investigator 971-501-9448 221 mollala ave oregon city or 12:00",
        "actor": "person:solomon",
        "target": "org:adult_protective_services",
        "text": "Juliet Sutherland APSS investigator 971-501-9448 221 Mollala Ave Oregon City OR 12:00",
    },
    {
        "event_id": "ev_solomon_provided_aps_reference_number",
        "predicate": "StatementProvidedApsReference",
        "phrase": "aps reference # 00439866",
        "actor": "person:solomon",
        "target": "org:adult_protective_services",
        "text": "APS reference # 00439866",
    },
    {
        "event_id": "ev_solomon_conditionally_cancel_pickup",
        "predicate": "StatementConditionalPickupCancellation",
        "phrase": "if she agrees to conduct the interview at your place, please ask her to let me know so i don't have to pick up jane",
        "actor": "person:solomon",
        "target": "person:jane_cortez",
        "text": "If she agrees to conduct the interview at your place, please ask her to let me know so I don't have to pick up Jane",
    },
    {
        "event_id": "ev_solomon_arrival_statement_for_pickup",
        "predicate": "StatementArrivalForPickup",
        "phrase": "anyway, i'll be there at 11:30. i don't need to go in, i'm just there to pickup jane.",
        "actor": "person:solomon",
        "target": "person:jane_cortez",
        "text": "Anyway, I'll be there at 11:30. I don't need to go in, I'm just there to pickup Jane.",
    },
    {
        "event_id": "ev_solomon_wait_for_service_eml",
        "predicate": "StatementWaitForServiceBeforeCompliance",
        "phrase": "once i get served and it goes into effect, i will comply with whatever the order states. but it is not in effect.",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "Once I get served and it goes into effect, I will comply with whatever the order states. But it is not in effect.",
    },
    {
        "event_id": "ev_solomon_order_not_in_effect_statement",
        "predicate": "StatementOrderNotInEffect",
        "phrase": "but it is not in effect.",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "But it is not in effect.",
    },
    {
        "event_id": "ev_solomon_judge_overturn_statement",
        "predicate": "StatementWouldHaveJudgeOverturnOrder",
        "phrase": "i'd just have the judge overturn anyway",
        "actor": "person:solomon",
        "target": "order:eppdapa_restraining_order",
        "text": "I'd just have the judge overturn anyway.",
    },
    {
        "event_id": "ev_solomon_entrapment_statement",
        "predicate": "StatementAccusedEntrapment",
        "phrase": "but we're talking about me, not her. so again, you trying to entrap me?",
        "actor": "person:solomon",
        "target": "person:benjamin_barber",
        "text": "But we're talking about me, not her. So again, you trying to entrap me?",
    },
]

NOTICE_PATTERNS = [
    {
        "event_id": "ev_hacc_notice_restrained_parties_question",
        "predicate": "MessageQuestionedHaccCommunicationWithRestrainedParties",
        "phrase": "are you still in communication with parties that have restraining orders against them in the courts?",
        "actor": "person:benjamin_barber",
        "target": "org:hacc",
        "text": "Are you still in communication with parties that have restraining orders against them in the courts?",
    },
    {
        "event_id": "ev_hacc_notice_brother_calls_after_granted_order",
        "predicate": "MessageReportedBrotherCallsAfterGrantedOrder",
        "phrase": "my mom is still getting phone calls this morning about my brother, against whom a restraining order has been filed and granted by the court",
        "actor": "person:benjamin_barber",
        "target": "org:hacc",
        "text": "My mom is still getting phone calls this morning about my brother, against whom a restraining order has been filed and granted by the court.",
    },
    {
        "event_id": "ev_hacc_notice_third_party_contact_with_restrained_person",
        "predicate": "MessageObjectedThirdPartyContactWithRestrainedPerson",
        "phrase": "making third party contact about her housing with a person against whom she has a restraining order issued in a court",
        "actor": "person:benjamin_barber",
        "target": "org:hacc",
        "text": "Making third party contact about her housing with a person against whom she has a restraining order issued in a court.",
    },
]


def discover_sources() -> Tuple[List[Path], List[Path], List[Path]]:
    emls = sorted(EML_ROOT.glob("*solomon*381-6911*.eml"))
    transcripts = sorted(GV_ROOT.glob("**/*-to-solomon-*/transcript.txt"))
    notices = [p for p in HACC_NOTICE_SOURCES if p.exists()]
    return emls, transcripts, notices


def _date_from_eml(text: str) -> str | None:
    m = re.search(r"^Date:\s*(.+)$", text, re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _date_from_transcript(text: str) -> str | None:
    m = re.search(r"\b([A-Z][a-z]{2} \d{1,2}, \d{4})\b", text)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%b %d, %Y").date().isoformat()
    except ValueError:
        return None


def parse_transcript_events(text: str, source: str) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    lowered = text.lower()
    d = _date_from_transcript(text)

    for spec in TRANSCRIPT_PATTERNS:
        if spec["phrase"] in lowered:
            events.append(
                {
                    "event_id": spec["event_id"],
                    "predicate": spec["predicate"],
                    "status": "verified",
                    "date": d,
                    "actor": spec["actor"],
                    "target": spec["target"],
                    "source": source,
                    "text": spec["phrase"],
                }
            )

    return events


def parse_eml_events(text: str, source: str) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    lowered = re.sub(r"\s+", " ", text.lower())
    d = _date_from_eml(text)

    for spec in EML_PATTERNS:
        if spec["phrase"] in lowered:
            events.append(
                {
                    "event_id": spec["event_id"],
                    "predicate": spec["predicate"],
                    "status": "verified",
                    "date": d,
                    "actor": spec["actor"],
                    "target": spec["target"],
                    "source": source,
                    "text": spec.get("text", spec["phrase"]),
                }
            )

    return events


def _date_from_json(text: str) -> str | None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    token = str(obj.get("date", "")).strip()
    return token[:10] if len(token) >= 10 else None


def parse_notice_events(text: str, source: str, suffix: str) -> List[Dict[str, object]]:
    lowered = re.sub(r"\s+", " ", text.lower())
    if suffix == ".json":
        d = _date_from_json(text)
    else:
        d = _date_from_eml(text)

    events: List[Dict[str, object]] = []
    for spec in NOTICE_PATTERNS:
        if spec["phrase"] in lowered:
            events.append(
                {
                    "event_id": spec["event_id"],
                    "predicate": spec["predicate"],
                    "status": "verified",
                    "date": d,
                    "actor": spec["actor"],
                    "target": spec["target"],
                    "source": source,
                    "text": spec["text"],
                }
            )

    return events


def dedupe_events(events: List[Dict[str, object]]) -> List[Dict[str, object]]:
    seen = set()
    out: List[Dict[str, object]] = []
    for ev in events:
        key = (ev.get("event_id"), ev.get("date"), ev.get("source"), ev.get("text"))
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    out.sort(key=lambda e: (str(e.get("date") or ""), str(e.get("event_id") or ""), str(e.get("source") or "")))
    return out


def enrich_confidence(events: List[Dict[str, object]]) -> List[Dict[str, object]]:
    enriched: List[Dict[str, object]] = []
    for ev in events:
        src = str(ev.get("source", "")).lower()
        confidence_level = "medium"
        confidence_score = 0.75
        evidence_kind = "derived_text"

        if src.endswith(".eml"):
            confidence_level = "high"
            confidence_score = 0.9
            evidence_kind = "direct_message"
        elif src.endswith("transcript.txt"):
            confidence_level = "medium_high"
            confidence_score = 0.8
            evidence_kind = "transcript_extract"
        elif src.endswith(".json"):
            confidence_level = "medium"
            confidence_score = 0.7
            evidence_kind = "json_export_extract"

        ev2 = dict(ev)
        ev2["confidence_level"] = confidence_level
        ev2["confidence_score"] = confidence_score
        ev2["evidence_kind"] = evidence_kind
        enriched.append(ev2)

    return enriched


def main() -> None:
    emls, transcripts, notices = discover_sources()

    events: List[Dict[str, object]] = []
    failed_sources: List[str] = []

    for p in transcripts:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            events.extend(parse_transcript_events(text, str(p)))
        except OSError:
            failed_sources.append(str(p))

    for p in emls:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            events.extend(parse_eml_events(text, str(p)))
        except OSError:
            failed_sources.append(str(p))

    for p in notices:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            events.extend(parse_notice_events(text, str(p), p.suffix.lower()))
        except OSError:
            failed_sources.append(str(p))

    deduped = dedupe_events(events)
    deduped = enrich_confidence(deduped)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "discovery": {
            "eml_scanned": len(emls),
            "transcripts_scanned": len(transcripts),
            "notice_sources_scanned": len(notices),
            "failed_sources": failed_sources,
        },
        "confidence_scheme": {
            "high": "direct message files (.eml)",
            "medium_high": "transcript extracts (transcript.txt)",
            "medium": "other extracted structured sources",
        },
        "events": deduped,
    }

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
