"""
Evidence-backed breach-of-contract / relocation-agreement analysis for the joinder record.

This module now emits:
- narrative contract-breach findings
- F-logic knowledge-graph framing for the findings and support record
- DCEC-style formal event and obligation statements
- temporal deontic formulas shaped for the vendored ipfs_datasets_py logic stack
"""

from __future__ import annotations

import asyncio
import json
import os
from functools import lru_cache
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Sequence, Tuple


ROOT = Path("/home/barberb/HACC/Breach of Contract")
JOINDER_FIXTURE_PATH = ROOT / "fixtures" / "joinder_quantum_case.json"
OUTPUTS = ROOT / "outputs"


PARTY_LABELS = {
    "org:hacc": "Housing Authority of Clackamas County",
    "org:quantum": "Quantum Residential",
    "org:hud": "Housing and Urban Development",
    "org:hillside_manor_lp": "Hillside Manor Limited Partnership",
    "person:plaintiff_household": "Benjamin Barber / Jane Cortez household",
}

PARTY_AGENT_TYPES = {
    "org:hacc": "government",
    "org:quantum": "organization",
    "org:hud": "government",
    "org:hillside_manor_lp": "organization",
    "person:plaintiff_household": "person",
}

CONFIDENCE_SCORES = {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.5,
}

EXTRA_AUTHORITIES: List[Dict[str, Any]] = [
    {
        "id": "or_case_neiss_ehlers",
        "label": "Neiss v. Ehlers, 135 Or App 218 (1995)",
        "proposition": "In Oregon, promissory estoppel is a theory of recovery within a contract claim and may support relief where a promise induced reliance even though ordinary contract remedies are unavailable because the promise is indefinite or incomplete.",
        "sourceUrl": "https://law.justia.com/cases/oregon/court-of-appeals/1995/135-or-app-218.html",
    },
    {
        "id": "or_case_staley_taylor",
        "label": "Staley v. Taylor, 165 Or App 256 (2000)",
        "proposition": "An implied-in-fact contract has the same legal effect as an express contract; the difference is only that the parties' agreement is inferred in whole or in part from their conduct.",
        "sourceUrl": "https://law.justia.com/cases/oregon/court-of-appeals/2000/a101516.html",
    },
    {
        "id": "or_case_wiggins_barrett",
        "label": "Wiggins v. Barrett & Associates, 295 Or 679 (1983)",
        "proposition": "A public entity may be bound in a narrow contract setting if an apparent agent made a lawful promise, the entity clothed the agent with apparent authority, the other side lacked notice of a limitation, and the entity retained the bargained-for benefit.",
        "sourceUrl": "https://law.justia.com/cases/oregon/supreme-court/1983/295-or-679-0.html",
    },
    {
        "id": "or_case_onita_pacific",
        "label": "Onita Pacific Corp. v. Trustees of Bronson, 315 Or 149 (1992)",
        "proposition": "Oregon generally bars recovery for purely economic loss in negligence absent a special relationship or a negligent-information setting that makes reliance foreseeable and justifiable.",
        "sourceUrl": "https://law.justia.com/cases/oregon/supreme-court/1992/315-or-149.html",
    },
    {
        "id": "or_case_brennen_city_of_eugene",
        "label": "Brennen v. City of Eugene, 285 Or 401 (1979)",
        "proposition": "When a public body undertakes a specific licensing or processing function, ordinary negligence principles can apply to the operational act, but the claim must still fit within Oregon tort-law limits and immunity doctrines.",
        "sourceUrl": "https://law.justia.com/cases/oregon/supreme-court/1979/285-or-401-0.html",
    },
    {
        "id": "or_case_john_city_of_gresham",
        "label": "John v. City of Gresham, 214 Or App 305 (2007)",
        "proposition": "Under the Oregon Tort Claims Act, a public body is generally subject to tort suit, but discretionary-function immunity protects claims that challenge delegated policy judgment rather than routine implementation.",
        "sourceUrl": "https://law.justia.com/cases/oregon/court-of-appeals/2007/a128278.html",
    },
    {
        "id": "ors_30_265_otca",
        "label": "ORS 30.265 — Oregon Tort Claims Act scope and discretionary immunity",
        "proposition": "Public bodies are generally liable for torts of officers, employees, and agents acting within the scope of duty, subject to statutory immunity for discretionary functions or duties.",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/ors030.html",
    },
    {
        "id": "ors_30_275_otca_notice",
        "label": "ORS 30.275 — Oregon Tort Claims Act notice of claim",
        "proposition": "A tort claim against an Oregon public body requires timely notice, so negligence theories against HACC need OTCA notice facts or an exception before they can be treated as fully mature claims.",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/ors030.html",
    },
]

TITLE18_CONTRACT_LINKS: Dict[str, Dict[str, Any]] = {
    "contract:hacc:relocation_commitment": {
        "incorporatedTitle18Terms": [
            "Relocation must be completed before displacement is finalized.",
            "Replacement housing must be comparable and usable to the displaced household.",
            "Relocation counseling and moving-expense support are part of the expected relocation performance.",
        ],
        "impliedTitle18PerformanceTerms": [
            "HACC could not treat relocation as complete while the household still lacked a completed replacement path.",
            "HACC's relocation performance had to track the Section 18 process it itself triggered and described to the household.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 and its implementing regulations supply the strongest performance standard for what the relocation commitment required HACC to do.",
    },
    "implied_contract:hacc:relocation_process": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "The implied relocation agreement is informed by Section 18's comparability, timing, and assistance requirements.",
            "Because HACC undertook a Section 18 relocation process, those statutory duties help define the content of the implied-in-fact agreement.",
        ],
        "statutoryDutySupportingContractTheory": "Title 18 does not automatically create the contract, but it strongly defines the performance HACC's implied relocation undertaking had to provide.",
    },
    "contract:quantum:intake_processing_commitment": {
        "incorporatedTitle18Terms": [
            "Replacement-housing intake and processing had to function in service of the Section 18 relocation path HACC had already triggered.",
        ],
        "impliedTitle18PerformanceTerms": [
            "Quantum's processing role had to be timely and functional enough to allow the Section 18 relocation path to move forward.",
            "Quantum could not obstruct the very intake chain used to implement the relocation duties owed to the displaced household.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 does not by itself prove Quantum had a final direct contract with the household, but it strongly supports the argument that Quantum's intake role was part of the relocation performance chain.",
    },
    "implied_contract:quantum:application_processing_path": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "The implied processing agreement arose inside a Section 18 relocation setting, so timely intake handling is naturally measured against that relocation context.",
            "Quantum's owner/agent review function had to operate consistently with the relocation path HACC directed the household into.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 helps explain why Quantum's intake conduct mattered contractually even before the written management agreements are produced.",
    },
    "promissory_estoppel:hacc:relocation_reliance": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "The promised relocation pathways were represented against a Section 18 backdrop that implied real, usable, timely alternatives to displacement.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 strengthens the reasonableness of reliance because HACC's relocation representations were not casual suggestions; they were made within a legal relocation program.",
    },
    "negligence:hacc:undertaken_relocation_administration": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "The narrower operational negligence theory is informed by Section 18 because HACC undertook to implement a regulated relocation process for this household.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 helps define the operational context and expected care, but the negligence claim still has to satisfy OTCA and tort-law limits.",
    },
    "negligence:quantum:intake_mishandling": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "Quantum's intake role mattered because it was one step in a relocation process already shaped by Section 18 duties.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 makes the intake mishandling more consequential, but the tort theory still depends on Oregon special-relationship and economic-loss rules.",
    },
    "contract:quantum:rad_successor_obligations": {
        "incorporatedTitle18Terms": [
            "If the RAD/HAP/management documents incorporate relocation protections, Section 18 duties become direct contract terms in the successor structure.",
        ],
        "impliedTitle18PerformanceTerms": [
            "The successor-side obligations are best understood as carrying forward the relocation protections triggered by the underlying disposition and conversion process.",
        ],
        "statutoryDutySupportingContractTheory": "This is where the Title 18-to-contract connection may become the most explicit once the operative RAD and management documents are produced.",
    },
    "contract:hacc_quantum:interparty_allocation": {
        "incorporatedTitle18Terms": [
            "Any management or owner-participation agreement allocating relocation implementation likely uses Section 18 duties as the underlying performance backdrop.",
        ],
        "impliedTitle18PerformanceTerms": [
            "The HACC-Quantum relationship only matters interparty because both sides were participating in the same relocation structure shaped by Section 18.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 is the performance standard that makes the HACC-Quantum allocation issue contractually important rather than merely administrative.",
    },
    "no_contract_breach:household:substantial_performance": {
        "incorporatedTitle18Terms": [],
        "impliedTitle18PerformanceTerms": [
            "The household's conduct should be evaluated against the relocation steps HACC actually directed under the Section 18 process, not against invented after-the-fact completion standards.",
        ],
        "statutoryDutySupportingContractTheory": "Section 18 helps show why the household's submission and cooperation efforts count as substantial performance in context.",
    },
}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _evidence_map(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in fixture.get("evidence", [])}


def _event_map(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in fixture.get("events", [])}


def _authority_map(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    merged = {item["id"]: item for item in fixture.get("authorities", [])}
    for item in EXTRA_AUTHORITIES:
        merged[item["id"]] = item
    return merged


def _summary_line(evidence: Dict[str, Any]) -> str:
    label = evidence.get("documentLabel") or evidence["id"]
    date = evidence.get("emailDate") or evidence.get("documentDate")
    text = evidence.get("sourceText", "")
    short = text if len(text) <= 220 else text[:217] + "..."
    if date:
        return f"{label} ({date}): {short}"
    return f"{label}: {short}"


def _event_line(event: Dict[str, Any]) -> str:
    date = event.get("time", "undated")
    details = json.dumps(event.get("details", {}), sort_keys=True)
    return f"{event['event']} ({date}): {details}"


def _authority_line(authority: Dict[str, Any]) -> str:
    proposition = authority.get("proposition", "")
    return f"{authority['label']}: {proposition}"


def _candidate_ipfs_datasets_roots() -> Tuple[Path, ...]:
    repo_root = ROOT.parent
    return (repo_root / "complaint-generator" / "ipfs_datasets_py",)


@lru_cache(maxsize=1)
def _load_ipfs_logic_components() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "package_available": False,
        "source": None,
        "errors": [],
        "FLogicClass": None,
        "FLogicFrame": None,
        "FLogicOntology": None,
        "DeonticFormula": None,
        "DeonticOperator": None,
        "LegalAgent": None,
        "TemporalCondition": None,
        "TemporalOperator": None,
        "LegalContext": None,
        "ProofExecutionEngine": None,
        "check_document_consistency_from_parameters": None,
    }

    package_error: Exception | None = None
    for candidate in _candidate_ipfs_datasets_roots():
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        try:
            import ipfs_datasets_py  # type: ignore

            info["package_available"] = True
            info["source"] = getattr(ipfs_datasets_py, "__file__", candidate_str)
            break
        except Exception as exc:  # pragma: no cover - best effort discovery
            package_error = exc

    if not info["package_available"]:
        if package_error is not None:
            info["errors"].append(f"ipfs_datasets_py import failed: {package_error}")
        return info

    try:
        from ipfs_datasets_py.logic.flogic import FLogicClass, FLogicFrame, FLogicOntology  # type: ignore

        info["FLogicClass"] = FLogicClass
        info["FLogicFrame"] = FLogicFrame
        info["FLogicOntology"] = FLogicOntology
    except Exception as exc:  # pragma: no cover - optional dependency path
        info["errors"].append(f"F-logic import failed: {exc}")

    try:
        from ipfs_datasets_py.logic.integration.converters.deontic_logic_core import (  # type: ignore
            DeonticFormula,
            DeonticOperator,
            LegalAgent,
            LegalContext,
            TemporalCondition,
            TemporalOperator,
        )

        info["DeonticFormula"] = DeonticFormula
        info["DeonticOperator"] = DeonticOperator
        info["LegalAgent"] = LegalAgent
        info["TemporalCondition"] = TemporalCondition
        info["TemporalOperator"] = TemporalOperator
        info["LegalContext"] = LegalContext
    except Exception as exc:  # pragma: no cover - optional dependency path
        info["errors"].append(f"Deontic core import failed: {exc}")

    try:
        from ipfs_datasets_py.logic.integration.reasoning.proof_execution_engine import (  # type: ignore
            ProofExecutionEngine,
        )

        info["ProofExecutionEngine"] = ProofExecutionEngine
    except Exception as exc:  # pragma: no cover - optional dependency path
        info["errors"].append(f"Proof engine import failed: {exc}")

    try:
        from ipfs_datasets_py.logic.integration.domain.temporal_deontic_api import (  # type: ignore
            check_document_consistency_from_parameters,
        )

        info["check_document_consistency_from_parameters"] = check_document_consistency_from_parameters
    except Exception as exc:  # pragma: no cover - optional dependency path
        info["errors"].append(f"Temporal consistency API import failed: {exc}")

    return info


def _logic_atom(value: str) -> str:
    atom = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    if not atom:
        atom = "item"
    if atom[0].isdigit():
        atom = f"n_{atom}"
    return atom


def _string_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _time_symbol(value: str) -> str:
    return f"t_{_logic_atom(value)}"


def _primary_counterparty(finding: Dict[str, Any]) -> str:
    counterparties = finding.get("counterparties", [])
    if counterparties:
        return str(counterparties[0])
    return "person:plaintiff_household"


def _finding_formula_stem(finding_id: str) -> str:
    parts = [_logic_atom(item) for item in finding_id.split(":")]
    if len(parts) >= 2:
        return "_".join(parts[-2:])
    return _logic_atom(finding_id)


def _frame_to_dict(frame: Any) -> Dict[str, Any]:
    return {
        "objectId": frame.object_id,
        "scalarMethods": dict(frame.scalar_methods),
        "setMethods": dict(frame.set_methods),
        "isa": frame.isa,
        "isaset": list(frame.isaset),
        "ergoString": frame.to_ergo_string(),
    }


def _class_to_dict(cls: Any) -> Dict[str, Any]:
    return {
        "classId": cls.class_id,
        "superclasses": list(cls.superclasses),
        "signatureMethods": dict(cls.signature_methods),
        "ergoString": cls.to_ergo_string(),
    }


def _build_frame_logic_model(report: Dict[str, Any], components: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    refs: Dict[str, Dict[str, Any]] = {}
    classes_data = [
        {
            "classId": "LegalEntity",
            "superclasses": [],
            "signatureMethods": {"label": "string", "kind": "string"},
        },
        {
            "classId": "Party",
            "superclasses": ["LegalEntity"],
            "signatureMethods": {"role": "string"},
        },
        {
            "classId": "ContractBreachFinding",
            "superclasses": ["LegalEntity"],
            "signatureMethods": {
                "actor": "Party",
                "disposition": "string",
                "confidence": "string",
                "theory": "string",
            },
        },
        {
            "classId": "EvidenceRecord",
            "superclasses": ["LegalEntity"],
            "signatureMethods": {"summary": "string"},
        },
        {
            "classId": "CaseEvent",
            "superclasses": ["LegalEntity"],
            "signatureMethods": {"summary": "string"},
        },
        {
            "classId": "AuthorityRecord",
            "superclasses": ["LegalEntity"],
            "signatureMethods": {"summary": "string"},
        },
    ]

    FLogicClass = components.get("FLogicClass")
    FLogicFrame = components.get("FLogicFrame")
    FLogicOntology = components.get("FLogicOntology")

    class_objects: List[Any] = []
    frame_objects: List[Any] = []

    if FLogicClass and FLogicFrame and FLogicOntology:
        for item in classes_data:
            class_objects.append(
                FLogicClass(
                    class_id=item["classId"],
                    superclasses=item["superclasses"],
                    signature_methods=item["signatureMethods"],
                )
            )

        for party_id, label in PARTY_LABELS.items():
            frame_objects.append(
                FLogicFrame(
                    object_id=_logic_atom(party_id),
                    scalar_methods={
                        "label": _string_literal(label),
                        "kind": _string_literal(PARTY_AGENT_TYPES.get(party_id, "organization")),
                        "role": _string_literal(party_id.split(":", 1)[0]),
                    },
                    isa="Party",
                )
            )

        evidence_seen = set()
        event_seen = set()
        authority_seen = set()

        for finding in report["findings"]:
            finding_object_id = _logic_atom(finding["findingId"])
            refs[finding["findingId"]] = {
                "frameObjectId": finding_object_id,
                "dcecFormulaIds": [],
                "temporalFormulaIds": [],
            }
            frame_objects.append(
                FLogicFrame(
                    object_id=finding_object_id,
                    scalar_methods={
                        "label": _string_literal(finding["findingId"]),
                        "actor": _logic_atom(finding["actor"]),
                        "disposition": _string_literal(finding["disposition"]),
                        "confidence": _string_literal(finding["confidence"]),
                        "theory": _string_literal(finding["theory"]),
                        "contract_basis": _string_literal(finding["contractBasis"]),
                    },
                    set_methods={
                        "counterparty": [_logic_atom(item) for item in finding["counterparties"]],
                        "evidence": [_logic_atom(item["id"]) for item in finding["supportingEvidence"]],
                        "event": [_logic_atom(item["id"]) for item in finding["supportingEvents"]],
                        "authority": [_logic_atom(item["id"]) for item in finding["supportingAuthorities"]],
                    },
                    isa="ContractBreachFinding",
                )
            )

            for item in finding["supportingEvidence"]:
                if item["id"] in evidence_seen:
                    continue
                evidence_seen.add(item["id"])
                frame_objects.append(
                    FLogicFrame(
                        object_id=_logic_atom(item["id"]),
                        scalar_methods={
                            "label": _string_literal(item["id"]),
                            "summary": _string_literal(item["summary"]),
                        },
                        isa="EvidenceRecord",
                    )
                )

            for item in finding["supportingEvents"]:
                if item["id"] in event_seen:
                    continue
                event_seen.add(item["id"])
                frame_objects.append(
                    FLogicFrame(
                        object_id=_logic_atom(item["id"]),
                        scalar_methods={
                            "label": _string_literal(item["id"]),
                            "summary": _string_literal(item["summary"]),
                        },
                        isa="CaseEvent",
                    )
                )

            for item in finding["supportingAuthorities"]:
                if item["id"] in authority_seen:
                    continue
                authority_seen.add(item["id"])
                frame_objects.append(
                    FLogicFrame(
                        object_id=_logic_atom(item["id"]),
                        scalar_methods={
                            "label": _string_literal(item["id"]),
                            "summary": _string_literal(item["summary"]),
                        },
                        isa="AuthorityRecord",
                    )
                )

        ontology = FLogicOntology(
            name="contract_breach_knowledge_graph",
            classes=class_objects,
            frames=frame_objects,
            rules=[],
        )
        return {
            "status": "success",
            "usedIpfsTypes": True,
            "ontologyName": ontology.name,
            "classCount": len(class_objects),
            "frameCount": len(frame_objects),
            "classes": [_class_to_dict(item) for item in class_objects],
            "frames": [_frame_to_dict(item) for item in frame_objects],
            "ergoProgram": ontology.to_ergo_program(),
        }, refs

    return {
        "status": "unavailable",
        "usedIpfsTypes": False,
        "reason": "ipfs_datasets_py F-logic types were not importable.",
        "classCount": len(classes_data),
        "frameCount": 0,
        "classes": classes_data,
        "frames": [],
        "ergoProgram": "",
    }, refs


def _build_dcec_model(report: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    refs: Dict[str, Dict[str, Any]] = {}
    formulas: List[Dict[str, Any]] = []
    current_time = "t_current_2026_04_05"

    for finding in report["findings"]:
        finding_id = finding["findingId"]
        stem = _finding_formula_stem(finding_id)
        actor = _logic_atom(finding["actor"])
        beneficiary = _logic_atom(_primary_counterparty(finding))
        trigger_event_id = finding["supportingEvents"][0]["id"] if finding["supportingEvents"] else finding_id
        trigger_time = _time_symbol(trigger_event_id)
        refs[finding_id] = {
            "frameObjectId": _logic_atom(finding_id),
            "dcecFormulaIds": [],
            "temporalFormulaIds": [],
        }
        entries = [
            ("trigger", f"Happens(Trigger_{stem}({actor}, {beneficiary}), {trigger_time})."),
            ("knowledge", f"Knows({actor}, Basis_{stem}({actor}, {beneficiary}), {trigger_time})."),
            (
                "initiation",
                f"Initiates(Trigger_{stem}({actor}, {beneficiary}), DutyActive({stem}({actor}, {beneficiary})), {trigger_time}).",
            ),
            (
                "ought",
                f"Ought({actor}, Perform_{stem}({actor}, {beneficiary}), {trigger_time}, {current_time}).",
            ),
        ]
        if finding["disposition"] != "no_current_breach_shown":
            entries.append(
                (
                    "holding",
                    f"HoldsAt(DutyActive({stem}({actor}, {beneficiary})), {current_time}).",
                )
            )
        if finding["disposition"] == "likely_breach":
            entries.append(
                (
                    "breach",
                    f"HoldsAt(Breach({stem}({actor}, {beneficiary})), {current_time}).",
                )
            )

        for suffix, formula in entries:
            formula_id = f"dcec:{finding_id}:{suffix}"
            refs[finding_id]["dcecFormulaIds"].append(formula_id)
            formulas.append(
                {
                    "formulaId": formula_id,
                    "findingId": finding_id,
                    "formula": formula,
                }
            )

    return {
        "status": "success",
        "syntax": "dcec-inspired",
        "timepointSymbols": [current_time] + sorted({_time_symbol(item["id"]) for finding in report["findings"] for item in finding["supportingEvents"]}),
        "formulaCount": len(formulas),
        "formulas": formulas,
    }, refs


def _build_temporal_formula_specs(finding: Dict[str, Any], components: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any], Any]]:
    DeonticFormula = components.get("DeonticFormula")
    DeonticOperator = components.get("DeonticOperator")
    LegalAgent = components.get("LegalAgent")
    TemporalCondition = components.get("TemporalCondition")
    TemporalOperator = components.get("TemporalOperator")
    LegalContext = components.get("LegalContext")

    if not all((DeonticFormula, DeonticOperator, LegalAgent, TemporalCondition, TemporalOperator, LegalContext)):
        return []

    finding_id = finding["findingId"]
    actor = finding["actor"]
    beneficiary = _primary_counterparty(finding)
    actor_agent = LegalAgent(_logic_atom(actor), PARTY_LABELS[actor], PARTY_AGENT_TYPES.get(actor, "organization"))
    beneficiary_agent = LegalAgent(
        _logic_atom(beneficiary),
        PARTY_LABELS.get(beneficiary, beneficiary),
        PARTY_AGENT_TYPES.get(beneficiary, "person"),
    )
    conditions = [f"EventObserved({_logic_atom(item['id'])})" for item in finding["supportingEvents"][:2]]
    context = LegalContext(
        jurisdiction="Federal",
        legal_domain="contract",
        applicable_law=finding["contractBasis"],
        precedents=[item["id"] for item in finding["supportingAuthorities"]],
        exceptions=list(finding["missingProof"]),
    )
    confidence = CONFIDENCE_SCORES.get(finding["confidence"], 0.6)

    def build_formula(
        formula_id: str,
        operator_name: str,
        proposition: str,
        temporal_condition: str,
        source_text: str,
    ) -> Tuple[str, Dict[str, Any], Any]:
        raw_formula = DeonticFormula(
            operator=getattr(DeonticOperator, operator_name),
            proposition=proposition,
            agent=actor_agent,
            beneficiary=beneficiary_agent,
            conditions=conditions,
            temporal_conditions=[
                TemporalCondition(
                    operator=getattr(TemporalOperator, temporal_condition),
                    condition="case_timeline",
                )
            ],
            legal_context=context,
            confidence=confidence,
            source_text=source_text,
        )
        payload = raw_formula.to_dict()
        payload["formulaId"] = formula_id
        payload["findingId"] = finding_id
        return formula_id, payload, raw_formula

    formulas: List[Tuple[str, Dict[str, Any], Any]] = []
    if finding_id == "contract:hacc:relocation_commitment":
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:complete_relocation",
                "OBLIGATION",
                f"CompleteRelocation({_logic_atom(actor)}, {_logic_atom(beneficiary)})",
                "EVENTUALLY",
                "HACC must complete relocation before eviction can lawfully proceed.",
            )
        )
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:eviction_prohibited_before_completion",
                "PROHIBITION",
                f"PursueEviction({_logic_atom(actor)}, {_logic_atom(beneficiary)})",
                "ALWAYS",
                "Eviction remains prohibited while relocation is incomplete.",
            )
        )
    elif finding_id == "contract:quantum:intake_processing_commitment":
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:forward_packet",
                "OBLIGATION",
                f"ForwardApplicationPacket({_logic_atom(actor)}, {_logic_atom('org:hacc')}, {_logic_atom('person:plaintiff_household')})",
                "EVENTUALLY",
                "Quantum must receive, review, and forward the household packet within the relocation intake chain.",
            )
        )
    elif finding_id == "contract:quantum:rad_successor_obligations":
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:facilitate_accessible_relocation",
                "OBLIGATION",
                f"FacilitateAccessibleRelocation({_logic_atom(actor)}, {_logic_atom(beneficiary)})",
                "EVENTUALLY",
                "The RAD successor or manager must facilitate an accessible replacement path.",
            )
        )
    elif finding_id == "contract:hacc_quantum:interparty_allocation":
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:relay_materials_to_hacc",
                "OBLIGATION",
                f"RelayApplicantMaterials({_logic_atom(actor)}, {_logic_atom('org:hacc')})",
                "EVENTUALLY",
                "Quantum must relay applicant materials to HACC under the interparty management structure.",
            )
        )
    else:
        formulas.append(
            build_formula(
                f"tdfol:{finding_id}:household_right_to_continue",
                "RIGHT",
                f"ContinueRelocationPath({_logic_atom(actor)}, {_logic_atom('org:hacc')}, {_logic_atom('org:quantum')})",
                "ALWAYS",
                "The household retains the right to continue the relocation path without being treated as the breaching party on the current record.",
            )
        )
    return formulas


def _attempt_temporal_proofs(raw_formulas: List[Tuple[str, Any]], components: Dict[str, Any]) -> Dict[str, Any]:
    ProofExecutionEngine = components.get("ProofExecutionEngine")
    if ProofExecutionEngine is None:
        return {
            "status": "unavailable",
            "reason": "ProofExecutionEngine was not importable from ipfs_datasets_py.",
            "availableProvers": {},
            "results": [],
        }

    os.environ.setdefault("IPFS_DATASETS_PY_AUTO_INSTALL_PROVERS", "0")
    try:
        engine = ProofExecutionEngine(timeout=5, enable_validation=False)
        available_provers = dict(getattr(engine, "available_provers", {}) or {})
        installed = [name for name, available in available_provers.items() if available]
        if not installed:
            return {
                "status": "unavailable",
                "reason": "No theorem prover binaries were detected by ProofExecutionEngine.",
                "availableProvers": available_provers,
                "results": [],
            }

        selected = installed[0]
        results = []
        for formula_id, raw_formula in raw_formulas[:3]:
            proof = engine.prove_deontic_formula(raw_formula, prover=selected)
            proof_result = proof.to_dict()
            proof_result["formulaId"] = formula_id
            results.append(proof_result)
        overall = "success" if all(item["status"] == "success" for item in results) else "partial"
        return {
            "status": overall,
            "attemptedProver": selected,
            "availableProvers": available_provers,
            "results": results,
        }
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        return {
            "status": "error",
            "reason": str(exc),
            "availableProvers": {},
            "results": [],
        }


def _build_consistency_document(report: Dict[str, Any]) -> str:
    lines = []
    for sentence in report["summary"]["strongestLikelyContractBreaches"]:
        lines.append(sentence)
    for finding in report["findings"]:
        if finding["disposition"] == "likely_breach":
            lines.append(f"{finding['actorLabel']} has a contract-related obligation: {finding['contractBasis']}")
            lines.append(finding["whyItMatters"])
    return "\n".join(lines)


def _attempt_temporal_consistency_check(report: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    checker = components.get("check_document_consistency_from_parameters")
    if checker is None:
        temporal_errors = [item for item in components.get("errors", []) if item.startswith("Temporal consistency API import failed:")]
        reason = temporal_errors[0] if temporal_errors else "Temporal consistency API was not importable."
        return {
            "status": "unavailable",
            "reason": reason,
        }

    document_text = _build_consistency_document(report)
    try:
        result = asyncio.run(
            checker(
                {
                    "document_text": document_text,
                    "document_id": report["meta"]["reportId"],
                    "jurisdiction": "Federal",
                    "legal_domain": "contract",
                    "temporal_context": "2026-04-05T00:00:00",
                },
                tool_version="1.0.0",
            )
        )
        return {
            "status": "success" if result.get("success") else "error",
            "documentText": document_text,
            "result": result,
        }
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        return {
            "status": "error",
            "reason": str(exc),
            "documentText": document_text,
        }


def _build_temporal_deontic_model(report: Dict[str, Any], components: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    refs: Dict[str, Dict[str, Any]] = {}
    formula_payloads: List[Dict[str, Any]] = []
    raw_formulas: List[Tuple[str, Any]] = []

    for finding in report["findings"]:
        refs[finding["findingId"]] = {
            "frameObjectId": _logic_atom(finding["findingId"]),
            "dcecFormulaIds": [],
            "temporalFormulaIds": [],
        }
        for formula_id, payload, raw_formula in _build_temporal_formula_specs(finding, components):
            refs[finding["findingId"]]["temporalFormulaIds"].append(formula_id)
            formula_payloads.append(payload)
            raw_formulas.append((formula_id, raw_formula))

    proof_results = _attempt_temporal_proofs(raw_formulas, components)
    consistency_check = _attempt_temporal_consistency_check(report, components)

    return {
        "status": "success" if formula_payloads else "unavailable",
        "formulaCount": len(formula_payloads),
        "formulas": formula_payloads,
        "proofAnalysis": proof_results,
        "consistencyCheck": consistency_check,
    }, refs


def _build_formal_analysis(report: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    components = _load_ipfs_logic_components()
    frame_logic, frame_refs = _build_frame_logic_model(report, components)
    dcec, dcec_refs = _build_dcec_model(report)
    temporal_deontic, temporal_refs = _build_temporal_deontic_model(report, components)

    refs: Dict[str, Dict[str, Any]] = {}
    for finding in report["findings"]:
        finding_id = finding["findingId"]
        refs[finding_id] = {
            "frameObjectId": frame_refs.get(finding_id, {}).get("frameObjectId", _logic_atom(finding_id)),
            "dcecFormulaIds": dcec_refs.get(finding_id, {}).get("dcecFormulaIds", []),
            "temporalFormulaIds": temporal_refs.get(finding_id, {}).get("temporalFormulaIds", []),
        }

    return {
        "tooling": {
            "ipfsDatasetsPyAvailable": components["package_available"],
            "ipfsDatasetsPySource": components["source"],
            "importErrors": list(components["errors"]),
        },
        "frameLogic": frame_logic,
        "dcec": dcec,
        "temporalDeontic": temporal_deontic,
    }, refs


def build_contract_breach_report() -> Dict[str, Any]:
    fixture = _load_json(JOINDER_FIXTURE_PATH)
    evidence = _evidence_map(fixture)
    events = _event_map(fixture)
    authorities = _authority_map(fixture)
    findings: List[Dict[str, Any]] = []

    def add_finding(
        finding_id: str,
        actor: str,
        counterparties: Sequence[str],
        disposition: str,
        confidence: str,
        theory: str,
        contract_basis: str,
        element_assessment: Dict[str, str],
        supporting_evidence_ids: Sequence[str],
        supporting_event_ids: Sequence[str],
        supporting_authority_ids: Sequence[str],
        why: str,
        missing_proof: Sequence[str],
    ) -> None:
        findings.append(
            {
                "findingId": finding_id,
                "actor": actor,
                "actorLabel": PARTY_LABELS[actor],
                "counterparties": list(counterparties),
                "counterpartyLabels": [PARTY_LABELS[item] for item in counterparties],
                "disposition": disposition,
                "confidence": confidence,
                "theory": theory,
                "contractBasis": contract_basis,
                "elementAssessment": element_assessment,
                "whyItMatters": why,
                "supportingEvidence": [
                    {"id": item_id, "summary": _summary_line(evidence[item_id])}
                    for item_id in supporting_evidence_ids
                ],
                "supportingEvents": [
                    {"id": item_id, "summary": _event_line(events[item_id])}
                    for item_id in supporting_event_ids
                ],
                "supportingAuthorities": [
                    {"id": item_id, "summary": _authority_line(authorities[item_id])}
                    for item_id in supporting_authority_ids
                ],
                "missingProof": list(missing_proof),
            }
        )

    add_finding(
        finding_id="contract:hacc:relocation_commitment",
        actor="org:hacc",
        counterparties=["person:plaintiff_household"],
        disposition="likely_breach",
        confidence="high",
        theory="breach_of_contract_or_relocation_agreement",
        contract_basis="HACC's approval-triggered relocation commitment and linked replacement-housing pathway to the displaced household.",
        element_assessment={
            "existence": "Strong support that HACC undertook a concrete relocation path through the September 2024 Section 18 notice, the public redevelopment materials, and the January 2026 Blossom notice.",
            "performance": "Current record supports that the household pursued the directed relocation path and submitted the Blossom packet through the office HACC later identified.",
            "breach": "Current record supports noncompletion of relocation, lack of counseling/expense support, inaccessible replacement offering, and eviction before completion.",
            "damages": "Housing instability and the eviction posture are directly tied to the unfinished relocation process.",
        },
        supporting_evidence_ids=[
            "evidence:section18_phase2_notice",
            "evidence:hillside_park_public_redevelopment_page",
            "evidence:hacc_jan2026_notice_ashley_ferron_contact",
            "evidence:accommodation_records",
        ],
        supporting_event_ids=[
            "evt:e1_section18_hud_approval",
            "evt:e3_blossom_application_submitted",
            "evt:e8_third_floor_unit_offered",
            "evt:e9_eviction_filed",
        ],
        supporting_authority_ids=[
            "cfr_970_21",
            "ors_105_135_eviction_defense",
        ],
        why="The strongest contract-style theory against HACC is not an abstract statutory violation; it is that HACC put the household into a specific relocation transaction and then failed to carry that transaction through before suing for possession.",
        missing_proof=[
            "Any written relocation plan or household-specific relocation commitment naming the promised replacement path and timing.",
            "Any HACC counseling logs, moving-expense records, or completion certification to test HACC's anticipated defense that performance was complete.",
        ],
    )

    add_finding(
        finding_id="implied_contract:hacc:relocation_process",
        actor="org:hacc",
        counterparties=["person:plaintiff_household"],
        disposition="likely_breach",
        confidence="medium",
        theory="breach_of_implied_in_fact_relocation_agreement",
        contract_basis="HACC's notices, referral instructions, and relocation-process conduct created at least an implied-in-fact undertaking to administer a real replacement-housing path with continuity and ordinary care.",
        element_assessment={
            "existence": "The Phase II notice, public redevelopment page, and January 2026 direction to contact Ashley Ferron support an implied-in-fact agreement inferred from HACC's conduct rather than from a fully produced written household contract.",
            "performance": "The current record supports that the household followed the directed path by working through the HACC/Quantum intake chain and continuing relocation efforts.",
            "breach": "The implied process was not carried through to a completed, usable relocation outcome before eviction pressure intensified.",
            "damages": "The same stalled relocation path exposed the household to housing loss, delay, and relocation instability.",
        },
        supporting_evidence_ids=[
            "evidence:section18_phase2_notice",
            "evidence:hillside_park_public_redevelopment_page",
            "evidence:hacc_jan2026_notice_ashley_ferron_contact",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
        ],
        supporting_event_ids=[
            "evt:e1_section18_hud_approval",
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e9_eviction_filed",
        ],
        supporting_authority_ids=[
            "or_case_staley_taylor",
            "or_case_wiggins_barrett",
            "cfr_970_21",
        ],
        why="This is the safer Oregon contract framing when the full household-specific written agreement is still missing: HACC's conduct can itself support an implied-in-fact relocation agreement, and the current record supports that the process it set in motion was not completed.",
        missing_proof=[
            "Any household-specific relocation plan, relocation checklist, or internal HACC service standard tying the general relocation process to concrete promised steps and deadlines.",
            "Any written acceptance or acknowledgment by HACC showing the exact scope of the relocation pathway it was undertaking for this household.",
        ],
    )

    add_finding(
        finding_id="contract:quantum:intake_processing_commitment",
        actor="org:quantum",
        counterparties=["person:plaintiff_household", "org:hacc"],
        disposition="likely_breach",
        confidence="high",
        theory="breach_of_contract_or_processing_agreement",
        contract_basis="Quantum's owner/agent duty to receive, review, and timely process the application and its role in the HACC-linked replacement-housing intake chain.",
        element_assessment={
            "existence": "Strong support from the owner/agent review clause, HACC's PBV waitlist/Blossom linkage, and HACC's own proof that the packet was routed through Quantum staff.",
            "performance": "Current record supports substantial household performance by submitting the packet and pursuing the directed application path.",
            "breach": "Current record supports that Quantum received the packet, failed to transmit it to HACC, and did not issue a timely review result.",
            "damages": "The non-transmission and delay bear directly on the failed relocation path and the later eviction posture.",
        },
        supporting_evidence_ids=[
            "evidence:vera_application_owner_agent_duty",
            "evidence:blossom_graphrag_pbv_waitlist",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:email_falsely_claimed_quote",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e5_ferron_directs_quantum_to_forward",
            "evt:e7_household_asserts_falsely_claimed",
        ],
        supporting_authority_ids=[
            "hacc_admin_plan_rad_obligations",
            "hud_pih_2019_23_rad",
        ],
        why="The most developed contract-breach theory against Quantum is the failed intake-and-processing obligation: the current record already shows receipt, non-transmission, and a missing outcome on a housing application that was supposed to move the relocation forward.",
        missing_proof=[
            "The written management, owner-participation, HAP, or leasing agreement defining Quantum's formal processing duties for Blossom/Hillside relocation applicants.",
            "Quantum's internal intake log, CRM record, or receipt timestamp confirming when the packet entered and stalled in its system.",
        ],
    )

    add_finding(
        finding_id="implied_contract:quantum:application_processing_path",
        actor="org:quantum",
        counterparties=["person:plaintiff_household"],
        disposition="likely_breach",
        confidence="high",
        theory="breach_of_implied_in_fact_processing_agreement",
        contract_basis="By serving as the HACC-linked intake office and owner/agent review point, Quantum's conduct created an implied-in-fact agreement to receive, communicate about, and timely process the household's application materials.",
        element_assessment={
            "existence": "The current record strongly supports an implied agreement arising from conduct: HACC routed the packet through Quantum, Quantum staff received it, and the application materials themselves contemplate owner/agent review and notice back to the applicant.",
            "performance": "The household appears to have substantially performed by submitting the packet through the exact office HACC later identified.",
            "breach": "The present record supports non-transmission, no timely review result, and a later claim that the application had not been provided.",
            "damages": "The failure interrupted the relocation chain and contributed to delay, uncertainty, and later eviction exposure.",
        },
        supporting_evidence_ids=[
            "evidence:vera_application_owner_agent_duty",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:email_falsely_claimed_quote",
            "evidence:blossom_graphrag_pbv_waitlist",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e5_ferron_directs_quantum_to_forward",
            "evt:e7_household_asserts_falsely_claimed",
        ],
        supporting_authority_ids=[
            "or_case_staley_taylor",
            "or_case_wiggins_barrett",
            "hacc_admin_plan_rad_obligations",
        ],
        why="This implied-contract theory is stronger than waiting for a produced written management agreement because the current record already supports assent-by-conduct, receipt, and a failed processing path.",
        missing_proof=[
            "Quantum's internal intake log, front-desk record, or CRM entry confirming receipt date and handling steps.",
            "Any written policy or operating instruction at the Hillside Manor office explaining how relocation packets were supposed to be processed once accepted.",
        ],
    )

    add_finding(
        finding_id="promissory_estoppel:hacc:relocation_reliance",
        actor="org:hacc",
        counterparties=["person:plaintiff_household"],
        disposition="supported_reliance_theory",
        confidence="medium",
        theory="promissory_estoppel",
        contract_basis="HACC represented that relocation pathways existed, directed the household into those pathways, and should reasonably have expected the household to rely on those directions in lieu of making other housing arrangements.",
        element_assessment={
            "promise_or_representation": "The relocation notices and public redevelopment materials represent that residents would be guided through a relocation process and given replacement-housing or voucher-based options.",
            "reliance": "The current record supports reliance through the household's packet submission, continued application efforts, and participation in HACC-directed relocation steps.",
            "foreseeability": "HACC should reasonably have expected the household to rely on those relocation representations when deciding how to respond to displacement.",
            "injustice": "If HACC induced reliance on unfinished relocation paths and still pressed toward eviction, estoppel is a natural corrective theory.",
        },
        supporting_evidence_ids=[
            "evidence:section18_phase2_notice",
            "evidence:hillside_park_public_redevelopment_page",
            "evidence:hacc_jan2026_notice_ashley_ferron_contact",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
        ],
        supporting_event_ids=[
            "evt:e1_section18_hud_approval",
            "evt:e3_blossom_application_submitted",
            "evt:e9_eviction_filed",
        ],
        supporting_authority_ids=[
            "or_case_neiss_ehlers",
            "or_case_wiggins_barrett",
        ],
        why="This is the strongest non-final-contract theory against HACC: even if the precise relocation promises were too incomplete to be treated as a finished contract, the current record supports induced reliance on a specific relocation path.",
        missing_proof=[
            "Any direct HACC communication promising a move date, reserved unit, or specific completed relocation outcome.",
            "Out-of-pocket reliance evidence such as application fees, mailing costs, lost opportunities, or other steps taken because HACC represented the path was real.",
        ],
    )

    add_finding(
        finding_id="negligence:hacc:undertaken_relocation_administration",
        actor="org:hacc",
        counterparties=["person:plaintiff_household"],
        disposition="supported_but_otca_and_discretion_limits_apply",
        confidence="medium",
        theory="negligent_performance_of_undertaken_operational_duties",
        contract_basis="Once HACC undertook a specific household relocation process, routine implementation mistakes or careless routing may support negligence, but the claim must fit the Oregon Tort Claims Act and avoid discretionary-immunity barriers.",
        element_assessment={
            "duty": "The strongest negligence-duty theory is not a general duty to the public; it is a narrower duty arising from HACC's undertaken operational handling of this household's relocation process.",
            "breach": "The current record supports possible careless implementation through stalled routing, incomplete follow-through, inaccessible replacement handling, and eviction pressure before the path was completed.",
            "causation": "Causation is plausible because the alleged mishandling appears tied to the failed relocation path, but the claim still needs proof that HACC's acts made the household worse off or blocked protective alternatives.",
            "limitations": "OTCA notice, discretionary-function immunity, and the line between policy judgment and routine implementation are the main limiting issues.",
        },
        supporting_evidence_ids=[
            "evidence:section18_phase2_notice",
            "evidence:hacc_jan2026_notice_ashley_ferron_contact",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:accommodation_records",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e8_third_floor_unit_offered",
            "evt:e9_eviction_filed",
        ],
        supporting_authority_ids=[
            "or_case_brennen_city_of_eugene",
            "or_case_john_city_of_gresham",
            "ors_30_265_otca",
            "ors_30_275_otca_notice",
        ],
        why="A negligence theory against HACC is viable only in a narrowed form. The safest version is negligent operational handling of an undertaken relocation process, not a broad claim that HACC failed the public in the abstract.",
        missing_proof=[
            "Proof that OTCA notice was timely given to HACC, or facts showing an exception or alternative notice path.",
            "A clearer separation between operational acts and discretionary policy decisions, such as intake routing logs, assignment decisions, and staff implementation notes.",
            "Evidence that HACC's conduct affirmatively worsened the household's position or foreclosed other protective housing options.",
        ],
    )

    add_finding(
        finding_id="negligence:quantum:intake_mishandling",
        actor="org:quantum",
        counterparties=["person:plaintiff_household"],
        disposition="supported_if_special_relationship_or_information_duty_shown",
        confidence="medium",
        theory="negligent_processing_or_negligent_misrepresentation",
        contract_basis="Quantum's handling of intake materials may support negligence if Oregon's economic-loss limits are satisfied by a special relationship, an owner/agent information duty, or a negligent processing role tied to justified reliance.",
        element_assessment={
            "duty": "The best negligence theory is that Quantum acted in a role where applicants could reasonably rely on it to accurately receive, route, and communicate about housing-application materials.",
            "breach": "The current record supports packet non-transmission and at least some evidence of inaccurate communication about whether the application had been provided.",
            "causation": "The alleged mishandling plausibly delayed or derailed the relocation path, but causation still needs better proof of what would have happened absent the mishandling.",
            "limitations": "Because the main harm is economic and housing-process related, Oregon's economic-loss and special-relationship doctrines are the key limiters.",
        },
        supporting_evidence_ids=[
            "evidence:vera_application_owner_agent_duty",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:email_falsely_claimed_quote",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e7_household_asserts_falsely_claimed",
        ],
        supporting_authority_ids=[
            "or_case_onita_pacific",
            "or_case_staley_taylor",
        ],
        why="Quantum's tort exposure is narrower than its implied-contract exposure, but it remains live if discovery shows a role that made applicant reliance on Quantum's intake handling reasonable and foreseeable.",
        missing_proof=[
            "Any applicant instructions, signage, or policy showing that Quantum undertook to give accurate intake-status information to applicants and HACC.",
            "Proof of the counterfactual: what HACC would have done differently or earlier if Quantum had accurately forwarded or reported the packet.",
        ],
    )

    add_finding(
        finding_id="contract:quantum:rad_successor_obligations",
        actor="org:quantum",
        counterparties=["person:plaintiff_household"],
        disposition="supported_but_needs_contract_production",
        confidence="medium",
        theory="breach_of_rad_successor_or_relocation_commitment",
        contract_basis="Quantum's role as property manager for the RAD successor structure and related replacement-housing properties that inherited tenant-protection duties.",
        element_assessment={
            "existence": "The fixture strongly supports Quantum's role in the RAD successor chain, but the exact operative contract documents tying that role to this household's relocation path remain unproduced.",
            "performance": "The household appears to have pursued the available relocation paths in the thread, including Quantum-managed properties.",
            "breach": "There is meaningful support for inaccessible or incomplete housing pathways, but the precise contractual language still needs production.",
            "damages": "If the successor/manager duties attach, the same failed relocation path and eviction exposure supply damages and equitable prejudice.",
        },
        supporting_evidence_ids=[
            "evidence:admin_plan_ch18_hillside_manor_lp",
            "evidence:admin_plan_excluded_units",
            "evidence:parkside_heights_quantumres_in_thread",
            "evidence:accommodation_records",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e8_third_floor_unit_offered",
            "evt:e9_eviction_filed",
        ],
        supporting_authority_ids=[
            "hud_pih_2019_23_rad",
            "hacc_admin_plan_rad_obligations",
            "cfr_8_disability",
        ],
        why="The record supports more than a one-off leasing-office mistake; it supports a broader theory that the successor/manager side of the Hillside relocation structure inherited duties it did not carry out, but the written HAP and management agreements still need to be produced to make that theory harder to attack.",
        missing_proof=[
            "The RAD HAP contract, management agreement, and any owner-participation agreement specifically binding Quantum or affiliated entities to tenant-protection and relocation duties.",
            "Any property-specific operating records showing that Quantum or Hillside Manor LP had authority over accessible unit assignment and return-right administration.",
        ],
    )

    add_finding(
        finding_id="contract:hacc_quantum:interparty_allocation",
        actor="org:quantum",
        counterparties=["org:hacc"],
        disposition="supported_but_needs_contract_production",
        confidence="medium",
        theory="breach_of_management_or_owner_participation_agreement",
        contract_basis="The HACC-Quantum management / HAP / owner-participation relationship reflected in HACC's own Administrative Plan entries.",
        element_assessment={
            "existence": "The fixture strongly supports an ongoing HACC-Quantum contractual relationship across multiple properties.",
            "performance": "HACC appears to have depended on Quantum staff to receive and route at least part of the household's intake path.",
            "breach": "If Quantum had a contractual duty to process or relay intake materials, the non-transmission event would support an interparty breach/allocation claim.",
            "damages": "This theory matters primarily for third-party allocation, indemnity, and causation within the eviction/joinder litigation rather than for direct household damages alone.",
        },
        supporting_evidence_ids=[
            "evidence:admin_plan_ch17_hillside_manor",
            "evidence:admin_plan_ch18_hillside_manor_lp",
            "evidence:admin_plan_ch17_clayton_mohr_commons",
            "evidence:ferron_email_jan26_hacc_directs_quantum",
        ],
        supporting_event_ids=[
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e5_ferron_directs_quantum_to_forward",
        ],
        supporting_authority_ids=[
            "hacc_admin_plan_rad_obligations",
            "orcp_22b",
        ],
        why="Your added joinder materials already point to this theory: the record is strong that HACC and Quantum were in a contractual housing-management relationship, but the actual written agreement still needs to be in hand before that interparty breach theory can be framed with high confidence.",
        missing_proof=[
            "The operative management agreement, owner-participation agreement, or other contract allocating intake-processing and replacement-housing duties between HACC and Quantum.",
            "Any indemnity, delegation, or performance-standard clauses governing applicant intake, packet transmission, or tenant-protection compliance.",
        ],
    )

    add_finding(
        finding_id="no_contract_breach:household:substantial_performance",
        actor="person:plaintiff_household",
        counterparties=["org:hacc", "org:quantum"],
        disposition="no_current_breach_shown",
        confidence="medium",
        theory="substantial_performance",
        contract_basis="Household performance of the application and relocation-cooperation steps reflected in the current record.",
        element_assessment={
            "existence": "Assumes the same relocation/application commitments asserted in the direct breach theories.",
            "performance": "Current evidence tends to show the household submitted the packet and continued pursuing the paths identified by HACC and Quantum-linked properties.",
            "breach": "The current record does not strongly support a defense theory that the household, rather than HACC/Quantum, materially caused the collapse of the relocation path.",
            "damages": "Not applicable as an affirmative household breach theory on the current record.",
        },
        supporting_evidence_ids=[
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:parkside_heights_quantumres_in_thread",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
        ],
        supporting_authority_ids=[],
        why="That matters because a contract-breach defense from HACC or Quantum will likely try to shift failure back onto application completeness or cooperation; the current record cuts the other way.",
        missing_proof=[
            "A completeness checklist or submission packet copy, in case the other side argues the household failed to supply a required item.",
        ],
    )

    likely = [item for item in findings if item["disposition"] == "likely_breach"]
    report = {
        "meta": {
            "reportId": "contract_breach_report_001",
            "fixtureUsed": str(JOINDER_FIXTURE_PATH),
            "generatedAt": "April 5, 2026",
            "findingCount": len(findings),
            "likelyBreachCount": len(likely),
            "relatedArtifactsReviewed": [
                str(OUTPUTS / "title18_quantum_party_motion.md"),
                str(OUTPUTS / "title18_filing_draft.md"),
                str(OUTPUTS / "joinder_quantum_001_motion_for_joinder.md"),
            ],
        },
        "summary": {
            "strongestLikelyContractBreaches": [
                "HACC likely breached the relocation commitment by leaving relocation incomplete and still pursuing eviction.",
                "HACC also appears exposed on an implied-in-fact relocation-process theory, because its notices and routing conduct created a concrete process the household then followed.",
                "Quantum likely breached the intake-processing / application-review commitment by receiving but not forwarding the packet and not completing the promised path.",
                "Quantum also appears exposed on an implied-in-fact processing theory because the record supports assent-by-conduct at the intake office even before the written management contracts are produced.",
            ],
            "developingContractTheories": [
                "Promissory estoppel is a meaningful HACC theory if the relocation paths were specific enough to induce reliance but too incomplete to count as finished contracts.",
                "A negligence theory against HACC is narrower and must fit OTCA notice and discretionary-immunity limits; the safest version is negligent operational handling of an undertaken relocation process.",
                "Quantum may face a negligence or negligent-information theory if applicant reliance on its intake handling can be shown strongly enough to satisfy Oregon economic-loss limits.",
                "Quantum or the RAD successor structure may be in breach of inherited relocation or tenant-protection duties, but the operative contracts still need production.",
                "Quantum may also be in breach of a management or owner-participation agreement with HACC, supporting allocation or third-party liability.",
            ],
            "currentNoBreachShowing": [
                "The current record does not strongly support a theory that the household materially breached the relocation/application path.",
            ],
        },
        "findings": findings,
    }

    for finding in report["findings"]:
        title18_link = TITLE18_CONTRACT_LINKS.get(
            finding["findingId"],
            {
                "incorporatedTitle18Terms": [],
                "impliedTitle18PerformanceTerms": [],
                "statutoryDutySupportingContractTheory": "",
            },
        )
        finding["title18ContractLink"] = title18_link

    formal_analysis, formal_refs = _build_formal_analysis(report)
    for finding in report["findings"]:
        finding["formalRefs"] = formal_refs.get(
            finding["findingId"],
            {
                "frameObjectId": _logic_atom(finding["findingId"]),
                "dcecFormulaIds": [],
                "temporalFormulaIds": [],
            },
        )
    report["formalAnalysis"] = formal_analysis
    return report


def render_formal_analysis_markdown(formal_analysis: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Contract Breach Formal Model")
    lines.append("")
    lines.append("## Tooling")
    lines.append("")
    lines.append(f"- ipfs_datasets_py available: {formal_analysis['tooling']['ipfsDatasetsPyAvailable']}")
    if formal_analysis["tooling"].get("ipfsDatasetsPySource"):
        lines.append(f"- ipfs_datasets_py source: {formal_analysis['tooling']['ipfsDatasetsPySource']}")
    for item in formal_analysis["tooling"].get("importErrors", []):
        lines.append(f"- Import note: {item}")
    lines.append("")
    lines.append("## Frame Logic")
    lines.append("")
    lines.append(f"- Status: {formal_analysis['frameLogic']['status']}")
    lines.append(f"- Classes: {formal_analysis['frameLogic']['classCount']}")
    lines.append(f"- Frames: {formal_analysis['frameLogic']['frameCount']}")
    lines.append("")
    lines.append("## DCEC")
    lines.append("")
    lines.append(f"- Status: {formal_analysis['dcec']['status']}")
    lines.append(f"- Formulas: {formal_analysis['dcec']['formulaCount']}")
    lines.append("")
    lines.append("## Temporal Deontic")
    lines.append("")
    lines.append(f"- Status: {formal_analysis['temporalDeontic']['status']}")
    lines.append(f"- Formulas: {formal_analysis['temporalDeontic']['formulaCount']}")
    proof = formal_analysis["temporalDeontic"]["proofAnalysis"]
    lines.append(f"- Proof analysis status: {proof['status']}")
    if proof.get("reason"):
        lines.append(f"- Proof analysis note: {proof['reason']}")
    consistency = formal_analysis["temporalDeontic"]["consistencyCheck"]
    lines.append(f"- Consistency check status: {consistency['status']}")
    if consistency.get("reason"):
        lines.append(f"- Consistency check note: {consistency['reason']}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_contract_breach_report_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Contract Breach Analysis")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Likely contract-breach findings: {report['meta']['likelyBreachCount']}")
    for item in report["summary"]["strongestLikelyContractBreaches"]:
        lines.append(f"- {item}")
    for item in report["summary"]["developingContractTheories"]:
        lines.append(f"- Developing theory: {item}")
    for item in report["summary"]["currentNoBreachShowing"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Formal Analysis")
    lines.append("")
    lines.append(f"- Frame logic status: {report['formalAnalysis']['frameLogic']['status']}")
    lines.append(f"- Frame logic frames: {report['formalAnalysis']['frameLogic']['frameCount']}")
    lines.append(f"- DCEC formulas: {report['formalAnalysis']['dcec']['formulaCount']}")
    lines.append(f"- Temporal deontic formulas: {report['formalAnalysis']['temporalDeontic']['formulaCount']}")
    lines.append(f"- Proof analysis status: {report['formalAnalysis']['temporalDeontic']['proofAnalysis']['status']}")
    consistency = report["formalAnalysis"]["temporalDeontic"]["consistencyCheck"]
    lines.append(f"- Temporal consistency status: {consistency['status']}")
    if consistency.get("reason"):
        lines.append(f"- Temporal consistency note: {consistency['reason']}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for finding in report["findings"]:
        lines.append(f"### {finding['findingId']}")
        lines.append("")
        lines.append(f"- Actor: {finding['actorLabel']}")
        lines.append(f"- Counterparties: {', '.join(finding['counterpartyLabels'])}")
        lines.append(f"- Disposition: `{finding['disposition']}`")
        lines.append(f"- Confidence: `{finding['confidence']}`")
        lines.append(f"- Theory: {finding['theory']}")
        lines.append(f"- Contract basis: {finding['contractBasis']}")
        title18_link = finding.get("title18ContractLink", {})
        if title18_link.get("incorporatedTitle18Terms") or title18_link.get("impliedTitle18PerformanceTerms") or title18_link.get("statutoryDutySupportingContractTheory"):
            lines.append("- Title 18 linkage:")
            for item in title18_link.get("incorporatedTitle18Terms", []):
                lines.append(f"  - incorporated term: {item}")
            for item in title18_link.get("impliedTitle18PerformanceTerms", []):
                lines.append(f"  - implied performance term: {item}")
            if title18_link.get("statutoryDutySupportingContractTheory"):
                lines.append(f"  - statutory support: {title18_link['statutoryDutySupportingContractTheory']}")
        lines.append(f"- Why it matters: {finding['whyItMatters']}")
        lines.append(
            f"- Formal refs: frame `{finding['formalRefs']['frameObjectId']}`, DCEC {len(finding['formalRefs']['dcecFormulaIds'])}, temporal deontic {len(finding['formalRefs']['temporalFormulaIds'])}"
        )
        lines.append("- Element assessment:")
        for key, value in finding["elementAssessment"].items():
            lines.append(f"  - {key}: {value}")
        lines.append("- Supporting evidence:")
        for item in finding["supportingEvidence"]:
            lines.append(f"  - `{item['id']}`: {item['summary']}")
        lines.append("- Supporting events:")
        for item in finding["supportingEvents"]:
            lines.append(f"  - `{item['id']}`: {item['summary']}")
        if finding["supportingAuthorities"]:
            lines.append("- Supporting authorities:")
            for item in finding["supportingAuthorities"]:
                lines.append(f"  - `{item['id']}`: {item['summary']}")
        if finding["missingProof"]:
            lines.append("- Missing proof:")
            for item in finding["missingProof"]:
                lines.append(f"  - {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_contract_breach_report(report: Dict[str, Any] | None = None) -> Dict[str, Path]:
    report = report or build_contract_breach_report()
    outputs = {
        "json": OUTPUTS / "contract_breach_report.json",
        "markdown": OUTPUTS / "contract_breach_report.md",
        "formal_json": OUTPUTS / "contract_breach_formal_model.json",
        "formal_markdown": OUTPUTS / "contract_breach_formal_model.md",
    }
    outputs["json"].write_text(json.dumps(report, indent=2) + "\n")
    outputs["markdown"].write_text(render_contract_breach_report_markdown(report))
    outputs["formal_json"].write_text(json.dumps(report["formalAnalysis"], indent=2) + "\n")
    outputs["formal_markdown"].write_text(render_formal_analysis_markdown(report["formalAnalysis"]))
    return outputs


def main() -> int:
    outputs = write_contract_breach_report()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
