---
Name: Scoring
description: >
  Severity assignment (1-5), the Reporting Integrity Score boundary, Intelligence Indicators
  narrative rules, the no-maturity-modeling scope boundary, and the You-Write vs Software-Computes
  table. Read during Stage 6 (Engineer & Score) before assigning severity or writing Synthesis.
version: 1.0.0
---

## Contents

- [9.1 Severity (1–5) — You assign this](#91-severity-15--you-assign-this)
- [9.2 Reporting Integrity Score (0–100) — You do NOT calculate this](#92-reporting-integrity-score-0100--you-do-not-calculate-this)
- [9.3 Intelligence Indicators — Narrative only](#93-intelligence-indicators--narrative-only)
- [9.4 Scope Boundary: No Maturity Modeling](#94-scope-boundary-no-maturity-modeling)
- [9.5 What You Write vs. What Software Writes](#95-what-you-write-vs-what-software-writes)

## 9.1 Severity (1–5) — You assign this

Every finding gets a severity rating. This is your judgment. Use the full scale.

| Severity | Label    | Definition                                                                                                  | When to Apply                                                                                                                                                         |
| -------- | -------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | Cosmetic | The gap exists but has no material impact on delivery capability or decision quality.                       | A field is inconsistently formatted but the data is readable and usable. A template has a typo in the header.                                                         |
| 2        | Minor    | The gap causes friction, rework, or confusion but does not threaten delivery outcomes.                      | Status reports lack a required section but the missing data is available elsewhere. A governance pack is late by one day.                                             |
| 3        | Moderate | The gap degrades a specific process or decision but does not cascade to other processes.                    | Risk register lacks mitigation plans for 20% of risks. Baseline exists but was approved after work began.                                                             |
| 4        | Major    | The gap threatens delivery outcomes, breaks a critical process, or creates significant compliance exposure. | No earned value measurement on a fixed-price contract. Steering committee has not met in 6 months on a critical program. RAID log is missing all high-severity risks. |
| 5        | Critical | The gap threatens program/portfolio failure, regulatory breach, or strategic objective collapse.            | No baseline exists for any project in the portfolio. Financial controls are bypassed. Governance packs are fabricated or backdated.                                   |

The three factors behind the calibration rules below — delivery threat, spread, and persistence —
are formalized into a scored, PMI-cited rubric in `references/severity-matrix.md` (Appendix D).
Read it for the fully worked-out version of this judgment call. The 1–5 field above stays the one
the Manifest/schema/RIS actually consume; Appendix D is calibration reference, not a parsed input.

### Severity Calibration Rules

- **Base on delivery threat, not documentation completeness.** A missing signature on a low-value project is not Severity 5. A missing baseline on a strategic program is.
- **Consider spread.** A gap affecting one project is lower severity than the same gap affecting all projects in a portfolio.
- **Consider persistence.** A one-time error is lower severity than a gap that has existed across multiple reporting periods.
- **Never average.** If a gap is sometimes Severity 2 and sometimes Severity 4 depending on context, split it into two findings — one per context.

---

## 9.2 Reporting Integrity Score (0–100) — You do NOT calculate this

This score is computed **deterministically by software** from your findings. You do not assign it. You do not estimate it.

Software calculates it from:

- Gap density (findings per artifact)
- Severity distribution
- Root cause diversity
- Missing gap penalties

You will see the score in the rendered report. You do not produce it.

---

## 9.3 Intelligence Indicators — Narrative only

In the Synthesis section of your Audit Manifest, provide qualitative diagnostics for seven dimensions:

| Dimension                  | What to Describe                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------ |
| **Visibility**             | Can the organization see its delivery state accurately and in time?                  |
| **Integrity**              | Is the delivery data trustworthy, consistent, and verifiable?                        |
| **Connectivity**           | Do processes, data, and decisions flow between artifacts and teams?                  |
| **Governance**             | Are decisions made at the right level, with the right evidence, by the right people? |
| **Predictability**         | Can the organization forecast outcomes based on current data?                        |
| **Decision Quality**       | Are decisions supported by evidence, or made despite it?                             |
| **Continuous Improvement** | Does the organization learn from delivery and adapt its standards?                   |

**Rules:**

- These are **narrative only**. Never assign scores, percentages, grades, or color codes.
- One paragraph per dimension. Specific observations from your findings.
- If a dimension has no relevant findings, state: "No significant evidence observed."
- A positive claim ("X traces consistently," "figures match") needs the same grounding a Finding
  does — only assert it for what Stage 3's self-consistency check (`audit-stages.md` Stage 3
  Activity 3) actually verified, not as a general impression of a well-formed artifact.

---

## 9.4 Scope Boundary: No Maturity Modeling

IEM-PM measures and traces gaps. It does not model organizational maturity — not PMI's OPM3, not any other maturity scale.

Maturity modeling is a distinct discipline from gap auditing: it requires calibration across many audits and a licensed assessment instrument, neither of which IEM-PM provides. Extrapolating a maturity level from one audit's gap profile would be exactly the kind of unearned inference Principle 2 (Evidence First) forbids — it isn't a finding, it's a guess dressed up as a score.

Your Synthesis section ends at the seven Intelligence Indicators (§9.3). Do not add a maturity statement, an OPM3 position, or any other capability-level claim.

---

## 9.5 What You Write vs. What Software Writes

| Element                             | You Write | Software Computes |
| ------------------------------------ | --------- | ----------------- |
| Severity per finding                | ✓         |                   |
| Reporting Integrity Score           |           | ✓                 |
| Intelligence Indicators narrative   | ✓         |                   |
| Intelligence Indicators score/grade |           | ✗ (never scored)  |
| Gap density                         |           | ✓                 |
| Severity distribution               |           | ✓                 |
