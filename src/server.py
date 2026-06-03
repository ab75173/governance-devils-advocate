"""FastMCP server entrypoint for the AI Governance Devil's Advocate.

Exposes five tools to any MCP client over Streamable HTTP at ``/mcp``.

Architectural principle (do not violate): tools return structured
knowledge and templates only. The calling LLM does all reasoning.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastmcp import FastMCP

from .tools import ethics, eu_ai_act, memo, mitre_atlas, nist_rmf

log = logging.getLogger("governance-devils-advocate")

mcp: FastMCP = FastMCP(
    name="AI Governance Devil's Advocate",
    instructions=(
        "Use this server to look up AI-governance knowledge and format a "
        "decision memo while reasoning through a proposed AI deployment. "
        "Typical chain for a new scenario: classify_eu_ai_act → "
        "lookup_nist_ai_rmf (governance and measurement subcategories) → "
        "lookup_mitre_atlas (relevant techniques and mitigations) → "
        "get_ethical_framework (call once per framework you want to apply) → "
        "format_decision_memo. The server returns structured data; you do "
        "the reasoning."
    ),
)


@mcp.tool
def lookup_nist_ai_rmf(query: str) -> dict[str, Any]:
    """Search the NIST AI Risk Management Framework (AI 100-1) and Generative AI Profile (AI 600-1).

    Use this to surface relevant subcategories — for example, when you need
    governance, mapping, measurement, or management guidance for a proposed
    deployment. Returns one entry per matching subcategory with the
    implementation guidance text.

    Args:
        query: free-text query. Examples: ``"security"``, ``"human oversight"``,
            ``"post-deployment monitoring"``, ``"generative"``.

    Returns:
        ``{"matches": [...], "source_version": str, "source_url": str}`` —
        each match is ``{function, category, subcategory, text, guidance}``.
    """
    log.info("lookup_nist_ai_rmf", extra={"query": query})
    return nist_rmf.lookup(query)


@mcp.tool
def lookup_mitre_atlas(query: str) -> dict[str, Any]:
    """Search MITRE ATLAS for adversarial-ML techniques and mitigations.

    Curated subset focused on LLM-integrated systems: prompt injection,
    jailbreak, data leakage, tool/plugin compromise, and the canonical
    mitigations (input detection, output filtering, least-privilege tool
    permissions, query rate-limiting).

    Args:
        query: free-text query. Examples: ``"prompt injection"``,
            ``"data leakage"``, ``"tool compromise"``, ``"AML.T0051"``.

    Returns:
        ``{"matches": [...], "source_version": str, "source_url": str}`` —
        each match is ``{id, type, name, tactic, description, [mitigations]}``.
    """
    log.info("lookup_mitre_atlas", extra={"query": query})
    return mitre_atlas.lookup(query)


@mcp.tool
def classify_eu_ai_act(scenario: str) -> dict[str, Any]:
    """Classify an AI deployment scenario into an EU AI Act risk tier.

    Rule-based and deterministic. The classification surfaces the applicable
    regime — it is not a substitute for legal counsel. The calling LLM
    should treat the result as a starting point for its analysis.

    Args:
        scenario: free-text description of the proposed AI deployment.

    Returns:
        ``{"tier": "prohibited"|"high_risk"|"limited_risk"|"minimal_risk",
        "rationale": str, "obligations": [str], "annex_reference": str,
        "tier_description": str, "matched_triggers": [str],
        "source_version": str, "source_url": str}``.
    """
    log.info("classify_eu_ai_act", extra={"scenario_len": len(scenario or "")})
    return eu_ai_act.classify(scenario)


@mcp.tool
def get_ethical_framework(framework: str) -> dict[str, Any]:
    """Return a structured analytical scaffold for a philosophical framework.

    Feed the returned scaffold back into your own reasoning as a prompt — the
    server does not generate arguments itself. Call this tool once per
    framework you want to apply to a scenario.

    Args:
        framework: one of ``"utilitarian"``, ``"deontological"``,
            ``"virtue_ethics"``, ``"care_ethics"``, ``"rawlsian"``.

    Returns:
        ``{"framework": str, "tradition": str, "core_question": str,
        "analytical_steps": [str], "key_considerations": [str],
        "typical_failure_modes": [str]}``.
    """
    log.info("get_ethical_framework", extra={"framework": framework})
    return ethics.get(framework)


@mcp.tool
def format_decision_memo(
    scenario: str,
    pro_arguments: list[str],
    con_arguments: list[str],
    frameworks_cited: list[str],
    recommendation: str,
) -> str:
    """Render a Markdown decision memo from arguments you have already produced.

    Pure formatting — no analysis. Sections: Scenario Summary, Analysis
    (For / Against), Frameworks Cited, Recommendation.

    Args:
        scenario: short statement of the deployment under review.
        pro_arguments: arguments in favor of the deployment (one per item).
        con_arguments: arguments against the deployment (one per item).
        frameworks_cited: governance or ethical frameworks consulted
            (e.g., ``"NIST AI RMF GOVERN-1.1"``, ``"EU AI Act high-risk"``,
            ``"utilitarian"``).
        recommendation: the recommendation you have decided on.

    Returns:
        Markdown string ready to display or save.
    """
    log.info(
        "format_decision_memo",
        extra={
            "pros": len(pro_arguments or []),
            "cons": len(con_arguments or []),
            "cites": len(frameworks_cited or []),
        },
    )
    return memo.format_memo(
        scenario=scenario,
        pro_arguments=pro_arguments,
        con_arguments=con_arguments,
        frameworks_cited=frameworks_cited,
        recommendation=recommendation,
    )


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
    )


def main() -> None:
    _configure_logging()
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    log.info("Starting governance-devils-advocate on %s:%d/mcp", host, port)
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        path="/mcp",
    )


if __name__ == "__main__":
    main()
