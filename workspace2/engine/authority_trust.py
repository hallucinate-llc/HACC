#!/usr/bin/env python3
"""Authority trust helpers shared across exported artifacts."""

from __future__ import annotations

from typing import Any, Dict


def build_authority_trust_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    authorities = payload.get("authorities", [])
    verified = sum(1 for item in authorities if item.get("excerptKind") == "verified_quote")
    paraphrase = sum(1 for item in authorities if item.get("excerptKind") == "paraphrase")
    missing = max(0, len(authorities) - verified - paraphrase)

    if paraphrase == 0 and missing == 0:
        severity = "info"
        label = "fully_verified"
        advisory = "All currently attached authority support is marked as verified_quote."
    elif paraphrase >= verified:
        severity = "warning"
        label = "paraphrase_heavy"
        advisory = (
            "This case relies heavily on paraphrase support, so downstream consumers should present the authority grounding as lower-trust."
        )
    else:
        severity = "warning"
        label = "mixed_support"
        advisory = (
            "This case mixes verified quotes with paraphrase support, so downstream consumers should distinguish direct support from fallback grounding."
        )

    return {
        "authorityCount": len(authorities),
        "verifiedQuoteCount": verified,
        "paraphraseCount": paraphrase,
        "missingCount": missing,
        "severity": severity,
        "label": label,
        "advisory": advisory,
    }
