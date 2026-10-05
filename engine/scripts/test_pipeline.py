#!/usr/bin/env python3
"""
IEM-PM Regression Test -- Full Pipeline Verification
Exercises the real pipeline end to end via subprocess (no mocking) against
the project's actual checked-in fixture (test_manifest.md: 3 artifacts,
2 findings) rather than a synthetic one-liner.
Run this after any code change to confirm the engine is intact.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Force UTF-8 stdout so this doesn't crash on Windows consoles that default
# to cp1252 -- belt-and-suspenders alongside keeping output ASCII-only below.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from paths import ENGINE_DIR, SCRIPTS_DIR, ASSETS_DIR
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import ENGINE_DIR, SCRIPTS_DIR, ASSETS_DIR

# The project's real regression fixture -- "actual data", not an inline stub.
REAL_MANIFEST_PATH = SCRIPTS_DIR / "test_manifest.md"

# Real Halt Condition 6 output (the fresh-session Pilot-audit-4 run), not a synthetic stub.
REAL_NOTICE_PATH = SCRIPTS_DIR / "test_scope_limitation_notice.md"

CANONICAL_INDICATOR_ORDER = [
    "visibility", "integrity", "connectivity", "governance",
    "predictability", "decision_quality", "continuous_improvement",
]


def run_script(name: str, args: list, cwd: Path = SCRIPTS_DIR) -> subprocess.CompletedProcess:
    """Run a script and return the CompletedProcess. Does not raise."""
    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))


def run_script_ok(name: str, args: list, cwd: Path = SCRIPTS_DIR) -> subprocess.CompletedProcess:
    """Run a script and raise if it exits non-zero."""
    result = run_script(name, args, cwd)
    if result.returncode != 0:
        print(f"FAILED: {name}")
        print(f"  stdout: {result.stdout}")
        print(f"  stderr: {result.stderr}")
        raise RuntimeError(f"{name} exited with code {result.returncode}")
    return result


def _copy_manifest_to_tmp(tmp_dir: Path, source: Path = None) -> Path:
    """Copy a manifest into tmp_dir and return the copy's path.

    manifest_to_findings.py (Stage 8) now writes timing.log next to whatever --manifest
    path it's given (SKILL.md §6.9), unconditionally -- not just next to --output. Passing
    REAL_MANIFEST_PATH directly as --manifest would append timing.log into this repo's own
    scripts/ folder on every test run, since the fixture lives there. Every test must use a
    tempdir copy instead, never the fixture in place.
    """
    dest = tmp_dir / "test_manifest.md"
    dest.write_text((source or REAL_MANIFEST_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def _generate_findings(manifest_path: Path, tmp_dir: Path) -> dict:
    """Run manifest_to_findings.py against a manifest and return the parsed JSON."""
    output_path = tmp_dir / "findings.json"
    run_script_ok("manifest_to_findings.py", [
        "--manifest", str(manifest_path),
        "--output", str(output_path),
    ])
    return json.loads(output_path.read_text(encoding="utf-8"))


# ─── Tests (each independent -- generates its own fixtures/output) ───

def test_manifest_to_findings():
    """Test 1: real fixture Manifest -> Canonical JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        data = _generate_findings(_copy_manifest_to_tmp(tmp_path), tmp_path)

        assert data["schema_version"] == "1.4.0"
        assert len(data["findings"]) == 2
        assert {f["id"] for f in data["findings"]} == {"FIND-0001", "FIND-0002"}
        assert data["reporting_integrity_score"]["score"] > 0
        assert "maturity_assessment" not in data, "OPM3/maturity modeling was scrapped -- must not reappear"

        # v1.4.0: provenance. Fixture declares both explicitly -- must parse
        # verbatim, not fall back to "unknown".
        assert data["skill_version"] == "1.13.0", "skill_version must parse from the Manifest header"
        assert data["model"] == "claude-sonnet-5", "model must parse from the Manifest header"

        # v1.2.0: human approval. FIND-0001 is Severity 4 and the fixture
        # declares "Human Approved: Yes" -- must parse to True, not a string.
        # FIND-0002 is Severity 3 (below the gate) and declares nothing --
        # must parse to None, not False (None means "not applicable", not
        # "explicitly denied").
        by_id = {f["id"]: f for f in data["findings"]}
        assert by_id["FIND-0001"]["human_approved"] is True, "Severity-4 finding must record real approval"
        assert by_id["FIND-0002"]["human_approved"] is None, "Severity-3 finding has no approval requirement"

        # v1.3.0: an approval must name who gave it, not just a bare boolean.
        assert by_id["FIND-0001"]["human_approved_by"] == "Test Fixture Approver", (
            "approved finding must record who approved it"
        )
        assert by_id["FIND-0001"]["human_approved_at"] == "2026-07-26", (
            "approved finding must record when it was approved"
        )
        assert by_id["FIND-0002"]["human_approved_by"] is None, "unapproved finding has no approver"

        # v1.2.0: RIS components/limitations must be present and non-empty --
        # this is the transparency disclosure, not decorative metadata.
        ris = data["reporting_integrity_score"]
        assert ris["components"]["total_findings"] == 2
        assert len(ris["limitations"]) > 0, "RIS must disclose its own limitations"

        # Artifact Name resolution (regression: used to fall back to the ID)
        names = {a["artifact_id"]: a["artifact_name"] for a in data["baseline"]["artifacts_examined"]}
        assert names == {
            "ART-001": "Project Schedule",
            "ART-002": "RAID Log",
            "ART-003": "Governance Pack",
        }, f"artifact names not resolved correctly: {names}"

        # Field coverage averaged from the manifest's declared per-artifact
        # values (85%, 92%, "39 of 50" -> 78% -> 85.0). Regression: used to be
        # hardcoded 0.0; later regression: "N of M" prose was misread as the
        # raw column count (39) instead of computing 39/50*100.
        assert data["evidence_summary"]["coverage_percentage"] == 85.0

        # Standards Baseline / Scope split on ";", not ",". Regression: a
        # comma-splitter shreds any standard title that contains a comma of
        # its own (e.g. "...in Portfolios, Programs, and Projects") into
        # bogus fragments.
        assert data["baseline"]["standards_declared"] == [
            "PMBOK 8th Edition",
            "Standard for Risk Management in Portfolios, Programs, and Projects",
        ], f"standards_declared corrupted by comma-splitting: {data['baseline']['standards_declared']}"
        assert data["baseline"]["scope"] == ["Projects", "Programs"]

        # Indicator order must be canonical and stable (regression: used to be
        # a Python set, so iteration order was randomized per process).
        assert list(data["intelligence_indicators"].keys()) == CANONICAL_INDICATOR_ORDER

        print(f"  PASS: {len(data['findings'])} finding(s) parsed from real fixture")
        print(f"  PASS: RIS = {data['reporting_integrity_score']['score']}")
        print(f"  PASS: no maturity_assessment in output (scrapped, not scored)")
        print(f"  PASS: artifact names resolved: {names}")
        print(f"  PASS: coverage_percentage = {data['evidence_summary']['coverage_percentage']}")
        print(f"  PASS: indicator order is canonical")


def test_schema_validation():
    """Test 2: canonical JSON produced from the real fixture passes schema validation."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        output_path = tmp_path / "findings.json"
        run_script_ok("manifest_to_findings.py", [
            "--manifest", str(_copy_manifest_to_tmp(tmp_path)),
            "--output", str(output_path),
        ])
        result = run_script_ok("schema.py", [str(output_path)])
        assert "VALIDATION PASSED" in result.stdout
        print("  PASS: schema validation passed on real-fixture output")


def test_rendering():
    """Test 3: JSON -> HTML + TXT, checking real content and both prior render bugs."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        findings_path = tmp_path / "findings.json"
        html_path = tmp_path / "report.html"
        txt_path = tmp_path / "report.txt"

        run_script_ok("manifest_to_findings.py", [
            "--manifest", str(_copy_manifest_to_tmp(tmp_path)),
            "--output", str(findings_path),
        ])
        data = json.loads(findings_path.read_text(encoding="utf-8"))

        run_script_ok("render.py", [
            "--canonical", str(findings_path),
            "--template", str(ASSETS_DIR / "report_template.html"),
            "--output-html", str(html_path),
            "--output-txt", str(txt_path),
        ])

        html_content = html_path.read_text(encoding="utf-8")
        txt_content = txt_path.read_text(encoding="utf-8")

        assert "FIND-0001" in html_content and "FIND-0002" in html_content
        assert "Missing" in html_content and "Underutilized" in html_content

        # v1.3.0: an approved finding's report must show WHO approved it, not
        # just a bare "Approved" flag (regression: this was the actual bug --
        # the field was parsed and stored but never rendered anywhere).
        assert "Test Fixture Approver" in html_content, "approver name missing from HTML report"
        assert "Test Fixture Approver" in txt_content, "approver name missing from TXT report"

        # v1.4.0: provenance must actually render, not just parse into JSON.
        assert "1.13.0" in html_content, "skill_version missing from HTML report"
        assert "claude-sonnet-5" in html_content, "model missing from HTML report"
        assert "1.13.0" in txt_content, "skill_version missing from TXT report"
        assert "claude-sonnet-5" in txt_content, "model missing from TXT report"

        # Regression: skill_version/model must appear in the TXT Appendix
        # section specifically, not just the header block above it -- the
        # HTML Appendix table already had explicit rows for both; the TXT
        # Appendix was initially missed, contradicting the User Guide's claim
        # that both fields are "repeated in the Appendix section."
        appendix_txt = txt_content.split("10. APPENDIX", 1)[1]
        assert "Skill Version: 1.13.0" in appendix_txt, "skill_version missing from TXT Appendix section"
        assert "Model: claude-sonnet-5" in appendix_txt, "model missing from TXT Appendix section"

        # Artifact names actually rendered, not just IDs (regression check).
        for name in ("Project Schedule", "RAID Log", "Governance Pack"):
            assert name in html_content, f"{name!r} missing from rendered HTML"

        # TXT ellipsis regression: any indicator text shorter than 180 chars
        # must appear whole, with no phantom "..." appended.
        for dim, text in data["intelligence_indicators"].items():
            if len(text) <= 180:
                assert text in txt_content, f"{dim} text missing verbatim from TXT report"
                assert f"{text}..." not in txt_content, f"{dim} got a phantom '...' appended"

        print(f"  PASS: HTML report: {len(html_content):,} chars, artifact names resolved")
        print(f"  PASS: TXT report: {len(txt_content):,} chars, no phantom truncation")


def test_timing_log():
    """
    Test: SKILL.md §6.9 -- Stage 8 (manifest_to_findings.py) and Stage 9 (render.py) must
    each log their own ENTRY/EXIT to timing.log automatically, and render.py must append a
    final AUDIT END summary once Stage 9 completes. This is the machine-logged half of the
    timing log (Stages 0-7 are LLM-logged via Bash and can't be exercised by this suite).
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        findings_path = tmp_path / "findings.json"
        html_path = tmp_path / "report.html"
        txt_path = tmp_path / "report.txt"

        run_script_ok("manifest_to_findings.py", [
            "--manifest", str(_copy_manifest_to_tmp(tmp_path)),
            "--output", str(findings_path),
        ])
        run_script_ok("render.py", [
            "--canonical", str(findings_path),
            "--template", str(ASSETS_DIR / "report_template.html"),
            "--output-html", str(html_path),
            "--output-txt", str(txt_path),
        ])

        log_path = tmp_path / "timing.log"
        assert log_path.exists(), "timing.log was not created"
        log_content = log_path.read_text(encoding="utf-8")

        for line in (
            "[Stage 8 Findings JSON] ENTRY",
            "[Stage 8 Findings JSON] EXIT",
            "[Stage 9 Render] ENTRY",
            "[Stage 9 Render] EXIT",
        ):
            assert line in log_content, f"{line!r} missing from timing.log"

        assert "=== AUDIT END |" in log_content, "AUDIT END summary missing from timing.log"
        assert "TOTAL:" in log_content, "AUDIT END summary must state total elapsed time"

        # Entry must come before exit for each stage -- catches an accidental swap.
        assert log_content.index("[Stage 8 Findings JSON] ENTRY") < log_content.index("[Stage 8 Findings JSON] EXIT")
        assert log_content.index("[Stage 9 Render] ENTRY") < log_content.index("[Stage 9 Render] EXIT")
        # AUDIT END must be the last thing written, after both stages finish.
        assert log_content.index("[Stage 9 Render] EXIT") < log_content.index("=== AUDIT END |")

        print(f"  PASS: timing.log has Stage 8/9 entry+exit and a final AUDIT END summary")


def test_default_output_location():
    """
    Test: with no --output/--output-html/--output-txt given, each script must
    default to writing next to its own input file -- the project's own reports/
    folder (sibling of evidence/), not any fixed global directory. Regression for
    the Audit/<Project>/evidence/+reports/ per-project layout.
    """
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp) / "SomeProject"
        reports_dir = project_dir / "reports"
        reports_dir.mkdir(parents=True)

        manifest_path = reports_dir / "manifest.md"
        manifest_path.write_text(REAL_MANIFEST_PATH.read_text(encoding="utf-8"), encoding="utf-8")

        run_script_ok("manifest_to_findings.py", ["--manifest", str(manifest_path)])
        json_candidates = list(reports_dir.glob("IEMPM_AuditGap_Report_*.json"))
        assert len(json_candidates) == 1, f"expected 1 default-named JSON in {reports_dir}, found {json_candidates}"
        findings_path = json_candidates[0]

        run_script_ok("render.py", ["--canonical", str(findings_path)])
        html_candidates = list(reports_dir.glob("IEMPM_AuditGap_Report_*.html"))
        txt_candidates = list(reports_dir.glob("IEMPM_AuditGap_Report_*.txt"))
        assert len(html_candidates) == 1, f"expected 1 default-named HTML in {reports_dir}"
        assert len(txt_candidates) == 1, f"expected 1 default-named TXT in {reports_dir}"

        print(f"  PASS: JSON/HTML/TXT all defaulted next to their input, in {reports_dir.name}/")


def test_knowledge_index():
    """Test 4: knowledge index generation against the real knowledge/ folder."""
    result = run_script_ok("derive_knowledge_index.py", [])
    assert "Knowledge index written" in result.stdout
    index_path = ENGINE_DIR / "knowledge_index.json"
    assert index_path.exists(), "knowledge_index.json was not created"
    print("  PASS: knowledge index generated")


def test_duplicate_detection():
    """
    Test 5: two full findings sharing the same gap_type + root_origin +
    artifact_id + standard identifier must be rejected as a duplicate --
    specifically, not for some unrelated parse failure.
    """
    base = REAL_MANIFEST_PATH.read_text(encoding="utf-8")

    # A genuine clone of FIND-0002's signature (Underutilized / Behavior /
    # ART-002 / Process 11.7), inserted as a real, complete finding block --
    # not a mangled header with no body, which is what the old version of
    # this test accidentally produced.
    duplicate_block = """
### FINDING: FIND-0003

**Gap Type:** Underutilized
**Root Origin:** Behavior
**Standard:** PMBOK 8th Edition
**Clause:** 11.7.2.3
**Identifier:** Process 11.7
**Requirement Summary:** Risk data must inform governance decisions and steering committee reviews.
**Description:** Deliberately duplicated finding inserted to test the no-duplicate validator end to end.
**Severity:** 2
**Impact:** Test impact text for duplicate detection.
**Recommended Action:** Test recommended action for duplicate detection.
**Intelligence Dimensions:** Governance

- **Artifact:** ART-002 | **Location:** Steering Pack, months 7-9 | **Evidence:** Deliberately duplicated evidence for validator testing.

"""
    bad_manifest = base.replace("## SYNTHESIS", duplicate_block + "## SYNTHESIS", 1)
    assert "FIND-0003" in bad_manifest, "injection into the fixture failed -- test is broken"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_path = tmp_path / "duplicate_manifest.md"
        output_path = tmp_path / "should_not_exist.json"
        manifest_path.write_text(bad_manifest, encoding="utf-8")

        result = run_script("manifest_to_findings.py", [
            "--manifest", str(manifest_path), "--output", str(output_path),
        ])
        combined = result.stdout + result.stderr

        assert result.returncode != 0, "duplicate manifest was NOT rejected"
        assert "Duplicate finding signature" in combined, (
            f"rejected, but not for the duplicate-signature reason:\n{combined}"
        )
        assert not output_path.exists(), "findings.json must not be written on validation failure"
        print("  PASS: duplicate signature (Underutilized/Behavior/ART-002/Process 11.7) correctly rejected")


def test_major_finding_requires_approval():
    """
    Test 7 (v1.2.0): a Severity 4/5 finding with no "Human Approved" field
    must be rejected -- both at parse time (fast fail, before validation)
    and, independently, at schema-validation time if it somehow got past
    parsing. Mirrors test_duplicate_detection's approach: mutate the real
    fixture, confirm rejection for the RIGHT reason, not just any failure.
    """
    # Strip the "Human Approved: Yes" line this session added to FIND-0001
    # (Severity 4) -- everything else about the fixture stays real.
    base = REAL_MANIFEST_PATH.read_text(encoding="utf-8")
    unapproved = base.replace("**Human Approved:** Yes\n", "", 1)
    assert "Human Approved" not in unapproved, "fixture mutation failed -- test is broken"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_path = tmp_path / "unapproved_manifest.md"
        output_path = tmp_path / "should_not_exist.json"
        manifest_path.write_text(unapproved, encoding="utf-8")

        result = run_script("manifest_to_findings.py", [
            "--manifest", str(manifest_path), "--output", str(output_path),
        ])
        combined = result.stdout + result.stderr

        assert result.returncode != 0, "Severity-4 finding without Human Approved was NOT rejected"
        assert "E-PARSE-008" in combined, (
            f"rejected, but not for the missing-human-approval reason:\n{combined}"
        )
        assert not output_path.exists(), "findings.json must not be written on validation failure"
        print("  PASS: Severity-4 finding without Human Approved correctly rejected (E-PARSE-008)")


def test_approval_requires_approver_name():
    """
    Test 8 (v1.3.0): a finding with "Human Approved: Yes" but no "Approved By"
    must be rejected -- a bare approval flag with no accountable name isn't a
    real approval record. Mirrors test_major_finding_requires_approval's
    approach: mutate the real fixture, confirm rejection for the RIGHT reason.
    """
    base = REAL_MANIFEST_PATH.read_text(encoding="utf-8")
    unattributed = base.replace("**Approved By:** Test Fixture Approver\n", "", 1)
    assert "Approved By" not in unattributed, "fixture mutation failed -- test is broken"
    assert "**Human Approved:** Yes" in unattributed, "fixture mutation removed the wrong line"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_path = tmp_path / "unattributed_manifest.md"
        output_path = tmp_path / "should_not_exist.json"
        manifest_path.write_text(unattributed, encoding="utf-8")

        result = run_script("manifest_to_findings.py", [
            "--manifest", str(manifest_path), "--output", str(output_path),
        ])
        combined = result.stdout + result.stderr

        assert result.returncode != 0, "Yes-approved finding without Approved By was NOT rejected"
        assert "E-PARSE-009" in combined, (
            f"rejected, but not for the missing-approver reason:\n{combined}"
        )
        assert not output_path.exists(), "findings.json must not be written on validation failure"
        print("  PASS: 'Human Approved: Yes' without Approved By correctly rejected (E-PARSE-009)")


def test_provenance_fallback():
    """
    Test 9 (v1.4.0): a Manifest with no Skill Version / Model header fields must
    NOT be rejected -- provenance is a soft-fallback header field (like
    charter_version), not a hard gate like Human Approved. Confirms both fields
    default to the literal string "unknown" rather than crashing, guessing a
    plausible-looking value, or blocking the audit.
    """
    base = REAL_MANIFEST_PATH.read_text(encoding="utf-8")
    stripped = base.replace("**Skill Version:** 1.13.0\n", "").replace("**Model:** claude-sonnet-5\n", "")
    assert "Skill Version" not in stripped and "Model" not in stripped, "fixture mutation failed -- test is broken"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_path = tmp_path / "no_provenance_manifest.md"
        output_path = tmp_path / "findings.json"
        manifest_path.write_text(stripped, encoding="utf-8")

        run_script_ok("manifest_to_findings.py", [
            "--manifest", str(manifest_path), "--output", str(output_path),
        ])
        data = json.loads(output_path.read_text(encoding="utf-8"))

        assert data["skill_version"] == "unknown", "missing skill_version must fall back to 'unknown'"
        assert data["model"] == "unknown", "missing model must fall back to 'unknown'"
        print("  PASS: missing Skill Version/Model correctly fall back to 'unknown', audit still completes")


def test_scope_limitation_render():
    """Test 6: real Halt Condition 6 notice (md) -> HTML, checking real content,
    not just that a file got written."""
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "notice.html"

        run_script_ok("render_scope_limitation.py", [
            "--notice", str(REAL_NOTICE_PATH),
            "--output-html", str(html_path),
        ])

        html_content = html_path.read_text(encoding="utf-8")

        assert "IEM-20260729-PA4001" in html_content
        assert "SCOPE LIMITED" in html_content

        # Both mandatory categories (A, E) must render as missing.
        assert html_content.count("status-missing") >= 2, "mandatory failures not rendered as missing"

        # All 7 categories present as table rows (7 data rows, not just the header).
        assert html_content.count("<tr>") >= 7

        # Mandatory Failures narrative and the cited artifact must survive parsing.
        assert "Mandatory Failures" in html_content
        assert "Project Management (1).csv" in html_content

        # Recommendation list (4 numbered items in the fixture) must all come through.
        assert html_content.count("Category A") >= 1 and html_content.count("Category E") >= 1

        print(f"  PASS: HTML notice: {len(html_content):,} chars, 7 categories, mandatory failures rendered")


def test_non_art_artifact_id_scheme():
    """Test: a Charter using a non-ART-NNN ID scheme (e.g. WK8-01, multi-segment) must
    still parse and validate. Regression for the real bug this fixture exercises: the
    parser/schema artifact_id pattern used to be hardcoded to ^ART-[0-9]{3}$, which
    silently dropped any '## ARTIFACT:' block using a different scheme -- caught in a
    real audit run (STATUS.md fix log), not by this suite, because every prior fixture
    only ever used ART-NNN IDs."""
    fixture = REAL_MANIFEST_PATH.read_text(encoding="utf-8")
    fixture = (
        fixture.replace("ART-001", "WK8-01")
        .replace("ART-002", "WK8-02")
        .replace("ART-003", "WK8-03")
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        manifest_path = tmp_dir / "test_manifest.md"
        manifest_path.write_text(fixture, encoding="utf-8")

        findings = _generate_findings(manifest_path, tmp_dir)

        artifact_ids = {a["artifact_id"] for a in findings["baseline"]["artifacts_examined"]}
        assert artifact_ids == {"WK8-01", "WK8-02", "WK8-03"}, (
            f"expected all 3 WK8-NN artifacts parsed, got {artifact_ids}"
        )
        evidence_ids = {
            ev["artifact_id"] for f in findings["findings"] for ev in f["evidence"]
        }
        assert evidence_ids <= {"WK8-01", "WK8-02", "WK8-03"}

        # Schema validation happens inside manifest_to_findings.py itself (run_script_ok
        # already asserted a zero exit code) -- also assert on the output directly so a
        # future change that starts silently swallowing schema errors is still caught.
        schema = json.loads(
            (SCRIPTS_DIR / "findings.schema.json").read_text(encoding="utf-8")
        )
        import jsonschema
        jsonschema.validate(findings, schema)

        print(f"  PASS: non-ART-NNN ID scheme (WK8-01 style) parses and validates: {sorted(artifact_ids)}")


def main():
    print("=" * 60)
    print("IEM-PM Regression Test Suite")
    print("=" * 60)

    tests = [
        ("Manifest -> JSON", test_manifest_to_findings),
        ("Schema Validation", test_schema_validation),
        ("JSON -> Reports", test_rendering),
        ("Timing Log", test_timing_log),
        ("Default Output Location", test_default_output_location),
        ("Knowledge Index", test_knowledge_index),
        ("Duplicate Detection", test_duplicate_detection),
        ("Major Finding Requires Approval", test_major_finding_requires_approval),
        ("Approval Requires Approver Name", test_approval_requires_approver_name),
        ("Provenance Fallback", test_provenance_fallback),
        ("Scope Limitation Notice Render", test_scope_limitation_render),
        ("Non-ART Artifact ID Scheme", test_non_art_artifact_id_scheme),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    print("All regression tests passed.")


if __name__ == "__main__":
    main()
