#!/usr/bin/env python3
"""
IEM-PM Manifest → Canonical Findings
Reads the LLM-generated Audit Manifest (markdown) and converts it to
validated canonical findings JSON (Contract 4).

The LLM judges. This script validates, scores, and canonicalizes.
"""

import json
import re
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Import our validator from the same directory
try:
    from schema import validate_canonical, validate_no_duplicates, validate_evidence_coverage, validate_major_finding_approval
    from timing_log import log_stage
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from schema import validate_canonical, validate_no_duplicates, validate_evidence_coverage, validate_major_finding_approval
    from timing_log import log_stage


def _to_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _iempm_filename(dt: datetime, ext: str) -> str:
    """IEMPM_AuditGap_Report_DDMMYY_HHMM.<ext> -- see references/file-naming.md."""
    return f"IEMPM_AuditGap_Report_{_to_utc(dt).strftime('%d%m%y_%H%M')}.{ext}"


# ─── Closed Taxonomies (must match schema and SKILL.md) ───
GAP_TYPES = {
    "Missing", "Ignored", "Disconnected", "Untrusted",
    "Underutilized", "Misclassified", "Divergent"
}
ROOT_ORIGINS = {
    "Capture", "Integration", "Definition / Taxonomy",
    "Ownership", "Process / Cadence", "Tooling", "Behavior"
}
INTELLIGENCE_DIMS = [
    "Visibility", "Integrity", "Connectivity", "Governance",
    "Predictability", "Decision Quality", "Continuous Improvement"
]


class ManifestParser:
    """
    Parses the Audit Manifest markdown into canonical findings JSON.
    """

    def __init__(self, manifest_path: Path, charter_path: Optional[Path] = None):
        self.manifest_path = manifest_path
        self.charter_path = charter_path
        self.raw = manifest_path.read_text(encoding="utf-8")
        self.errors: List[str] = []
        self.warnings: List[str] = []

    # ─── Public API ───

    def parse(self) -> Dict[str, Any]:
        """Main entry: manifest → canonical JSON dict."""
        header = self._parse_header()
        artifacts = self._parse_artifacts()
        findings = self._parse_findings()
        synthesis = self._parse_synthesis()

        # generated_at is the audit's own Date (Manifest header), not "now" --
        # this is what lets every artifact from one audit share one file name
        # (Appendix G) even when this script and render.py run minutes apart.
        audit_date = self._parse_date(header.get("date")) or datetime.now(timezone.utc)

        # Build canonical structure
        canonical = {
            "audit_id": header.get("audit_id", self._generate_audit_id()),
            "schema_version": "1.4.0",
            "charter_version": header.get("charter_version", "unknown"),
            "skill_version": header.get("skill_version", "unknown"),
            "model": header.get("model", "unknown"),
            "generated_at": audit_date.isoformat(),
            "baseline": {
                "standards_declared": self._parse_standards(header.get("standards_baseline", "")),
                "artifacts_examined": artifacts,
                "scope": self._parse_scope(header.get("scope", ""))
            },
            "evidence_summary": self._compute_evidence_summary(artifacts),
            "findings": findings,
            "intelligence_indicators": synthesis["indicators"],
            "reporting_integrity_score": self._compute_ris(findings)
        }

        return canonical

    def validate(self, canonical: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Run all validations and return (is_valid, errors)."""
        all_errors: List[str] = []

        all_errors.extend(validate_canonical(canonical))
        all_errors.extend(validate_no_duplicates(canonical))
        all_errors.extend(validate_evidence_coverage(canonical))
        all_errors.extend(validate_major_finding_approval(canonical))
        all_errors.extend(self.errors)

        return len(all_errors) == 0, all_errors

    # ─── Header Parsing ───

    def _parse_header(self) -> Dict[str, str]:
        """Extract header metadata from the manifest."""
        header = {}
        patterns = {
            "audit_id": r'\*\*Audit ID:\*\*\s*(.+?)(?=\n|$)',
            "charter_version": r'\*\*Charter Version:\*\*\s*(.+?)(?=\n|$)',
            "standards_baseline": r'\*\*Standards Baseline:\*\*\s*(.+?)(?=\n|$)',
            "scope": r'\*\*Scope:\*\*\s*(.+?)(?=\n|$)',
            "status": r'\*\*Status:\*\*\s*(.+?)(?=\n|$)',
            "date": r'\*\*Date:\*\*\s*(.+?)(?=\n|$)',
            "skill_version": r'\*\*Skill Version:\*\*\s*(.+?)(?=\n|$)',
            "model": r'\*\*Model:\*\*\s*(.+?)(?=\n|$)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, self.raw, re.IGNORECASE)
            if match:
                header[key] = match.group(1).strip()
        return header

    def _parse_standards(self, text: str) -> List[str]:
        """Parse semicolon-separated standards list.

        Full standard titles routinely contain commas of their own (e.g. "Standard
        for Risk Management in Portfolios, Programs, and Projects"), so splitting on
        "," shreds a single title into several bogus entries. ";" is the Manifest's
        declared separator (AUDIT_MANIFEST_template.md Sec 10.2.1) precisely to avoid
        that collision.
        """
        return [s.strip() for s in text.split(";") if s.strip()]

    def _parse_scope(self, text: str) -> List[str]:
        """Parse semicolon-separated scope list. See _parse_standards for why ';'."""
        return [s.strip() for s in text.split(";") if s.strip()]

    # ─── Artifact Parsing ───

    def _parse_artifacts(self) -> List[Dict[str, Any]]:
        """Extract all ## ARTIFACT: blocks."""
        artifacts = []
        # Keep in sync with findings.schema.json's #/definitions/artifact_id -- any
        # Charter-declared PREFIX-SUFFIX scheme (ART-001, WK8-01, DOC-2026-08, ...).
        pattern = r'## ARTIFACT:\s*([A-Za-z0-9]{1,10}(?:-[A-Za-z0-9]{1,10}){1,3})\n(.*?)(?=## ARTIFACT:|## SYNTHESIS|### FINDING:|$)'
        for match in re.finditer(pattern, self.raw, re.DOTALL):
            art_id = match.group(1)
            block = match.group(2)
            art = {
                "artifact_id": art_id,
                "artifact_name": self._extract_field(block, "Artifact Name") or art_id,
                "source_path": self._extract_field(block, "Path") or "unknown",
                "checksum": self._extract_field(block, "Checksum") or "computed"
            }
            coverage = self._parse_percentage(self._extract_field(block, "Field Coverage"))
            if coverage is not None:
                art["field_coverage_pct"] = coverage
            artifacts.append(art)
        return artifacts

    # ─── Finding Parsing ───

    def _parse_findings(self) -> List[Dict[str, Any]]:
        """Extract all ### FINDING: blocks."""
        findings = []
        pattern = r'### FINDING:\s*(FIND-\d{4})\n(.*?)(?=### FINDING:|## SYNTHESIS|$)'
        for match in re.finditer(pattern, self.raw, re.DOTALL):
            fid = match.group(1)
            block = match.group(2)
            finding = self._parse_single_finding(fid, block)
            if finding:
                findings.append(finding)
        return findings

    def _parse_single_finding(self, fid: str, block: str) -> Optional[Dict[str, Any]]:
        """Parse one finding block."""
        gap_type = self._extract_field(block, "Gap Type")
        root_origin = self._extract_field(block, "Root Origin")

        # Validate closed taxonomies
        if gap_type not in GAP_TYPES:
            self.errors.append(f"[E-PARSE-002] {fid}: Invalid gap_type '{gap_type}'")
            return None
        if root_origin not in ROOT_ORIGINS:
            self.errors.append(f"[E-PARSE-003] {fid}: Invalid root_origin '{root_origin}'")
            return None

        # Parse evidence bullets
        evidence = self._parse_evidence_bullets(block)
        if not evidence:
            self.errors.append(f"[E-PARSE-004] {fid}: No evidence bullets found")
            return None

        # Parse intelligence dimensions
        dims_text = self._extract_field(block, "Intelligence Dimensions") or ""
        dims = [d.strip() for d in dims_text.split(",") if d.strip() in INTELLIGENCE_DIMS]

        # Parse severity
        sev_str = self._extract_field(block, "Severity") or "3"
        try:
            severity = int(sev_str)
            if not 1 <= severity <= 5:
                raise ValueError
        except ValueError:
            self.errors.append(f"[E-PARSE-005] {fid}: Invalid severity '{sev_str}'")
            severity = 3

        # v1.2.0: human approval, required for Major (4) and Critical (5) findings
        human_approved = self._parse_human_approved(block, severity, fid)
        # v1.3.0: who approved it and when -- required whenever human_approved is True,
        # regardless of severity, since a bare "Approved" with no accountable name isn't
        # a real approval record.
        approved_by, approved_at = self._parse_approval_metadata(block, human_approved, fid)

        return {
            "id": fid,
            "gap_type": gap_type,
            "root_origin": root_origin,
            "description": self._extract_field(block, "Description") or "",
            "evidence": evidence,
            "standard_reference": {
                "standard": self._extract_field(block, "Standard") or "",
                "clause": self._extract_field(block, "Clause") or "",
                "identifier": self._extract_field(block, "Identifier") or "",
                "summary": self._extract_field(block, "Requirement Summary") or ""
            },
            "severity": severity,
            "human_approved": human_approved,
            "human_approved_by": approved_by,
            "human_approved_at": approved_at,
            "impact": self._extract_field(block, "Impact") or "",
            "recommended_action": self._extract_field(block, "Recommended Action") or "",
            "intelligence_dimensions": dims
        }

    def _parse_human_approved(self, block: str, severity: int, fid: str) -> Optional[bool]:
        """v1.2.0: parse Human Approved status. Required for Severity 4-5.

        Flagged as a parse-time error (fails fast, before the manifest even
        reaches schema.py's validate_major_finding_approval) when a Major or
        Critical finding has no Human Approved field at all -- the same rule
        is also enforced at validation time as a second, independent check,
        not because one is redundant, but because a manifest that never even
        declares the field should be caught here, while a manifest that
        declares it as e.g. "Pending" should be caught by the validator.
        """
        text = self._extract_field(block, "Human Approved")
        if not text:
            if severity >= 4:
                self.errors.append(
                    f"[E-PARSE-008] {fid}: Severity {severity} (Major/Critical) finding "
                    f"requires a Human Approved field"
                )
            return None
        val = text.strip().lower()
        if val in ("yes", "true", "approved"):
            return True
        if val in ("no", "false", "pending"):
            return False
        self.warnings.append(f"[W-PARSE-008] {fid}: Unrecognized Human Approved value '{text}'; treated as pending")
        return None

    def _parse_approval_metadata(
        self, block: str, human_approved: Optional[bool], fid: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """v1.3.0: parse who approved and when. Required whenever human_approved is True --
        a bare "Approved" flag with no accountable name is not an audit trail. Approval Date
        is kept as free text (not parsed as a machine timestamp): real approvals often happen
        conversationally ("yes, confirmed in-session"), and forcing a fabricated-looking ISO
        timestamp onto that would be less honest than recording what was actually said.
        """
        approved_by = self._extract_field(block, "Approved By") or None
        approved_at = self._extract_field(block, "Approval Date") or None

        if human_approved is True and not approved_by:
            self.errors.append(
                f"[E-PARSE-009] {fid}: Human Approved is Yes but no Approved By field is "
                f"present. Record the real name/role of who approved it -- do not leave the "
                f"approval unattributed."
            )

        return approved_by, approved_at

    def _parse_evidence_bullets(self, block: str) -> List[Dict[str, str]]:
        """Parse '- **Artifact:** ... | **Location:** ... | **Evidence:** ...' bullets."""
        evidence = []
        pattern = r'-\s*\*\*Artifact:\*\*\s*(.*?)\s*\|\s*\*\*Location:\*\*\s*(.*?)\s*\|\s*\*\*Evidence:\*\*\s*(.*?)(?=\n- \*\*Artifact:|\n\n|$)'
        for match in re.finditer(pattern, block, re.DOTALL):
            evidence.append({
                "artifact_id": match.group(1).strip(),
                "location": match.group(2).strip(),
                "quote_or_absence": match.group(3).strip()
            })
        return evidence

    # ─── Synthesis Parsing ───

    def _parse_synthesis(self) -> Dict[str, Any]:
        """Extract intelligence indicators from ## SYNTHESIS."""
        indicators = {}

        match = re.search(r'## SYNTHESIS(.*?)(?=## APPENDIX|$)', self.raw, re.DOTALL | re.IGNORECASE)
        if not match:
            self.warnings.append("[W-PARSE-001] No SYNTHESIS section found")
            return {"indicators": indicators}

        synth_text = match.group(1)

        for dim in INTELLIGENCE_DIMS:
            dim_key = dim.lower().replace(" ", "_")
            indicators[dim_key] = "No significant evidence observed."
            dim_pattern = rf'###\s*{re.escape(dim)}\n(.*?)(?=###\s|## |$)'
            dim_match = re.search(dim_pattern, synth_text, re.DOTALL | re.IGNORECASE)
            if dim_match:
                indicators[dim_key] = dim_match.group(1).strip()

        return {"indicators": indicators}

    # ─── Scoring (Deterministic) ───

    def _compute_ris(self, findings: List[Dict]) -> Dict[str, Any]:
        """
        Reporting Integrity Score v1.2.0 — deterministic. The formula and
        weights are UNCHANGED from v1.1.0 (see below) -- v1.2.0 only adds
        `components` and `limitations` to the output, so the score is
        auditable instead of asserted. This does not add a categorical
        "band" on top of the raw score: an independent review (Dr. Tony
        Prensa, TP Global Business Consulting, 2026-08-14) correctly noted
        the two-decimal score implies unearned calibration -- but bucketing
        it into a handful of arbitrarily-cut bands doesn't fix that, it just
        hides the same lack of calibration behind coarser numbers. Disclosing
        the real components and limitations is the honest fix; inventing new
        unvalidated cut points is not.

        Formula:
        - Base: 100
        - Deduct severity points: sum(severity) capped at 50 (saturates at total
          severity 50 — e.g. ~17 Critical findings, not ~6)
        - Deduct density penalty: (findings / artifacts) * 5, capped at 20
          (saturates at density 4/artifact, not 2/artifact)
        - Deduct root cause diversity penalty: unique origins > 4 ? 10 : 0
        - Deduct Missing gap penalty: count(Missing) * 3, capped at 20

        v1.0.0's severity/density caps saturated too easily — a routine,
        moderately-thorough audit (e.g. 14 findings, avg severity ~2.6) already
        hit both caps and floored at 0, identical to a genuinely catastrophic
        audit. These weights are widened so the score keeps discriminating
        between "flawed" and "catastrophic" instead of both reading as the same
        zero.
        """
        limitations = [
            "This score has not been calibrated across multiple organizations or decision types.",
            "Severity is assigned by LLM judgment (Stage 6) and is not empirically derived.",
            "A score from one audit is not directly comparable to another unless scope, "
            "standards, and materiality are identical.",
            "The score describes evidence state at a point in time; it does not predict outcomes."
        ]

        if not findings:
            return {
                "score": 100.0,
                "methodology": "Weighted Gap Profile v1.2.0",
                "version": "1.2.0",
                "components": {
                    "severity_deduction": 0, "density_deduction": 0,
                    "diversity_deduction": 0, "missing_deduction": 0,
                    "total_findings": 0, "total_artifacts": max(len(self._parse_artifacts()), 1),
                    "unique_origins": 0
                },
                "limitations": limitations
            }

        total_severity = sum(f["severity"] for f in findings)
        severity_deduction = min(total_severity, 50)

        # Artifact count from manifest or default to 1
        art_count = max(len(self._parse_artifacts()), 1)
        density = len(findings) / art_count
        density_deduction = min(density * 5, 20)

        origins = {f["root_origin"] for f in findings}
        diversity_deduction = 10 if len(origins) > 4 else 0

        missing_count = sum(1 for f in findings if f["gap_type"] == "Missing")
        missing_deduction = min(missing_count * 3, 20)

        score = max(0.0, 100.0 - severity_deduction - density_deduction - diversity_deduction - missing_deduction)

        return {
            "score": round(score, 2),
            "methodology": "Weighted Gap Profile v1.2.0",
            "version": "1.2.0",
            "components": {
                "severity_deduction": severity_deduction,
                "density_deduction": round(density_deduction, 2),
                "diversity_deduction": diversity_deduction,
                "missing_deduction": missing_deduction,
                "total_findings": len(findings),
                "total_artifacts": art_count,
                "unique_origins": len(origins)
            },
            "limitations": limitations
        }

    def _compute_evidence_summary(self, artifacts: List[Dict]) -> Dict[str, Any]:
        """
        Averages the per-artifact Field Coverage the Manifest declares.
        total_fields_mapped is not derivable from the Manifest format (there is
        no per-field enumeration, only a per-artifact percentage) and stays 0
        until the Charter's Field Semantics Map is wired in as a source.
        """
        coverages = [a["field_coverage_pct"] for a in artifacts if "field_coverage_pct" in a]
        avg_coverage = round(sum(coverages) / len(coverages), 1) if coverages else 0.0
        return {
            "total_artifacts": len(artifacts),
            "total_fields_mapped": 0,
            "coverage_percentage": avg_coverage
        }

    # ─── Helpers ───

    def _extract_field(self, text: str, field: str) -> Optional[str]:
        """
        Extract **Field:** value from markdown.
        Uses non-greedy match and requires the field label to be explicitly present.
        """
        pattern = rf'\*\*{re.escape(field)}:\*\*\s*(.*?)(?=\n\*\*|\n\n\*\*|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        value = match.group(1).strip()
        # Defensive: if the captured value starts with another **Label:**, we bled.
        # This happens when the original field was blank and greedy \s* ate the newline.
        if value.startswith("**") and ":" in value.split("**")[1].split("\n")[0]:
            # We captured the next field's label. Treat as blank.
            return ""
        return value

    @staticmethod
    def _parse_percentage(text: Optional[str]) -> Optional[float]:
        """Parse a Field Coverage value into a 0-100 float.

        Accepts an explicit percentage ("85%", "(100%)") or the "N of M declared
        columns present" count the Manifest template actually asks for
        (AUDIT_MANIFEST_template.md Sec 10.2.2), computing N/M*100 in that case.
        The "%" sign is required for the bare-number form -- without it, any number
        in the Observations-style text (a row count, a dollar figure) would be
        silently misread as a percentage. Returns None if neither form is present;
        a field this stage cannot confidently parse must be omitted, not guessed.
        """
        if not text:
            return None
        of_match = re.search(r'(\d+)\s+of\s+(\d+)', text, re.IGNORECASE)
        if of_match:
            n, m = int(of_match.group(1)), int(of_match.group(2))
            return round((n / m) * 100, 1) if m else None
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
        return float(pct_match.group(1)) if pct_match else None

    @staticmethod
    def _parse_date(text: Optional[str]) -> Optional[datetime]:
        """Parse the Manifest header's **Date:** field (ISO 8601, 'Z' or offset)."""
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        except ValueError:
            return None

    def _generate_audit_id(self) -> str:
        """Generate fallback audit ID."""
        return f"IEM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{hashlib.sha256(self.raw.encode()).hexdigest()[:6].upper()}"


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(description="IEM-PM: Manifest → Canonical Findings")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to Audit Manifest markdown")
    parser.add_argument("--charter", type=Path, help="Optional: Path to ratified PMO Data Charter")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Output path for findings.json. Defaults to IEMPM_AuditGap_Report_DDMMYY_HHMM.json "
             "(Appendix G) using the audit's own Date, written into the same reports/ folder as "
             "--manifest (a sibling of the project's evidence/ folder).",
    )
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[E-PARSE-001] Manifest not found: {args.manifest}")
        exit(1)

    # timing.log (SKILL.md §6.9) always lives next to the Manifest itself, regardless of
    # where --output redirects the JSON -- this is Stage 8's own entry/exit, logged
    # automatically since this stage has no LLM reasoning to log it by hand. EXIT is in a
    # finally block so it's still logged even if parsing/validation/writing raises --
    # otherwise an unhandled exception leaves an orphaned ENTRY with no matching EXIT.
    reports_dir = args.manifest.resolve().parent
    log_stage(reports_dir, "Stage 8 Findings JSON", "ENTRY")
    try:
        # Parse
        parser_engine = ManifestParser(args.manifest, args.charter)
        canonical = parser_engine.parse()

        # Validate
        is_valid, errors = parser_engine.validate(canonical)

        # Printed regardless of outcome -- a parse-time warning (e.g. an
        # unrecognized "Human Approved" value) is often the actual explanation
        # for a validation error on the same finding, and must not be silently
        # dropped just because validation also failed.
        if parser_engine.warnings:
            print("Warnings:")
            for w in parser_engine.warnings:
                print(f"  - {w}")
            print()

        if not is_valid:
            print("VALIDATION FAILED:")
            for e in errors:
                print(f"  - {e}")
            exit(1)

        # Write -- explicit --output always wins; otherwise land next to --manifest itself,
        # i.e. the same project reports/ folder the Manifest was already written into.
        output_path = args.output
        if output_path is None:
            reports_dir.mkdir(parents=True, exist_ok=True)
            audit_dt = datetime.fromisoformat(canonical["generated_at"])
            output_path = reports_dir / _iempm_filename(audit_dt, "json")

        output_path.write_text(json.dumps(canonical, indent=2), encoding="utf-8")
        print(f"Canonical findings written to {output_path}")
        print(f"Total findings: {len(canonical['findings'])}")
        print(f"Reporting Integrity Score: {canonical['reporting_integrity_score']['score']}")
    finally:
        log_stage(reports_dir, "Stage 8 Findings JSON", "EXIT")


if __name__ == "__main__":
    main()