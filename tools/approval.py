from typing import Any

from langchain.tools import tool
from langgraph.types import interrupt

APPROVAL_ACTION = "approve_finding"


@tool(parse_docstring=True)
def request_human_approval(findings: list[dict[str, Any]]) -> dict:
    """
    §10.2.3: a real person must approve every Severity 4 or 5 finding before it
    is final. This pauses the audit and asks the human reviewer to approve or
    reject each finding. Call it once, at Stage 7, with every Severity 4–5
    finding. Use the returned decisions exactly; never approve anything yourself.

    Args:
        findings: One entry per Severity 4–5 finding, each with clause_id, artifact_id, severity, severity_label, and summary (one plain sentence describing the gap).
    """
    if not findings:
        return {"approvals": [], "note": "No Severity 4–5 findings; no approval needed."}

    request = {
        "action_requests": [
            {
                "name": APPROVAL_ACTION,
                "args": {
                    "clause_id": f.get("clause_id", ""),
                    "artifact_id": f.get("artifact_id", ""),
                    "severity": f.get("severity"),
                    "severity_label": f.get("severity_label", ""),
                    "summary": f.get("summary", ""),
                    "approved_by": "",
                    "approver_role": "",
                    "approval_date": "",
                },
                     "description": (
                    f"Severity {f.get('severity')} ({f.get('severity_label', '')}) finding on "
                    f"{f.get('clause_id', '')} × {f.get('artifact_id', '')}: {f.get('summary', '')}\n\n"
                    "Why this needs your approval: under the methodology (§10.2.3), every "
                    "Severity 4 (Major) or 5 (Critical) finding requires explicit human approval "
                    "before it is final. A qualified person validates its meaning and materiality; "
                    "the AI can never approve it.\n\n"
                    "To APPROVE: choose Edit, enter your name in approved_by, your role in "
                    "approver_role and today's date in approval_date, then submit.\n"
                    "To REJECT: choose Reject and say why. A rejection stops the audit; "
                    "the report cannot be final."
                ),
            }
            for f in findings
        ],
        "review_configs": [{"action_name": APPROVAL_ACTION, "allowed_decisions": ["edit", "reject"]}],
    }

    # Pauses the run until the human answers in the UI. The answer comes back from
    # the platform, not from the agent's own text.
    response = interrupt(request) or {}
    decisions = response.get("decisions", []) if isinstance(response, dict) else []

    approvals = []
    for i, f in enumerate(findings):
        d = decisions[i] if i < len(decisions) else {}
        kind = d.get("type") if isinstance(d, dict) else None
        record = {"clause_id": f.get("clause_id", ""), "artifact_id": f.get("artifact_id", ""),
                  "severity": f.get("severity")}
        if kind == "edit":
            args = (d.get("edited_action") or {}).get("args", {}) or {}
            by, role, date = (str(args.get(k, "")).strip() for k in ("approved_by", "approver_role", "approval_date"))
            if by and date:
                record.update(decision="approved", approved_by=f"{by}, {role}" if role else by, approval_date=date)
            else:
                record.update(decision="incomplete",
                              message="Approval needs the approver's name (approved_by) and a date (approval_date).")
        elif kind == "reject":
            record.update(decision="rejected", message=d.get("message", ""))
        else:
            record.update(decision="no_decision", message="No decision was recorded for this finding.")
        approvals.append(record)

    return {"approvals": approvals, "recorded_by": "human review (interrupt)"}
