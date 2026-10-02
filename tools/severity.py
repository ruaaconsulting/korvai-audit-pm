import hashlib
import math

import yaml
from langchain.tools import tool, ToolRuntime
from langchain_typesafe import Score

from tools.jev_classifier import (
    classifier,
    CONFIDENCE_THRESHOLD,
    normalize,
    supplied_text,
    REFERENCE_DIR,
)

# ───────── 1. Load the rubric once, at startup ─────────
_RAW = (REFERENCE_DIR / "severity-matrix.yaml").read_text(encoding="utf-8")
RUBRIC = yaml.safe_load(_RAW)

SEVERITY_VERSION = str(RUBRIC["version"])
SEVERITY_FINGERPRINT = hashlib.sha256(_RAW.encode("utf-8")).hexdigest()[:12]
DIMENSIONS = RUBRIC["dimensions"]
BANDS = RUBRIC["bands"]
FLOOR = RUBRIC["floor_rule"]
BAND_NAMES = [b["name"] for b in BANDS]

# ───────── 2. Startup checks: refuse to run on a malformed rubric ─────────
EXPECTED_LEVELS = {"decision_impact": 4, "spread": 5, "persistence": 4}

for key, count in EXPECTED_LEVELS.items():
    scores = [level["score"] for level in DIMENSIONS[key]["levels"]]
    if scores != list(range(1, count + 1)):
        raise ValueError(f"severity-matrix.yaml: {key} must have scores 1..{count}, found {scores}")

if BAND_NAMES != ["Low", "Medium", "High", "Critical"]:
    raise ValueError(f"severity-matrix.yaml: unexpected bands {BAND_NAMES}")

if FLOOR["minimum_band"] not in BAND_NAMES:
    raise ValueError("severity-matrix.yaml: floor_rule.minimum_band is not a band name")


# ───────── 3. Small helpers ─────────
def _question(key: str) -> Score:
    """One Jev Score question: the dimension's question, levels as ordered descriptions."""
    dim = DIMENSIONS[key]
    return Score(
        instructions=dim["question"],
        criteria=[level["meaning"] for level in dim["levels"]],
    )


def _most_probable_level(answer, key: str) -> dict:
    """The level Jev found most probable (not the rounded score)."""
    best_index = max(answer.probabilities, key=answer.probabilities.get)
    return DIMENSIONS[key]["levels"][best_index]


def _band(score: int, decision_impact_name: str) -> tuple[str, bool]:
    """Band from the score, then the floor rule."""
    band = next(b["name"] for b in BANDS if b["max"] is None or score <= b["max"])
    if (decision_impact_name == FLOOR["when_decision_impact"]
            and BAND_NAMES.index(band) < BAND_NAMES.index(FLOOR["minimum_band"])):
        return FLOOR["minimum_band"], True
    return band, False


# ───────── 4. The tool ─────────
@tool(parse_docstring=True)
def rate_severity(requirement: str, evidence: str, expected: str,
                  observed: str, runtime: ToolRuntime) -> dict:
    """
    Rate the severity of one audit finding using Jev on three dimensions
    (Decision Impact, Spread, Persistence). The score and band are computed
    by code and are final; use them exactly as returned.

    Args:
        requirement: The baseline clause, quoted exactly.
        evidence: An exact, unedited quote from the supplied evidence.
        expected: What the clause requires, in a few words.
        observed: What the evidence shows, in a few words.
    """
    # a. Verbatim check, same as classify_gap: no Jev call if it fails
    if normalize(evidence) not in supplied_text(runtime):
        return {
            "error": "evidence_not_verbatim",
            "message": "Quote the evidence exactly and call again.",
            "evidence_verified": False,
        }

    variance = f"Required: {expected}. Observed: {observed}."
    state = {"requirement": requirement, "evidence": evidence, "variance": variance}

    # b. One Jev call, three Score questions
    response = classifier.invoke({
        "state": state,
        "questions": {key: _question(key) for key in EXPECTED_LEVELS},
    })

    # c. Jev judges each dimension; code does the arithmetic
    result = {}
    levels = {}
    for key in EXPECTED_LEVELS:
        answer = response.scores[key]
        level = _most_probable_level(answer, key)
        levels[key] = level
        result[key] = level["name"]
        result[f"{key}_confidence"] = answer.confidence
        result[f"{key}_position"] = answer.score
        result[f"{key}_probabilities"] = answer.probabilities

    score = math.prod(level["score"] for level in levels.values())
    band, floor_applied = _band(score, levels["decision_impact"]["name"])

    needs_review = any(
        result[f"{key}_confidence"] < CONFIDENCE_THRESHOLD for key in EXPECTED_LEVELS
    )

    return {
        "severity": band,
        "severity_score": score,
        "floor_applied": floor_applied,
        **result,
        "needs_review": needs_review,
        "threshold_used": CONFIDENCE_THRESHOLD,
        "evidence_verified": True,
        "variance_sent": variance,
        "classified_by": response.model,
        "severity_rubric": {"version": SEVERITY_VERSION, "fingerprint": SEVERITY_FINGERPRINT},
    }