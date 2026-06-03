"""Tool: get_ethical_framework.

Returns a structured analytical scaffold for one of five philosophical
frameworks. The output is designed to be fed back into the client LLM as
a reasoning prompt — the server does not generate arguments itself.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "ethical_frameworks.json"

SUPPORTED = ("utilitarian", "deontological", "virtue_ethics", "care_ethics", "rawlsian")


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    with _DATA_PATH.open() as f:
        return json.load(f)


def get(framework: str) -> dict[str, Any]:
    """Return the analytical scaffold for ``framework``.

    Args:
        framework: one of ``"utilitarian"``, ``"deontological"``,
            ``"virtue_ethics"``, ``"care_ethics"``, ``"rawlsian"``.

    Returns:
        ``{"framework": ..., "tradition": ..., "core_question": ...,
           "analytical_steps": [...], "key_considerations": [...],
           "typical_failure_modes": [...]}`` for the requested framework.

    Raises:
        ValueError: if ``framework`` is not one of the supported names.
    """
    key = (framework or "").strip().lower()
    frameworks = _load().get("frameworks", {})
    if key not in frameworks:
        raise ValueError(
            f"Unknown framework {framework!r}. Supported: {', '.join(SUPPORTED)}."
        )
    return dict(frameworks[key])
