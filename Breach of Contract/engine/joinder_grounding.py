#!/usr/bin/env python3
"""Dependency graph and authority grounding for the joinder/eviction-defense case.

Parallel module to legal_grounding.py, but specific to the HACC v. Barber/Cortez
Motion for Joinder of Quantum Residential in Clackamas County Circuit Court.

Public API
----------
dependency_graph_payload(case_payload)      -> {branch, activeOutcome, nodes, edges}
build_dependency_citations_jsonld(case_payload) -> JSON-LD @graph dict

Internal evaluator (_evaluate_joinder) is self-contained so this module does not
depend on the live-in-aide evaluate_case.py.
"""

from __future__ import annotations

from typing import Any, Dict, List

from engine.authority_fit import infer_fit_kind

# ---------------------------------------------------------------------------
# Finding → fact key mapping
# ---------------------------------------------------------------------------

JOINDER_FINDING_FACT_SOURCES: Dict[str, List[str]] = {
    "joinder": [
        "hacc_routed_intake_through_quantum_office",
        "quantum_received_cortez_documents",
        "quantum_failed_to_transmit_to_hacc",
        "quantum_falsely_denied_receiving_application",
        "joint_email_notice_hacc_and_quantum",
        "ferron_misrepresentation_quantum_separate",
        "ferron_misrepresentation_contradicted_by_admin_plan",
        "household_still_in_eviction_no_completed_relocation",
    ],
    "successorInInterest": [
        "hacc_pha_owns_hillside_manor",
        "quantum_named_pm_admin_plan_ch17",
        "quantum_named_pm_admin_plan_ch18_rad",
        "hillside_manor_lp_rad_successor",
        "eminent_domain_acquisition_documented",
        "rad_conversion_closed_2021_01_01",
        "rad_pih_2019_23_governs",
        "quantum_portfolio_wide_hacc_relationship",
    ],
    "section18Violation": [
        "section18_phase2_notice_served_sept_2024",
        "no_hqs_comparability_analysis_produced",
        "no_relocation_expenses_paid",
        "no_counseling_provided",
        "no_consultation_records_produced",
        "household_still_in_eviction_no_completed_relocation",
    ],
    "radObligations": [
        "hillside_manor_lp_rad_successor",
        "rad_conversion_closed_2021_01_01",
        "rad_pih_2019_23_governs",
        "quantum_named_pm_admin_plan_ch18_rad",
    ],
    "disabilityAccommodation": [
        "third_floor_unit_offered_mobility_impaired",
        "disability_accommodation_unmet",
    ],
    "preventionDefense": [
        "quantum_failed_to_transmit_to_hacc",
        "quantum_falsely_denied_receiving_application",
        "ferron_misrepresentation_quantum_separate",
        "ferron_misrepresentation_contradicted_by_admin_plan",
        "household_still_in_eviction_no_completed_relocation",
    ],
}

# ---------------------------------------------------------------------------
# Finding → authority ID mapping
# ---------------------------------------------------------------------------

JOINDER_FINDING_AUTHORITY_SOURCES: Dict[str, List[str]] = {
    "joinder": ["orcp_29a", "orcp_22b", "ors_105_135_eviction_defense"],
    "successorInInterest": ["hud_pih_2019_23_rad", "hacc_admin_plan_rad_obligations"],
    "section18Violation": [
        "usc_1437p_section18",
        "cfr_970_7",
        "cfr_970_21",
        "ors_105_135_eviction_defense",
    ],
    "radObligations": ["hud_pih_2019_23_rad", "hacc_admin_plan_rad_obligations"],
    "disabilityAccommodation": ["cfr_8_disability", "fha_42_usc_3604", "giebeler"],
    "preventionDefense": ["orcp_29a", "ors_105_135_eviction_defense"],
}

# ---------------------------------------------------------------------------
# Dependency graph — nodes
# ---------------------------------------------------------------------------

DEPENDENCY_NODES: List[str] = [
    # ORCP 29A joinder test elements
    "complete_relief_impossible",
    "inconsistent_obligations_risk",
    "joinder_required",
    # Integrated transaction / same-occurrence privity chain
    "hacc_controls_displacement",
    "quantum_controls_intake_processing",
    "hacc_quantum_contractual_relationship",
    "same_transaction_or_occurrence",
    "quantum_portfolio_wide_relationship",
    # Successor-in-interest chain
    "eminent_domain_acquisition",
    "rad_conversion_to_lp",
    "quantum_named_lp_manager",
    "quantum_is_successor_in_interest",
    # RAD parallel obligations (PIH 2019-23)
    "rad_pih_2019_23_governs",
    "rad_right_to_return",
    "rad_obligations_bind_quantum",
    # Section 18 compliance elements
    "section18_hud_approval_obtained",
    "section18_90day_notice_served",
    "section18_comparable_housing_required",
    "section18_relocation_expenses_required",
    "section18_consultation_required",
    "section18_compliance_deficient",
    "section18_violation",
    # Disability accommodation
    "disability_accommodation_owed",
    "third_floor_inaccessible",
    "accommodation_not_provided",
    "disability_rights_violated",
    # Prevention / estoppel defense
    "hacc_prevented_relocation",
    "quantum_prevented_application_processing",
    "prevention_estoppel_defense",
    # Outcome nodes
    "quantum_joinder_proper",
    "eviction_defense_viable",
]

# ---------------------------------------------------------------------------
# Dependency graph — edges
# (each entry is [source, target] or [source, target, "defeater"])
# ---------------------------------------------------------------------------

DEPENDENCY_EDGES: List[List[str]] = [
    # ── ORCP 29A joinder test ──────────────────────────────────────────────
    ["complete_relief_impossible", "joinder_required"],
    ["inconsistent_obligations_risk", "joinder_required"],
    # Same-transaction privity establishes "complete relief impossible"
    ["hacc_controls_displacement", "same_transaction_or_occurrence"],
    ["quantum_controls_intake_processing", "same_transaction_or_occurrence"],
    ["hacc_quantum_contractual_relationship", "same_transaction_or_occurrence"],
    ["quantum_portfolio_wide_relationship", "same_transaction_or_occurrence"],
    ["same_transaction_or_occurrence", "complete_relief_impossible"],
    # ── Successor-in-interest chain ────────────────────────────────────────
    ["eminent_domain_acquisition", "rad_conversion_to_lp"],
    ["rad_conversion_to_lp", "quantum_named_lp_manager"],
    ["quantum_named_lp_manager", "quantum_is_successor_in_interest"],
    ["quantum_is_successor_in_interest", "hacc_quantum_contractual_relationship"],
    ["quantum_is_successor_in_interest", "inconsistent_obligations_risk"],
    # ── RAD obligations (PIH 2019-23) ──────────────────────────────────────
    ["rad_pih_2019_23_governs", "rad_right_to_return"],
    ["rad_pih_2019_23_governs", "rad_obligations_bind_quantum"],
    ["quantum_named_lp_manager", "rad_obligations_bind_quantum"],
    ["rad_obligations_bind_quantum", "complete_relief_impossible"],
    ["rad_obligations_bind_quantum", "inconsistent_obligations_risk"],
    # ── Section 18 compliance chain ────────────────────────────────────────
    # HUD approval triggers the three mandatory preconditions
    ["section18_hud_approval_obtained", "section18_comparable_housing_required"],
    ["section18_hud_approval_obtained", "section18_relocation_expenses_required"],
    ["section18_hud_approval_obtained", "section18_consultation_required"],
    # Each unmet precondition is a defeater (evidence of non-compliance)
    ["section18_comparable_housing_required", "section18_compliance_deficient", "defeater"],
    ["section18_relocation_expenses_required", "section18_compliance_deficient", "defeater"],
    ["section18_consultation_required", "section18_compliance_deficient", "defeater"],
    ["section18_compliance_deficient", "section18_violation"],
    ["section18_violation", "eviction_defense_viable"],
    # ── Disability accommodation ───────────────────────────────────────────
    ["disability_accommodation_owed", "accommodation_not_provided"],
    ["third_floor_inaccessible", "accommodation_not_provided"],
    ["accommodation_not_provided", "disability_rights_violated"],
    ["accommodation_not_provided", "section18_compliance_deficient"],
    ["disability_rights_violated", "eviction_defense_viable"],
    # ── Prevention / estoppel defense ─────────────────────────────────────
    ["hacc_prevented_relocation", "prevention_estoppel_defense"],
    ["quantum_prevented_application_processing", "prevention_estoppel_defense"],
    ["prevention_estoppel_defense", "eviction_defense_viable"],
    # ── Outcome ───────────────────────────────────────────────────────────
    ["joinder_required", "quantum_joinder_proper"],
    ["quantum_is_successor_in_interest", "quantum_joinder_proper"],
    ["quantum_joinder_proper", "eviction_defense_viable"],
]

# ---------------------------------------------------------------------------
# Authority grounding — keyed by authority ID in the case fixture
# ---------------------------------------------------------------------------

AUTHORITY_GROUNDING: Dict[str, Dict[str, Any]] = {
    "orcp_29a": {
        "excerptText": (
            "A person who is subject to service of process shall be joined as a party in the "
            "action if: (1) in the person's absence complete relief cannot be accorded among "
            "those already parties, or (2) the person claims an interest relating to the subject "
            "of the action and is so situated that the disposition of the action in the person's "
            "absence may as a practical matter impair or impede the person's ability to protect "
            "that interest or leave any of the persons already parties subject to a substantial "
            "risk of incurring double, multiple, or otherwise inconsistent obligations."
        ),
        "proposition": (
            "Joinder is required where complete relief cannot be accorded without the absent "
            "party, or where absence creates risk of inconsistent obligations."
        ),
        "court": "Oregon",
        "year": "current",
        "pincite": "(A)",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/orcp.pdf",
        "excerptKind": "paraphrase",
    },
    "orcp_22b": {
        "excerptText": (
            "A defending party, as a third-party plaintiff, may cause a summons and complaint "
            "to be served upon a person not a party to the action who is or may be liable to "
            "the third-party plaintiff for all or part of the plaintiff's claim against the "
            "third-party plaintiff."
        ),
        "proposition": (
            "A defendant may implead any person who may be liable for all or part of the "
            "claim against the defendant."
        ),
        "court": "Oregon",
        "year": "current",
        "pincite": "(B)",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/orcp.pdf",
        "excerptKind": "paraphrase",
    },
    "usc_1437p_section18": {
        "excerptText": (
            "A public housing agency shall not proceed with the demolition or disposition of any "
            "public housing project unless the Secretary has approved the demolition or disposition "
            "plan ... [including] resident relocation, 90-day notice, comparable housing, "
            "relocation expenses, and consultation requirements."
        ),
        "proposition": (
            "PHAs must satisfy mandatory relocation, notice, comparability, and consultation "
            "preconditions before Section 18 demolition or disposition."
        ),
        "court": "Federal",
        "year": "current",
        "pincite": "(a)(4)",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1437p",
        "excerptKind": "paraphrase",
    },
    "cfr_970_7": {
        "excerptText": (
            "The PHA must submit an application to HUD that includes a relocation plan, "
            "consultation records, board resolution, environmental review, and all required "
            "supporting documentation before HUD approval may be granted."
        ),
        "proposition": (
            "Full application package including relocation plan and consultation records "
            "must precede HUD approval."
        ),
        "court": "HUD",
        "year": "current",
        "pincite": "(a)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-970/section-970.7",
        "excerptKind": "paraphrase",
    },
    "cfr_970_21": {
        "excerptText": (
            "The PHA must offer each family a comparable dwelling unit ... [that is] decent, "
            "safe, sanitary, and in an area not generally less desirable ... No family may be "
            "required to move until a comparable dwelling unit is actually available ... "
            "The PHA must pay actual and reasonable moving expenses."
        ),
        "proposition": (
            "Relocation housing must be comparable (HQS-compliant, accessible, similarly "
            "desirable). No displacement before relocation is complete. Moving expenses must be paid."
        ),
        "court": "HUD",
        "year": "current",
        "pincite": "(a), (b), (e)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-970/section-970.21",
        "excerptKind": "paraphrase",
    },
    "hud_pih_2019_23_rad": {
        "excerptText": (
            "Residents have the right to return to the converted project upon completion. "
            "The converting PHA must maintain a relocation plan approved by HUD. "
            "The successor owner-operator is bound by all RAD requirements, including tenant "
            "protection, lease continuation, and right to return. All tenant rights that existed "
            "under the ACC continue under the RAD HAP contract."
        ),
        "proposition": (
            "The RAD successor LP and its property manager inherit the converting PHA's "
            "tenant-protection and relocation obligations; right to return is mandatory."
        ),
        "court": "HUD",
        "year": "2019",
        "pincite": "Section 1.6, 3.3",
        "sourceUrl": "https://www.hud.gov/sites/dfiles/PIH/documents/PIH-2019-23.pdf",
        "excerptKind": "paraphrase",
    },
    "cfr_8_disability": {
        "excerptText": (
            "Recipients must make reasonable accommodations in rules, policies, practices, or "
            "services when necessary to afford a qualified person with a disability equal "
            "opportunity to use and enjoy a dwelling."
        ),
        "proposition": (
            "HUD program recipients (including PHAs and their contractors) must provide "
            "reasonable accommodations to persons with disabilities."
        ),
        "court": "HUD",
        "year": "current",
        "pincite": "§ 8.26",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/subtitle-A/part-8",
        "excerptKind": "paraphrase",
    },
    "fha_42_usc_3604": {
        "excerptText": (
            "It shall be unlawful to refuse to make reasonable accommodations in rules, policies, "
            "practices, or services, when such accommodations may be necessary to afford such "
            "person equal opportunity to use and enjoy a dwelling."
        ),
        "proposition": (
            "Property owners and public housing actors must make reasonable accommodations "
            "for disability-related housing needs."
        ),
        "court": "Federal",
        "year": "current",
        "pincite": "(f)(3)(B)",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section3604",
        "excerptKind": "verified_quote",
    },
    "giebeler": {
        "excerptText": (
            "Imposition of burdensome policies can interfere with disabled persons' right to "
            "use and enjoyment of their dwellings."
        ),
        "proposition": (
            "Burdensome housing policies that impair disabled persons' use and enjoyment may "
            "require accommodation regardless of standard policy."
        ),
        "court": "9th Cir.",
        "year": "2003",
        "pincite": "1155",
        "sourceUrl": "https://law.justia.com/cases/federal/appellate-courts/F3/343/1143/636375/",
        "excerptKind": "verified_quote",
    },
    "ors_105_135_eviction_defense": {
        "excerptText": (
            "In any action for possession of a dwelling unit, it is an affirmative defense that "
            "the landlord has not complied with applicable federal law governing the displacement "
            "of public-housing residents."
        ),
        "proposition": (
            "Non-compliance with Section 18 federal relocation requirements is an affirmative "
            "defense to eviction under Oregon law."
        ),
        "court": "Oregon",
        "year": "current",
        "pincite": "(3)",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/ors105.html",
        "excerptKind": "paraphrase",
    },
    "hacc_admin_plan_rad_obligations": {
        "excerptText": (
            "Development Name: Hillside Manor Apartments / Owner Information: Hillside Manor "
            "Limited Partnership / Property Management Company: Quantum Residential Property "
            "Management (HillsideManor@QResInc.com) / PHA-Owned: Yes / Mixed-Finance "
            "Development: Yes / Closing Date: 1/1/2021 / RAD Notice: PIH 2019-23 / "
            "HAP Contracts: 06/01/2020 (Eminent Domain 5 PBV plus 26 Enhanced PBV) and "
            "01/01/2021 (RAD HAP contract, 70 RAD PBV)."
        ),
        "proposition": (
            "HACC's own filed Administrative Plan names Quantum Residential as property manager "
            "of the Hillside Manor Limited Partnership, the private RAD successor entity created "
            "from former Hillside Park public housing through eminent domain acquisition and "
            "RAD conversion."
        ),
        "court": "N/A",
        "year": "2025",
        "pincite": "Exhibit 18-1, Hillside Manor Apartments RAD PBV entry",
        "sourceUrl": None,
        "excerptKind": "verified_quote",
    },
}

# ---------------------------------------------------------------------------
# Finding → dependency graph targets
# Each bucket maps to nodes and edges (by "source->target" string ID)
# that the finding's authorities substantiate.
# ---------------------------------------------------------------------------

FINDING_TO_TARGETS: Dict[str, Dict[str, List[str]]] = {
    "joinder": {
        "nodes": [
            "joinder_required",
            "complete_relief_impossible",
            "inconsistent_obligations_risk",
            "same_transaction_or_occurrence",
        ],
        "edges": [
            "complete_relief_impossible->joinder_required",
            "inconsistent_obligations_risk->joinder_required",
            "same_transaction_or_occurrence->complete_relief_impossible",
            "hacc_controls_displacement->same_transaction_or_occurrence",
            "quantum_controls_intake_processing->same_transaction_or_occurrence",
        ],
    },
    "successorInInterest": {
        "nodes": [
            "quantum_is_successor_in_interest",
            "quantum_named_lp_manager",
            "rad_conversion_to_lp",
            "eminent_domain_acquisition",
            "hacc_quantum_contractual_relationship",
        ],
        "edges": [
            "eminent_domain_acquisition->rad_conversion_to_lp",
            "rad_conversion_to_lp->quantum_named_lp_manager",
            "quantum_named_lp_manager->quantum_is_successor_in_interest",
            "quantum_is_successor_in_interest->hacc_quantum_contractual_relationship",
            "quantum_is_successor_in_interest->inconsistent_obligations_risk",
        ],
    },
    "section18Violation": {
        "nodes": [
            "section18_compliance_deficient",
            "section18_violation",
            "section18_comparable_housing_required",
            "section18_relocation_expenses_required",
            "section18_consultation_required",
        ],
        "edges": [
            "section18_comparable_housing_required->section18_compliance_deficient",
            "section18_relocation_expenses_required->section18_compliance_deficient",
            "section18_consultation_required->section18_compliance_deficient",
            "section18_compliance_deficient->section18_violation",
            "section18_violation->eviction_defense_viable",
        ],
    },
    "radObligations": {
        "nodes": [
            "rad_obligations_bind_quantum",
            "rad_right_to_return",
            "rad_pih_2019_23_governs",
        ],
        "edges": [
            "rad_pih_2019_23_governs->rad_right_to_return",
            "rad_pih_2019_23_governs->rad_obligations_bind_quantum",
            "quantum_named_lp_manager->rad_obligations_bind_quantum",
            "rad_obligations_bind_quantum->complete_relief_impossible",
            "rad_obligations_bind_quantum->inconsistent_obligations_risk",
        ],
    },
    "disabilityAccommodation": {
        "nodes": [
            "accommodation_not_provided",
            "disability_rights_violated",
            "disability_accommodation_owed",
            "third_floor_inaccessible",
        ],
        "edges": [
            "disability_accommodation_owed->accommodation_not_provided",
            "third_floor_inaccessible->accommodation_not_provided",
            "accommodation_not_provided->disability_rights_violated",
            "accommodation_not_provided->section18_compliance_deficient",
            "disability_rights_violated->eviction_defense_viable",
        ],
    },
    "preventionDefense": {
        "nodes": [
            "prevention_estoppel_defense",
            "hacc_prevented_relocation",
            "quantum_prevented_application_processing",
        ],
        "edges": [
            "hacc_prevented_relocation->prevention_estoppel_defense",
            "quantum_prevented_application_processing->prevention_estoppel_defense",
            "prevention_estoppel_defense->eviction_defense_viable",
        ],
    },
}

# ---------------------------------------------------------------------------
# Internal evaluator (self-contained — does not depend on evaluate_case.py)
# ---------------------------------------------------------------------------


def _evaluate_joinder(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a joinder/eviction-defense case fixture and return findings."""
    facts: Dict[str, bool] = dict(case_payload.get("assertedFacts", {}))
    for key, val in case_payload.get("acceptedFindings", {}).items():
        facts[key] = val

    outcomes: Dict[str, bool] = {
        bucket: any(facts.get(k, False) for k in fact_keys)
        for bucket, fact_keys in JOINDER_FINDING_FACT_SOURCES.items()
    }

    authorities_index: Dict[str, Dict[str, Any]] = {
        item["id"]: item for item in case_payload.get("authorities", [])
    }

    authority_support: Dict[str, List[Dict[str, str]]] = {
        bucket: [
            {
                "id": aid,
                "label": (
                    authorities_index[aid]["label"]
                    if aid in authorities_index
                    else aid
                ),
                "weight": (
                    authorities_index[aid].get("weight", "binding")
                    if aid in authorities_index
                    else "binding"
                ),
            }
            for aid in authority_ids
        ]
        for bucket, authority_ids in JOINDER_FINDING_AUTHORITY_SOURCES.items()
    }

    return {
        "caseId": case_payload.get("caseId", "joinder_quantum_001"),
        "branch": case_payload.get("branch", "joinder_eviction_defense"),
        "outcome": outcomes,
        "findings": outcomes,
        "authoritySupport": authority_support,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def dependency_graph_payload(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the dependency graph skeleton with branch/outcome metadata."""
    result = _evaluate_joinder(case_payload)
    return {
        "branch": result["branch"],
        "activeOutcome": (
            "quantum_joinder_viable"
            if result["outcome"].get("joinder", False)
            else "joinder_contested"
        ),
        "nodes": DEPENDENCY_NODES,
        "edges": DEPENDENCY_EDGES,
    }


def build_dependency_citations_jsonld(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a full JSON-LD @graph linking authorities to dependency-graph nodes and edges."""
    result = _evaluate_joinder(case_payload)
    payload = dependency_graph_payload(case_payload)
    authorities: Dict[str, Dict[str, Any]] = {
        item["id"]: item for item in case_payload.get("authorities", [])
    }

    graph: List[Dict[str, Any]] = [
        {
            "id": f"case:{result['caseId']}",
            "type": "ReasoningCase",
            "caseId": result["caseId"],
            "branch": result["branch"],
            "activeOutcome": payload["activeOutcome"],
        }
    ]

    for node in payload["nodes"]:
        graph.append(
            {
                "id": f"dep:node:{node}",
                "type": "DependencyNode",
                "nodeId": node,
                "label": node.replace("_", " "),
            }
        )

    for edge in payload["edges"]:
        source = edge[0]
        target = edge[1]
        role = edge[2] if len(edge) > 2 else "support"
        graph.append(
            {
                "id": f"dep:edge:{source}->{target}",
                "type": "DependencyEdge",
                "edgeId": f"{source}->{target}",
                "fromNode": f"dep:node:{source}",
                "toNode": f"dep:node:{target}",
                "edgeRole": role,
            }
        )

    seen_authorities: set = set()
    seen_excerpts: set = set()

    for bucket, authority_refs in result.get("authoritySupport", {}).items():
        targets = FINDING_TO_TARGETS.get(bucket, {"nodes": [], "edges": []})
        for authority_ref in authority_refs:
            authority = authorities.get(authority_ref["id"], {})
            authority_id = authority_ref["id"]
            authority_node_id = f"authority:{authority_id}"
            excerpt_node_id = f"excerpt:{authority_id}"

            # Prefer fixture data; fall back to AUTHORITY_GROUNDING; then bare minimum
            grounding_base = AUTHORITY_GROUNDING.get(authority_id, {})
            grounding: Dict[str, Any] = {
                "excerptText": (
                    authority.get("excerptText")
                    or grounding_base.get("excerptText", "Authority grounding summary unavailable.")
                ),
                "proposition": (
                    authority.get("proposition")
                    or grounding_base.get("proposition", "Authority proposition unavailable.")
                ),
                "excerptKind": (
                    authority.get("excerptKind")
                    or grounding_base.get("excerptKind", "paraphrase")
                ),
                "fitKind": (
                    authority.get("fitKind")
                    or grounding_base.get("fitKind")
                    or infer_fit_kind(authority)
                ),
                "sourceUrl": (
                    authority.get("sourceUrl") or grounding_base.get("sourceUrl")
                ),
                "court": authority.get("court") or grounding_base.get("court", ""),
                "year": authority.get("year") or grounding_base.get("year", ""),
                "pincite": authority.get("pincite") or grounding_base.get("pincite", ""),
            }

            if authority_node_id not in seen_authorities:
                seen_authorities.add(authority_node_id)
                graph.append(
                    {
                        "id": authority_node_id,
                        "type": "LegalAuthority",
                        "label": authority.get("label", authority_id),
                        "citation": authority.get("citation"),
                        "weight": authority.get("weight"),
                        "jurisdiction": authority.get("jurisdiction"),
                        "court": grounding["court"],
                        "year": grounding["year"],
                        "pincite": grounding["pincite"],
                        "sourceUrl": grounding["sourceUrl"],
                    }
                )

            if excerpt_node_id not in seen_excerpts:
                seen_excerpts.add(excerpt_node_id)
                graph.append(
                    {
                        "id": excerpt_node_id,
                        "type": "AuthorityExcerpt",
                        "authority": authority_node_id,
                        "excerptText": grounding["excerptText"],
                        "proposition": grounding["proposition"],
                        "excerptKind": grounding["excerptKind"],
                        "fitKind": grounding["fitKind"],
                        "court": grounding["court"],
                        "year": grounding["year"],
                        "pincite": grounding["pincite"],
                        "sourceUrl": grounding["sourceUrl"],
                    }
                )

            for node in targets["nodes"]:
                graph.append(
                    {
                        "id": f"support:{bucket}:{authority_id}:node:{node}",
                        "type": "DependencySupport",
                        "supportKind": "node",
                        "findingBucket": bucket,
                        "target": f"dep:node:{node}",
                        "authority": authority_node_id,
                        "authorityExcerpt": excerpt_node_id,
                    }
                )

            for edge_id in targets["edges"]:
                graph.append(
                    {
                        "id": f"support:{bucket}:{authority_id}:edge:{edge_id}",
                        "type": "DependencySupport",
                        "supportKind": "edge",
                        "findingBucket": bucket,
                        "target": f"dep:edge:{edge_id}",
                        "authority": authority_node_id,
                        "authorityExcerpt": excerpt_node_id,
                    }
                )

    return {
        "@context": {
            "id": "@id",
            "type": "@type",
            "caseId": "https://example.org/legal/caseId",
            "branch": "https://example.org/legal/branch",
            "activeOutcome": "https://example.org/legal/activeOutcome",
            "nodeId": "https://example.org/legal/nodeId",
            "edgeId": "https://example.org/legal/edgeId",
            "fromNode": {"@id": "https://example.org/legal/fromNode", "@type": "@id"},
            "toNode": {"@id": "https://example.org/legal/toNode", "@type": "@id"},
            "edgeRole": "https://example.org/legal/edgeRole",
            "label": "https://example.org/legal/label",
            "citation": "https://example.org/legal/citation",
            "weight": "https://example.org/legal/weight",
            "jurisdiction": "https://example.org/legal/jurisdiction",
            "court": "https://example.org/legal/court",
            "year": "https://example.org/legal/year",
            "pincite": "https://example.org/legal/pincite",
            "sourceUrl": "https://example.org/legal/sourceUrl",
            "fitKind": "https://example.org/legal/fitKind",
            "authority": {"@id": "https://example.org/legal/authority", "@type": "@id"},
            "authorityExcerpt": {
                "@id": "https://example.org/legal/authorityExcerpt",
                "@type": "@id",
            },
            "excerptText": "https://example.org/legal/excerptText",
            "proposition": "https://example.org/legal/proposition",
            "excerptKind": "https://example.org/legal/excerptKind",
            "supportKind": "https://example.org/legal/supportKind",
            "findingBucket": "https://example.org/legal/findingBucket",
            "target": {"@id": "https://example.org/legal/target", "@type": "@id"},
        },
        "@graph": graph,
    }
