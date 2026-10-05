import hashlib
import math

import yaml
from langchain.tools import tool, ToolRuntime
from langchain_typesafe import Score

from tools.jev_classifier import (
    classifier,
    CONFIDENCE_THRESHOLD,
    all_verbatim,
    REFERENCE_DIR,
)


def _load(name: str):
    raw = (REFERENCE_DIR / name).read_text(encoding="utf-8")
    return yaml.safe_load(raw), hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


# ───────── 1. Official severity: scoring.md §9.1 (Severity 1–5) ─────────
SCALE, SCALE_FP = _load("severity-scale.yaml")
LEVELS = SCALE["levels"]
APPROVAL_AT = int(SCALE["human_approval_required_at_or_above"])

if [lv["severity"] for lv in LEVELS] != [1, 2, 3, 4, 5]:
    raise ValueError("severity-scale.yaml: levels must be severities 1..5 in order")
if not 1 <= APPROVAL_AT <= 5:
    raise ValueError("severity-scale.yaml: human_approval_required_at_or_above must be 1..5")

SEVERITY_QUESTION = Score(
    instructions=SCALE["instructions"],
    # Each level: its definition plus the "When to Apply" examples from §9.1
    criteria=[{"what": lv["what"], "examples": lv["examples"]} for lv in LEVELS],
)

# ───────── 2. Calibration reference: Appendix D (severity-matrix.yaml) ─────────
RUBRIC, RUBRIC_FP = _load("severity-matrix.yaml")
DIMENSIONS = RUBRIC["dimensions"]
BANDS = RUBRIC["bands"]
FLOOR = RUBRIC["floor_rule"]
BAND_NAMES = [b["name"] for b in BANDS]
EXPECTED_LEVELS = {"decision_impact": 4, "spread": 5, "persistence": 4}

for key, count in EXPECTED_LEVELS.items():
    scores = [lv["score"] for lv in DIMENSIONS[key]["levels"]]
    if scores != list(range(1, count + 1)):
        raise ValueError(f"severity-matrix.yaml: {key} must have scores 1..{count}, found {scores}")
if BAND_NAMES != ["Low", "Medium", "High", "Critical"]:
    raise ValueError(f"severity-matrix.yaml: unexpected bands {BAND_NAMES}")


def _dimension_question(key: str) -> Score:
    dim = DIMENSIONS[key]
    return Score(instructions=dim["question"],
                 criteria=[lv["meaning"] for lv in dim["levels"]])


def _band(score: int, decision_impact_name: str) -> tuple[str, bool]:
    band = next(b["name"] for b in BANDS if b["max"] is None or score <= b["max"])
    if (decision_impact_name == FLOOR["when_decision_impact"]
            and BAND_NAMES.index(band) < BAND_NAMES.index(FLOOR["minimum_band"])):
        return FLOOR["minimum_band"], True
    return band, False


def _ranked(probabilities: dict) -> list:
    return sorted(probabilities, key=probabilities.get, reverse=True)


# ───────── 3. The tool ─────────
@tool(parse_docstring=True)
def rate_severity(requirement: str, evidence: str, expected: str,
                  observed: str, runtime: ToolRuntime) -> dict:
    """
    Rate the severity of one finding using Jev. The official severity is the
    1–5 rating defined in scoring.md §9.1; the three Appendix D dimensions are
    returned as calibration reference only. Use the results exactly as returned.

    Args:
        requirement: The baseline clause, quoted exactly.
        evidence: Exact, unedited quotes from the supplied evidence, one quote per line (one line per failing record for a consolidated gap).
        expected: What the clause requires, in a few words.
        observed: What the evidence shows, in a few words.
    """
    if not all_verbatim(evidence, runtime):
        return {
            "error": "evidence_not_verbatim",
            "message": "Quote the evidence exactly and call again.",
            "evidence_verified": False,
        }

    variance = f"Required: {expected}. Observed: {observed}."
    state = {"requirement": requirement, "evidence": evidence, "variance": variance}

    # One Jev call: the official severity plus the three calibration dimensions
    questions = {"severity": SEVERITY_QUESTION}
    questions.update({key: _dimension_question(key) for key in EXPECTED_LEVELS})
    response = classifier.invoke({"state": state, "questions": questions})

    # a. Official severity (§9.1): the most probable level
    sev = response.scores["severity"]
    order = _ranked(sev.probabilities)
    level = LEVELS[order[0]]
    runner = LEVELS[order[1]] if len(order) > 1 else None
    approval_required = level["severity"] >= APPROVAL_AT

    # b. Calibration reference (Appendix D), computed exactly as before
    calibration, levels_chosen = {}, {}
    for key in EXPECTED_LEVELS:
        answer = response.scores[key]
        chosen = DIMENSIONS[key]["levels"][_ranked(answer.probabilities)[0]]
        levels_chosen[key] = chosen
        calibration[key] = chosen["name"]
        calibration[f"{key}_score"] = chosen["score"]
        calibration[f"{key}_confidence"] = answer.confidence
    cal_score = math.prod(lv["score"] for lv in levels_chosen.values())
    cal_band, floor_applied = _band(cal_score, levels_chosen["decision_impact"]["name"])
    calibration.update({
        "band": cal_band,
        "score": cal_score,
        "floor_applied": floor_applied,
        "rubric": {"version": str(RUBRIC["version"]), "fingerprint": RUBRIC_FP},
    })

    return {
        # Official severity: what the Manifest records
        "severity": level["severity"],
        "severity_label": level["label"],
        "severity_confidence": sev.confidence,
        "severity_probabilities": {LEVELS[i]["label"]: p for i, p in sev.probabilities.items()},
        "severity_runner_up": None if runner is None else {
            "severity": runner["severity"],
            "label": runner["label"],
            "probability": sev.probabilities[order[1]],
            "approval_required": runner["severity"] >= APPROVAL_AT,
        },
        "human_approval_required": approval_required,
        "needs_review": sev.confidence < CONFIDENCE_THRESHOLD,
        "threshold_used": CONFIDENCE_THRESHOLD,
        # Calibration reference: shown, never parsed
        "calibration": calibration,
        "severity_scale": {"source": SCALE["source"], "version": str(SCALE["version"]),
                           "fingerprint": SCALE_FP},
        "evidence_verified": True,
        "variance_sent": variance,
        "classified_by": response.model,
    }