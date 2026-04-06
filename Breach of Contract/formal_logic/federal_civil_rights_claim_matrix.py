"""
Generate a federal civil-rights claim matrix across HACC / Quantum / related theories.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List


CURRENT_DATE = date(2026, 4, 5)
OUTPUT_DIR = Path("/home/barberb/HACC/Breach of Contract/outputs")


CLAIMS: List[Dict[str, Any]] = [
    {
        "claimId": "claim_fha_retaliation_interference",
        "claimLabel": "Fair Housing Act retaliation / interference",
        "strongestDefendants": ["HACC", "Quantum"],
        "overallStrength": "strongest_now",
        "bestVehicle": "FED case and broader federal complaint",
        "why": "Protected complaints, alleged nonprocessing, continued burdens, and later housing pressure are already tied to concrete housing events.",
        "mainEvidence": [
            "Preserved February 26, March 2, and March 9 discrimination / civil-rights complaint emails.",
            "Blossom nonprocessing allegations preserved in message-support materials.",
            "Post-complaint notice, documentation, voucher, and relocation pressure sequence.",
        ],
        "mainLimiters": [
            "Cleaner causation proof would still help.",
            "Internal communications referencing the complaints would materially strengthen motive.",
        ],
    },
    {
        "claimId": "claim_1981_quantum",
        "claimLabel": "42 U.S.C. § 1981 contracting discrimination",
        "strongestDefendants": ["Quantum"],
        "overallStrength": "plausible_supported_but_needs_more",
        "bestVehicle": "federal complaint or amended broader civil-rights complaint",
        "why": "Quantum is a private actor in the Blossom housing-contracting path, and the record supports receipt plus nonprocessing/nontransmission of the application.",
        "mainEvidence": [
            "Ferron's January 26, 2026 statement that the packet was submitted to Quantum staff but not provided to HACC.",
            "Blossom path processed through the HACC PBV waitlist.",
            "Written race-discrimination complaints tied to Blossom nonprocessing.",
            "Benjamin's statement that Quantum falsely claimed the application had not been provided.",
        ],
        "mainLimiters": [
            "Comcast but-for causation requirement.",
            "Need for comparator / pipeline proof showing similarly situated households moved forward.",
            "Need for intake logs, criteria, or other direct evidence of unequal handling.",
        ],
    },
    {
        "claimId": "claim_1983_first_amendment_retaliation",
        "claimLabel": "42 U.S.C. § 1983 First Amendment retaliation",
        "strongestDefendants": ["HACC"],
        "overallStrength": "strongest_now",
        "bestVehicle": "federal complaint and narrower FED-supportive framing",
        "why": "The record already preserves civil-rights complaints and intent-to-sue language followed by continued housing-related adverse conduct.",
        "mainEvidence": [
            "Protected complaint emails to HACC and county-linked staff.",
            "Message-level support for Civil Rights Act / intent-to-sue language.",
            "Chronology showing later notice, voucher, documentation, and relocation problems after protected activity.",
        ],
        "mainLimiters": [
            "Direct evidence linking the complaints to a specific later decision would strengthen the claim.",
        ],
    },
    {
        "claimId": "claim_1983_equal_protection_or_1981_routed",
        "claimLabel": "42 U.S.C. § 1983 race discrimination / equal protection / § 1981-routed theory",
        "strongestDefendants": ["HACC"],
        "overallStrength": "plausible_but_needs_more",
        "bestVehicle": "broader federal complaint, not a narrow FED filing",
        "why": "HACC may still face race-discrimination exposure, but the direct § 1981 route is structurally weaker for a state actor and the better path is generally through § 1983 or related federal vehicles.",
        "mainEvidence": [
            "Written race-discrimination complaints.",
            "Public Clackamas / HACC SHS documents stating that services and housing should be provided to Black, Indigenous and people of color at higher rates than their representation among those experiencing homelessness.",
            "SHS / RLRA race-equity policy environment.",
            "HACC's placement and relocation role in the Blossom path.",
        ],
        "mainLimiters": [
            "Need stronger proof that HACC itself engaged in intentional unequal treatment in this pipeline.",
            "Need comparator evidence or direct statements.",
            "Need to avoid overrelying on policy language alone.",
        ],
    },
    {
        "claimId": "claim_title_vi_race_discrimination",
        "claimLabel": "Title VI race discrimination",
        "strongestDefendants": ["HACC", "county-linked funded actors"],
        "overallStrength": "plausible_but_needs_more",
        "bestVehicle": "administrative complaint or broader federal complaint",
        "why": "The record shows a federally funded housing context, race-discrimination complaints, and a race-conscious policy environment, but it still needs a stronger funded-program and intentional-discrimination tie.",
        "mainEvidence": [
            "Public Clackamas / HACC SHS documents containing the exact race-conscious outcome-goal quote.",
            "RLRA / SHS / Metro policy context.",
            "Written race-discrimination complaints.",
            "Blossom nonprocessing and referral-pipeline allegations.",
        ],
        "mainLimiters": [
            "Need proof the specific Blossom / relocation path was federally funded in the relevant way.",
            "Need stronger intent or comparator evidence.",
            "Need actual implementation criteria or certification documents.",
        ],
    },
    {
        "claimId": "claim_fha_race_steering",
        "claimLabel": "Fair Housing Act race steering / unequal treatment",
        "strongestDefendants": ["HACC", "Quantum"],
        "overallStrength": "plausible_but_needs_more",
        "bestVehicle": "federal complaint or HUD complaint",
        "why": "The current record supports written complaints of race discrimination and steering, plus allegations that the housing opportunity was handled on unequal terms.",
        "mainEvidence": [
            "Written steering and discrimination complaints.",
            "Application accepted/received then stalled or not transmitted.",
            "Supportive-services and referral environment as motive context, including the published SHS outcome goal.",
        ],
        "mainLimiters": [
            "Need comparators, referral lists, placement logs, or direct statements.",
        ],
    },
    {
        "claimId": "claim_fca_civil_rights_fraud",
        "claimLabel": "False Claims Act / civil-rights-fraud theory",
        "strongestDefendants": ["HACC", "county-linked funded actors", "possibly contractors"],
        "overallStrength": "early_stage_only",
        "bestVehicle": "separate research / qui tam / DOJ-facing framework, not current FED filing",
        "why": "Current DOJ framing exists, but the record does not yet show the needed certification layer or a clear false statement tied to payment or funding.",
        "mainEvidence": [
            "Race-conscious policy environment including public SHS outcome-goal documents.",
            "Discrimination complaints.",
            "Need for SHS / RLRA / Metro contracts and nondiscrimination certifications already identified in discovery plans.",
        ],
        "mainLimiters": [
            "Need grant agreements, certifications, assurances, and implementation evidence.",
            "Need proof of knowing falsity or materially misleading compliance representations.",
        ],
    },
]


def build_matrix() -> Dict[str, Any]:
    return {
        "metadata": {
            "reportId": "federal_civil_rights_claim_matrix_001",
            "generatedAt": CURRENT_DATE.isoformat(),
        },
        "claims": CLAIMS,
        "rankedTakeaways": [
            "Strongest immediate federal-civil-rights targets: FHA retaliation/interference, § 1983 retaliation against HACC, and § 1981 against Quantum.",
            "Best race-discrimination claim against Quantum: § 1981 tied to the Blossom contracting opportunity.",
            "Best race-discrimination path against HACC: usually through § 1983 / Title VI / FHA rather than a direct standalone § 1981 damages claim.",
            "The SHS quote about serving Black, Indigenous, and people of color at higher rates than representation is now grounded to public Clackamas / HACC documents, but it remains motive, notice, and discovery context unless and until comparator and operating-criteria records are obtained.",
        ],
        "bestNextDiscovery": [
            "Quantum Blossom intake logs and status history.",
            "Comparator records showing which displaced households moved forward in Blossom during the same period.",
            "HACC referral and relocation tracking records for Blossom and related replacement-housing paths.",
            "SHS / RLRA / Metro contracts, assurances, and nondiscrimination certifications.",
            "Any criteria, scoring, prioritization, or race-disaggregated dashboards actually used operationally.",
        ],
    }


def render_markdown(matrix: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# Federal Civil Rights Claim Matrix",
        "",
        "## Ranked Takeaways",
        "",
    ]
    for item in matrix["rankedTakeaways"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claims", ""])
    for claim in matrix["claims"]:
        lines.append(f"### {claim['claimLabel']}")
        lines.append("")
        lines.append(f"- Claim ID: `{claim['claimId']}`")
        lines.append(f"- Strongest defendants: {', '.join(claim['strongestDefendants'])}")
        lines.append(f"- Current strength: `{claim['overallStrength']}`")
        lines.append(f"- Best vehicle: {claim['bestVehicle']}")
        lines.append(f"- Why: {claim['why']}")
        lines.append("- Main evidence:")
        for item in claim["mainEvidence"]:
            lines.append(f"  - {item}")
        lines.append("- Main limiters:")
        for item in claim["mainLimiters"]:
            lines.append(f"  - {item}")
        lines.append("")
    lines.extend(["## Best Next Discovery", ""])
    for item in matrix["bestNextDiscovery"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs() -> Dict[str, Path]:
    matrix = build_matrix()
    outputs = {
        "json": OUTPUT_DIR / "federal_civil_rights_claim_matrix.json",
        "markdown": OUTPUT_DIR / "federal_civil_rights_claim_matrix.md",
    }
    outputs["json"].write_text(json.dumps(matrix, indent=2) + "\n")
    outputs["markdown"].write_text(render_markdown(matrix))
    return outputs


def main() -> int:
    for path in write_outputs().values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
