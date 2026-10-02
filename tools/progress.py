from typing import Literal

import yaml
from langchain.tools import tool

from tools.jev_classifier import REFERENCE_DIR

# ───────── Load the stage list from the methodology ─────────
_DOC = yaml.safe_load((REFERENCE_DIR / "audit-stages.yaml").read_text(encoding="utf-8"))
STAGES = _DOC["stages"]
SOURCE_VERSION = str(_DOC.get("source_version", ""))

# The agent may only report stages performed by judgment (0–7).
# Deterministic stages (8–10) belong to code and are never reported by the agent.
JUDGMENT_KEYS = tuple(s["key"] for s in STAGES if s["performed_by"] == "judgment")
if not JUDGMENT_KEYS:
    raise ValueError("audit-stages.yaml: no judgment stages found")

StageKey = Literal[JUDGMENT_KEYS]
_BY_KEY = {s["key"]: s for s in STAGES}


@tool(parse_docstring=True)
def set_stage(stage: StageKey, note: str) -> dict:
    """
    Record that the audit is entering a methodology stage. Call this at the
    start of every stage, in methodology order, before doing that stage's work.

    Args:
        stage: The methodology stage being started.
        note: One short sentence describing what this stage will do in this audit.
    """
    s = _BY_KEY[stage]
    return {
        "stage": stage,
        "number": s["number"],
        "name": s["name"],
        "status": "started",
        "note": note,
        "stages": STAGES,              # the full list, so the UI never hardcodes it
        "source_version": SOURCE_VERSION,
    }