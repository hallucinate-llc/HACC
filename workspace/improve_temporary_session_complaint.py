#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

def _resolve_project_root() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parent / "complaint-generator",
        script_path.parents[1] / "complaint-generator",
        script_path.parents[1],
    ]
    for candidate in candidates:
        if (candidate / "applications").exists():
            return candidate
    raise RuntimeError(f"Could not locate complaint-generator project root from {script_path}")


PROJECT_ROOT = _resolve_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from applications.complaint_workspace import ComplaintWorkspaceService


DEFAULT_STATEFILE = Path("/home/barberb/HACC/complaint-generator/statefiles/temporary-cli-session-latest.json")
DEFAULT_WORKSPACE_ROOT = Path("/home/barberb/HACC/workspace")
MIGRATED_SOURCES_ROOTNAME = "migrated_sources"

PRIMARY_POLICY_PATHS = [
    Path("/home/barberb/HACC/hacc_website/knowledge_graph/texts/a38c7914-ea37-4c2f-a815-711d4a97c92b.txt"),
    Path("/home/barberb/HACC/hacc_website/knowledge_graph/texts/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt"),
]
PRIMARY_LEGAL_PATHS = [
    Path("/home/barberb/HACC/research_data/raw_documents/HUD_Fair_Housing_Act.html"),
    Path("/home/barberb/HACC/research_data/raw_documents/ORS_Chapter_659A_Discrimination_Definitions_and_Procedures.html"),
    Path("/home/barberb/HACC/research_data/raw_documents/ORS_Chapter_456_Housing_Authorities.html"),
]
SUPPORTING_PROGRAM_PATHS = [
    Path("/home/barberb/HACC/hacc_website/knowledge_graph/texts/945af141-c7d1-4973-88c0-b57024243114.txt"),
    Path("/home/barberb/HACC/hacc_website/knowledge_graph/texts/b53a0523-fa60-4df6-bba3-6ae34a47cb02.txt"),
]
SUPPORTING_MISC_PATHS = [
    Path("/home/barberb/HACC/hacc_research/engine.py"),
    Path("/home/barberb/HACC/hacc_website/knowledge_graph/summary.json"),
]


@dataclass
class CaseFacts:
    caption_plaintiffs: str
    signature_plaintiff: str
    mailing_address: str
    defendants_caption: str
    defendants_short: str
    court_header: str
    disability_facts: List[str]
    protected_activity: str
    adverse_action: str
    harm: str
    emergency_priority: str
    chronology_paragraphs: List[str]
    claims_summary: List[str]
    requested_relief: List[str]
    evidence_map: List[Dict[str, str]]
    unresolved_gaps: List[str]
    intake_answers: Dict[str, str]


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\u2014", "-").split())


def _normalize_lower(value: Any) -> str:
    return _normalize_text(value).lower()


def _sentence_case(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    return text[0].upper() + text[1:]


def _sanitize_phrase(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""

    replacements = {
        " via Email": " via email",
        "2br": "2BR",
        "$50000": "$50,000",
        "accomodation": "accommodation",
        "accomodations": "accommodations",
        "premesis": "premises",
        "effected": "affected",
        "injuctive": "injunctive",
        "hoemelessness": "homelessness",
        ", and lost opportunities": " and lost opportunities",
        ", and have caused": ", and caused",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"^yes,?\s*i do,?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^i (?:have|had|am)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmy mother\b", "Jane Kay Cortez", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmy sleep\b", "sleep", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthis has\b", "this has", text, flags=re.IGNORECASE)
    text = re.sub(r"stress levels,? and caused", "stress levels and caused", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" ,;.")
    return text


def _join_phrases(parts: Iterable[str]) -> str:
    cleaned: List[str] = []
    for part in parts:
        sanitized = _sanitize_phrase(part)
        if sanitized:
            cleaned.append(sanitized)
    return "; ".join(cleaned)


def _caption_name_list(caption: str) -> List[str]:
    normalized = _normalize_text(caption).replace(", and ", ", ")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _format_address(address: str) -> str:
    cleaned = _normalize_text(address)
    if not cleaned:
        return ""
    cleaned = re.sub(r"\bave\b", "Ave", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bmilwaukie\b", "Milwaukie", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\boregon\b", "OR", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bse\b", "SE", cleaned, flags=re.IGNORECASE)
    return cleaned


def _render_numbered_section(title: str, paragraphs: List[str], start: int) -> tuple[str, int]:
    lines = [title, ""]
    current = start
    for paragraph in paragraphs:
        lines.append(f"{current}. {paragraph}")
        current += 1
    lines.append("")
    return "\n".join(lines), current


def _load_migration_manifest(workspace_root: Path) -> Dict[str, Any]:
    manifest_path = workspace_root / "migration_manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _complaint_narrative_text(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    text = re.sub(r"\b[Pp]laintiff alleges\b", "Plaintiffs allege", text)
    text = re.sub(r"\b[Pp]laintiff\b", "Benjamin Barber", text)
    text = text.replace("Benjamin Barber was placed back on the lease", "Benjamin Jay Barber was placed back on the lease")
    text = text.replace("could sleep in the living room instead", "could sleep in the living room")
    return text


def _question_matches(question: str, contains_any: Iterable[str]) -> bool:
    lowered = _normalize_lower(question)
    return any(token.lower() in lowered for token in contains_any)


def _answered_inquiries(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for inquiry in list(state.get("inquiries") or []):
        answer = _normalize_text(inquiry.get("answer"))
        if not answer or answer.lower() == "none":
            continue
        rows.append(
            {
                "question": _normalize_text(inquiry.get("question")),
                "answer": answer,
            }
        )
    return rows


def _first_answer(inquiries: Iterable[Dict[str, str]], contains_any: Iterable[str], default: str = "") -> str:
    for inquiry in inquiries:
        if _question_matches(inquiry.get("question", ""), contains_any):
            answer = _normalize_text(inquiry.get("answer"))
            if answer:
                return answer
    return default


def _extract_primary_name(raw_identity: str) -> tuple[str, str]:
    cleaned = _normalize_text(raw_identity)
    address = ""
    lowered = cleaned.lower()
    for splitter in (", my address is ", " my address is "):
        if splitter in lowered:
            idx = lowered.index(splitter)
            name_part = cleaned[:idx]
            address = cleaned[idx + len(splitter):].strip(" ,")
            cleaned = name_part.strip(" ,")
            break
    cleaned = re.sub(r"^(i am|i'm)\s+", "", cleaned, flags=re.IGNORECASE).strip(" ,")
    return cleaned or "Benjamin Barber", address


def _extract_plaintiff_caption(inquiries: List[Dict[str, str]], fallback_name: str) -> tuple[str, str]:
    exact_names = _first_answer(
        inquiries,
        ["exact legal name you want on the complaint", "legal name you want on the complaint"],
    )
    if exact_names:
        parts = [item.strip() for item in exact_names.split(",") if item.strip()]
        if parts:
            if len(parts) == 1:
                return parts[0], parts[0]
            caption = ", ".join(parts[:-1]) + f", and {parts[-1]}"
            return caption, parts[0]
    return fallback_name, fallback_name


def _extract_defendants(inquiries: List[Dict[str, str]]) -> tuple[str, str]:
    parties_answer = _first_answer(inquiries, ["which parties do you want to name as defendants"])
    if parties_answer.lower() in {"both", "hacc and quantum", "hacc, quantum", "hacc and quantum residential"}:
        defendants = "Housing Authority of Clackamas County and Quantum Residential"
        return defendants, defendants

    raw = _first_answer(
        inquiries,
        ["who is named as the plaintiff, and who are the defendants"],
        "Housing Authority of Clackamas County and Quantum Residential",
    )
    lowered = raw.lower()
    if " vs " in lowered:
        raw = raw[lowered.index(" vs ") + 4:].strip()
    raw = re.sub(r"^both(?: plus specific staff)?$", "Housing Authority of Clackamas County and Quantum Residential", raw, flags=re.IGNORECASE)
    raw = raw.strip(" ,")
    if not raw:
        raw = "Housing Authority of Clackamas County and Quantum Residential"
    return raw, raw


def _extract_timeline_paragraphs(inquiries: List[Dict[str, str]]) -> List[str]:
    narrative = _first_answer(
        inquiries,
        ["chronological order", "timeline of events", "event or events started"],
    )
    if not narrative:
        return []

    priority_fragments = [
        "In October 2025, plaintiffs raised concerns about household abuse and requested lease bifurcation, and HACC said a restraining order was required before it would act.",
        "In November 2025, plaintiffs obtained a restraining order, and the order was later continued after a December 9, 2025 hearing.",
        "In December 2025, plaintiffs applied to Blossom Apartments, which was described as prioritized for displaced public-housing tenants, but the application was allegedly never processed.",
        "In January 2026, HACC removed Benjamin Barber from the lease and restored the restrained party to the lease.",
        "In February 2026, Benjamin Barber was placed back on the lease, requested a two-bedroom accommodation after being told he would receive only a one-bedroom voucher, and then received a February 4, 2026 eviction notice.",
        "Plaintiffs allege that HACC repeatedly demanded duplicative financial records and by March 2026 escalated those requests to as much as ten years of business records.",
        "Plaintiffs allege that they sought tenant protection voucher assistance before January 8, 2026, but the current documentary floor is HACC's January 8, 2026 notice stating that the process had not yet started, and written voucher communications do not appear until March 17 through March 20, 2026.",
        "Plaintiffs allege that the requested two-bedroom accommodation was denied in writing and that HACC redirected the household to an inadequate one-bedroom arrangement.",
    ]
    selected: List[str] = []
    lowered_narrative = narrative.lower()
    for fragment in priority_fragments:
        if any(token in lowered_narrative for token in fragment.lower().split()[:3]):
            selected.append(fragment)

    supplemental = _first_answer(inquiries, ["supplemental update regarding julio"])
    if supplemental:
        selected.append(
            "Plaintiffs also allege that Julio Regal Florez-Cortez was evicted instead of being bifurcated from the lease and was denied a hearing after an oral request because defendants insisted on a written request he could not make."
        )

    if not selected:
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", narrative) if item.strip()]
        selected = sentences[:8]
    return selected[:8]


def _extract_protected_activity(inquiries: List[Dict[str, str]]) -> str:
    communication = _first_answer(inquiries, ["if yes, when and how"], "on multiple occasions via email")
    return _sanitize_phrase(
        "complaining about race discrimination and housing steering, requesting reasonable accommodation "
        "for a two-bedroom voucher and caregiving needs, seeking domestic-violence-related safety and lease protections, "
        f"and communicating those complaints {communication}"
    )


def _extract_adverse_action(inquiries: List[Dict[str, str]]) -> str:
    return _sanitize_phrase(
        "removing Benjamin Barber from the lease while the restrained party was restored, failing to timely process the "
        "Blossom application and tenant protection voucher request, denying the requested two-bedroom accommodation, "
        "serving a February 4, 2026 eviction notice after protected complaints, and failing to provide Julio Regal Florez-Cortez "
        "a hearing after an oral request"
    )


def _extract_harm(inquiries: List[Dict[str, str]]) -> str:
    base = _first_answer(
        inquiries,
        ["what damages or harm have you suffered"],
        "financial losses and lost opportunities",
    )
    extra = _first_answer(
        inquiries,
        ["health, financial, or employment impacts"],
        "",
    )
    future = _first_answer(
        inquiries,
        ["what future damages are reasonably foreseeable"],
        "",
    )
    immediate = _first_answer(
        inquiries,
        ["what immediate harms would occur if evicted"],
        "",
    )
    parts = [base]
    if extra:
        parts.append(extra)
    if future:
        parts.append(f"foreseeable future housing and relocation losses of {future}")
    if immediate:
        parts.append(f"immediate risk of {immediate} if eviction proceeds")
    return _join_phrases(part.rstrip(".") for part in parts if part)


def _extract_disability_facts(inquiries: List[Dict[str, str]]) -> List[str]:
    details = _first_answer(
        inquiries,
        ["what are your documented disabilities and supporting medical findings"],
    )
    exact = _first_answer(
        inquiries,
        ["what are the exact disability-related facts you rely on"],
    )
    facts: List[str] = []
    if details:
        facts.append(
            "Plaintiffs allege disability-related housing needs affecting vision, neurodevelopmental functioning, cognition, memory, and mobility within the household."
        )
    if exact:
        facts.append(
            "Plaintiffs further allege physician-supported limitations affecting Jane Kay Cortez's ability to walk, comprehend decisions, and retain memories, increasing the need for stable and accessible housing conditions."
        )
    if _first_answer(inquiries, ["supplemental update regarding julio"]):
        facts.append(
            "Plaintiffs also allege that Julio Regal Florez-Cortez could not write in any language and therefore required an oral or otherwise assisted hearing-request process."
        )
    return facts


def _extract_emergency_priority(inquiries: List[Dict[str, str]]) -> str:
    priority = _first_answer(inquiries, ["what is your immediate priority today"])
    if priority:
        cleaned = _sanitize_phrase(priority)
        lowered = cleaned.lower()
        if "stop eviction" in lowered and "2br" in lowered:
            return "stop eviction, obtain a two-bedroom accommodation, and complete relocation from the current premises"
        cleaned = re.sub(r"\b2br accommodations\b", "a two-bedroom accommodation", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bmove out of this premises\b", "complete relocation from the current premises", cleaned, flags=re.IGNORECASE)
        if cleaned.lower().startswith("stop eviction and obtain"):
            cleaned = re.sub(r"^stop eviction and obtain", "stop eviction, obtain", cleaned, flags=re.IGNORECASE)
        return cleaned
    priority = _first_answer(inquiries, ["what is your immediate legal priorities right now"])
    if priority:
        return _sanitize_phrase(priority)
    return "stop eviction, secure a lawful two-bedroom accommodation, and complete relocation without housing loss"


def _extract_requested_relief() -> List[str]:
    return [
        "Temporary and preliminary injunctive relief preventing eviction, lockout, or loss of housing assistance while these claims are resolved.",
        "Declaratory relief that defendants' handling of the voucher, accommodation, grievance, hearing, and lease issues was unlawful.",
        "Injunctive relief requiring defendants to stop treating first-floor placement as a complete response to the accommodation request and to lawfully process and grant the remaining two-bedroom voucher accommodation if the verified disability-related criteria are met.",
        "Injunctive relief requiring meaningful hearing access and reasonable accommodation in any grievance or appeal process.",
        "Compensatory damages for housing instability, lost work time, emotional distress, and relocation-related losses.",
        "Costs, fees, and any further relief authorized by law.",
    ]


def _build_evidence_map() -> List[Dict[str, str]]:
    return [
        {
            "title": "Legacy temporary-session chronology",
            "kind": "testimony",
            "claim_element_id": "adverse_action",
            "content": "Statefile narrative describes October 2025 complaints, November 2025 restraining order, January 2026 lease removal, February 4, 2026 eviction notice, and March 20, 2026 voucher issuance.",
        },
        {
            "title": "HACC ACOP grievance and accommodation policies",
            "kind": "document",
            "claim_element_id": "causation",
            "content": "HACC policy text references reasonable accommodation, adverse-action notices, grievance procedures, remote hearings, and the right to request a hearing when lease termination is pursued.",
        },
        {
            "title": "HACC HCV Administrative Plan fair housing sections",
            "kind": "document",
            "claim_element_id": "causation",
            "content": "Administrative Plan includes fair housing and equal opportunity sections relevant to voucher administration and accommodation handling.",
        },
        {
            "title": "HUD Fair Housing Act overview",
            "kind": "document",
            "claim_element_id": "protected_activity",
            "content": "Federal fair housing source supporting discrimination, interference, and retaliation theories in housing.",
        },
        {
            "title": "ORS Chapter 659A real property discrimination provisions",
            "kind": "document",
            "claim_element_id": "harm",
            "content": "Oregon discrimination source includes disability discrimination and reasonable accommodation protections in real property transactions.",
        },
        {
            "title": "ORS Chapter 456 housing authority provisions",
            "kind": "document",
            "claim_element_id": "adverse_action",
            "content": "Oregon housing authority source includes anti-discrimination obligations and provisions governing housing authorities.",
        },
    ]


def _build_unresolved_gaps() -> List[str]:
    return [
        "Some exact dates for accommodation emails, staff-specific responses, and each notice still need to be tied to exhibit-level records.",
        "The statefile names several staff members but does not map each challenged act to a single individual with exact dates.",
        "The precise amount of wage loss and relocation damages still needs documentary support.",
        "The current documentary floor for the tenant protection voucher sequence is the January 8, 2026 notice stating the process had not yet started; any November or December 2025 request date still needs a direct email, notice, or declaration anchor.",
        "At least one co-plaintiff appears to have memory limitations, so declarations should be cross-checked against notices, emails, and agency records before filing.",
    ]


def _extract_case_facts(state: Dict[str, Any]) -> CaseFacts:
    inquiries = _answered_inquiries(state)
    raw_identity = _first_answer(inquiries, ["full legal name"], "Benjamin Barber")
    fallback_name, address = _extract_primary_name(raw_identity)
    caption_plaintiffs, signature_plaintiff = _extract_plaintiff_caption(inquiries, fallback_name)
    defendants_caption, defendants_short = _extract_defendants(inquiries)
    chronology = _extract_timeline_paragraphs(inquiries)
    disability_facts = _extract_disability_facts(inquiries)
    protected_activity = _extract_protected_activity(inquiries)
    adverse_action = _extract_adverse_action(inquiries)
    harm = _extract_harm(inquiries)
    emergency_priority = _extract_emergency_priority(inquiries)
    requested_relief = _extract_requested_relief()
    evidence_map = _build_evidence_map()
    unresolved_gaps = _build_unresolved_gaps()

    claims_summary = [
        "Fair housing discrimination based on disability and race in housing and voucher administration.",
        "Retaliation for complaints about discrimination, disability accommodation, and domestic-violence-related protections.",
        "Failure to fully accommodate caregiving, disability, privacy, and work-from-home needs in voucher sizing and housing placement, including the continued denial of a two-bedroom voucher after alleged recognition of the first-floor accessibility need.",
        "Denial of hearing or grievance access, including alleged refusal to honor an oral hearing request by Julio Regal Florez-Cortez.",
    ]
    immediate_priority = _first_answer(inquiries, ["what is your immediate priority today"])
    if immediate_priority:
        claims_summary.append(f"Immediate emergency objective described in the statefile: {_sanitize_phrase(immediate_priority).rstrip('.')}.")

    intake_answers = {
        "party_name": signature_plaintiff,
        "opposing_party": defendants_short,
        "protected_activity": _sentence_case(protected_activity),
        "adverse_action": _sentence_case(adverse_action),
        "timeline": " ".join(chronology),
        "harm": _sentence_case(harm),
        "court_header": "FOR THE DISTRICT OF OREGON",
    }

    return CaseFacts(
        caption_plaintiffs=caption_plaintiffs,
        signature_plaintiff=signature_plaintiff,
        mailing_address=_format_address(address),
        defendants_caption=defendants_caption,
        defendants_short=defendants_short,
        court_header="FOR THE DISTRICT OF OREGON",
        disability_facts=disability_facts,
        protected_activity=protected_activity,
        adverse_action=adverse_action,
        harm=harm,
        emergency_priority=emergency_priority,
        chronology_paragraphs=chronology,
        claims_summary=claims_summary,
        requested_relief=requested_relief,
        evidence_map=evidence_map,
        unresolved_gaps=unresolved_gaps,
        intake_answers=intake_answers,
    )


def _resolve_source_roots(workspace_root: Path) -> Dict[str, Path]:
    migrated_root = workspace_root / MIGRATED_SOURCES_ROOTNAME
    return {
        "hacc_research": migrated_root / "hacc_research" if (migrated_root / "hacc_research").exists() else Path("/home/barberb/HACC/hacc_research"),
        "hacc_website": migrated_root / "hacc_website" if (migrated_root / "hacc_website").exists() else Path("/home/barberb/HACC/hacc_website"),
        "legal_data": migrated_root / "legal_data" if (migrated_root / "legal_data").exists() else Path("/home/barberb/HACC/legal_data"),
        "research_data": migrated_root / "research_data" if (migrated_root / "research_data").exists() else Path("/home/barberb/HACC/research_data"),
        "research_results": migrated_root / "research_results" if (migrated_root / "research_results").exists() else Path("/home/barberb/HACC/research_results"),
    }


def _resolve_candidate(path: Path, roots: Dict[str, Path]) -> Path:
    raw = str(path)
    prefixes = {
        "/home/barberb/HACC/hacc_research": roots["hacc_research"],
        "/home/barberb/HACC/hacc_website": roots["hacc_website"],
        "/home/barberb/HACC/legal_data": roots["legal_data"],
        "/home/barberb/HACC/research_data": roots["research_data"],
        "/home/barberb/HACC/research_results": roots["research_results"],
    }
    for prefix, replacement in prefixes.items():
        if raw.startswith(prefix):
            return replacement / raw[len(prefix):].lstrip("/")
    return path


def _collect_research_results_paths(research_results_root: Path) -> List[Path]:
    ordered: List[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        lookup = str(path)
        if path.exists() and lookup not in seen:
            seen.add(lookup)
            ordered.append(path)

    for review_dir in sorted(research_results_root.glob("evidence_review_*"), reverse=True)[:5]:
        _add(review_dir / "evidence_review.md")
        _add(review_dir / "evidence_review.json")

    _add(research_results_root / "search_indexes" / "hacc_corpus.summary.json")
    _add(research_results_root / "search_indexes" / "hacc_enhanced_index_20260314_055513.summary.json")

    oregon_docs = research_results_root / "oregon_documents"
    if oregon_docs.exists():
        keywords = ("fair", "housing", "voucher", "accommodation", "discrimination", "659", "hacc", "quantum")
        matched: List[Path] = []
        for candidate in sorted(oregon_docs.glob("*")):
            if not candidate.is_file():
                continue
            lowered = candidate.name.lower()
            if any(token in lowered for token in keywords):
                matched.append(candidate)
            if len(matched) >= 8:
                break
        for candidate in matched:
            _add(candidate)

    return ordered


def _evidence_import_paths(workspace_root: Path) -> List[Path]:
    roots = _resolve_source_roots(workspace_root)
    ordered: List[Path] = []
    base_paths = PRIMARY_POLICY_PATHS + PRIMARY_LEGAL_PATHS + SUPPORTING_PROGRAM_PATHS + SUPPORTING_MISC_PATHS
    for path in base_paths:
        path = _resolve_candidate(path, roots)
        if path.exists() and path not in ordered:
            ordered.append(path)
    for extra in _collect_research_results_paths(roots["research_results"]):
        if extra not in ordered:
            ordered.append(extra)
    return ordered


def _render_custom_complaint(facts: CaseFacts) -> str:
    plaintiff_names = _caption_name_list(facts.caption_plaintiffs)
    address_block = facts.mailing_address or "Address on file in workspace"
    caption_block = [
        "IN THE UNITED STATES DISTRICT COURT",
        facts.court_header,
        "",
        f"{facts.caption_plaintiffs}, Plaintiffs,",
        "",
        "v.",
        "",
        f"{facts.defendants_caption}, Defendants.",
        "",
        "Civil Action No. ________________",
        "",
        "COMPLAINT FOR VIOLATION OF THE FAIR HOUSING ACT, SECTION 504 OF THE REHABILITATION ACT,",
        "TITLE II OF THE AMERICANS WITH DISABILITIES ACT, 42 U.S.C. section 1983,",
        "AND RELATED OREGON HOUSING LAW",
        "",
        "JURY TRIAL DEMANDED",
        "",
        "Plaintiffs allege as follows:",
        "",
    ]

    sections: List[str] = []
    paragraph_no = 1

    nature_section, paragraph_no = _render_numbered_section(
        "NATURE OF THE ACTION",
        [
            "This civil action arises from housing discrimination, refusal to accommodate disability-related housing needs, retaliation for protected complaints, interference with fair-housing rights, and denial of federally required hearing protections during the displacement of a public-housing household in Clackamas County, Oregon.",
            "Plaintiffs allege that defendants delayed or obstructed relocation, initially denied reasonable accommodation, later only partially recognized the need for first-floor placement, continued to deny the requested two-bedroom voucher accommodation, failed to process a represented housing opportunity, imposed retaliatory barriers after protected complaints, and denied a meaningful and accessible hearing process when housing rights were threatened.",
            f"Plaintiffs seek emergency and permanent relief sufficient to {facts.emergency_priority.rstrip('.')}, prevent unlawful eviction or displacement, require lawful housing and voucher administration, and compensate the household for the resulting harms.",
        ],
        paragraph_no,
    )
    sections.append(nature_section)

    jurisdiction_section, paragraph_no = _render_numbered_section(
        "JURISDICTION AND VENUE",
        [
            "This Court has federal-question jurisdiction under 28 U.S.C. section 1331 because this action arises under the Fair Housing Act, Section 504 of the Rehabilitation Act, Title II of the Americans with Disabilities Act, 42 U.S.C. section 1983, 42 U.S.C. section 1437d(k), and 24 C.F.R. section 982.555.",
            "This Court also has jurisdiction under 28 U.S.C. section 1343 because plaintiffs seek relief for deprivations of federal civil-rights protections under color of state law.",
            "This Court has supplemental jurisdiction over related Oregon-law claims under 28 U.S.C. section 1367 because those claims arise from the same nucleus of operative facts.",
            "Venue is proper in the District of Oregon under 28 U.S.C. section 1391 because the notices, voucher administration, accommodation requests, application failures, threatened eviction, and resulting harms occurred in Clackamas County, Oregon.",
        ],
        paragraph_no,
    )
    sections.append(jurisdiction_section)

    parties_paragraphs = [
        f"Plaintiffs are {facts.caption_plaintiffs}, members of the same displaced household whose housing stability, relocation, and continued occupancy were affected by the challenged conduct.",
        *facts.disability_facts,
        "Defendant Housing Authority of Clackamas County is a public housing authority that administered the relevant lease, displacement, voucher, accommodation, grievance, and hearing processes described in this complaint.",
        "Defendant Quantum Residential managed or controlled the Blossom Apartments application and placement process and is alleged to have participated in the denial, delay, or obstruction of housing access described below.",
    ]
    parties_section, paragraph_no = _render_numbered_section("PARTIES", parties_paragraphs, paragraph_no)
    sections.append(parties_section)

    chronology_facts = [_complaint_narrative_text(paragraph.rstrip(".") + ".") for paragraph in facts.chronology_paragraphs]
    factual_paragraphs = [
        f"Plaintiffs engaged in protected activity by {facts.protected_activity.rstrip('.')}.",
        f"Plaintiffs allege that defendants then took or maintained adverse actions by {facts.adverse_action.rstrip('.')}.",
        *chronology_facts,
        "Plaintiffs allege that defendants knew of restraining-order issues, disability-related housing needs, accommodation requests, service-animal concerns, and repeated written complaints before taking or continuing the challenged actions.",
        "Plaintiffs further allege that HACC conditioned Julio Regal Florez-Cortez's hearing access on a written request even though he could not write in any language and had orally requested a hearing.",
        "Plaintiffs allege that no meaningful interactive accommodation process occurred after the household requested a two-bedroom accommodation and explained the related caregiving, privacy, and disability-based needs, and that later recognition of first-floor placement did not resolve the separate bedroom-sizing component of the request.",
        "Plaintiffs further allege that HACC used repeated and excessive documentation demands to delay relocation, voucher issuance, or both after plaintiffs had already submitted substantial financial and household information.",
        f"As a direct and proximate result of defendants' conduct, plaintiffs allege harm including {facts.harm.rstrip('.')}.",
    ]
    factual_section, paragraph_no = _render_numbered_section("GENERAL ALLEGATIONS", factual_paragraphs, paragraph_no)
    sections.append(factual_section)

    authorities_section, paragraph_no = _render_numbered_section(
        "AUTHORITIES INCORPORATED INTO THIS PLEADING",
        [
            "The Fair Housing Act prohibits discrimination in the terms, conditions, privileges, services, or facilities connected to a dwelling because of disability and requires reasonable accommodations in rules, policies, practices, or services when necessary to afford equal opportunity to use and enjoy a dwelling. 42 U.S.C. section 3604(f)(2) and (3)(B).",
            "The Fair Housing Act also prohibits coercion, intimidation, threats, and interference with persons who exercise or aid fair-housing rights. 42 U.S.C. section 3617; 24 C.F.R. section 100.400.",
            "Section 504 of the Rehabilitation Act and Title II of the Americans with Disabilities Act prohibit disability discrimination by federally funded programs and public entities, including housing-authority programs and services. 29 U.S.C. section 794; 42 U.S.C. section 12132.",
            "Federal housing-program law requires notice and a meaningful opportunity for an informal hearing in covered participant disputes affecting housing benefits and related rights. 42 U.S.C. section 1437d(k); 24 C.F.R. section 982.555.",
            "Oregon law prohibits disability and source-of-income discrimination in housing and provides civil remedies, while Oregon notice law and HACC policy govern the termination and displacement process challenged here. ORS 659A.145; ORS 659A.421; ORS 659A.425; ORS 659A.885; ORS 90.427.",
            "The migrated research set also includes HACC policy materials and evidence-review outputs describing grievance procedures, accommodation duties, hearing access requirements, and the relocation and voucher framework at issue here.",
        ],
        paragraph_no,
    )
    sections.append(authorities_section)

    count_i, paragraph_no = _render_numbered_section(
        "COUNT I\nFAILURE TO PROVIDE REASONABLE ACCOMMODATION AND DISABILITY DISCRIMINATION\nAgainst HACC and Quantum under the Fair Housing Act, and against HACC only under Section 504 and Title II",
        [
            "Plaintiffs reallege the preceding paragraphs.",
            "Plaintiffs requested disability-related housing and program accommodations, including a two-bedroom, first-floor voucher arrangement for Jane Kay Cortez and an accessible hearing-request process for Julio Regal Florez-Cortez.",
            "Plaintiffs allege that HACC delayed or denied an effective accommodation process, initially rejected the request multiple times, later recognized the need for first-floor placement only in part, still reversed or reduced bedroom sizing, failed to provide an accessible method for Julio Regal Florez-Cortez to invoke hearing rights, and continued housing-administration decisions that did not afford equal access to the program.",
            "Plaintiffs further allege that Quantum participated in housing discrimination by failing to process or advance the Blossom housing opportunity and by participating in the refusal or delay of disability-related housing access, including service-animal and voucher-linked placement issues.",
            "These acts violated 42 U.S.C. section 3604(f)(2) and (3)(B), and as to HACC, also violated 29 U.S.C. section 794 and 42 U.S.C. section 12132.",
        ],
        paragraph_no,
    )
    sections.append(count_i)

    count_ii, paragraph_no = _render_numbered_section(
        "COUNT II\nFAIR HOUSING RETALIATION AND INTERFERENCE\nAgainst HACC and Quantum",
        [
            "Plaintiffs reallege the preceding paragraphs.",
            "Plaintiffs engaged in protected activity by complaining about race discrimination, disability discrimination, service-animal issues, accommodation denials, housing steering, and unlawful program administration.",
            "Defendants knew of those complaints and thereafter, according to plaintiffs, escalated adverse conduct by maintaining notices to vacate, delaying voucher issuance, demanding excessive documentation, failing to process the Blossom application, and burdening relocation out of HACC-controlled housing.",
            "Plaintiffs allege that this conduct was intended to coerce, intimidate, punish, or interfere with protected fair-housing activity.",
            "These acts violated 42 U.S.C. section 3617 and 24 C.F.R. section 100.400.",
        ],
        paragraph_no,
    )
    sections.append(count_ii)

    count_iii, paragraph_no = _render_numbered_section(
        "COUNT III\nPROCEDURAL DUE PROCESS AND FEDERAL HEARING VIOLATIONS\nAgainst HACC",
        [
            "Plaintiffs reallege the preceding paragraphs.",
            "HACC acted under color of state law when administering public-housing, displacement, voucher, grievance, and hearing processes.",
            "Plaintiffs had protected interests in continued housing benefits, lawful displacement procedures, and the notice and hearing protections attached to HACC-administered housing assistance.",
            "Plaintiffs allege that HACC issued or maintained adverse notices and housing-administration decisions without providing the clear, timely, meaningful, and accessible hearing process required by federal law, including after Julio Regal Florez-Cortez requested a hearing orally.",
            "Plaintiffs further allege that conditioning hearing access on a written request, without an oral or assisted alternative for a person who could not write in any language, denied meaningful access to the hearing process itself.",
            "These acts violated the Fourteenth Amendment, actionable under 42 U.S.C. section 1983, together with 42 U.S.C. section 1437d(k) and 24 C.F.R. section 982.555.",
        ],
        paragraph_no,
    )
    sections.append(count_iii)

    count_iv, paragraph_no = _render_numbered_section(
        "COUNT IV\nSUPPLEMENTAL OREGON HOUSING DISCRIMINATION CLAIMS\nAgainst HACC and Quantum",
        [
            "Plaintiffs reallege the preceding paragraphs.",
            "Plaintiffs allege that defendants discriminated in housing-related terms, services, processing, and access on the basis of disability and source of income by refusing or delaying accommodation, obstructing voucher-backed housing access, and imposing unreasonable or selectively administered intake barriers.",
            "Plaintiffs further allege that Quantum participated in the refusal to process a voucher-linked housing opportunity and in discrimination tied to accommodation or service-animal issues.",
            "These acts violated ORS 659A.145, ORS 659A.421, ORS 659A.425, and ORS 659A.885.",
        ],
        paragraph_no,
    )
    sections.append(count_iv)

    count_v, paragraph_no = _render_numbered_section(
        "COUNT V\nSUPPLEMENTAL OREGON NOTICE, LEASE, AND PROGRAM CLAIMS\nAgainst HACC",
        [
            "Plaintiffs reallege the preceding paragraphs.",
            "Plaintiffs allege that HACC issued or maintained termination and displacement notices while also controlling the relocation and voucher process needed to avoid unlawful housing loss.",
            "Plaintiffs further allege that HACC destabilized the household through unlawful lease-administration and household-composition handling despite requests for bifurcation, restraining-order-related protections, and relocation assistance, and effectively evicted Julio Regal Florez-Cortez instead of lawfully handling the requested bifurcation process.",
            "These acts violated ORS 90.427 and the applicable HACC lease and policy provisions incorporated into the tenancy and displacement process.",
        ],
        paragraph_no,
    )
    sections.append(count_v)

    relief_lines = [
        "PRAYER FOR RELIEF",
        "",
        "WHEREFORE, Plaintiffs request judgment against defendants as follows:",
    ]
    relief_lines.extend(f"{label}. {item}" for label, item in zip("ABCDEF", facts.requested_relief))
    relief_lines.extend(
        [
            "G. Pre-judgment and post-judgment interest as permitted by law.",
            "H. Such other and further relief as the Court deems just and proper.",
            "",
            "JURY DEMAND",
            "",
            "Plaintiffs demand a trial by jury on all issues so triable.",
            "",
            "SIGNATURE BLOCK",
            "",
            "Dated: ____________________",
            "",
            "Respectfully submitted,",
            "",
        ]
    )
    for name in plaintiff_names:
        relief_lines.extend([f"{name}, pro se", address_block, ""])

    return "\n".join(caption_block + sections + relief_lines).rstrip() + "\n"


def _build_quality_findings(custom_body: str, facts: CaseFacts, imported_paths: List[Path]) -> List[str]:
    findings: List[str] = []
    if "could sleep in the living room" in custom_body:
        findings.append("The complaint preserves the living-room alternative allegation, and Exhibit P supports that narrower point directly; keep that allegation tied to the text of the March 26, 2026 denial letter rather than treating it as a broader accommodation approval.")
    if (
        "later recognized" in custom_body
        or "first-floor placement was later recognized" in custom_body
        or "March 26, 2026 denial letter" in custom_body
        or "ground-floor unit within the affordability range" in custom_body
    ):
        findings.append("Exhibit P supports the narrower point that HACC allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit while still denying the requested two-bedroom increase; do not overstate that letter as approval of the full accommodation request.")
    if "county counsel" in custom_body:
        findings.append("The retaliation theory references county counsel based on intake narrative, but the reviewed preserved email set only shows metadata-level bwilliams@clackamas.us entries; confirm the underlying communication before filing.")
    if len(imported_paths) < 10:
        findings.append("The imported evidence set is thinner than expected; regenerate imports before relying on the complaint as a final filing draft.")
    if "January 8, 2026" in custom_body and "Tenant Protection Voucher process had not yet started" in custom_body:
        findings.append("The strongest current documentary anchor for TPV timing is Exhibit G on January 8, 2026; keep any earlier November or December request date tied to testimony or other direct records, not as an exhibit-proven date.")
    if facts.unresolved_gaps:
        findings.append("The pleading is now polished, but several allegations still need exhibit-level confirmation of dates, authors, or damages before filing.")
    return findings


def _render_generation_review(
    facts: CaseFacts,
    imported_paths: List[Path],
    quality_findings: List[str],
    review_overview: Dict[str, Any],
) -> str:
    lines = [
        "# Complaint Generation Review",
        "",
        "## Overall Assessment",
        "",
        "The generator now produces a substantially more filing-ready federal housing complaint from the temporary CLI session using the migrated workspace sources as primary support.",
        "",
        "## Improvements Applied",
        "",
        "- Uses the migrated `hacc_research`, `hacc_website`, `research_data`, and `research_results` sources from the workspace.",
        "- Preserves all named plaintiffs and both core defendants in the caption and signature block.",
        "- Converts the intake history into a cleaner chronology and count structure instead of pasting raw chat language.",
        "- Carries forward accommodation, retaliation, hearing-access, and Oregon supplemental claims in a coherent pleading format.",
        "- Writes the polished complaint to both markdown output and the workspace session draft.",
        "",
        "## Review Snapshot",
        "",
        f"- Supported claim elements: {review_overview.get('supported_elements', 0)}",
        f"- Testimony items: {review_overview.get('testimony_items', 0)}",
        f"- Document items: {review_overview.get('document_items', 0)}",
        f"- Imported source paths on this run: {len(imported_paths)}",
        "",
        "## Remaining Filing Risks",
        "",
    ]
    for item in facts.unresolved_gaps:
        lines.append(f"- {item}")
    if quality_findings:
        lines.extend(["", "## Quality Notes", ""])
        for item in quality_findings:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Immediate Recommendation",
            "",
            "Use this complaint as the polished base draft, then tie the key notice, voucher, accommodation, and hearing allegations to specific emails, notices, and declarations from the migrated evidence packet before filing.",
            "",
        ]
    )
    return "\n".join(lines)


def _recommended_exhibits(workspace_root: Path) -> List[Dict[str, str]]:
    base = workspace_root / "temporary-cli-session-migration" / "prior-research-results" / "full-evidence-review-run" / "chronology"
    packet = base / "formal_complaint_recommended_filing_packet"
    emergency = base / "emergency_motion_packet" / "exhibits"
    return [
        {
            "label": "Exhibit A",
            "title": "HACC add to lease",
            "path": str(packet / "included" / "01_Exhibit_A_HACC_add_to_lease.pdf"),
            "use": "Lease amendment or add/remove-tenant record for the household.",
        },
        {
            "label": "Exhibit B",
            "title": "HACC phase2 2024 notice",
            "path": str(packet / "included" / "02_Exhibit_B_HACC_phase2_2024.pdf"),
            "use": "General displacement and project notice.",
        },
        {
            "label": "Exhibit C",
            "title": "HACC 30-day notice without cause",
            "path": str(packet / "included" / "03_Exhibit_C_HACC_90_day_notice_2.pdf"),
            "use": "December 23, 2025 30-day lease termination notice without cause.",
        },
        {
            "label": "Exhibit D",
            "title": "HACC 90-day notice without cause",
            "path": str(packet / "included" / "04_Exhibit_D_HACC_90_day_notice.pdf"),
            "use": "December 23, 2025 90-day lease termination notice without cause.",
        },
        {
            "label": "Exhibit E",
            "title": "HACC notice of eligibility and 90-day displacement notice",
            "path": str(packet / "included" / "05_Exhibit_E_HACC_90_day_notice_3.pdf"),
            "use": "December 31, 2025 displacement notice.",
        },
        {
            "label": "Exhibit F",
            "title": "HACC VAWA-related lease amendment",
            "path": str(packet / "included" / "06_Exhibit_F_HACC_vawa_violation.pdf"),
            "use": "January 1, 2026 lease amendment tied to household composition.",
        },
        {
            "label": "Exhibit G",
            "title": "HACC January 2026 Blossom notice",
            "path": str(packet / "included" / "07_Exhibit_G_HACC_Jan_2026_blossom.pdf"),
            "use": "January 8, 2026 Blossom and TPV communication.",
        },
        {
            "label": "Exhibit H",
            "title": "HACC February 4, 2026 for-cause notice",
            "path": str(packet / "included" / "08_Exhibit_H_HACC_first_amendment.pdf"),
            "use": "February 4, 2026 30-day for-cause notice.",
        },
        {
            "label": "Exhibit I",
            "title": "HACC financial requests",
            "path": str(packet / "included" / "09_Exhibit_I_HACC_financial_requests.pdf"),
            "use": "February 9, 2026 additional-information demand.",
        },
        {
            "label": "Exhibit J",
            "title": "Additional information email thread export",
            "path": str(packet / "candidate_email_exhibits" / "10_Exhibit_J_Email_Thread_Export_starworks5_additional_info_import"),
            "use": "Escalating email documentation demands and complaints about Blossom processing, service-animal issues, and discrimination.",
        },
        {
            "label": "Exhibit K",
            "title": "HACC steering-related notice",
            "path": str(packet / "included" / "11_Exhibit_K_HACC_steering.pdf"),
            "use": "February 26, 2026 notice tied to ongoing occupancy and relocation handling.",
        },
        {
            "label": "Exhibit L",
            "title": "HACC inspection notice",
            "path": str(packet / "included" / "12_Exhibit_L_HACC_inspection.pdf"),
            "use": "March 17, 2026 NSPIRE inspection notice.",
        },
        {
            "label": "Exhibit M",
            "title": "HCV orientation email thread export",
            "path": str(packet / "candidate_email_exhibits" / "13_Exhibit_M_Email_Thread_Export_starworks5_ktilton_orientation_import"),
            "use": "Orientation, voucher issuance, bedroom-size reversal, and reasonable-accommodation emails.",
        },
        {
            "label": "Exhibit N",
            "title": "Julio eviction notice",
            "path": str(emergency / "Exhibit N - Julio Eviction notice.jpeg"),
            "use": "February 13, 2026 termination notice addressed directly to Julio Cortez.",
        },
        {
            "label": "Exhibit O",
            "title": "Reasonable accommodation packet",
            "path": str(packet / "included" / "14_Exhibit_O_Reasonable_accommodation.pdf"),
            "use": "March 24, 2026 provider letter and HACC verification form supporting disability status, service-animal need, and a two-bedroom first-floor accommodation request.",
        },
        {
            "label": "Exhibit P",
            "title": "HACC reasonable-accommodation denial letter",
            "path": str(packet / "included" / "15_Exhibit_P_HACC_RA_denial_03_26_2026.pdf"),
            "use": "March 26, 2026 denial of the two-bedroom increase while allowing use of the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range.",
        },
    ]


def _render_exhibit_cited_complaint(facts: CaseFacts) -> str:
    plaintiff_names = _caption_name_list(facts.caption_plaintiffs)
    address_block = facts.mailing_address or "Address on file in workspace"
    lines = [
        "IN THE UNITED STATES DISTRICT COURT",
        facts.court_header,
        "",
        f"{facts.caption_plaintiffs}, Plaintiffs,",
        "",
        "v.",
        "",
        f"{facts.defendants_caption}, Defendants.",
        "",
        "Civil Action No. ________________",
        "",
        "COMPLAINT FOR VIOLATION OF THE FAIR HOUSING ACT, SECTION 504 OF THE REHABILITATION ACT,",
        "TITLE II OF THE AMERICANS WITH DISABILITIES ACT, 42 U.S.C. section 1983,",
        "AND RELATED OREGON HOUSING LAW",
        "",
        "JURY TRIAL DEMANDED",
        "",
        "Plaintiffs allege as follows:",
        "",
        "NATURE OF THE ACTION",
        "",
        "1. This is a civil action arising from housing discrimination, refusal to accommodate disability-related housing needs, retaliation for protected complaints, interference with fair-housing rights, denial of federally required notice and hearing protections, and related Oregon housing-law violations.",
        "2. Plaintiffs seek emergency and permanent relief to prevent eviction and housing loss, require lawful voucher and accommodation processing, and recover damages caused by defendants' notice practices, application failures, documentation barriers, and retaliatory conduct.",
        "3. The dispute centers on HACC's public-housing, displacement, Tenant Protection Voucher, and Housing Choice Voucher administration; the handling of plaintiffs' relocation from HACC-controlled housing; and the failure to process or honor plaintiffs' transfer and accommodation requests connected to Blossom Apartments, a HACC-linked relocation destination managed by Quantum Residential.",
        "",
        "JURISDICTION AND VENUE",
        "",
        "4. This Court has federal-question jurisdiction under 28 U.S.C. section 1331 because Counts I through III arise under the Fair Housing Act, 42 U.S.C. sections 3601 through 3619, Section 504 of the Rehabilitation Act, 29 U.S.C. section 794, Title II of the Americans with Disabilities Act, 42 U.S.C. section 12132, 42 U.S.C. section 1983, 42 U.S.C. section 1437d(k), and 24 C.F.R. section 982.555.",
        "5. This Court also has jurisdiction under 28 U.S.C. section 1343 because plaintiffs seek redress for deprivations of federal civil-rights protections under color of state law.",
        "6. This Court has supplemental jurisdiction over Counts IV and V under 28 U.S.C. section 1367 because those claims arise from the same nucleus of operative facts.",
        "7. Venue is proper in this District under 28 U.S.C. section 1391 because the housing unit, the notices, the voucher administration, the application events, and the principal injuries all occurred in Clackamas County, Oregon.",
        "",
        "PARTIES",
        "",
        f"8. Plaintiffs are {facts.caption_plaintiffs}, members of the same displaced household whose housing stability, relocation process, and continued occupancy were affected by the challenged notices, lease-administration decisions, application failures, and voucher delays described below.",
        "9. Plaintiffs allege disability-related housing needs affecting vision, neurodevelopmental functioning, cognition, memory, and mobility within the household.",
        "10. Plaintiffs further allege physician-supported limitations affecting Jane Kay Cortez's ability to walk, comprehend decisions, and retain memories, increasing the need for stable and accessible housing conditions.",
        "11. Plaintiffs also allege that Julio Regal Florez-Cortez could not write in any language and therefore required an oral or otherwise assisted hearing-request process.",
        "12. Defendant Housing Authority of Clackamas County is a public housing authority and governmental housing provider operating public-housing, voucher, and relocation programs in Clackamas County, Oregon.",
        "13. Defendant Quantum Residential managed or controlled the Blossom Apartments intake, application, or placement process and participated in housing access decisions affecting displaced HACC households.",
        "",
        "GENERAL ALLEGATIONS",
        "",
        "14. On August 5, 2024, HACC generated a lease amendment or add/remove-tenant document for the household. Exhibit A.",
        "15. On September 19, 2024, HACC issued a general information notice concerning Hillside Park Apartments Phase II and the coming displacement sequence. Exhibit B.",
        "16. On December 23, 2025, HACC issued both a 30-day lease termination notice without cause and a 90-day lease termination notice without cause addressed to Jane Kay Cortez at the subject residence. Exhibits C and D.",
        "17. On December 31, 2025, HACC issued a notice of eligibility and 90-day notice to a residential tenant to be displaced. Exhibit E.",
        "18. Plaintiffs allege that, instead of lawfully bifurcating Julio Regal Florez-Cortez from the lease after bifurcation was requested, HACC removed or excluded him from the tenancy and effectively evicted him through the same notice and lease-administration sequence.",
        "19. On January 1, 2026, HACC generated another lease-amendment document tied to household composition and a VAWA-related sequence. Exhibit F.",
        "20. On January 8, 2026, HACC sent a Blossom-related notice stating in substance that if the letter was received, the Tenant Protection Voucher process had not yet started and that Ashley Ferron should be contacted to start that process. Exhibit G.",
        "21. Plaintiffs submitted Blossom-related paperwork in December 2025. According to the completed intake session, Quantum accepted the paper application in person and plaintiffs separately notified HACC about the application and service-animal issues that same day.",
        "22. Plaintiffs allege that Quantum failed to process or transmit the application to HACC and that neither HACC nor Quantum issued a timely approval, denial, or lawful written deficiency notice. Exhibit G; Exhibit J.",
        "23. On February 4, 2026, HACC issued a 30-day for-cause notice directed to Jane Kay Cortez and Benjamin Jay Barber. Exhibit H.",
        "24. On February 13, 2026, HACC issued a 30-Day Notice of Termination addressed directly to Julio Regal Florez-Cortez, effective March 19, 2026, stating that HACC was terminating his tenancy under the public housing lease. Exhibit N.",
        "25. Plaintiffs further allege that HACC told Julio Regal Florez-Cortez he could request a hearing in writing even though HACC knew or should have known that he was incapable of writing in any language, and that no hearing was provided after he requested one orally. Plaintiffs further allege that HACC policy materials allowed another written or oral request, making a written-only demand inconsistent with the transfer procedures identified in the workspace policy set.",
        "26. On February 9, 2026, HACC issued an additional-information demand requiring extensive income, tax, banking, and asset documentation. Exhibit I.",
        "27. The associated email thread shows repeated escalations of documentation demands even after plaintiffs had already supplied tax and financial materials. Exhibit J.",
        "28. In that thread, HACC requested proof of tax filings for multiple businesses, crypto-account statements, all bank statements for household members, and other asset categories, and demanded production by March 4, 2026. Exhibit J.",
        "29. Plaintiffs allege that those requests were excessive, duplicative, selectively imposed, and used to delay relocation, voucher issuance, or both. Exhibit I; Exhibit J.",
        "30. On February 26, 2026, HACC issued another written communication identified in the evidence review as a steering-related notice. Exhibit K.",
        "31. In emails preserved in Exhibit J, Benjamin Jay Barber wrote that Blossom had refused to process applications submitted for two months, refused to house a service animal, and engaged in race discrimination, while HACC and Quantum continued to delay the processes needed to leave HACC-controlled housing. Exhibit J.",
        "32. Plaintiffs allege that HACC knew of those complaints and continued the challenged documentation and relocation conduct afterward. Exhibit J; Exhibit K.",
        "33. Exhibit G identified Ashley Ferron as the contact to start the Tenant Protection Voucher process. Preserved complaint emails in Exhibit J show Ashley Ferron remained copied on plaintiffs' written complaints through March 10, 2026, and by March 17 through March 20, 2026 the orientation and voucher emails were being sent by Kati Tilton. Exhibit G; Exhibit J; Exhibit M. Plaintiffs further allege from the completed intake session that adverse treatment intensified after plaintiffs' protected complaints and threatened suit.",
        "34. Exhibit G shows that, as of January 8, 2026, HACC stated the Tenant Protection Voucher process had not yet started, and Exhibit M shows orientation and voucher communications on March 17 through March 20, 2026. Plaintiffs further allege from the completed intake session that they had sought voucher assistance earlier and repeatedly followed up before those March communications. Exhibit G; Exhibit M; intake responses.",
        "35. On March 17, 2026, HACC circulated an inspection notice referencing a HUD NSPIRE inspection. Exhibit L.",
        "36. On March 17 through March 20, 2026, HACC and Benjamin Jay Barber exchanged emails about HCV orientation, voucher issuance, and accommodation. Exhibit M.",
        "37. In those emails, HACC first sent a two-bedroom subsidy worksheet and voucher issuance, then stated on March 19, 2026 that the two-bedroom voucher had been created and sent in error and that a one-bedroom voucher would instead be issued. Exhibit M.",
        "38. Benjamin Jay Barber responded that he had a scheduled appointment to obtain a reasonable accommodation for a two-bedroom, first-floor unit and that the one-bedroom arrangement was not workable because Jane Kay Cortez could not climb stairs, Benjamin Barber served as her main caregiver, the two could not reasonably share a bedroom because of privacy concerns, and Jane needed ongoing assistance with ADLs and IADLs due to intellectual impairment, along with the household's other mobility, work-from-home, and service-animal needs. By March 24, 2026, plaintiffs further had provider verification stating that Jane Kay Cortez met the fair-housing disability definition, that her dog Sarah alleviated disability symptoms, and that the accommodation request was disability-related and necessary for equal housing access. Exhibit J; Exhibit M; Exhibit O; and the completed intake session.",
        "39. On March 20, 2026, Kati Tilton wrote that the voucher could be reissued as a two-bedroom if plaintiffs were approved for a reasonable accommodation. Exhibit M.",
        "40. Plaintiffs allege that HACC nevertheless delayed or denied the accommodation and redirected the household from the expected two-bedroom, first-floor arrangement to a one-bedroom configuration that did not meet the household's no-stairs, caregiving, privacy, ADL/IADL support, work-from-home, mobility, and service-animal needs, even after provider verification was completed in late March 2026. Exhibit J; Exhibit M; Exhibit O; Exhibit P. In Exhibit P, HACC denied the requested two-bedroom increase, stated that one household member could use the living room for sleep, but also stated that plaintiffs could use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range. Plaintiffs therefore allege that HACC at least partially recognized the no-stairs or ground-floor component while still refusing an effective two-bedroom accommodation.",
        "41. Plaintiffs further allege that defendants knew of disability-related needs affecting bedroom count, accessibility, service-animal use, caregiver status, dignitary privacy, and Julio Regal Florez-Cortez's inability to submit a written hearing request, but still refused to process the housing transition in a timely and lawful manner.",
        "42. Plaintiffs allege that defendants' conduct caused concrete injury including imminent eviction risk, delayed relocation, loss of housing opportunity, loss of time and income, emotional distress, and continuing instability for the household. See also intake summary and damages responses preserved in the workspace statefile.",
        "",
        "AUTHORITIES INCORPORATED INTO THIS PLEADING",
        "",
        "43. The Fair Housing Act prohibits discrimination in the terms, conditions, privileges, services, or facilities connected to a dwelling because of disability and requires reasonable accommodations in rules, policies, practices, or services when necessary to afford equal opportunity to use and enjoy a dwelling. 42 U.S.C. section 3604(f)(2) and (3)(B).",
        "44. The Fair Housing Act also prohibits coercion, intimidation, threats, and interference with persons who exercise or aid fair-housing rights. 42 U.S.C. section 3617; 24 C.F.R. section 100.400.",
        "45. Section 504 of the Rehabilitation Act prohibits disability discrimination by programs or activities receiving federal financial assistance. 29 U.S.C. section 794.",
        "46. Title II of the Americans with Disabilities Act prohibits disability discrimination by public entities in services, programs, and activities. 42 U.S.C. section 12132.",
        "47. Federal housing-program law requires notice and an opportunity for an informal hearing in covered participant disputes. 42 U.S.C. section 1437d(k); 24 C.F.R. section 982.555.",
        "48. Oregon law independently prohibits disability discrimination and source-of-income discrimination in housing transactions and authorizes civil remedies. ORS 659A.145; ORS 659A.421; ORS 659A.425; ORS 659A.885.",
        "49. Oregon law and HACC policy also govern the notice and termination process implicated by the challenged displacement and lease actions. ORS 90.427; HACC ACOP 13-IV.D.",
        "",
        "COUNT I",
        "FAILURE TO PROVIDE REASONABLE ACCOMMODATION AND DISABILITY DISCRIMINATION",
        "Against HACC and Quantum under the Fair Housing Act, and against HACC only under Section 504 and Title II",
        "",
        "50. Plaintiffs reallege the preceding paragraphs.",
        "51. Plaintiffs requested a two-bedroom, first-floor accommodation and related housing relief because Jane Kay Cortez required mobility and cognitive accommodations, could not climb stairs, needed Benjamin Jay Barber as her live-in caregiver and remote worker, could not reasonably share a bedroom with him because of privacy concerns, and required ongoing assistance with ADLs and IADLs, while the household also needed room for a scooter and service animal. Exhibit J; Exhibit M; Exhibit O; intake responses. Exhibit P states that plaintiffs could use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range, which supports the narrower allegation that HACC recognized the ground-floor component while leaving the two-bedroom voucher increase as the remaining denied accommodation. The HACC policy materials imported into the workspace also state that a couple with one child will ordinarily be issued a two-bedroom voucher.",
        "52. Plaintiffs further allege that Julio Regal Florez-Cortez required an accessible means of requesting a hearing because he could not write in any language and therefore could not use a hearing-request procedure conditioned on written submission. Exhibit N; intake responses. Plaintiffs further rely on HACC policy materials stating that transfer requests may be accepted as another written or oral request.",
        "53. HACC acknowledged in writing that the voucher could be reissued as a two-bedroom if the accommodation were approved, but had already reversed a two-bedroom issuance and replaced it with a one-bedroom issuance it claimed had been sent in error. Exhibit M. Plaintiffs further rely on Exhibit O as evidence that, by March 24, 2026, a provider had completed disability verification and marked the accommodation request as related to disability and necessary for equal housing access, with handwritten request text describing a two-bedroom first-floor unit because Jane could not climb stairs and needed caregiver privacy and ADL/IADL support from Benjamin Barber. Plaintiffs further rely on Exhibit P, which denied the two-bedroom increase yet expressly allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range. Plaintiffs therefore allege that first-floor placement was partially recognized, but the requested two-bedroom voucher was still withheld.",
        "54. Plaintiffs allege that defendants failed to provide a prompt, interactive, and lawful accommodation process; initially denied the accommodation multiple times; only partially recognized the request by later allowing use of a one-bedroom voucher for a two-bedroom ground-floor unit rather than granting the requested two-bedroom increase; and still denied or delayed the remaining accommodation needed for Jane's stair, privacy, and caregiver-support needs. Exhibit G; Exhibit J; Exhibit M; Exhibit O; Exhibit P.",
        "55. Plaintiffs further allege that Quantum refused to process the Blossom application and refused to accommodate the household's service animal, thereby participating in disability-based housing discrimination under the Fair Housing Act. Exhibit J.",
        "56. These acts violated 42 U.S.C. section 3604(f)(2) and (3)(B), and as to HACC also violated 29 U.S.C. section 794 and 42 U.S.C. section 12132.",
        "",
        "COUNT II",
        "FAIR HOUSING RETALIATION AND INTERFERENCE",
        "Against HACC and Quantum",
        "",
        "57. Plaintiffs reallege the preceding paragraphs.",
        "58. Plaintiffs engaged in protected activity by complaining to HACC and Quantum about race discrimination, disability discrimination, service-animal issues, unlawful housing administration, retaliation, and violations of fair-housing rights. Exhibit J. Plaintiffs further allege from the completed intake session that related complaints also reached county counsel. Intake responses.",
        "59. Defendants knew of those complaints.",
        "60. After those complaints, defendants escalated adverse conduct by issuing or maintaining notices to vacate, delaying voucher issuance, reversing a two-bedroom voucher, demanding excessive documentation, refusing to process the Blossom application, and blocking or burdening relocation out of HACC-controlled housing. Exhibits H, I, J, K, and M.",
        "61. Plaintiffs further allege, based on the completed intake session, that HACC personnel explicitly stated that Benjamin Jay Barber's threatened lawsuits were a reason for giving a 30-day notice to vacate, and that notice was later rescinded after county counsel was informed that the action was unlawful. Intake responses.",
        "62. These acts violated 42 U.S.C. section 3617 and 24 C.F.R. section 100.400.",
        "",
        "COUNT III",
        "PROCEDURAL DUE PROCESS AND FEDERAL HEARING VIOLATIONS",
        "Against HACC",
        "",
        "63. Plaintiffs reallege the preceding paragraphs.",
        "64. HACC acted under color of state law when administering public-housing, displacement, TPV, PBV, HCV, grievance, and hearing processes.",
        "65. Plaintiffs had protected interests in continued housing benefits, lawful displacement procedures, and the notice and hearing protections attached to HACC-administered housing assistance.",
        "66. HACC issued or maintained adverse notices and housing-administration decisions affecting plaintiffs' rights, obligations, welfare, or status without providing the clear, timely, and meaningful hearing process required by federal law, including the February 13, 2026 termination notice addressed to Julio Regal Florez-Cortez. Exhibits B, C, D, E, H, K, and N.",
        "67. Plaintiffs allege that HACC conditioned Julio Regal Florez-Cortez's access to a hearing on a written request even though he was incapable of writing in any language and had specifically requested a hearing orally. Exhibit N; intake responses. Plaintiffs further rely on HACC policy materials stating that transfer requests may be accepted as another written or oral request.",
        "68. Plaintiffs allege that no meaningful hearing or appeal was scheduled before the threatened loss of housing and that HACC failed to provide sufficient notice, document access, hearing access, accommodation in the hearing-request process, or a timely decision process.",
        "69. These acts violated the Fourteenth Amendment, actionable under 42 U.S.C. section 1983, together with 42 U.S.C. section 1437d(k) and 24 C.F.R. section 982.555.",
        "",
        "COUNT IV",
        "SUPPLEMENTAL OREGON HOUSING DISCRIMINATION CLAIMS",
        "Against HACC and Quantum",
        "",
        "70. Plaintiffs reallege the preceding paragraphs.",
        "71. Defendants discriminated in housing-related terms, services, processing, and access on the basis of disability and source of income by refusing or delaying accommodation, failing to process the Blossom application, obstructing voucher-backed housing access, and imposing unreasonable or selectively administered intake barriers. Exhibits G, I, J, and M.",
        "72. Plaintiffs further allege that Quantum participated in the refusal to process a voucher-linked application and in service-animal or accommodation-related discrimination at Blossom. Exhibit J.",
        "73. These acts violated ORS 659A.145, ORS 659A.421, ORS 659A.425, and ORS 659A.885.",
        "",
        "COUNT V",
        "SUPPLEMENTAL OREGON NOTICE, LEASE, AND PROGRAM CLAIMS",
        "Against HACC",
        "",
        "74. Plaintiffs reallege the preceding paragraphs.",
        "75. HACC issued or maintained termination and displacement notices while also controlling the relocation and voucher process needed to avoid unlawful housing loss. Exhibits A, C, D, E, F, H, and N.",
        "76. Plaintiffs further allege that HACC destabilized the household through unlawful lease-administration and household-composition handling despite prior requests for bifurcation, restraining-order-related protections, and relocation assistance, and that HACC effectively evicted Julio Regal Florez-Cortez instead of lawfully handling the requested bifurcation process.",
        "77. These acts violated ORS 90.427 and the applicable HACC lease and ACOP provisions incorporated into the tenancy and displacement process.",
        "",
        "PRAYER FOR RELIEF",
        "",
        "WHEREFORE, Plaintiffs request judgment against defendants as follows:",
        "A. Temporary, preliminary, and permanent injunctive relief preventing eviction, lockout, or loss of housing assistance while these claims are resolved.",
        "B. Declaratory relief that defendants' handling of the voucher, accommodation, grievance, hearing, application, and lease issues was unlawful.",
        "C. Injunctive relief requiring prompt processing of a two-bedroom accommodation, lawful voucher administration, and meaningful hearing access.",
        "D. Compensatory damages for housing instability, lost work time, emotional distress, and relocation-related losses.",
        "E. Punitive damages on the Fair Housing Act retaliation and interference claims to the extent permitted by law.",
        "F. Costs, fees, and any further relief authorized by law.",
        "G. Pre-judgment and post-judgment interest as permitted by law.",
        "H. Such other and further relief as the Court deems just and proper.",
        "",
        "JURY DEMAND",
        "",
        "Plaintiffs demand a trial by jury on all issues so triable.",
        "",
        "SIGNATURE BLOCK",
        "",
        "Dated: ____________________",
        "",
        "Respectfully submitted,",
        "",
    ]
    for name in plaintiff_names:
        lines.extend([f"{name}, pro se", address_block, ""])
    return "\n".join(lines).rstrip() + "\n"


def _render_exhibit_map(workspace_root: Path) -> str:
    exhibits = _recommended_exhibits(workspace_root)
    lines = [
        "# Workspace Exhibit Map",
        "",
        "This map identifies the exhibit set currently supporting the cited complaint generated from the temporary CLI session.",
        "",
    ]
    for exhibit in exhibits:
        lines.extend(
            [
                f"## {exhibit['label']}",
                "",
                f"- Title: {exhibit['title']}",
                f"- Path: {exhibit['path']}",
                f"- Use: {exhibit['use']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Core Citation Themes",
            "",
            "- Notice and displacement sequence: Exhibits B, C, D, E, H, K, and N.",
            "- Lease and household-composition handling: Exhibits A and F.",
            "- Blossom processing and transfer opportunity: Exhibit G and Exhibit J.",
            "- Documentation demands and retaliation sequence: Exhibits I and J.",
            "- Voucher issuance, bedroom size, and accommodation communications: Exhibits M and P.",
            "- Disability verification and requested two-bedroom first-floor accommodation: Exhibit O.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_paragraph_citation_table() -> str:
    rows = [
        ("14-20", "Lease/displacement chronology", "Exhibits A, B, C, D, E, F, G"),
        ("21-22", "Blossom application and non-processing", "Exhibits G, J"),
        ("23-25", "For-cause notice, Julio notice, inaccessible hearing issue", "Exhibits H, N; HACC oral-request policy; intake responses"),
        ("26-29", "Additional-information demands and escalation", "Exhibits I, J"),
        ("30-32", "Steering notice and complaint emails", "Exhibits J, K"),
        ("33-34", "TPV contacts, overlap, and timing", "Exhibits G, J, M; intake responses"),
        ("35-40", "Inspection, orientation, voucher reversal, accommodation exchange", "Exhibit L, Exhibit M, Exhibit P"),
        ("41-42", "Disability-related needs and household harms", "Exhibits J, M, O, P; HACC subsidy standards; intake responses"),
        ("51-56", "Accommodation and disability count", "Exhibits G, J, M, N, O, P; HACC subsidy standards and oral-request policy; intake responses"),
        ("58-62", "Retaliation and interference count", "Exhibits H, I, J, K, M; intake responses"),
        ("64-69", "Due-process and hearing count", "Exhibits B, C, D, E, H, K, N; HACC oral-request policy; intake responses"),
        ("71-77", "Oregon housing, notice, and lease counts", "Exhibits A, C, D, E, F, G, I, J, M, N"),
    ]
    lines = [
        "# Paragraph Citation Table",
        "",
        "| Paragraphs | Topic | Support |",
        "| --- | --- | --- |",
    ]
    for paragraph_range, topic, support in rows:
        lines.append(f"| {paragraph_range} | {topic} | {support} |")
    lines.extend(
        [
            "",
            "Intake-only references in this table identify allegations that still depend in part on the statefile narrative or later declarations rather than a standalone paper or email exhibit. Several points formerly treated as intake-only are now also supported by Exhibit J, including the written civil-rights complaints, the one-bedroom-sharing complaint, and the broader unsuitable-conditions theory. Policy references come from the imported HACC workspace materials describing oral-request procedures and subsidy standards.",
            "",
        ]
    )
    return "\n".join(lines)


def _save_structured_evidence(service: ComplaintWorkspaceService, user_id: str, facts: CaseFacts, statefile: Path) -> None:
    testimony_entries = [
        {
            "title": "Legacy chronology from temporary CLI session",
            "claim_element_id": "adverse_action",
            "content": " ".join(facts.chronology_paragraphs),
        },
        {
            "title": "Protected complaints and accommodation requests",
            "claim_element_id": "protected_activity",
            "content": facts.protected_activity,
        },
        {
            "title": "Housing harms and threatened eviction",
            "claim_element_id": "harm",
            "content": facts.harm,
        },
    ]
    for entry in testimony_entries:
        content = _normalize_text(entry["content"])
        if not content:
            continue
        service.save_evidence(
            user_id,
            kind="testimony",
            claim_element_id=entry["claim_element_id"],
            title=entry["title"],
            content=content[:7000],
            source=f"legacy_statefile:{statefile}",
        )

    for item in facts.evidence_map:
        if item["kind"] != "document":
            continue
        service.save_evidence(
            user_id,
            kind="document",
            claim_element_id=str(item.get("claim_element_id") or "causation"),
            title=item["title"],
            content=item["content"],
            source="workspace_custom_summary",
        )


def _render_reasonable_accommodation_ocr_memo() -> str:
    return """# Reasonable Accommodation OCR Memo

## Scope

This memo captures the usable typed text recovered from `temporary-cli-session-migration/paper-exhibits/Reasonable accomidation.pdf` after page-by-page OCR with system `tesseract-ocr` on March 31, 2026, together with the filer-provided manual reading of the handwritten accommodation fields. The scanned exhibit appears to contain a provider letter, a HACC verification form, and a Neighborhood Health Center after-visit summary. The typed portions are reliable enough to support disability verification and service-animal-related accommodation need. The handwritten accommodation fields are now usable at the level described below because the filer supplied a direct transcription from the exhibit.

## Typed OCR Findings

### EX-13 page 1: provider letter dated March 24, 2026

The first page OCR reads in substance:

- `Jane is a patient under my care.`
- The provider is familiar with Jane's medical history, disability-related functional limitations, impairment, and the impact on major life activities.
- `She meets the definition of disability under fair housing laws.`
- `Jane's dog, Sarah, alleviates the symptoms of her disability` and helps her self-regulate, promoting calmness.
- `This enhances her ability to live independently and enjoy full use of her dwelling.`

The page appears signed by `Samantha Jay Abbott, FNP` and dated `3/24/2026`.

### EX-13 page 2: HACC verification form

The second page OCR identifies a `Verification of Disability for Reasonable Accommodation Request` form. The typed instructions state that HACC must provide reasonable accommodations when necessary to afford equal opportunity to use and enjoy housing programs and services.

The clearest recoverable findings are:

- The form requests verification of need for reasonable accommodation.
- The provider completed the form.
- The provider marked that the requested accommodation is related to the applicant's disability.
- The provider marked that the accommodation is necessary to provide equal opportunity to participate in and use HACC housing programs, the unit, and common areas.
- The filer supplied the handwritten accommodation description as: `two bedroom apartment, first floor, cannot climb stairs, 1st floor unit`.
- The filer supplied the handwritten necessity explanation as: `Jane's son is her main caregiver and they cannot reasonably share a bedroom due to privacy concerns. Jane needs full time assistance from Benjamin due to her intellectual impairment she needs assistance with ADLS and iADLS`.

These handwritten fields align with the typed provider verification and materially sharpen the accommodation theory: the request sought both bedroom count and first-floor accessibility, and the stated necessity was tied to stair limitations, caregiver privacy, and full-time assistance with ADLs and IADLs.

### EX-13 pages 3 to 5: after-visit summary

The remaining pages appear to be a Neighborhood Health Center after-visit summary from March 24, 2026. OCR identifies conditions and visit topics including:

- `Housing instability`
- `Mild cognitive impairment`
- `Osteoporosis`
- `At risk for falls`
- `Abnormal walking`
- `Lower limb length difference`
- `Decreased exercise tolerance`

These pages help corroborate underlying functional limitations, but they are less direct than pages 1 and 2 for the housing-accommodation request itself.

## Evidentiary Use

EX-13 now supports the following points more directly than before:

1. Jane Kay Cortez had a provider-supported disability certification dated March 24, 2026.
2. A provider stated that Jane's dog, Sarah, alleviates disability symptoms and helps her live independently and enjoy full use of her dwelling.
3. A HACC reasonable-accommodation verification form was completed and marked yes for both disability relation and necessity.
4. The handwritten request sought a two-bedroom, first-floor unit because Jane could not climb stairs.
5. The handwritten necessity explanation tied the request to Benjamin Barber's caregiver role, privacy concerns, and Jane's need for full-time assistance with ADLs and IADLs due to intellectual impairment.
6. The exhibit supports that a formal accommodation-verification process was active in late March 2026.

EX-13 still does not reliably prove the following:

1. A final written approval or denial by HACC.
2. Whether any later exhibit in the packet contains a cleaner copy of the same handwritten accommodation text for easier authentication in motion practice or filing exhibits.

## Recommended Use In Drafting

Use EX-13 to support disability verification, service-animal-related accommodation need, the existence of a formal accommodation verification process, the request for a two-bedroom first-floor unit, and the stated necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance.

Do not use EX-13 alone to claim a final written denial unless the underlying scan is manually reviewed and confirmed.
"""


def _apply_ex13_summary_overrides(summary_payload: Dict[str, Any]) -> None:
    chronology = list(summary_payload.get("chronology_paragraphs") or [])
    if chronology:
        chronology[-1] = (
            "Plaintiffs allege that by March 24, 2026 the accommodation-verification process was active, with Exhibit O supporting disability status, service-animal-related need, and a two-bedroom first-floor accommodation request based on stair limits, caregiver privacy, and ADL/IADL assistance needs. Exhibit P then denied the requested two-bedroom increase but stated that plaintiffs could use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range, supporting the narrower allegation that HACC recognized the ground-floor component while still withholding the requested two-bedroom increase."
        )
        summary_payload["chronology_paragraphs"] = chronology

    intake_answers = dict(summary_payload.get("intake_answers") or {})
    intake_answers["protected_activity"] = (
        "Complaining about race discrimination, service-animal issues, Blossom non-processing, and housing obstruction in writing, while also requesting reasonable accommodation for a two-bedroom voucher and caregiving needs"
    )
    intake_answers["timeline"] = (
        "In October 2025, plaintiffs raised concerns about household abuse and requested lease bifurcation, and HACC said a restraining order was required before it would act. In November 2025, plaintiffs obtained a restraining order, and the order was later continued after a December 9, 2025 hearing. In December 2025, plaintiffs applied to Blossom Apartments, which was described as prioritized for displaced public-housing tenants, but the application was allegedly never processed. In January 2026, HACC removed Benjamin Barber from the lease and restored the restrained party to the lease. In February 2026, Benjamin Barber was placed back on the lease, requested a two-bedroom accommodation after being told he would receive only a one-bedroom voucher, and then received a February 4, 2026 eviction notice. Plaintiffs allege that HACC repeatedly demanded duplicative financial records and by March 2026 escalated those requests to as much as ten years of business records. Exhibit G shows that as of January 8, 2026 the tenant protection voucher process had not yet started, February 26 and March 9 emails complain about the continuing delay, and written voucher-sizing communications do not appear until March 17 through March 20, 2026; any earlier November or December 2025 request date remains testimony-dependent unless further records are located. On March 24, 2026, Exhibit O supported disability status, service-animal-related need, and a two-bedroom first-floor accommodation request based on Jane's inability to climb stairs and her need for caregiver support, privacy, and ADL/IADL assistance. On March 26, 2026, Exhibit P denied the requested two-bedroom increase but stated that plaintiffs could use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range. Plaintiffs therefore allege that the remaining denial was the two-bedroom voucher increase itself."
    )
    summary_payload["intake_answers"] = intake_answers


def _sync_workspace_generated_artifacts(workspace_root: Path) -> List[Path]:
    changed_paths: List[Path] = []
    generated_root = workspace_root / "temporary-cli-session-migration" / "workspace-generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    ocr_memo_path = generated_root / "reasonable_accommodation_ocr_memo.md"
    ocr_memo_text = _render_reasonable_accommodation_ocr_memo() + "\n"
    existing_ocr_text = ocr_memo_path.read_text(encoding="utf-8") if ocr_memo_path.exists() else None
    if existing_ocr_text != ocr_memo_text:
        ocr_memo_path.write_text(ocr_memo_text, encoding="utf-8")
        changed_paths.append(ocr_memo_path)

    email_memo_path = generated_root / "email_evidence_memo.md"
    related_non_email_section = (
        "\n## Related Non-Email Support\n\n"
        "The accommodation exhibit summarized in `temporary-cli-session-migration/workspace-generated/reasonable_accommodation_ocr_memo.md` now adds non-email support that was previously unavailable from OCR alone. In particular, EX-13 contains a March 24, 2026 provider letter and HACC verification form supporting disability status, service-animal-related need, and the necessity component of an accommodation request. The filer has also supplied the handwritten accommodation text as requesting a two-bedroom first-floor unit because Jane cannot climb stairs and needs Benjamin Barber, her main caregiver, to assist with ADLs and IADLs without having them reasonably share a bedroom. Separately, the March 26, 2026 HCV orientation denial letter now copied into the recommended filing packet as Exhibit P denies the requested two-bedroom increase but expressly states that plaintiffs may use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range.\n"
    )
    if email_memo_path.exists():
        email_text = email_memo_path.read_text(encoding="utf-8")
        if "## Related Non-Email Support" in email_text:
            email_text = re.sub(
                r"## Related Non-Email Support\n\n.*?(?=\n## |\Z)",
                related_non_email_section.strip("\n"),
                email_text,
                flags=re.DOTALL,
            )
            email_memo_path.write_text(email_text.rstrip() + "\n", encoding="utf-8")
            changed_paths.append(email_memo_path)
        else:
            email_memo_path.write_text(email_text.rstrip() + related_non_email_section, encoding="utf-8")
            changed_paths.append(email_memo_path)

    exhibit_index_path = generated_root / "exhibit_index.md"
    if exhibit_index_path.exists():
        exhibit_text = exhibit_index_path.read_text(encoding="utf-8")
        updated_text = exhibit_text.replace(
            "| EX-13 | `temporary-cli-session-migration/paper-exhibits/Reasonable accomidation.pdf` | Candidate reasonable-accommodation request or denial exhibit |",
            "| EX-13 | `temporary-cli-session-migration/paper-exhibits/Reasonable accomidation.pdf` | March 24, 2026 provider letter and HACC verification form supporting disability status, service-animal-related need, and a two-bedroom first-floor accommodation request tied to stair limits, caregiver privacy, and ADL/IADL assistance |",
        )
        updated_text = updated_text.replace(
            "| EX-13 | `temporary-cli-session-migration/paper-exhibits/Reasonable accomidation.pdf` | March 24, 2026 provider letter and HACC verification form supporting disability status, service-animal-related need, and accommodation necessity |",
            "| EX-13 | `temporary-cli-session-migration/paper-exhibits/Reasonable accomidation.pdf` | March 24, 2026 provider letter and HACC verification form supporting disability status, service-animal-related need, and a two-bedroom first-floor accommodation request tied to stair limits, caregiver privacy, and ADL/IADL assistance |",
        )
        if "| MEM-05 | `temporary-cli-session-migration/workspace-generated/reasonable_accommodation_ocr_memo.md` | OCR-based summary of typed portions of EX-13 |" not in updated_text:
            updated_text = updated_text.replace(
                "| MEM-04 | `temporary-cli-session-migration/workspace-generated/email_evidence_memo.md` | Workspace-local email evidence synthesis for Exhibit J and Exhibit M message-level support |",
                "| MEM-04 | `temporary-cli-session-migration/workspace-generated/email_evidence_memo.md` | Workspace-local email evidence synthesis for Exhibit J and Exhibit M message-level support |\n| MEM-05 | `temporary-cli-session-migration/workspace-generated/reasonable_accommodation_ocr_memo.md` | OCR-based summary of typed portions of EX-13 |",
            )
        updated_text = updated_text.replace(
            "| 38, 40, 51, 53, 54 | Two-bedroom accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04 | Partial | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 is still not readable enough to support a stronger formal-denial allegation without better OCR or manual review. |",
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance. The March 26, 2026 denial letter now separately carried in the filing packet as Exhibit P further shows that HACC denied the two-bedroom increase but allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit. |",
        )
        updated_text = updated_text.replace(
            "| 38, 40, 51, 53, 54 | Two-bedroom accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Partial to strong | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 now directly supports disability verification, service-animal need, and provider-certified necessity, but it still does not show a final written denial without further manual review. |",
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance. The March 26, 2026 denial letter now separately carried in the filing packet as Exhibit P further shows that HACC denied the two-bedroom increase but allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit. |",
        )
        updated_text = updated_text.replace(
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 now directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance, but it still does not show a final written denial. |",
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance. The March 26, 2026 denial letter now separately carried in the filing packet as Exhibit P further shows that HACC denied the two-bedroom increase but allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit. |",
        )
        updated_text = updated_text.replace(
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance, but it does not itself show either a final written denial or the later alleged recognition of first-floor placement, which presently remains intake-supported. |",
            "| 38, 40, 51, 53, 54 | Two-bedroom and first-floor accommodation request and ineffective interactive process | EX-16, EX-17, EX-13 | POL-02, POL-03, MEM-04, MEM-05 | Strong with limits | The March 19 to March 20 email chain strongly ties bedroom sizing to accommodation approval. EX-13 directly supports disability verification, service-animal need, a two-bedroom first-floor request, and provider-certified necessity tied to stair limits, caregiver privacy, and ADL/IADL assistance. The March 26, 2026 denial letter now separately carried in the filing packet as Exhibit P further shows that HACC denied the two-bedroom increase but allowed use of the one-bedroom voucher for a two-bedroom ground-floor unit. |",
        )
        updated_text = updated_text.replace(
            "1. OCR or manually review EX-13 to capture the exact accommodation approval or denial language and date.",
            "1. Determine whether EX-13 or a related packet contains any final written approval or denial language beyond the March 24, 2026 verification materials.",
        )
        updated_text = updated_text.replace(
            "1. Manually review EX-13 to capture the exact handwritten accommodation description and determine whether the scan contains any final approval or denial language beyond the typed verification pages.",
            "1. Determine whether EX-13 or a related packet contains any final written approval or denial language beyond the March 24, 2026 verification materials.",
        )
        if updated_text != exhibit_text:
            exhibit_index_path.write_text(updated_text, encoding="utf-8")
            changed_paths.append(exhibit_index_path)

    chronology_path = generated_root / "chronology_evidence_matrix.json"
    if chronology_path.exists():
        chronology_payload = json.loads(chronology_path.read_text(encoding="utf-8"))
        events = list(chronology_payload.get("events") or [])
        changed = False
        for event in events:
            if event.get("id") != "evt-006":
                continue
            event["date_or_period"] = "March 17 to March 24, 2026, with alleged earlier February 2026 request activity"
            event["event"] = "Plaintiff says a two-bedroom first-floor accommodation was actively pursued, a two-bedroom voucher was reversed to one bedroom, HACC conditioned reissuance on accommodation approval, and by March 24, 2026 provider verification supported disability status, service-animal need, stair-related accessibility limits, caregiver privacy, and the necessity of ADL/IADL assistance. The March 26, 2026 denial letter now carried in the filing packet as Exhibit P then denied the two-bedroom increase while stating that plaintiffs could use the one-bedroom voucher for a two-bedroom ground-floor unit within the affordability range, leaving the two-bedroom increase as the remaining denied accommodation."
            secondary_support = list(event.get("secondary_support") or [])
            memo_path = "temporary-cli-session-migration/workspace-generated/reasonable_accommodation_ocr_memo.md"
            if memo_path not in secondary_support:
                secondary_support.insert(1, memo_path)
            event["secondary_support"] = secondary_support
            event["evidentiary_status"] = "strong_with_limits"
            event["remaining_gaps"] = [
                "The March 19 and March 20 emails strongly show accommodation-linked bedroom sizing, but they do not by themselves prove the earliest request date.",
                "EX-13 now supports provider verification and necessity, but it still does not establish a final written approval or denial by HACC.",
                "Exhibit P supports the narrower point that HACC allowed use of the one-bedroom voucher for a ground-floor unit, but it should not be overstated as approval of the full two-bedroom accommodation request.",
                "If the handwritten EX-13 text will be excerpted verbatim in a filing exhibit, a cleaner scan or annotated page image would still help authentication and readability.",
            ]
            changed = True
            break
        if changed:
            chronology_path.write_text(json.dumps(chronology_payload, indent=2) + "\n", encoding="utf-8")
            changed_paths.append(chronology_path)

    return changed_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a stronger complaint draft from the legacy temporary session state.")
    parser.add_argument("--statefile", type=Path, default=DEFAULT_STATEFILE)
    parser.add_argument("--workspace-root", type=Path, default=DEFAULT_WORKSPACE_ROOT)
    parser.add_argument("--user-id", default="did:key:legacy-temporary-session")
    args = parser.parse_args()

    payload = json.loads(args.statefile.read_text(encoding="utf-8"))
    state = dict(payload.get("state") or {})
    facts = _extract_case_facts(state)
    service = ComplaintWorkspaceService(root_dir=args.workspace_root)

    service.reset_session(args.user_id)
    service.update_claim_type(args.user_id, "housing_discrimination")
    service.submit_intake_answers(args.user_id, facts.intake_answers)
    _save_structured_evidence(service, args.user_id, facts, args.statefile)

    imported_paths = _evidence_import_paths(args.workspace_root)
    for path in imported_paths:
        service.import_local_evidence(
            args.user_id,
            paths=[str(path)],
            claim_element_id="causation",
            kind="document",
        )

    draft_payload = service.generate_complaint(args.user_id, requested_relief=facts.requested_relief)
    custom_body = _render_exhibit_cited_complaint(facts)
    draft_title = f"{facts.caption_plaintiffs} v. {facts.defendants_caption} Housing Discrimination Complaint"
    service.update_draft(
        args.user_id,
        title=draft_title,
        body=custom_body,
        requested_relief=facts.requested_relief,
    )
    review_payload = service.call_mcp_tool("complaint.review_case", {"user_id": args.user_id})
    migration_manifest = _load_migration_manifest(args.workspace_root)

    out_dir = args.workspace_root
    out_dir.mkdir(parents=True, exist_ok=True)
    draft_path = out_dir / "improved-complaint-from-temporary-session.md"
    cited_draft_path = out_dir / "improved-complaint-from-temporary-session.cited.md"
    summary_path = out_dir / "improved-complaint-from-temporary-session.summary.json"
    review_path = out_dir / "improved-complaint-from-temporary-session.review.md"
    exhibit_map_path = out_dir / "improved-complaint-from-temporary-session.exhibit-map.md"
    citation_table_path = out_dir / "improved-complaint-from-temporary-session.citation-table.md"
    draft_path.write_text(custom_body + "\n", encoding="utf-8")
    cited_draft_path.write_text(_render_exhibit_cited_complaint(facts) + "\n", encoding="utf-8")
    review_overview = ((review_payload.get("review") or {}).get("overview") or {})
    quality_findings = _build_quality_findings(custom_body, facts, imported_paths)
    review_path.write_text(
        _render_generation_review(facts, imported_paths, quality_findings, review_overview) + "\n",
        encoding="utf-8",
    )
    exhibit_map_path.write_text(_render_exhibit_map(args.workspace_root) + "\n", encoding="utf-8")
    citation_table_path.write_text(_render_paragraph_citation_table() + "\n", encoding="utf-8")
    filing_metadata = {
        "caption_defendants": facts.defendants_caption,
        "caption_plaintiffs": facts.caption_plaintiffs,
        "mailing_address": facts.mailing_address,
        "signature_plaintiff": facts.signature_plaintiff,
        "signature_role": "Primary Filer / Proposed Plaintiff",
    }
    summary_payload = {
        "statefile": str(args.statefile),
        "workspace_root": str(args.workspace_root),
        "user_id": args.user_id,
        "draft_title": draft_title,
        "claim_type": "housing_discrimination",
        "caption_plaintiffs": facts.caption_plaintiffs,
        "defendants": facts.defendants_caption,
        "filing_metadata": filing_metadata,
        "intake_answers": facts.intake_answers,
        "chronology_paragraphs": facts.chronology_paragraphs,
        "claims_summary": facts.claims_summary,
        "disability_facts": facts.disability_facts,
        "emergency_priority": facts.emergency_priority,
        "requested_relief": facts.requested_relief,
        "unresolved_gaps": facts.unresolved_gaps,
        "quality_findings": quality_findings,
        "review_overview": review_overview,
        "generated_review_snapshot": ((draft_payload.get("review") or {}).get("overview") or {}),
        "imported_paths": [str(path) for path in imported_paths],
        "migration_manifest": migration_manifest,
        "output_markdown_path": str(draft_path),
        "cited_output_markdown_path": str(cited_draft_path),
        "review_markdown_path": str(review_path),
        "exhibit_map_markdown_path": str(exhibit_map_path),
        "citation_table_markdown_path": str(citation_table_path),
        "recommended_exhibits": _recommended_exhibits(args.workspace_root),
        "export_excerpt": custom_body[:1200],
    }
    _apply_ex13_summary_overrides(summary_payload)
    summary_path.write_text(json.dumps(summary_payload, indent=2, sort_keys=True), encoding="utf-8")

    synced_paths = _sync_workspace_generated_artifacts(args.workspace_root)

    print(str(draft_path))
    print(str(cited_draft_path))
    print(str(summary_path))
    print(str(review_path))
    print(str(exhibit_map_path))
    print(str(citation_table_path))
    for path in synced_paths:
        print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
