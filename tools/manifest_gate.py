import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from langchain.tools import tool, ToolRuntime

from tools.jev_classifier import normalize, evidence_quotes

# ───────── Locations (your engine, unedited; output folder from .env) ─────────
SCRIPTS_DIR = Path(__file__).resolve().parent / "engine" / "scripts"

_out = os.getenv("AUDIT_OUTPUT_DIR")
if not _out:
    raise RuntimeError("AUDIT_OUTPUT_DIR not set in .env")
OUTPUT_ROOT = Path(_out)

# Your parser, imported read-only for the fidelity checks
sys.path.insert(0, str(SCRIPTS_DIR))
from manifest_to_findings import ManifestParser  # noqa: E402


# ───────── Helpers: read what the tools returned earlier in this audit ─────────
def _get(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def _json(content):
    text = content if isinstance(content, str) else "".join(
        (p.get("text", "") if isinstance(p, dict) else "") for p in (content or [])
    )
    try:
        return json.loads(text)
    except Exception:
        return None


def _tool_trail(runtime) -> dict:
    """Pair every tool call's inputs with its result, grouped by tool name."""
    calls, trail = {}, {}
    for m in _get(runtime, "state", {}).get("messages", []):
        for c in _get(m, "tool_calls", None) or []:
            calls[_get(c, "id")] = (_get(c, "name"), _get(c, "args", {}) or {})
        if _get(m, "type") == "tool":
            cid = _get(m, "tool_call_id")
            if cid in calls:
                name, args = calls[cid]
                result = _json(_get(m, "content"))
                if result is not None:
                    trail.setdefault(name, []).append((args, result))
    return trail


def _n(text) -> str:
    return normalize(text or "")


def _contains(haystack: str, needle: str) -> bool:
    return bool(_n(needle)) and _n(needle) in _n(haystack)


def _consolidated_gaps(trail: dict) -> list:
    """Stage 3, Activity 7 and Decision Logic: failing records that share a
    criterion and artifact are ONE raw gap with one evidence bullet per record."""
    groups = {}
    for args, result in trail.get("check_criterion", []):
        if result.get("verdict") != "raw_gap":
            continue
        key = (_n(args.get("clause_id")), _n(args.get("artifact_id")))
        g = groups.setdefault(key, {"clause_id": args.get("clause_id"),
                                    "artifact_id": args.get("artifact_id"),
                                    "requirement": args.get("requirement"),
                                    "rows": []})
        g["rows"].append({"item_id": args.get("item_id"), "quote": args.get("evidence", "")})
    return list(groups.values())


def _quote_set(evidence: str) -> set:
    """The normalized quotes in a tool's evidence argument (one per line)."""
    return {_n(q) for q in evidence_quotes(evidence or "")}


def _gap_quotes(gap: dict) -> set:
    return {_n(row["quote"]) for row in gap["rows"]}


def _results_for(gap: dict, calls: list) -> list:
    """Tool results for exactly this consolidated gap: same requirement AND
    exactly the same set of failing-record quotes. Two gaps that share a record
    (e.g. R-001 under RS-1 and RS-2) can never be confused."""
    return [r for a, r in calls
            if _n(a.get("requirement")) == _n(gap["requirement"])
            and _quote_set(a.get("evidence", "")) == _gap_quotes(gap)]


# ───────── The Manifest Gate (Stage 7 → Stages 8, 9, 10) ─────────
@tool(parse_docstring=True)
def submit_manifest(manifest_markdown: str, runtime: ToolRuntime) -> dict:
    """
    Stage 7, the Manifest Gate: submit the complete Audit Manifest, written in
    the audit-manifest format. Code checks it; if accepted, code runs Stage 8
    (Findings JSON and RIS), Stage 9 (Render) and Stage 10 (Final Summary).
    If rejected, fix every listed error and submit again.

    Args:
        manifest_markdown: The complete Audit Manifest in the audit-manifest format.
    """
    trail = _tool_trail(runtime)
    run_id = (_get(runtime, "config", {}) or {}).get("configurable", {}).get("thread_id", "unthreaded")
    reports = OUTPUT_ROOT / str(run_id) / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    stem = "IEMPM_AuditGap_Report_" + datetime.now(timezone.utc).strftime("%d%m%y_%H%M")
    manifest_path = reports / f"{stem}.md"
    manifest_path.write_text(manifest_markdown, encoding="utf-8")

    # Parse with your own parser, to compare against what the tools returned
    parser = ManifestParser(manifest_path)
    canonical = parser.parse()
    findings = canonical.get("findings", [])
    errors = list(parser.errors)

    gaps = _consolidated_gaps(trail)
    classified = trail.get("classify_gap", [])
    rated = trail.get("rate_severity", [])

    def findings_for(gap):
        return [f for f in findings
                if _n(f["standard_reference"].get("clause")) == _n(gap["clause_id"])
                and any(_n(e.get("artifact_id")) == _n(gap["artifact_id"]) for e in f.get("evidence", []))]

    # Check 1: coverage (Stage 3: one raw gap per criterion + artifact, one bullet per failing record)
    for gap in gaps:
        label = f"{gap['clause_id']} × {gap['artifact_id']}"
        matches = findings_for(gap)
        if len(matches) != 1:
            errors.append(f"[GATE-COVERAGE] raw gap {label} must be exactly one finding "
                          f"(Clause {gap['clause_id']}, evidence bullets citing {gap['artifact_id']}); found {len(matches)}.")
            continue
        bullets = [_n(e.get("quote_or_absence", "")) for e in matches[0].get("evidence", [])]
        for row in gap["rows"]:
            if _n(row["quote"]) not in bullets:
                errors.append(f"[GATE-COVERAGE] {matches[0]['id']}: needs one evidence bullet for failing "
                              f"record {row['item_id']} whose Evidence is exactly the quote used in "
                              f"check_criterion, with nothing added or repeated.")
        for b in bullets:
            if b not in _gap_quotes(gap):
                errors.append(f"[GATE-COVERAGE] {matches[0]['id']}: an evidence bullet does not match any "
                              f"failing record's verbatim quote: '{b[:80]}'")
    if len(findings) != len(gaps):
        errors.append(f"[GATE-COVERAGE] Measure produced {len(gaps)} consolidated raw gaps "
                      f"but the Manifest has {len(findings)} findings.")

    # Check 2: fidelity (Jev's labels and the §9.1 severity are final)
    for gap in gaps:
        matches = findings_for(gap)
        if len(matches) != 1:
            continue
        f = matches[0]
        cls = _results_for(gap, classified)
        sev = _results_for(gap, rated)
        if not cls:
            errors.append(f"[GATE-FIDELITY] {f['id']}: no classify_gap result citing every failing record "
                          f"of this raw gap; classify the consolidated gap first.")
        elif (f["gap_type"], f["root_origin"]) != (cls[-1].get("gap_type"), cls[-1].get("root_origin")):
            errors.append(f"[GATE-FIDELITY] {f['id']}: Gap Type/Root Origin must be exactly "
                          f"{cls[-1].get('gap_type')} / {cls[-1].get('root_origin')} as returned by classify_gap.")
        if not sev:
            errors.append(f"[GATE-FIDELITY] {f['id']}: no rate_severity result citing every failing record "
                          f"of this raw gap; rate the consolidated gap first.")
        elif f["severity"] != sev[-1].get("severity"):
            errors.append(f"[GATE-FIDELITY] {f['id']}: Severity must be exactly "
                          f"{sev[-1].get('severity')} as returned by rate_severity.")

    # Check 3: approval (§10.2.3: only a real person approves, never the agent).
    # Approvals are trusted only when recorded by request_human_approval, whose
    # result comes from the human's answer in the UI, not from the agent's text.
    recorded = {}
    for _args, result in trail.get("request_human_approval", []):
        for a in result.get("approvals", []):
            recorded[(_n(a.get("clause_id")), _n(a.get("artifact_id")))] = a
    for f in findings:
        arts = {_n(e.get("artifact_id")) for e in f.get("evidence", [])}
        rec = next((recorded[(_n(f["standard_reference"].get("clause")), art)] for art in arts
                    if (_n(f["standard_reference"].get("clause")), art) in recorded), None)
        if f.get("human_approved") is True:
            if not rec or rec.get("decision") != "approved":
                errors.append(f"[GATE-APPROVAL] {f['id']}: no recorded human approval. "
                              f"Call request_human_approval; never write 'Human Approved: Yes' yourself.")
            elif not _contains(f.get("human_approved_by") or "", rec["approved_by"].split(",")[0]) \
                    or _n(f.get("human_approved_at")) != _n(rec.get("approval_date")):
                errors.append(f"[GATE-APPROVAL] {f['id']}: Approved By / Approval Date must be exactly "
                              f"'{rec['approved_by']}' / '{rec.get('approval_date')}' as recorded.")
        elif f.get("severity", 0) >= 4:
            if rec and rec.get("decision") == "rejected":
                errors.append(f"[GATE-APPROVAL] {f['id']}: rejected by the human reviewer "
                              f"({rec.get('message') or 'no reason given'}). The audit cannot be final; "
                              f"report the rejection to the user and stop.")
            elif not rec or rec.get("decision") != "approved":
                errors.append(f"[GATE-APPROVAL] {f['id']}: Severity {f['severity']} needs a real person's "
                              f"approval. Call request_human_approval, then write Human Approved: Yes "
                              f"with the recorded Approved By and Approval Date.")

    if errors:
        return {"accepted": False, "stage": 7, "errors": errors, "manifest_path": str(manifest_path)}

    # Stage 8: your manifest_to_findings.py, unedited (parse, validate, RIS, JSON)
    json_path = reports / f"{stem}.json"
    s8 = subprocess.run([sys.executable, "manifest_to_findings.py", "--manifest", str(manifest_path),
                         "--output", str(json_path)], cwd=SCRIPTS_DIR, capture_output=True, text=True)
    if s8.returncode != 0:
        return {"accepted": False, "stage": 8, "errors": (s8.stdout + s8.stderr).strip().splitlines(),
                "manifest_path": str(manifest_path)}

    # Stage 9: your render.py, unedited (HTML + TXT)
    html_path, txt_path = reports / f"{stem}.html", reports / f"{stem}.txt"
    s9 = subprocess.run([sys.executable, "render.py", "--canonical", str(json_path),
                         "--output-html", str(html_path), "--output-txt", str(txt_path)],
                        cwd=SCRIPTS_DIR, capture_output=True, text=True)
    if s9.returncode != 0:
        return {"accepted": False, "stage": 9, "errors": (s9.stdout + s9.stderr).strip().splitlines(),
                "manifest_path": str(manifest_path)}

    # Stage 10: final summary and file pointers
    result = json.loads(json_path.read_text(encoding="utf-8"))
    return {
        "accepted": True,
        "stages_completed": [8, 9, 10],
        "reporting_integrity_score": result["reporting_integrity_score"],
        "total_findings": len(result["findings"]),
        "summary_txt": txt_path.read_text(encoding="utf-8"),
        "files": {"manifest": str(manifest_path), "json": str(json_path),
                  "html": str(html_path), "txt": str(txt_path)},
    }
