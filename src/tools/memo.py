"""Tool: format_decision_memo.

Renders a clean Markdown decision memo from arguments the calling LLM
has already produced. Pure formatting — no analysis or generation.
"""

from __future__ import annotations


def _bullets(items: list[str]) -> str:
    if not items:
        return "_(none provided)_"
    return "\n".join(f"- {item.strip()}" for item in items if item and item.strip())


def format_memo(
    scenario: str,
    pro_arguments: list[str],
    con_arguments: list[str],
    frameworks_cited: list[str],
    recommendation: str,
) -> str:
    """Render a Markdown decision memo.

    Args:
        scenario: short statement of the deployment under review.
        pro_arguments: arguments in favor of the deployment (one per item).
        con_arguments: arguments against the deployment (one per item).
        frameworks_cited: governance or ethical frameworks consulted
            (e.g., ``"NIST AI RMF GOVERN-1.1"``, ``"EU AI Act high-risk"``,
            ``"utilitarian"``).
        recommendation: the final recommendation the LLM has decided on.

    Returns:
        Markdown string ready to display or save.
    """
    pros = _bullets(pro_arguments)
    cons = _bullets(con_arguments)
    cites = _bullets(frameworks_cited)
    rec = (recommendation or "").strip() or "_(no recommendation provided)_"
    summary = (scenario or "").strip() or "_(no scenario provided)_"

    return (
        "# AI Governance Decision Memo\n"
        "\n"
        "## Scenario Summary\n"
        f"{summary}\n"
        "\n"
        "## Analysis\n"
        "\n"
        "### Arguments For\n"
        f"{pros}\n"
        "\n"
        "### Arguments Against\n"
        f"{cons}\n"
        "\n"
        "## Frameworks Cited\n"
        f"{cites}\n"
        "\n"
        "## Recommendation\n"
        f"{rec}\n"
    )
