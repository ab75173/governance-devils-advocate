"""Tool: lookup_nist_ai_rmf.

Searches a curated subset of the NIST AI Risk Management Framework
(AI 100-1) and the Generative AI Profile (AI 600-1) and returns
matching subcategories with implementation guidance.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "nist_ai_rmf.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    with _DATA_PATH.open() as f:
        return json.load(f)


def _matches(entry: dict[str, Any], q: str) -> bool:
    if not q:
        return True
    haystacks = [
        entry.get("function", ""),
        entry.get("category", ""),
        entry.get("subcategory", ""),
        entry.get("text", ""),
        entry.get("guidance", ""),
        " ".join(entry.get("keywords", [])),
    ]
    blob = " ".join(haystacks).lower()
    return all(term in blob for term in q.lower().split())


def lookup(query: str) -> dict[str, Any]:
    """Return NIST AI RMF entries matching ``query``.

    Args:
        query: free-text query. All whitespace-separated terms must appear
            (case-insensitive) somewhere in the entry's function name,
            category, subcategory, text, guidance, or keyword list.

    Returns:
        ``{"matches": [...], "source_version": "...", "source_url": "..."}``.
        ``matches`` is a list of entries, each with ``function``, ``category``,
        ``subcategory``, ``text``, and ``guidance`` fields.
    """
    data = _load()
    entries: list[dict[str, Any]] = data.get("entries", [])
    matched = [
        {
            "function": e["function"],
            "category": e["category"],
            "subcategory": e["subcategory"],
            "text": e["text"],
            "guidance": e["guidance"],
        }
        for e in entries
        if _matches(e, query)
    ]
    return {
        "matches": matched,
        "source_version": data.get("version", ""),
        "source_url": data.get("source", ""),
    }
