"""Tool: classify_eu_ai_act.

Classifies an AI deployment scenario into an EU AI Act risk tier and
returns the regulatory obligations and a citation to the relevant
article or annex. Classification is rule-based and deterministic.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "eu_ai_act_tiers.json"

_TIER_PRIORITY = ["prohibited", "high_risk", "limited_risk", "minimal_risk"]


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    with _DATA_PATH.open() as f:
        return json.load(f)


def _tier_for(scenario: str) -> tuple[str, list[str]]:
    """Return (tier_name, matched_triggers). Highest-severity match wins."""
    text = scenario.lower()
    rules = _load().get("classification_rules", [])
    by_tier = {r["tier"]: r.get("any_of", []) for r in rules}
    for tier in _TIER_PRIORITY[:-1]:
        triggers = by_tier.get(tier, [])
        hits = [t for t in triggers if t in text]
        if hits:
            return tier, hits
    return "minimal_risk", []


def classify(scenario: str) -> dict[str, Any]:
    """Classify ``scenario`` into an EU AI Act tier.

    Args:
        scenario: free-text description of the proposed AI deployment.

    Returns:
        ``{"tier": "<prohibited|high_risk|limited_risk|minimal_risk>",
           "rationale": str, "obligations": [str, ...],
           "annex_reference": str, "matched_triggers": [str, ...]}``.

        The classification is rule-based and is intended to surface the
        applicable regime — not to substitute for legal counsel. The
        ``rationale`` explains which trigger fired and why; the calling
        LLM should treat it as a starting point for analysis.
    """
    tier, triggers = _tier_for(scenario)
    data = _load()
    tiers = data.get("tiers", {})
    tier_data = tiers.get(tier, {})

    if tier == "minimal_risk":
        rationale = (
            "No high-severity triggers matched in the supplied scenario. "
            "Treat as minimal risk under the EU AI Act; existing horizontal "
            "law still applies. Re-run this check if the scope changes."
        )
    else:
        rationale = (
            f"Scenario matched trigger(s) associated with the '{tier}' tier: "
            f"{', '.join(triggers)}."
        )

    return {
        "tier": tier,
        "rationale": rationale,
        "obligations": tier_data.get("obligations", []),
        "annex_reference": tier_data.get("annex_reference", ""),
        "tier_description": tier_data.get("description", ""),
        "matched_triggers": triggers,
        "source_version": data.get("version", ""),
        "source_url": data.get("source", ""),
    }
