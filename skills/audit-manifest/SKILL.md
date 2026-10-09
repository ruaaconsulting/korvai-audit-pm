---
name: audit-manifest
description: The parser-grade Audit Manifest format (SKILL.md section 10.2). Read this at Stage 7 (Synthesize) before writing the Audit Manifest. Follow it exactly; software parses it.
---

## Format Rules (parser-grade)

Follow these rules exactly. Software parses this file with regex and markdown parsers.

### Header Block Template

```markdown
# IEM-PM Audit Manifest

**Audit ID:** IEM-YYYYMMDD-XXXXXX
**Charter Version:** vX.X.X
**Standards Baseline:** [Standard1; Standard2; ...]
**Scope:** [Projects; Programs; Portfolios; PMO]
**Analyst:** IEM-PM Intelligence Engine
**Date:** [ISO-8601]
**Status:** [RATIFIED / PROVISIONAL]
**Skill Version:** [This skill's own version, read directly from SKILL.md §13.4 — never guessed]
**Model:** [The AI model actually running this audit, per your own system context, e.g. claude-sonnet-5 — never a guess; write "unknown" if you genuinely cannot state it]

Separate list items with `;`, not `,` — full standard titles routinely contain commas of their
own (e.g. "Standard for Risk Management in Portfolios, Programs, and Projects"), and a
comma-separated list cannot be split back apart unambiguously once that happens. The parser
(`manifest_to_findings.py`) splits both fields on `;`.

`Skill Version` and `Model` exist so that if two audits of the same evidence produce different
findings, it's possible to tell whether that's a real inconsistency or simply two different
model/skill versions doing the analysis (v1.4.0 — provenance, not a taxonomy or scoring change).
If either is genuinely unavailable, write "unknown" rather than fabricate a plausible-looking
value — software falls back to "unknown" itself if the field is missing entirely.

### Per-Artifact Evidence Log Template

For every artifact declared in the Charter, write:

## ARTIFACT: [ART-XXX]

**Artifact Name:** [Human-readable name]
**Path:** [file path]
**Checksum:** [Real SHA-256 of the artifact file — compute it, never write the literal word
"computed" as a stand-in value. A placeholder that isn't a real hash defeats Stage 1 Activity 2's
checksum-based prior-audit lookup for every future run against this evidence.]
**Status:** [Examined / Partial / Corrupted / Empty]
**Field Coverage:** [N of M declared columns present (X%)]
**Observations:** [Narrative of what you found, field completeness, anomalies]

The `(X%)` figure is mandatory, not optional narration — the parser needs an explicit percentage
(or an "N of M" count it can compute one from) to populate `field_coverage_pct`. A prose-only
count with no percentage and no "of" phrasing cannot be parsed and will be dropped.

### Finding Block Template

One block per gap. This is the parser's critical section.

### FINDING: FIND-NNNN

**Gap Type:** [Missing | Ignored | Disconnected | Untrusted | Underutilized | Misclassified | Divergent]
**Root Origin:** [Capture | Integration | Definition / Taxonomy | Ownership | Process / Cadence | Tooling | Behavior]
**Standard:** [Standard name]
**Clause:** [Clause reference]
**Identifier:** [Process/Practice ID]
**Requirement Summary:** [One-sentence paraphrase — never full text]
**Description:** [What you found and why it violates the standard — minimum 20 words]
**Severity:** [1 | 2 | 3 | 4 | 5]
**Human Approved:** [Yes | No — required only if Severity is 4 or 5]
**Approved By:** [Name/role of the human who approved — required only if Human Approved is Yes]
**Approval Date:** [When they gave that approval, in their own words — required only if Human Approved is Yes]
**Impact:** [Narrative impact on delivery capability]
**Recommended Action:** [Specific, actionable remediation addressing the root origin]
**Intelligence Dimensions:** [Visibility, Integrity, ... comma-separated]

- **Artifact:** [ART-XXX] | **Location:** [Sheet/Page/Line/Cell] | **Evidence:** [Direct quote or explicit absence statement]
- **Artifact:** [ART-XXX] | **Location:** [Sheet/Page/Line/Cell] | **Evidence:** [Direct quote or explicit absence statement]
```

Rules for Finding Blocks:

- Every finding must have at least one evidence bullet.
- Every evidence bullet must reference an artifact declared in the Charter.
- Gap Type and Root Origin must match the closed taxonomies exactly (case-sensitive).
- Severity must be an integer 1–5.
- If Severity is 4 or 5, Human Approved is mandatory (v1.2.0). Do not write "Yes" on your own
  authority — surface the finding to the human operator in plain terms and record their actual
  response. Writing "Yes" without having actually asked is a fabricated approval, not a
  shortcut: the whole point of this gate is that a real person, not the model, confirms a
  Major or Critical finding before it becomes final. A manifest with a Severity 4/5 finding and
  no Human Approved field is rejected outright (`E-PARSE-008`).
- If Human Approved is Yes, Approved By and Approval Date are mandatory (v1.3.0). "Human
  Approved: Yes" with no name attached is a bare flag, not an audit trail — record who actually
  said yes and when, in their own words (a real timestamp isn't required; "confirmed in-session"
  is fine). A finding with Human Approved: Yes and no Approved By is rejected outright
  (`E-PARSE-009`).
- Requirement Summary is one sentence maximum. Never reproduce standard text.
- Description must be at least 20 words.
- Recommended Action must address the root origin, not the symptom.

### Example: Complete Finding Block

### FINDING: FIND-0001

**Gap Type:** Missing
**Root Origin:** Capture
**Standard:** PMBOK 7th Edition
**Clause:** 6.4.2.3
**Identifier:** Process 6.4 — Develop Schedule
**Requirement Summary:** A schedule baseline must be established and approved before work begins.
**Description:** The project schedule file (ART-001) contains task start dates and durations, but no baseline_start or baseline_finish fields are populated. The Charter defines these as required fields for schedule artifacts. Without baseline dates, schedule variance cannot be calculated, and earned value measurement is impossible.
**Severity:** 4
**Human Approved:** Yes
**Approved By:** Ramani Viswanathan, PMO Director
**Approval Date:** Confirmed in-session, 2026-08-16
**Impact:** Inability to measure schedule performance exposes the project to undetected delays and prevents accurate forecasting for portfolio reporting.
**Recommended Action:** Establish and approve a schedule baseline before the next reporting period. Assign Ownership accountability for baseline maintenance (addresses Root Origin: Capture → Ownership).
**Intelligence Dimensions:** Predictability, Visibility

- **Artifact:** ART-001 | **Location:** Schedule.xlsx, Column D, all 47 rows | **Evidence:** Field `baseline_start` is null across all rows. Field `baseline_finish` is null across all rows.
- **Artifact:** ART-003 | **Location:** Governance Pack, Page 4 | **Evidence:** "Schedule baseline approved: [blank]" — no date, no signature.

### Synthesis Section Template

## SYNTHESIS

### Visibility

[Narrative diagnostic only. No scores, percentages, or grades.]

### Integrity

[Narrative diagnostic only. No scores, percentages, or grades.]

### Connectivity

[Narrative diagnostic only. No scores, percentages, or grades.]

### Governance

[Narrative diagnostic only. No scores, percentages, or grades.]

### Predictability

[Narrative diagnostic only. No scores, percentages, or grades.]

### Decision Quality

[Narrative diagnostic only. No scores, percentages, or grades.]

### Continuous Improvement

[Narrative diagnostic only. No scores, percentages, or grades.]

### Appendix Template

## APPENDIX

**Schema Version:** 1.0.0
**Canonical JSON:** [To be generated by software from this manifest]
**Total Findings:** [N]
**Artifacts Examined:** [List of artifact IDs, e.g. ART-XXX -- must match the Charter's declared scheme]
**Standards Referenced:** [List of standard names]
