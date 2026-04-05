"""
GraphRAG-backed temporal deontic and frame-logic analysis for the Title 18 corpus.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

if __package__ in {None, ""}:
    workspace_root = Path(__file__).resolve().parent.parent
    workspace_root_str = str(workspace_root)
    if workspace_root_str not in sys.path:
        sys.path.insert(0, workspace_root_str)

from formal_logic.frame_logic import FrameKnowledgeBase
from formal_logic.title18_temporal_deontic_logic import DeonticModality


PARTY_SPECS: Dict[str, Dict[str, Any]] = {
    "person:benjamin_barber": {
        "name": "Benjamin Barber",
        "role": "Resident",
        "aliases": [r"\bbenjamin barber\b", r"\bbarber\b"],
    },
    "person:jane_cortez": {
        "name": "Jane Cortez",
        "role": "Resident",
        "aliases": [r"\bjane cortez\b", r"\bcortez\b"],
    },
    "org:hacc": {
        "name": "Housing Authority of Clackamas County",
        "role": "PHA",
        "aliases": [
            r"\bhousing authority of clackamas county\b",
            r"\bclackamas county housing authority\b",
            r"\bhacc\b",
        ],
    },
    "org:quantum": {
        "name": "Quantum Residential",
        "role": "Property Manager",
        "aliases": [
            r"\bquantum residential(?: property management)?\b",
            r"\bqresinc\b",
        ],
    },
    "org:hud": {
        "name": "Housing and Urban Development",
        "role": "Federal Agency",
        "aliases": [
            r"\bhousing and urban development\b",
            r"\bdepartment of housing and urban development\b",
            r"\bhud\b",
        ],
    },
}

DATE_PATTERNS = [
    ("%Y-%m-%d", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("%Y-%m", re.compile(r"\b\d{4}-\d{2}\b")),
    ("%m/%d/%Y", re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")),
    ("%m/%d/%y", re.compile(r"\b\d{1,2}/\d{1,2}/\d{2}\b")),
    ("%B %d, %Y", re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b", re.I)),
    ("%B %Y", re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", re.I)),
]


@dataclass(frozen=True)
class Party:
    party_id: str
    name: str
    role: str


@dataclass
class Mention:
    party_id: str
    entity_id: str
    document: str
    text: str
    confidence: float


@dataclass
class TemporalEvent:
    event_id: str
    label: str
    document: str
    event_type: str
    actors: List[str] = field(default_factory=list)
    related_parties: List[str] = field(default_factory=list)
    date: Optional[str] = None
    text: str = ""
    evidence_entities: List[str] = field(default_factory=list)


@dataclass
class ObligationRecord:
    obligation_id: str
    modality: str
    actor: str
    recipient: str
    action: str
    legal_basis: str
    trigger_summary: str
    event_ids: List[str]
    source_documents: List[str]
    evidence_entities: List[str]
    temporal_status: str
    trigger_date: Optional[str]
    due_date: Optional[str]
    breach_state: str
    formal_rule: str
    confidence: float


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _iter_texts(entity: Dict[str, Any]) -> Iterable[str]:
    yield entity.get("name", "")
    for key, value in sorted(entity.get("attributes", {}).items()):
        if isinstance(value, str):
            yield value


def _extract_datetimes(text: str) -> List[str]:
    matches: List[datetime] = []
    for fmt, pattern in DATE_PATTERNS:
        for raw in pattern.findall(text):
            try:
                matches.append(datetime.strptime(raw, fmt))
            except ValueError:
                continue
    deduped = sorted({item.strftime("%Y-%m-%d") for item in matches})
    return deduped


def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def _candidate_ipfs_dataset_paths() -> List[Path]:
    repo_root = Path(__file__).resolve().parents[2]
    return [
        repo_root / "complaint-generator" / "ipfs_datasets_py",
    ]


def _import_ipfs_datasets_py() -> Tuple[Optional[Any], Optional[str]]:
    try:
        import ipfs_datasets_py  # type: ignore
        return ipfs_datasets_py, getattr(ipfs_datasets_py, "__file__", None)
    except ImportError:
        pass

    for candidate in _candidate_ipfs_dataset_paths():
        if not candidate.exists():
            continue
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        try:
            import ipfs_datasets_py  # type: ignore
            return ipfs_datasets_py, candidate_str
        except ImportError:
            continue

    return None, None


def _guess_ipfs_dataset_loader() -> Optional[Any]:
    ipfs_datasets_py, _source = _import_ipfs_datasets_py()
    return ipfs_datasets_py


def _ipfs_datasets_source() -> Optional[str]:
    _module, source = _import_ipfs_datasets_py()
    return source


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def _action_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return token or "obligation"


ACTION_DEADLINE_DAYS: Dict[str, int] = {
    "provide relocation counseling before displacement": 90,
    "offer comparable replacement housing": 120,
    "pay or commit relocation moving expenses": 90,
    "accept, process, and transmit intake/application materials without obstruction": 5,
    "forward resident intake/application packets to HACC": 5,
    "coordinate relocation operations for replacement-housing placements": 120,
    "submit complete application and intake materials needed for placement processing": 30,
}


def _derive_due_date(action: str, events: Sequence[TemporalEvent]) -> Optional[str]:
    deadline_days = ACTION_DEADLINE_DAYS.get(action)
    if deadline_days is None:
        return None
    dated_events = sorted(filter(None, (_parse_date(event.date) for event in events)))
    if not dated_events:
        return None
    return dated_events[0].replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d") if deadline_days == 0 else (dated_events[0] + __import__("datetime").timedelta(days=deadline_days)).strftime("%Y-%m-%d")


def _derive_trigger_date(events: Sequence[TemporalEvent]) -> Optional[str]:
    dated_events = sorted(filter(None, (_parse_date(event.date) for event in events)))
    if not dated_events:
        return None
    return dated_events[0].strftime("%Y-%m-%d")


def _derive_breach_state(modality: DeonticModality, trigger_date: Optional[str], due_date: Optional[str], current_date: datetime, supporting_events: Sequence[TemporalEvent]) -> str:
    trigger_at = _parse_date(trigger_date)
    due_at = _parse_date(due_date)
    event_text = " ".join(f"{event.label} {event.text}" for event in supporting_events).lower()
    if modality == DeonticModality.PROHIBITED and _contains_any(event_text, ["evict", "termination", "adverse action"]):
        return "potential_breach"
    if due_at and current_date > due_at:
        return "overdue"
    if trigger_at and current_date >= trigger_at:
        return "active"
    if trigger_at and current_date < trigger_at:
        return "future"
    return "undated"


def _derive_temporal_status(trigger_date: Optional[str], due_date: Optional[str], current_date: datetime) -> str:
    trigger_at = _parse_date(trigger_date)
    due_at = _parse_date(due_date)
    if due_at and current_date > due_at:
        return "overdue"
    if trigger_at and current_date >= trigger_at:
        return "active"
    if trigger_at and current_date < trigger_at:
        return "future"
    return "undated"


def _build_formal_rule(record: ObligationRecord) -> str:
    modal_symbol = {
        "obligatory": "O",
        "permitted": "P",
        "prohibited": "F",
        "optional": "Opt",
    }.get(record.modality, record.modality.upper())
    action_token = _action_token(record.action)
    if record.trigger_date and record.due_date:
        time_part = f", [{record.trigger_date}, {record.due_date}]"
    elif record.trigger_date:
        time_part = f", from={record.trigger_date}"
    else:
        time_part = ""
    return f"{modal_symbol}({record.actor}, {action_token}, {record.recipient}{time_part})"


def _build_formal_models(
    obligations: Sequence[ObligationRecord],
    corpus: GraphRAGCorpus,
    current_date: datetime,
    frames: FrameKnowledgeBase,
) -> Dict[str, Any]:
    party_universe = [
        {
            "partyId": party_id,
            "name": spec["name"],
            "role": spec["role"],
        }
        for party_id, spec in sorted(PARTY_SPECS.items())
    ]
    event_predicates = []
    for event in corpus.events:
        when = event.date or "undated"
        event_predicates.append(
            {
                "eventId": event.event_id,
                "formula": f"Happens({event.event_id}, {when})",
                "document": event.document,
                "relatedParties": event.related_parties,
            }
        )

    obligation_formulas = []
    initiates = []
    holds_at = []
    breaches = []
    for record in obligations:
        obligation_token = _action_token(record.action)
        formula = record.formal_rule
        obligation_formulas.append(
            {
                "obligationId": record.obligation_id,
                "formula": formula,
                "legalBasis": record.legal_basis,
                "temporalStatus": record.temporal_status,
                "breachState": record.breach_state,
            }
        )
        active_fluent = f"ObligationState({record.actor}, {obligation_token}, {record.recipient}, {record.temporal_status})"
        for event_id in record.event_ids:
            initiates.append(
                {
                    "obligationId": record.obligation_id,
                    "formula": f"Initiates({event_id}, {active_fluent}, {record.trigger_date or 'undated'})",
                }
            )
        holds_formula = f"HoldsAt({active_fluent}, {current_date.strftime('%Y-%m-%d')})"
        holds_at.append(
            {
                "obligationId": record.obligation_id,
                "formula": holds_formula,
            }
        )
        if record.breach_state in {"overdue", "potential_breach"}:
            breaches.append(
                {
                    "obligationId": record.obligation_id,
                    "formula": f"HoldsAt(BreachState({record.actor}, {obligation_token}, {record.recipient}, {record.breach_state}), {current_date.strftime('%Y-%m-%d')})",
                }
            )

    first_order_predicates = []
    for record in obligations:
        first_order_predicates.extend(
            [
                f"Party({record.actor})",
                f"Party({record.recipient})",
                f"Action({_action_token(record.action)})",
                f"LegalBasis({record.obligation_id}, {json.dumps(record.legal_basis)})",
            ]
        )

    return {
        "deonticFirstOrderLogic": {
            "partyUniverse": party_universe,
            "predicates": sorted(set(first_order_predicates)),
            "eventPredicates": event_predicates,
            "obligationFormulas": obligation_formulas,
        },
        "deonticCognitiveEventCalculus": {
            "happens": [item["formula"] for item in event_predicates],
            "initiates": initiates,
            "holdsAt": holds_at,
            "breaches": breaches,
        },
        "frameLogic": frames.to_dict(),
    }


class GraphRAGCorpus:
    def __init__(self, corpus_root: Path) -> None:
        self.corpus_root = corpus_root
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.parties = {
            party_id: Party(party_id=party_id, name=spec["name"], role=spec["role"])
            for party_id, spec in PARTY_SPECS.items()
        }
        self.mentions: List[Mention] = []
        self.events: List[TemporalEvent] = []
        self._relationship_index: Dict[Tuple[str, str], List[str]] = {}

    @property
    def using_ipfs_datasets_py(self) -> bool:
        return _guess_ipfs_dataset_loader() is not None

    def scan(self) -> "GraphRAGCorpus":
        for path in sorted(self.corpus_root.rglob("document_knowledge_graph.json")):
            self._scan_document(path)
        self.events.sort(key=lambda item: (item.date or "9999-12-31", item.document, item.event_id))
        self.mentions.sort(key=lambda item: (item.party_id, item.document, item.entity_id))
        return self

    def _scan_document(self, path: Path) -> None:
        payload = json.loads(path.read_text())
        doc_key = str(path.relative_to(self.corpus_root.parent.parent.parent))
        entities = payload.get("entities", {})
        relationships = payload.get("relationships", {})
        self.documents[doc_key] = {
            "path": str(path),
            "entityCount": len(entities),
            "relationshipCount": len(relationships),
        }
        entity_parties: Dict[str, Set[str]] = {}

        for rel in relationships.values():
            rel_type = rel.get("relation_type", "")
            self._relationship_index.setdefault((doc_key, rel.get("source_id", "")), []).append(rel.get("target_id", ""))
            self._relationship_index.setdefault((doc_key, rel.get("target_id", "")), []).append(rel.get("source_id", ""))
            self._relationship_index.setdefault((doc_key, f"{rel.get('source_id', '')}:{rel_type}"), []).append(rel.get("target_id", ""))

        for entity_id, entity in entities.items():
            full_text = _normalize_text(" ".join(_iter_texts(entity)))
            parties = self._detect_parties(full_text)
            if parties:
                entity_parties[entity_id] = parties
                for party_id in sorted(parties):
                    self.mentions.append(
                        Mention(
                            party_id=party_id,
                            entity_id=entity_id,
                            document=doc_key,
                            text=full_text[:400],
                            confidence=float(entity.get("confidence", 0.0) or 0.0),
                        )
                    )

        for entity_id, entity in entities.items():
            event = self._build_event(doc_key, entity_id, entity, entities, entity_parties)
            if event is not None:
                self.events.append(event)

    def _detect_parties(self, text: str) -> Set[str]:
        matches: Set[str] = set()
        for party_id, spec in PARTY_SPECS.items():
            for alias in spec["aliases"]:
                if re.search(alias, text, re.I):
                    matches.add(party_id)
                    break
        return matches

    def _linked_entity_ids(self, doc_key: str, entity_id: str, relation_type: Optional[str] = None) -> List[str]:
        key = (doc_key, entity_id if relation_type is None else f"{entity_id}:{relation_type}")
        return self._relationship_index.get(key, [])

    def _build_event(
        self,
        doc_key: str,
        entity_id: str,
        entity: Dict[str, Any],
        entities: Dict[str, Dict[str, Any]],
        entity_parties: Dict[str, Set[str]],
    ) -> Optional[TemporalEvent]:
        entity_type = entity.get("type", "")
        attrs = entity.get("attributes", {})
        event_like = entity_type == "fact" or bool(attrs.get("event_label")) or "event" in entity.get("name", "").lower()
        if not event_like:
            return None

        full_text = _normalize_text(" ".join(_iter_texts(entity)))
        linked_parties: Set[str] = set(entity_parties.get(entity_id, set()))
        linked_entities = set(self._linked_entity_ids(doc_key, entity_id))
        linked_entities.update(self._linked_entity_ids(doc_key, entity_id, "involves"))
        linked_entities.update(self._linked_entity_ids(doc_key, entity_id, "associated_with"))
        linked_entities.update(self._linked_entity_ids(doc_key, entity_id, "communicated_with"))
        for linked_entity_id in linked_entities:
            linked_parties.update(entity_parties.get(linked_entity_id, set()))

        date_candidates = _extract_datetimes(full_text)
        for linked_date_id in self._linked_entity_ids(doc_key, entity_id, "occurred_on"):
            linked_entity = entities.get(linked_date_id, {})
            date_candidates.extend(_extract_datetimes(" ".join(_iter_texts(linked_entity))))

        date_value = sorted(set(date_candidates))[0] if date_candidates else None
        if not linked_parties and not date_value and not _contains_any(full_text, ["approval", "notice", "application", "evict", "relocat", "packet"]):
            return None

        parties = sorted(linked_parties)
        return TemporalEvent(
            event_id=f"{Path(doc_key).parent.name}:{entity_id}",
            label=attrs.get("event_label") or entity.get("name", entity_id),
            document=doc_key,
            event_type=attrs.get("predicate_family") or entity_type or "fact",
            actors=parties[:2],
            related_parties=parties,
            date=date_value,
            text=full_text[:600],
            evidence_entities=[entity_id],
        )


def _load_supplemental_case_context(base_dir: Path) -> Tuple[Dict[str, Dict[str, Any]], List[Mention], List[TemporalEvent]]:
    fixture_path = base_dir / "fixtures" / "joinder_quantum_case.json"
    if not fixture_path.exists():
        return {}, [], []

    payload = json.loads(fixture_path.read_text())
    actor_map = payload.get("actors", {})
    documents: Dict[str, Dict[str, Any]] = {}
    mentions: List[Mention] = []
    events: List[TemporalEvent] = []

    for evidence in payload.get("evidence", []):
        doc_key = f"fixtures/joinder_quantum_case.json#{evidence.get('id', 'evidence')}"
        text = _normalize_text(" ".join(str(evidence.get(key, "")) for key in ("label", "sourceText", "summary", "sourceFile")))
        documents[doc_key] = {
            "path": str(fixture_path),
            "entityCount": 1,
            "relationshipCount": 0,
        }
        for party_id in PARTY_SPECS:
            if party_id == "person:benjamin_barber" and re.search(r"benjamin barber|plaintiff household", text, re.I):
                mentions.append(Mention(party_id=party_id, entity_id=evidence.get("id", ""), document=doc_key, text=text[:400], confidence=0.95))
            elif party_id == "person:jane_cortez" and re.search(r"jane cortez|plaintiff household", text, re.I):
                mentions.append(Mention(party_id=party_id, entity_id=evidence.get("id", ""), document=doc_key, text=text[:400], confidence=0.95))
            elif any(re.search(alias, text, re.I) for alias in PARTY_SPECS[party_id]["aliases"]):
                mentions.append(Mention(party_id=party_id, entity_id=evidence.get("id", ""), document=doc_key, text=text[:400], confidence=0.95))

    for raw_event in payload.get("events", []):
        doc_key = f"fixtures/joinder_quantum_case.json#{raw_event.get('id', 'event')}"
        actor_ids = []
        for actor_id in raw_event.get("actors", []):
            actor_text = actor_map.get(actor_id, actor_id)
            detected = _detect_parties_from_text(actor_text)
            actor_ids.extend(sorted(detected))
        details_text = _normalize_text(json.dumps(raw_event.get("details", {}), sort_keys=True))
        event_text = _normalize_text(f"{raw_event.get('event', '')} {details_text}")
        actor_ids = sorted(set(actor_ids) | _detect_parties_from_text(event_text))
        documents[doc_key] = {
            "path": str(fixture_path),
            "entityCount": 1,
            "relationshipCount": 0,
        }
        events.append(
            TemporalEvent(
                event_id=raw_event.get("id", doc_key),
                label=raw_event.get("event", doc_key),
                document=doc_key,
                event_type="supplemental_case_event",
                actors=actor_ids[:2],
                related_parties=actor_ids,
                date=raw_event.get("time"),
                text=event_text[:600],
                evidence_entities=[raw_event.get("id", doc_key)],
            )
        )
    return documents, mentions, events


def _detect_parties_from_text(text: str) -> Set[str]:
    matches: Set[str] = set()
    for party_id, spec in PARTY_SPECS.items():
        for alias in spec["aliases"]:
            if re.search(alias, text, re.I):
                matches.add(party_id)
                break
    if "plaintiff household" in text.lower():
        matches.update({"person:benjamin_barber", "person:jane_cortez"})
    return matches


def _add_matrix_entry(matrix: Dict[str, Dict[str, List[Dict[str, Any]]]], actor: str, recipient: str, obligation: Dict[str, Any]) -> None:
    matrix.setdefault(actor, {}).setdefault(recipient, []).append(obligation)


def _status_for_date(date_value: Optional[str], current_date: datetime) -> str:
    if not date_value:
        return "undated"
    try:
        when = datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError:
        return "undated"
    return "triggered" if when <= current_date else "future"


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def analyze_title18_corpus(
    corpus_root: Path,
    current_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    current_date = current_date or datetime(2026, 4, 5)
    corpus = GraphRAGCorpus(corpus_root=corpus_root).scan()
    supplemental_documents, supplemental_mentions, supplemental_events = _load_supplemental_case_context(
        Path(__file__).resolve().parent.parent
    )
    corpus.documents.update(supplemental_documents)
    corpus.mentions.extend(supplemental_mentions)
    corpus.events.extend(supplemental_events)
    corpus.events.sort(key=lambda item: (item.date or "9999-12-31", item.document, item.event_id))
    corpus.mentions.sort(key=lambda item: (item.party_id, item.document, item.entity_id))
    mention_index: Dict[str, List[Mention]] = {}
    for mention in corpus.mentions:
        mention_index.setdefault(mention.party_id, []).append(mention)

    event_buckets: Dict[str, List[TemporalEvent]] = {
        "phase2": [],
        "intake": [],
        "replacement_housing": [],
        "application_steps": [],
        "eviction": [],
        "monitoring": [],
    }
    for event in corpus.events:
        text = f"{event.label} {event.text}".lower()
        if "phase ii" in text or ("hud" in text and "approval" in text):
            event_buckets["phase2"].append(event)
        if _contains_any(text, ["application", "intake", "packet", "waitlist", "pre-application"]):
            event_buckets["intake"].append(event)
        if _contains_any(text, ["replacement housing", "demolished original project", "first-occupancy preference", "relocat"]):
            event_buckets["replacement_housing"].append(event)
        if _contains_any(text, ["need to submit", "submit a complete pre-application", "application steps", "waitlist"]):
            event_buckets["application_steps"].append(event)
        if _contains_any(text, ["evict", "termination", "90 day notice", "adverse action"]):
            event_buckets["eviction"].append(event)
        if _contains_any(text, ["monitor", "oversight", "approval granted", "hud"]):
            event_buckets["monitoring"].append(event)

    obligations: List[ObligationRecord] = []
    frames = FrameKnowledgeBase()

    def add_obligation(
        obligation_id: str,
        modality: DeonticModality,
        actor: str,
        recipient: str,
        action: str,
        legal_basis: str,
        trigger_summary: str,
        events: Sequence[TemporalEvent],
    ) -> None:
        event_ids = sorted({event.event_id for event in events})
        source_documents = sorted({event.document for event in events})
        evidence_entities = sorted({entity_id for event in events for entity_id in event.evidence_entities})
        trigger_date = _derive_trigger_date(events)
        due_date = _derive_due_date(action, events)
        confidence_inputs = [
            mention.confidence
            for party_id in {actor, recipient}
            for mention in mention_index.get(party_id, [])
            if not source_documents or mention.document in source_documents
        ]
        record = ObligationRecord(
            obligation_id=obligation_id,
            modality=modality.name.lower(),
            actor=actor,
            recipient=recipient,
            action=action,
            legal_basis=legal_basis,
            trigger_summary=trigger_summary,
            event_ids=event_ids,
            source_documents=source_documents,
            evidence_entities=evidence_entities,
            temporal_status=_derive_temporal_status(trigger_date, due_date, current_date),
            trigger_date=trigger_date,
            due_date=due_date,
            breach_state=_derive_breach_state(modality, trigger_date, due_date, current_date, events),
            formal_rule="",
            confidence=_mean(confidence_inputs) or 0.7,
        )
        record.formal_rule = _build_formal_rule(record)
        obligations.append(record)
        actor_spec = PARTY_SPECS[actor]
        recipient_spec = PARTY_SPECS[recipient]
        frame_source = source_documents[0] if source_documents else "derived"
        frames.add_fact(actor, actor_spec["name"], "owes_to", recipient_spec["name"], frame_source)
        frames.add_fact(actor, actor_spec["name"], "has_outgoing_obligation", action, frame_source)
        frames.add_fact(recipient, recipient_spec["name"], "is_owed", action, frame_source)
        frames.add_fact(recipient, recipient_spec["name"], "is_owed_by", actor_spec["name"], frame_source)

    resident_ids = ["person:benjamin_barber", "person:jane_cortez"]
    phase2_events = event_buckets["phase2"] or event_buckets["replacement_housing"]
    intake_events = event_buckets["intake"]
    eviction_events = event_buckets["eviction"]
    monitoring_events = event_buckets["monitoring"] or phase2_events
    application_events = event_buckets["application_steps"] or intake_events

    for resident_id in resident_ids:
        add_obligation(
            f"obl:{resident_id}:hacc:relocation_counseling",
            DeonticModality.OBLIGATORY,
            "org:hacc",
            resident_id,
            "provide relocation counseling before displacement",
            "42 U.S.C. 1437p(d); Title 18 relocation framework",
            "Phase II approval and relocation evidence in the GraphRAG corpus trigger counseling duties.",
            phase2_events,
        )
        add_obligation(
            f"obl:{resident_id}:hacc:comparable_housing",
            DeonticModality.OBLIGATORY,
            "org:hacc",
            resident_id,
            "offer comparable replacement housing",
            "42 U.S.C. 1437p(d); replacement-housing findings in HACC administrative materials",
            "Replacement-housing and demolished-project references indicate a resident-specific relocation duty.",
            phase2_events + event_buckets["replacement_housing"],
        )
        add_obligation(
            f"obl:{resident_id}:hacc:moving_expenses",
            DeonticModality.OBLIGATORY,
            "org:hacc",
            resident_id,
            "pay or commit relocation moving expenses",
            "42 U.S.C. 1437p(d)",
            "Section 18 demolition relocation requires moving-expense coverage before displacement is completed.",
            phase2_events,
        )
        add_obligation(
            f"obl:{resident_id}:quantum:intake_processing",
            DeonticModality.OBLIGATORY,
            "org:quantum",
            resident_id,
            "accept, process, and transmit intake/application materials without obstruction",
            "RAD successor-management and PBV application workflow evidence",
            "The corpus ties Quantum to intake receipt, PBV processing, and failure-to-forward allegations.",
            intake_events,
        )
        add_obligation(
            f"obl:{resident_id}:hacc:no_premature_eviction",
            DeonticModality.PROHIBITED,
            "org:hacc",
            resident_id,
            "evict before relocation duties are completed",
            "42 U.S.C. 1437p(d) read against the recorded eviction and relocation timeline",
            "Eviction-related events appear in the same timeline as unresolved relocation activity.",
            phase2_events + eviction_events,
        )
        add_obligation(
            f"obl:{resident_id}:resident:submit_packet",
            DeonticModality.OBLIGATORY,
            resident_id,
            "org:quantum",
            "submit complete application and intake materials needed for placement processing",
            "Application-step requirements reflected in the GraphRAG intake corpus",
            "The application and waitlist materials describe a packet-submission duty for placement processing.",
            application_events,
        )

    add_obligation(
        "obl:quantum:hacc:forward_packet",
        DeonticModality.OBLIGATORY,
        "org:quantum",
        "org:hacc",
        "forward resident intake/application packets to HACC",
        "PBV intake workflow and HACC acknowledgement of non-transmission",
        "The corpus includes a direct HACC statement that Quantum received but did not transmit the packet.",
        intake_events,
    )
    add_obligation(
        "obl:quantum:hacc:coordinate_relocation",
        DeonticModality.OBLIGATORY,
        "org:quantum",
        "org:hacc",
        "coordinate relocation operations for replacement-housing placements",
        "Administrative-plan evidence naming Quantum as manager for replacement-housing developments",
        "Quantum appears as the property manager across the replacement-housing track used for Section 18 relocation.",
        intake_events + event_buckets["replacement_housing"],
    )
    for resident_id in resident_ids:
        add_obligation(
            f"obl:hud:{resident_id}:oversight",
            DeonticModality.OBLIGATORY,
            "org:hud",
            resident_id,
            "monitor and enforce Section 18 relocation compliance by HACC",
            "HUD approval and oversight function reflected in the approval timeline",
            "HUD appears in the approval chain that activates the Section 18 relocation regime affecting the household.",
            monitoring_events,
        )
    add_obligation(
        "obl:hud:hacc:oversight",
        DeonticModality.OBLIGATORY,
        "org:hud",
        "org:hacc",
        "monitor and enforce Section 18 relocation compliance",
        "HUD approval and federal oversight role",
        "The approval documents place HUD in an ongoing compliance-monitoring role after Phase II approval.",
        monitoring_events,
    )

    matrix: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for record in sorted(obligations, key=lambda item: (item.actor, item.recipient, item.action)):
        _add_matrix_entry(matrix, record.actor, record.recipient, asdict(record))

    formal_models = _build_formal_models(obligations, corpus, current_date, frames)

    return {
        "metadata": {
            "generatedAt": current_date.isoformat(),
            "corpusRoot": str(corpus_root),
            "documentsScanned": len(corpus.documents),
            "eventsExtracted": len(corpus.events),
            "mentionsExtracted": len(corpus.mentions),
            "usingIpfsDatasetsPy": corpus.using_ipfs_datasets_py,
            "ipfsDatasetsPySource": _ipfs_datasets_source(),
        },
        "parties": {
            party_id: {
                "name": spec["name"],
                "role": spec["role"],
                "mentions": len(mention_index.get(party_id, [])),
                "documents": sorted({mention.document for mention in mention_index.get(party_id, [])}),
            }
            for party_id, spec in PARTY_SPECS.items()
        },
        "documents": corpus.documents,
        "events": [asdict(event) for event in corpus.events],
        "obligations": [asdict(record) for record in sorted(obligations, key=lambda item: item.obligation_id)],
        "obligationMatrix": matrix,
        "frames": frames.to_dict(),
        "formalModels": formal_models,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Analyze the Title 18 GraphRAG corpus into a deontic obligation matrix.")
    parser.add_argument(
        "--corpus-root",
        default="/home/barberb/HACC/evidence/paper documents/graphrag",
        help="Path to the GraphRAG corpus root.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the JSON report into the Breach of Contract workspace.",
    )
    args = parser.parse_args(argv)

    report = analyze_title18_corpus(Path(args.corpus_root))
    output = json.dumps(report, indent=2, sort_keys=True)
    if args.write:
        target = Path(__file__).resolve().parent.parent / "outputs" / "title18_graphrag_obligations.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output + "\n")
        print(target)
        return 0

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
