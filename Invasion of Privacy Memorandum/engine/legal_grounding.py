#!/usr/bin/env python3
"""Shared authority-grounding helpers for package and memorandum exports."""

from __future__ import annotations

from typing import Any, Dict, List

from engine.authority_fit import infer_fit_kind
from engine.evaluate_case import evaluate_case

DEPENDENCY_NODES = [
    "disabled_tenant",
    "needs_live_in_aide",
    "medical_verification",
    "requested_separate_bedroom",
    "approved_aide_in_principle",
    "denied_separate_bedroom",
    "aide_sleeps_in_living_room",
    "night_access_needed",
    "sleep_interruption",
    "work_interference",
    "caregiving_impairment",
    "privacy_loss",
    "necessary",
    "reasonable",
    "duty_to_grant",
    "not_effective",
    "constructive_denial",
    "undue_burden",
    "fundamental_alteration",
    "violation",
]

DEPENDENCY_EDGES = [
    ["aide_sleeps_in_living_room", "sleep_interruption"],
    ["night_access_needed", "sleep_interruption"],
    ["sleep_interruption", "work_interference"],
    ["sleep_interruption", "caregiving_impairment"],
    ["sleep_interruption", "necessary"],
    ["work_interference", "necessary"],
    ["caregiving_impairment", "necessary"],
    ["privacy_loss", "necessary"],
    ["medical_verification", "reasonable"],
    ["necessary", "reasonable"],
    ["undue_burden", "reasonable", "defeater"],
    ["fundamental_alteration", "reasonable", "defeater"],
    ["disabled_tenant", "duty_to_grant"],
    ["needs_live_in_aide", "duty_to_grant"],
    ["requested_separate_bedroom", "duty_to_grant"],
    ["reasonable", "duty_to_grant"],
    ["denied_separate_bedroom", "not_effective"],
    ["sleep_interruption", "not_effective"],
    ["approved_aide_in_principle", "constructive_denial"],
    ["denied_separate_bedroom", "constructive_denial"],
    ["not_effective", "constructive_denial"],
    ["duty_to_grant", "violation"],
    ["denied_separate_bedroom", "violation"],
    ["constructive_denial", "violation"],
]

AUTHORITY_GROUNDING = {
    "giebeler": {
        "excerptText": "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings.",
        "proposition": "Burdensome housing policies may require accommodation when they interfere with use and enjoyment.",
        "court": "9th Cir.",
        "year": "2003",
        "pincite": "1155",
        "sourceUrl": "https://law.justia.com/cases/federal/appellate-courts/F3/343/1143/636375/",
        "excerptKind": "verified_quote",
    },
    "california_mobile_home": {
        "excerptText": "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons.",
        "proposition": "Reasonable accommodation may require landlords to shoulder reasonable financial burdens.",
        "court": "9th Cir.",
        "year": "1994",
        "pincite": "1416",
        "sourceUrl": "https://law.justia.com/cases/federal/appellate-courts/F3/29/1413/479940/",
        "excerptKind": "verified_quote",
    },
    "mcgary": {
        "excerptText": "The lien the City put on McGary's house prevents the full use and enjoyment of his property.",
        "proposition": "Housing-related financial burdens can impair the full use and enjoyment of a dwelling.",
        "court": "9th Cir.",
        "year": "2004",
        "pincite": "1265",
        "sourceUrl": "https://law.justia.com/cases/federal/appellate-courts/F3/386/1259/632471/",
        "excerptKind": "verified_quote",
    },
    "hud_joint_statement": {
        "excerptText": "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling.",
        "proposition": "Equal use and enjoyment may require necessary accommodation changes.",
        "court": "HUD/DOJ",
        "year": "2004",
        "pincite": "Question 1, p. 2",
        "sourceUrl": "https://www.justice.gov/crt/about/hce/joint_statement_ra.pdf",
        "excerptKind": "verified_quote",
    },
    "cfr_982_316": {
        "excerptText": "The PHA must approve a live-in aide if needed as a reasonable accommodation.",
        "proposition": "A PHA must approve a live-in aide when needed as a reasonable accommodation.",
        "court": "24 C.F.R.",
        "year": "current",
        "pincite": "(a)",
        "sourceUrl": "https://www.law.cornell.edu/cfr/text/24/982.316",
        "excerptKind": "verified_quote",
    },
}

FINDING_TO_TARGETS = {
    "necessary": {
        "nodes": ["necessary"],
        "edges": [
            "sleep_interruption->necessary",
            "work_interference->necessary",
            "caregiving_impairment->necessary",
            "privacy_loss->necessary",
        ],
    },
    "reasonable": {
        "nodes": ["reasonable"],
        "edges": [
            "medical_verification->reasonable",
            "necessary->reasonable",
            "undue_burden->reasonable",
            "fundamental_alteration->reasonable",
        ],
    },
    "dutyToGrant": {
        "nodes": ["duty_to_grant"],
        "edges": [
            "disabled_tenant->duty_to_grant",
            "needs_live_in_aide->duty_to_grant",
            "requested_separate_bedroom->duty_to_grant",
            "reasonable->duty_to_grant",
        ],
    },
    "constructiveDenial": {
        "nodes": ["constructive_denial", "not_effective"],
        "edges": [
            "approved_aide_in_principle->constructive_denial",
            "denied_separate_bedroom->constructive_denial",
            "not_effective->constructive_denial",
            "denied_separate_bedroom->not_effective",
            "sleep_interruption->not_effective",
        ],
    },
    "violation": {
        "nodes": ["violation"],
        "edges": [
            "duty_to_grant->violation",
            "denied_separate_bedroom->violation",
            "constructive_denial->violation",
        ],
    },
}


def dependency_graph_payload(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    return {
        "branch": result["branch"],
        "activeOutcome": "violation" if result["outcome"]["violation"] else "no_violation",
        "nodes": DEPENDENCY_NODES,
        "edges": DEPENDENCY_EDGES,
    }


def build_dependency_citations_jsonld(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    payload = dependency_graph_payload(case_payload)
    authorities = {item["id"]: item for item in case_payload.get("authorities", [])}
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

    seen_authorities = set()
    seen_excerpts = set()
    for bucket, authority_refs in result.get("authoritySupport", {}).items():
        targets = FINDING_TO_TARGETS.get(bucket, {"nodes": [], "edges": []})
        for authority_ref in authority_refs:
            authority = authorities.get(authority_ref["id"], {})
            authority_id = authority_ref["id"]
            authority_node_id = f"authority:{authority_id}"
            excerpt_node_id = f"excerpt:{authority_id}"
            grounding = AUTHORITY_GROUNDING.get(
                authority_id,
                {
                    "excerptText": authority.get("notes", "Authority grounding summary unavailable."),
                    "proposition": authority.get("notes", "Authority proposition unavailable."),
                    "excerptKind": authority.get("excerptKind", "paraphrase"),
                    "fitKind": infer_fit_kind(authority),
                    "sourceUrl": authority.get("sourceUrl"),
                    "court": authority.get("court"),
                    "year": authority.get("year"),
                    "pincite": authority.get("pincite"),
                },
            )
            grounding = {
                "excerptText": authority.get("excerptText", grounding.get("excerptText", authority.get("notes", "Authority grounding summary unavailable."))),
                "proposition": authority.get("proposition", grounding.get("proposition", authority.get("notes", "Authority proposition unavailable."))),
                "excerptKind": authority.get("excerptKind", grounding.get("excerptKind", "paraphrase")),
                "fitKind": authority.get("fitKind", grounding.get("fitKind", infer_fit_kind(authority))),
                "sourceUrl": authority.get("sourceUrl", grounding.get("sourceUrl")),
                "court": authority.get("court", grounding.get("court", "")),
                "year": authority.get("year", grounding.get("year", "")),
                "pincite": authority.get("pincite", grounding.get("pincite", "")),
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
                        "court": grounding.get("court"),
                        "year": grounding.get("year"),
                        "pincite": grounding.get("pincite"),
                        "sourceUrl": grounding.get("sourceUrl"),
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
                        "excerptKind": grounding.get("excerptKind", "paraphrase"),
                        "fitKind": grounding.get("fitKind", infer_fit_kind(authority)),
                        "court": grounding.get("court"),
                        "year": grounding.get("year"),
                        "pincite": grounding.get("pincite"),
                        "sourceUrl": grounding.get("sourceUrl"),
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
            "authorityExcerpt": {"@id": "https://example.org/legal/authorityExcerpt", "@type": "@id"},
            "excerptText": "https://example.org/legal/excerptText",
            "proposition": "https://example.org/legal/proposition",
            "excerptKind": "https://example.org/legal/excerptKind",
            "supportKind": "https://example.org/legal/supportKind",
            "findingBucket": "https://example.org/legal/findingBucket",
            "target": {"@id": "https://example.org/legal/target", "@type": "@id"},
        },
        "@graph": graph,
    }
