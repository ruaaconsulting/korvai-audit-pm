---
notice_id: IEM-20260729-PA4001
type: Scope Limitation Notice
standards_declared:
  - PMI Standards (PMBOK 8th Edition, PMI Practice Guides)
audit_path: examples/pilot-audit-4/evidence/
artifact_count: 1
generated_at: 2026-07-29T00:00:00Z
status: SCOPE LIMITED — NO OPINION ISSUED
---

# IEM-PM Scope Limitation Notice

**Notice ID:** IEM-20260729-PA4001
**Standards Baseline:** PMI Standards (PMBOK 8th Edition, PMI Practice Guides)
**Evidence Path:** `examples/pilot-audit-4/evidence/`
**Generated:** 2026-07-29T00:00:00Z
**Status:** SCOPE LIMITED — NO OPINION ISSUED

---

## 1. Executive Summary

The IEM-PM audit of `examples/pilot-audit-4/evidence/` cannot proceed. The evidence set contains
one artifact — a CSV-format project tracking spreadsheet (`Project Management (1).csv`) covering
task-level data for multiple projects. While the artifact is readable, it fails the Minimum Evidence
Sufficiency Gate on two independent rules: it represents fewer than the minimum distinct artifact
count (Rule 3), and it is missing both mandatory categories — Authorization (Category A) and Risk
(Category E) — that PMI standards require any credible PMO audit to address (Rule 1). An audit
conducted on this evidence would have no authorization baseline to measure governance compliance
against, no risk data to assess uncertainty management, and would rest on a single self-contained
source that cannot independently verify its own claims. No Gap Register, no Reporting Integrity
Score, and no audit opinion can be issued.

---

## 2. Coverage Analysis

| Category | Domain | Status | Artifact(s) Mapped |
|---|---|---|---|
| A — Authorization *(Mandatory)* | Charter | **MISSING** | — |
| B — Scope | Scope | Present (partial) | Project Management (1).csv |
| C — Cost | Cost | Present (partial) | Project Management (1).csv |
| D — Schedule | Schedule | Present (partial) | Project Management (1).csv |
| E — Risk *(Mandatory)* | Risk | **MISSING** | — |
| F — Change Control | Change control | **MISSING** | — |
| G — Performance Monitoring | Reports | Present (partial) | Project Management (1).csv |

**4 of 7 categories nominally represented. 1 distinct artifact supplied.**

Note: Categories B, C, D, and G are marked "Present (partial)" because the CSV contains the
relevant fields (Start/End dates, Budget, Actual Cost, Progress %). These are not formal baseline
artifacts — they are operational data fields — but they constitute evidence that these domains are
at least partially tracked. The "partial" qualification is material: no scope statement, no cost
baseline, no approved schedule baseline, and no formal performance report is present.

---

## 3. Mandatory Failures

- **A — Authorization**: No project charter, program charter, governance authorization, or sponsor
  approval document has been supplied. The CSV contains project names, statuses, and priorities, but
  none of these constitute formal authorization of the endeavors under PMI standards, which require
  a documented charter that authorizes the project and establishes the project manager's authority
  (PMBOK 8th Edition, Performance Domain: Stakeholders; Process Group Practice Guide, Initiating
  Process Group). Without an authorization artifact, the audit cannot verify that any project
  exists within a governance framework, was formally chartered, or has an accountable sponsor.

- **E — Risk**: No risk register, risk log, RAID log, or any artifact containing risk identifiers,
  probability/impact assessments, risk owners, or response plans has been supplied. The CSV has no
  risk-related columns. PMI standards require that uncertainty be identified, analyzed, and owned
  throughout the project lifecycle (PMBOK 8th Edition, Performance Domain: Uncertainty; Practice
  Standard for Project Risk Management). Without a risk artifact, the audit cannot assess whether
  risks are captured, classified, owned, or mitigated.

---

## 4. Professional Opinion

The IEM-PM Intelligence Engine is unable to issue an audit opinion on the delivery performance of
the projects in scope. The evidence supplied — one multi-project task spreadsheet — is insufficient
to support a credible assessment of PMO compliance against PMI standards. An opinion formed on this
evidence would be materially misleading: it could not speak to authorization governance, risk
management, change control, or the independence of evidence across delivery processes. This notice
is issued in place of an audit opinion, consistent with the practice of a scope limitation
disclaimer under professional audit standards. The engine has not read delivery data beyond what
was necessary to classify the submitted artifact and assess coverage. No findings have been formed,
classified, or scored.

---

## 5. Recommendation

To proceed with a full IEM-PM PMO Data Gap audit against PMI standards, the following additional
artifacts are required at minimum:

1. **Category A — Authorization**: Supply at least one project charter or program charter for
   each project or program in scope. The charter must identify the project sponsor, authorize the
   project manager, and establish high-level scope and objectives. If individual project charters
   do not exist, a portfolio-level governance authorization document or PMO operating mandate
   may serve as a proxy — but its scope limitations must be declared in the Charter.

2. **Category E — Risk**: Supply a risk register or RAID log for at least one project in scope.
   The register must contain risk identifiers, probability/impact indicators, risk owners, and
   response or mitigation plans. A risk register that contains only open issues without risk-
   specific fields does not satisfy this category.

3. **Minimum artifact count (Rule 3)**: The audit requires at least 3 distinct artifacts across
   at least 3 distinct PMO process areas. The current CSV — however detailed — is a single source.
   Adding the charter (Category A) and risk register (Category E) as separate documents would
   bring the artifact count to 3, satisfy Rule 3, and simultaneously resolve the Rule 1 failures.
   Additional artifacts (status reports, change logs, lessons learned) are strongly recommended
   to enable a credible assessment of the full Performance Domain coverage.

4. **Scope clarification**: The CSV covers 50 projects spanning multiple project types, locations,
   and statuses. Before the audit begins, the user should confirm whether all 50 projects are in
   scope or whether a subset (by program, geography, or strategic priority) is intended. This will
   inform the materiality thresholds in the PMO Data Charter.

---

## 6. Next Step

Once the mandatory artifacts (Category A Authorization and Category E Risk) have been provided and
at least 3 distinct artifacts are available in `examples/pilot-audit-4/evidence/`, re-run the
IEM-PM skill. The engine will re-apply the sufficiency gate at Phase 0. If the gate is satisfied,
it will proceed to propose a PMO Data Charter for user ratification before beginning the audit.
If any remaining coverage gaps are present at that point (e.g., Change Control — Category F), they
will be reflected in the Charter's declared scope, and any standard-required artifacts absent from
the evidence will become candidate Missing gap findings in the audit itself.

---

*IEM-PM Intelligence Engine | Local-First Audit | Read-Only Analysis*
*No Gap Register. No Reporting Integrity Score. Generated: 2026-07-29T00:00:00Z*
