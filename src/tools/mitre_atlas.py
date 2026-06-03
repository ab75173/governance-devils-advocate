"""Tool: lookup_mitre_atlas.

Searches a curated subset of MITRE ATLAS techniques and mitigations
relevant to LLM-integrated systems.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mitre_atlas.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    with _DATA_PATH.open() as f:
        return json.load(f)


def _matches(entry: dict[str, Any], q: str) -> bool:
    if not q:
        return True
    haystacks = [
        entry.get("id", ""),
        entry.get("name", ""),
        entry.get("tactic", ""),
        entry.get("type", ""),
        entry.get("description", ""),
        " ".join(entry.get("keywords", [])),
    ]
    blob = " ".join(haystacks).lower()
    return all(term in blob for term in q.lower().split())


def lookup(query: str) -> dict[str, Any]:
    """Return MITRE ATLAS entries matching ``query``.

    Args:
        query: free-text query matched against the ATLAS id, name, tactic,
            description, and keywords (case-insensitive, all terms must match).

    Returns:
        ``{"matches": [...], "source_url": "..."}``. ``matches`` is a list of
        entries, each with ``id``, ``type`` (``"technique"`` or
        ``"mitigation"``), ``name``, ``tactic``, ``description``, and (for
        techniques) a list of related ``mitigations`` ids.
    """
    data = _load()
    entries: list[dict[str, Any]] = data.get("entries", [])
    matched: list[dict[str, Any]] = []
    for e in entries:
        if not _matches(e, query):
            continue
        out = {
            "id": e["id"],
            "type": e.get("type", ""),
            "name": e["name"],
            "tactic": e.get("tactic", ""),
            "description": e["description"],
        }
        if "mitigations" in e:
            out["mitigations"] = e["mitigations"]
        matched.append(out)
    return {
        "matches": matched,
        "source_version": data.get("version", ""),
        "source_url": data.get("source", ""),
    }
