import hashlib

import yaml
from langchain.tools import tool, ToolRuntime
from langchain_typesafe import Noul, NoulCriteria

from tools.jev_classifier import (
    classifier,
    normalize,
    supplied_text,
    REFERENCE_DIR,
)

# ───────── 1. Load Stage 3 evaluation rules from the methodology file ─────────
_RAW = (REFERENCE_DIR / "conformance.yaml").read_text(encoding="utf-8")
_DOC = yaml.safe_load(_RAW)

CONFORMANCE_VERSION = str(_DOC["version"])
CONFORMANCE_SOURCE = str(_DOC["source"])
CONFORMANCE_FINGERPRINT = hashlib.sha256(_RAW.encode("utf-8")).hexdigest()[:12]

_Q = _DOC["criterion_evaluation"]
SATISFIED_AT = float(_DOC["decision"]["satisfied_at_or_above"])
NOT_SATISFIED_AT = float(_DOC["decision"]["not_satisfied_at_or_below"])

# ───────── 2. Startup checks: refuse to run on a malformed file ─────────
for field in ("instructions", "true", "false"):
    if not str(_Q.get(field, "")).strip():
        raise ValueError(f"conformance.yaml: criterion_evaluation.{field} is empty")
if not (0.0 <= NOT_SATISFIED_AT < SATISFIED_AT <= 1.0):
    raise ValueError("conformance.yaml: thresholds must satisfy 0 ≤ not_satisfied < satisfied ≤ 1")

# The single Jev question, built entirely from the file
QUESTION = Noul(
    instructions=_Q["instructions"],
    criteria=NoulCriteria(true=_Q["true"], false=_Q["false"]),
)


# ───────── 3. The tool ─────────
@tool(parse_docstring=True)
def check_criterion(clause_id: str, requirement: str, artifact_id: str, item_id: str,
                    evidence: str, runtime: ToolRuntime,
                    evaluation_method: str = "") -> dict:
    """
    Stage 3 (Measure): evaluate one applicable criterion against one evidence
    item using Jev. Only a "raw_gap" verdict is recorded as a gap; a "pass" is
    not a finding. The verdict is final; use it exactly as returned.

    Args:
        clause_id: The criterion identifier, for example "RS-1".
        requirement: The criterion text, quoted exactly from the baseline.
        artifact_id: The artifact the item belongs to, for example "ART-001".
        item_id: The evidence item identifier, for example "R-001" or "Register header".
        evidence: An exact, unedited quote of that evidence item.
        evaluation_method: The criterion's Evaluation Method, if the baseline supplies one; otherwise leave empty.
    """
    # a. Verbatim check, same as the other tools
    if normalize(evidence) not in supplied_text(runtime):
        return {
            "error": "evidence_not_verbatim",
            "message": "Quote the evidence exactly and call again.",
            "evidence_verified": False,
        }

    # b. State for Jev: the criterion, its evaluation method if any, the evidence
    state = {"criterion": requirement, "evidence": evidence}
    if evaluation_method.strip():
        state["evaluation_method"] = evaluation_method

    response = classifier.invoke({
        "state": state,
        "questions": {"criterion_evaluation": QUESTION},
    })
    p = response.nouls["criterion_evaluation"].noul

    # c. Code applies the thresholds from the file
    if p >= SATISFIED_AT:
        verdict = "pass"            # "a pass is not a finding"
    elif p <= NOT_SATISFIED_AT:
        verdict = "raw_gap"         # "record one raw gap"
    else:
        verdict = "needs_review"    # pipeline step 4: a human decides

    return {
        "clause_id": clause_id,
        "artifact_id": artifact_id,
        "item_id": item_id,
        "verdict": verdict,
        "is_finding": verdict == "raw_gap",
        "probability_satisfied": p,
        "satisfied_at_or_above": SATISFIED_AT,
        "not_satisfied_at_or_below": NOT_SATISFIED_AT,
        "evidence_verified": True,
        "classified_by": response.model,
        "conformance_rules": {
            "source": CONFORMANCE_SOURCE,
            "version": CONFORMANCE_VERSION,
            "fingerprint": CONFORMANCE_FINGERPRINT,
        },
    }