#!/usr/bin/env python3
"""
IEM-PM Renderer — Contract 5 / Stage 9
Reads canonical findings JSON and produces HTML + TXT reports.
Deterministic: same JSON in → byte-identical out.

v1.2.0: renders the RIS score's components/limitations breakdown and each
finding's human-approval status, both new in schema v1.2.0.
v1.3.0: an approved finding now renders who approved it and when, not just
a bare "Approved" flag.
v1.4.0: renders skill_version/model provenance in the report header.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from jinja2 import Template

try:
    from paths import DEFAULT_TEMPLATE
    from timing_log import log_stage, append_audit_end_summary
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import DEFAULT_TEMPLATE
    from timing_log import log_stage, append_audit_end_summary


def _to_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _iempm_filename(dt: datetime, ext: str) -> str:
    """IEMPM_AuditGap_Report_DDMMYY_HHMM.<ext> -- see references/file-naming.md."""
    return f"IEMPM_AuditGap_Report_{_to_utc(dt).strftime('%d%m%y_%H%M')}.{ext}"


def _parse_iso(iso_string: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    except Exception:
        return None


def load_template(template_path: Path) -> Template:
    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def render_html(canonical: dict, template: Template) -> str:
    findings = canonical.get("findings", [])
    ris = canonical.get("reporting_integrity_score", {})
    return template.render(
        audit=canonical,
        generated_at=_format_timestamp(canonical.get("generated_at", "")),
        findings_count=len(findings),
        severity_counts=_count_by(findings, "severity"),
        gap_counts=_count_by(findings, "gap_type"),
        origin_counts=_count_by(findings, "root_origin"),
        artifact_count=len(canonical.get("baseline", {}).get("artifacts_examined", [])),
        ris_components=ris.get("components", {}),
        ris_limitations=ris.get("limitations", [])
    )


def render_txt(canonical: dict) -> str:
    lines = [
        "=" * 80,
        "IEM-PM  PMO DATA GAP AUDIT REPORT",
        "=" * 80,
        f"Audit ID:       {canonical['audit_id']}",
        f"Charter:        {canonical['charter_version']}",
        f"Generated:      {_format_timestamp(canonical.get('generated_at', ''))}",
        f"Schema:         {canonical['schema_version']}",
        f"Skill Version:  {canonical.get('skill_version', 'unknown')}",
        f"Model:          {canonical.get('model', 'unknown')}",
        "",
        "1. EXECUTIVE SUMMARY",
        "-" * 40,
        f"Total Findings: {len(canonical.get('findings', []))}",
        f"Reporting Integrity Score: {canonical['reporting_integrity_score']['score']}/100",
        "",
        "2. AUDIT SCOPE & BASELINE",
        "-" * 40,
        f"Standards: {', '.join(canonical['baseline']['standards_declared'])}",
        f"Artifacts Examined: {len(canonical['baseline']['artifacts_examined'])}",
        f"Scope: {', '.join(canonical['baseline']['scope'])}",
        "",
        "3. DELIVERY EVIDENCE SUMMARY",
        "-" * 40,
        f"Total artifacts: {canonical['evidence_summary']['total_artifacts']}",
        f"Field coverage: {canonical['evidence_summary']['coverage_percentage']}%",
        "",
        "4. GAP REGISTER",
        "-" * 40,
    ]

    for f in canonical.get("findings", []):
        lines.extend([
            "",
            f"  {f['id']} | {f['gap_type']} | Severity: {f['severity']}/5",
            f"  Origin: {f['root_origin']}",
        ])
        if f.get("human_approved") is True:
            by = f.get("human_approved_by") or "unrecorded"
            at = f.get("human_approved_at")
            when = f" on {at}" if at else ""
            lines.append(f"  Human Approval: Approved by {by}{when}")
        elif f.get("human_approved") is False:
            lines.append("  Human Approval: Pending Review")
        elif f["severity"] >= 4:
            lines.append("  Human Approval: NOT RECORDED (required for this severity)")
        lines.extend([
            f"  Standard: {f['standard_reference']['standard']} {f['standard_reference']['identifier']}",
            f"  {f['description']}",
            "  Evidence:",
        ])
        for ev in f.get("evidence", []):
            quote = ev["quote_or_absence"][:120]
            if len(ev["quote_or_absence"]) > 120:
                quote += "..."
            lines.append(f"    - {ev['artifact_id']} @ {ev['location']}: {quote}")
        lines.append(f"  Action: {f['recommended_action']}")

    lines.extend([
        "",
        "5. ROOT CAUSE ANALYSIS",
        "-" * 40,
    ])
    for origin, count in _count_by(canonical.get("findings", []), "root_origin").items():
        pct = (count / max(len(canonical.get("findings", [])), 1)) * 100
        lines.append(f"  {origin:25s} : {count:3d} ({pct:5.1f}%)")

    lines.extend([
        "",
        "6. INTELLIGENCE INDICATORS (Narrative)",
        "-" * 40,
    ])
    for dim, text in canonical.get("intelligence_indicators", {}).items():
        lines.append(f"  {dim.replace('_', ' ').title()}:")
        suffix = "..." if len(text) > 180 else ""
        lines.append(f"    {text[:180]}{suffix}")
        lines.append("")

    ris = canonical.get("reporting_integrity_score", {})
    lines.extend([
        "7. REPORTING INTEGRITY SCORE",
        "-" * 40,
        f"  Score: {ris.get('score')}/100",
        f"  Methodology: {ris.get('methodology')}",
    ])
    components = ris.get("components", {})
    if components:
        lines.append("")
        lines.append("  Score Components:")
        for key, val in components.items():
            lines.append(f"    {key.replace('_', ' ').title()}: {val}")
    limitations = ris.get("limitations", [])
    if limitations:
        lines.append("")
        lines.append("  Limitations:")
        for i, lim in enumerate(limitations, 1):
            lines.append(f"    {i}. {lim}")

    lines.extend([
        "",
        "8. RECOMMENDED ACTIONS",
        "-" * 40,
    ])
    for i, f in enumerate(canonical.get("findings", []), 1):
        lines.append(f"  {i}. [{f['id']}] {f['recommended_action']}")
        lines.append(f"      (Addresses {f['root_origin']} origin)")

    lines.extend([
        "",
        "9. ROADMAP",
        "-" * 40,
        "  Prioritize by root origin frequency and severity concentration:",
        "  1. Address highest-frequency root origin first",
        "  2. Resolve all Severity 5 gaps within 30 days",
        "  3. Close Missing gaps by updating Charter or capturing data",
        "  4. Re-run audit after remediation to measure delta",
        "",
        "10. APPENDIX",
        "-" * 40,
        f"  Schema Version: {canonical['schema_version']}",
        f"  Skill Version: {canonical.get('skill_version', 'unknown')}",
        f"  Model: {canonical.get('model', 'unknown')}",
        "  Canonical JSON: (see separate file)",
        "",
        "=" * 80,
        "END OF REPORT",
        "=" * 80,
    ])

    return "\n".join(lines)


def _count_by(findings: list, key: str) -> dict:
    counts = {}
    for f in findings:
        val = f.get(key, "Unknown")
        counts[val] = counts.get(val, 0) + 1
    return dict(sorted(counts.items()))


def _format_timestamp(iso_string: str) -> str:
    dt = _parse_iso(iso_string)
    return dt.strftime("%Y-%m-%d %H:%M UTC") if dt else (iso_string or "unknown")


def main():
    parser = argparse.ArgumentParser(description="IEM-PM: JSON → HTML + TXT")
    parser.add_argument("--canonical", required=True, type=Path, help="Path to findings.json")
    parser.add_argument(
        "--template", type=Path, default=None,
        help=f"Path to HTML template. Defaults to {DEFAULT_TEMPLATE.name}.",
    )
    parser.add_argument(
        "--output-html", type=Path, default=None,
        help="Output path for the HTML report. Defaults to IEMPM_AuditGap_Report_DDMMYY_HHMM.html "
             "(Appendix G) using the audit's own Date, written into the same reports/ folder as "
             "--canonical (a sibling of the project's evidence/ folder).",
    )
    parser.add_argument(
        "--output-txt", type=Path, default=None,
        help="Output path for the TXT report. Defaults to IEMPM_AuditGap_Report_DDMMYY_HHMM.txt "
             "(Appendix G) using the audit's own Date, written into the same reports/ folder as "
             "--canonical (a sibling of the project's evidence/ folder).",
    )
    args = parser.parse_args()

    if not args.canonical.exists():
        print(f"[E-RENDER-001] Canonical findings JSON not found: {args.canonical}")
        exit(1)

    canonical = json.loads(args.canonical.read_text(encoding="utf-8"))
    audit_dt = _parse_iso(canonical.get("generated_at", "")) or datetime.now(timezone.utc)

    # Explicit paths always win; otherwise land next to --canonical itself, i.e. the
    # same project reports/ folder Stage 8 already wrote the JSON into.
    reports_dir = args.canonical.resolve().parent
    log_stage(reports_dir, "Stage 9 Render", "ENTRY")
    try:
        output_txt = args.output_txt or (reports_dir / _iempm_filename(audit_dt, "txt"))
        output_html = args.output_html or (reports_dir / _iempm_filename(audit_dt, "html"))
        template_path = args.template or DEFAULT_TEMPLATE

        if args.output_txt is None or args.output_html is None:
            reports_dir.mkdir(parents=True, exist_ok=True)

        # TXT
        txt = render_txt(canonical)
        output_txt.write_text(txt, encoding="utf-8")
        print(f"TXT report: {output_txt}")

        # HTML
        template = load_template(template_path)
        html = render_html(canonical, template)
        output_html.write_text(html, encoding="utf-8")
        print(f"HTML report: {output_html}")
    finally:
        # Stage 9 is the last stage that logs anything -- close out the audit's own
        # timing.log with a total-elapsed summary (SKILL.md §6.9). In a finally block so
        # both the EXIT line and the summary are still written if rendering raised partway
        # through, rather than leaving timing.log silently incomplete. Stage 10 (console
        # handover) does no new work, so nothing after this point needs instrumenting.
        log_stage(reports_dir, "Stage 9 Render", "EXIT")
        append_audit_end_summary(reports_dir)


if __name__ == "__main__":
    main()