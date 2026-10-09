# IEM-PM Audit Manifest

**Audit ID:** IEM-20260726-TEST01
**Charter Version:** v1.0.0
**Standards Baseline:** PMBOK 8th Edition; Standard for Risk Management in Portfolios, Programs, and Projects
**Scope:** Projects; Programs
**Analyst:** IEM-PM Intelligence Engine
**Date:** 2026-07-26T11:30:00-05:00
**Status:** RATIFIED
**Skill Version:** 1.13.0
**Model:** claude-sonnet-5

## ARTIFACT: ART-001

**Artifact Name:** Project Schedule
**Path:** /data/schedules/schedule.mpp
**Checksum:** a1b2c3d4e5f6
**Status:** Examined
**Field Coverage:** 85%
**Observations:** Schedule contains tasks, durations, and actual dates. Baseline_start and baseline_finish fields are null in all rows. No earned value calculations present.

## ARTIFACT: ART-002

**Artifact Name:** RAID Log
**Path:** /data/raid/raid.xlsx
**Checksum:** b2c3d4e5f6g7
**Status:** Examined
**Field Coverage:** 92%
**Observations:** RAID log fully populated with 23 risks. All fields present. No links to issues or changes. Steering packs show no risk-based decisions.

## ARTIFACT: ART-003

**Artifact Name:** Governance Pack
**Path:** /data/governance/pack.pdf
**Checksum:** c3d4e5f6g7h8
**Status:** Examined
**Field Coverage:** 39 of 50 declared columns present
**Observations:** Governance pack produced monthly. Baseline approval section is blank.

### FINDING: FIND-0001

**Gap Type:** Missing
**Root Origin:** Capture
**Standard:** PMBOK 8th Edition
**Clause:** 6.4.2.3
**Identifier:** Process 6.4
**Requirement Summary:** A schedule baseline must be established and approved before work begins.
**Description:** The project schedule file (ART-001) contains task start dates and durations, but no baseline_start or baseline_finish fields are populated. The Charter defines these as required fields for schedule artifacts. Without baseline dates, schedule variance cannot be calculated, and earned value measurement is impossible.
**Severity:** 4
**Human Approved:** Yes
**Approved By:** Test Fixture Approver
**Approval Date:** 2026-07-26
**Impact:** Inability to measure schedule performance exposes the project to undetected delays and prevents accurate forecasting for portfolio reporting.
**Recommended Action:** Establish and approve a schedule baseline before the next reporting period. Assign Ownership accountability for baseline maintenance.
**Intelligence Dimensions:** Predictability, Visibility

- **Artifact:** ART-001 | **Location:** Schedule.xlsx, Column D, all 47 rows | **Evidence:** Field `baseline_start` is null across all rows. Field `baseline_finish` is null across all rows.
- **Artifact:** ART-003 | **Location:** Governance Pack, Page 4 | **Evidence:** "Schedule baseline approved: [blank]" — no date, no signature.

### FINDING: FIND-0002

**Gap Type:** Underutilized
**Root Origin:** Behavior
**Standard:** PMBOK 8th Edition
**Clause:** 11.7.2.3
**Identifier:** Process 11.7
**Requirement Summary:** Risk data must inform governance decisions and steering committee reviews.
**Description:** The RAID log (ART-002) contains 23 active risks with complete mitigation plans. However, the last 6 steering packs contain zero references to any risk. The project manager updates the log weekly but the data is never used in governance. Risks are collected but not acted upon.
**Severity:** 3
**Impact:** Governance makes decisions without visibility of active risks, increasing probability of unmanaged threats materializing.
**Recommended Action:** Mandate risk review as a standing agenda item in every steering committee. Link top 5 risks to every steering pack.
**Intelligence Dimensions:** Governance, Decision Quality

- **Artifact:** ART-002 | **Location:** RAID.xlsx, Tab "Risks", all 23 rows | **Evidence:** All 23 risks have status=Open, mitigation_plan populated, owner assigned.
- **Artifact:** ART-002 | **Location:** Steering Pack, last 6 months | **Evidence:** Zero risk references in any pack. No risk-based decisions recorded.

## SYNTHESIS

### Visibility

Project status is partially visible but baseline absence creates blind spots for variance tracking. Risk data exists but is invisible to governance.

### Integrity

Schedule data exists but cannot be trusted for performance measurement without baseline. RAID log is complete and consistent.

### Connectivity

Risk data does not flow to steering packs. Schedule data does not flow to portfolio dashboard.

### Governance

Governance packs are produced but lack baseline approval evidence and risk review. Decisions are made without full evidence.

### Predictability

Severely degraded due to missing baseline — forecast accuracy is unmeasurable. Risk-based forecasting is absent.

### Decision Quality

Decisions are made without earned value data and without risk visibility, reducing evidence basis.

### Continuous Improvement

No evidence of lessons learned feeding into schedule planning or risk process improvement.

## APPENDIX

**Schema Version:** 1.0.0
**Canonical JSON:** To be generated by software from this manifest
**Total Findings:** 2
**Artifacts Examined:** ART-001, ART-002
**Standards Referenced:** PMBOK 8th Edition
