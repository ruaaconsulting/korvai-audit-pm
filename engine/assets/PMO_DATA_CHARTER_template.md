---
name: PMO Data Charter
description:
  > The authoritative data-interpretation contract for IEM-PM audits.
  Defines what the data is, what its fields mean, and what matters.
  Machine-proposed, human-ratified. Without ratification, no audit.
version: 1.0.1
---

# PMO Data Charter

> **This is Contract 2.** It is not the baseline — the Standards in `knowledge/` are the baseline.
> This Charter is the lens through which the audit interprets delivery evidence.
>
> **Rule:** No ratified Charter → no comparison. Never guess what the data means.

---

## Charter Metadata

| Field               | Value                                          |
| ------------------- | ---------------------------------------------- |
| **Organization**    | [ORGANIZATION NAME]                            |
| **Charter Version** | v1.0.0                                         |
| **Audit Scope**     | [Projects / Programs / Portfolios / PMO / All] |
| **Ratified By**     | [NAME, ROLE]                                   |
| **Ratified Date**   | [YYYY-MM-DD]                                   |
| **Charter Status**  | [RATIFIED / PROVISIONAL]                       |
| **Proposed By**     | IEM-PM Intelligence Engine                     |
| **Proposal Date**   | [YYYY-MM-DD]                                   |

---

## 1. Artifact Declaration

Every artifact in scope for this audit. The machine proposes this list from the data you supply. You ratify, correct, or waive each item.

### 1.1 Artifact Inventory

| Artifact ID | Artifact Name        | Source Location       | Format                    | Materiality | Status                        |
| ----------- | -------------------- | --------------------- | ------------------------- | ----------- | ----------------------------- |
| ART-001     | Project Schedule     | `/data/schedules/`    | MS Project / XML / XLSX   | Critical    | [In Scope / Waived / Missing] |
| ART-002     | RAID Log             | `/data/raid/`         | Excel / CSV               | Critical    | [In Scope / Waived / Missing] |
| ART-003     | Governance Pack      | `/data/governance/`   | PDF / DOCX                | Critical    | [In Scope / Waived / Missing] |
| ART-004     | Portfolio Dashboard  | `/data/portfolio/`    | JSON / Excel / Power BI   | High        | [In Scope / Waived / Missing] |
| ART-005     | Financial Report     | `/data/finance/`      | Excel / CSV               | High        | [In Scope / Waived / Missing] |
| ART-006     | Status Report        | `/data/status/`       | PDF / Markdown / DOCX     | Medium      | [In Scope / Waived / Missing] |
| ART-007     | Lessons Learned      | `/data/lessons/`      | Word / Markdown           | Medium      | [In Scope / Waived / Missing] |
| ART-008     | Project Charter      | `/data/charters/`     | PDF / DOCX                | Critical    | [In Scope / Waived / Missing] |
| ART-009     | Risk Register        | `/data/risk/`         | Excel / CSV / Tool Export | Critical    | [In Scope / Waived / Missing] |
| ART-010     | Issue Log            | `/data/issues/`       | Excel / Jira Export       | High        | [In Scope / Waived / Missing] |
| ART-011     | Change Log           | `/data/changes/`      | Excel / Tool Export       | High        | [In Scope / Waived / Missing] |
| ART-012     | Decision Log         | `/data/decisions/`    | Excel / DOCX              | Medium      | [In Scope / Waived / Missing] |
| ART-013     | Benefits Register    | `/data/benefits/`     | Excel                     | Medium      | [In Scope / Waived / Missing] |
| ART-014     | Stakeholder Register | `/data/stakeholders/` | Excel                     | Medium      | [In Scope / Waived / Missing] |
| ART-015     | Communication Plan   | `/data/comms/`        | DOCX / PDF                | Low         | [In Scope / Waived / Missing] |

_Add or remove rows as needed. Every artifact in scope must have a unique ID (ART-XXX is the
convention used below; any PREFIX-SUFFIX scheme is accepted -- e.g. WK8-01, DOC-2026-08 -- as long
as it's used consistently across this Charter and the resulting Manifest)._

### 1.2 Artifact Waivers

If the Standards expect an artifact that you do not have, record the waiver here. Only waived artifacts are out of scope.

| Standard Requirement | Expected Artifact  | Waiver Reason                                 | Waived By | Date   |
| -------------------- | ------------------ | --------------------------------------------- | --------- | ------ |
| [e.g., PMBOK 8 §6.4] | Resource Histogram | "We use FTE tracking in the schedule instead" | [Name]    | [Date] |
|                      |                    |                                               |           |        |

_If an expected artifact is not waived and not supplied, it will surface as a **Missing** gap in the audit._

---

## 2. Field Semantics Map

For each artifact in scope, define what its significant fields mean. The machine proposes fields from the data. You ratify the definitions.

### 2.1 How to Read This Section

- **Field:** The column name, attribute, or data element as it appears in the artifact.
- **Type:** Data type (String, Date, Number, Enum, Boolean, Calculated).
- **Meaning:** The business definition. What does this field actually represent?
- **Nullability:** Can this field be empty? (NOT NULL / NULLABLE).
- **Business Rule:** Constraints, valid values, or derivation logic.
- **Standard Mapping:** Which standard requirement does this field satisfy?

### 2.2 ART-001: Project Schedule

| Field              | Type    | Meaning                           | Nullability | Business Rule                 | Standard Mapping |
| ------------------ | ------- | --------------------------------- | ----------- | ----------------------------- | ---------------- |
| `task_id`          | String  | Unique task identifier            | NOT NULL    | UUID or auto-increment        | PMBOK 8 §6.3     |
| `task_name`        | String  | Human-readable task description   | NOT NULL    | Max 255 chars                 | PMBOK 8 §6.3     |
| `baseline_start`   | Date    | Approved baseline start date      | NOT NULL    | Cannot be after actual_start  | PMBOK 8 §6.4     |
| `baseline_finish`  | Date    | Approved baseline finish date     | NOT NULL    | Used for variance calculation | PMBOK 8 §6.4     |
| `actual_start`     | Date    | Actual start date                 | NULLABLE    | NULL = not started            | PMBOK 8 §6.6     |
| `actual_finish`    | Date    | Actual finish date                | NULLABLE    | NULL = in progress            | PMBOK 8 §6.6     |
| `percent_complete` | Number  | Physical percent complete         | NOT NULL    | 0–100, no decimals            | PMBOK 8 §6.6     |
| `duration_days`    | Number  | Original duration in working days | NOT NULL    | > 0                           | PMBOK 8 §6.4     |
| `resource_names`   | String  | Assigned resources                | NULLABLE    | Comma-separated               | PMBOK 8 §9.2     |
| `milestone_flag`   | Boolean | Is this a milestone?              | NOT NULL    | TRUE/FALSE                    | PMBOK 8 §6.3     |

_Machine-proposed fields not listed above: [List any additional fields discovered in the data that are not yet mapped.]_

### 2.3 ART-002: RAID Log

| Field             | Type       | Meaning                        | Nullability | Business Rule                                      | Standard Mapping   |
| ----------------- | ---------- | ------------------------------ | ----------- | -------------------------------------------------- | ------------------ |
| `risk_id`         | String     | Risk registry identifier       | NOT NULL    | Format: RSK-YYYY-NNNN                              | Std Risk Mgmt §3.2 |
| `risk_title`      | String     | Short description of the risk  | NOT NULL    | Max 200 chars                                      | Std Risk Mgmt §3.2 |
| `category`        | Enum       | Risk category per org taxonomy | NOT NULL    | Technical, Financial, Schedule, Resource, External | Std Risk Mgmt §4.1 |
| `probability`     | Integer    | Likelihood 1–5                 | NOT NULL    | 1=Rare, 5=Almost Certain                           | Std Risk Mgmt §4.2 |
| `impact`          | Integer    | Impact 1–5                     | NOT NULL    | 1=Negligible, 5=Catastrophic                       | Std Risk Mgmt §4.2 |
| `risk_score`      | Calculated | Probability × Impact           | NOT NULL    | Auto-calculated, 1–25                              | Std Risk Mgmt §4.2 |
| `owner_email`     | String     | Risk owner                     | NOT NULL    | Must be active directory user                      | Std Risk Mgmt §5.1 |
| `mitigation_plan` | String     | Planned response               | NOT NULL    | Required for all risks score > 12                  | Std Risk Mgmt §5.2 |
| `status`          | Enum       | Current state                  | NOT NULL    | Open / Closed / Transferred / Avoided              | Std Risk Mgmt §5.3 |
| `target_date`     | Date       | Mitigation target date         | NULLABLE    | Required if status=Open                            | Std Risk Mgmt §5.2 |
| `linked_issue_id` | String     | Related issue reference        | NULLABLE    | Must match Issue Log issue_id                      | Std Risk Mgmt §5.4 |

_Machine-proposed fields not listed above: [List any additional fields discovered.]_

### 2.4 ART-003: Governance Pack

| Field                    | Type    | Meaning                           | Nullability | Business Rule                                | Standard Mapping   |
| ------------------------ | ------- | --------------------------------- | ----------- | -------------------------------------------- | ------------------ |
| `pack_date`              | Date    | Reporting period end date         | NOT NULL    | Last day of reporting period                 | Gov Framework §3.1 |
| `project_id`             | String  | Project identifier                | NOT NULL    | Must match Charter                           | Gov Framework §3.1 |
| `rag_status`             | Enum    | Overall health                    | NOT NULL    | Red / Amber / Green / Blue                   | Org Std-PM-01      |
| `budget_variance_pct`    | Number  | (Actual - Baseline) / Baseline    | NOT NULL    | -∞ to +∞, 2 decimals                         | PMBOK 8 §7.4       |
| `schedule_variance_days` | Number  | Baseline finish - Forecast finish | NOT NULL    | Negative = behind                            | PMBOK 8 §6.6       |
| `top_risks_count`        | Integer | Number of risks in pack           | NOT NULL    | ≥ 0                                          | Std Risk Mgmt §6.1 |
| `steering_decisions`     | String  | Decisions made this period        | NULLABLE    | List with decision ID, description, approver | Gov Framework §4.2 |
| `next_review_date`       | Date    | Next steering committee date      | NOT NULL    | Must be within 30 days                       | Gov Framework §3.2 |
| `approved_by`            | String  | Pack approver                     | NOT NULL    | Must be named sponsor                        | Gov Framework §4.1 |

### 2.5 Unmapped Fields

Fields discovered in the data but not defined in this Charter:

| Artifact ID | Field Name      | Machine Proposal              | Human Disposition          |
| ----------- | --------------- | ----------------------------- | -------------------------- |
| ART-001     | `float_days`    | "Total float in working days" | [Accept / Reject / Rename] |
| ART-002     | `risk_age_days` | "Days since risk was opened"  | [Accept / Reject / Rename] |
|             |                 |                               |                            |

_Unmapped fields will not be interpreted by the audit. They may be noted in the Evidence Log but will not drive findings._

---

## 3. Materiality and Scope

### 3.1 Organizational Scope

| Element                     | Definition                                           |
| --------------------------- | ---------------------------------------------------- |
| **Business Units Included** | [List]                                               |
| **Business Units Excluded** | [List, with reason]                                  |
| **Portfolios in Scope**     | [List or "All active portfolios"]                    |
| **Programs in Scope**       | [List or "All programs under included portfolios"]   |
| **Projects in Scope**       | [List or "All projects active within last 90 days"]  |
| **PMO Functions in Scope**  | [Governance / Reporting / Methodology / Tools / All] |

### 3.2 Time Horizon

| Element                  | Definition                                               |
| ------------------------ | -------------------------------------------------------- |
| **Audit As-Of Date**     | [YYYY-MM-DD]                                             |
| **Lookback Period**      | [e.g., 90 days / Current fiscal year / Project lifetime] |
| **Baseline Review Date** | [YYYY-MM-DD]                                             |

### 3.3 Materiality Thresholds

| Threshold                        | Value                      | Rationale                                                    |
| -------------------------------- | -------------------------- | ------------------------------------------------------------ |
| **Minimum Project Value**        | $[Amount]                  | Projects below this value are excluded                       |
| **Minimum Strategic Importance** | [Critical / High / Medium] | Projects below this rating are excluded                      |
| **Budget Variance Threshold**    | [±X%]                      | Variances below this are not findings                        |
| **Schedule Variance Threshold**  | [±X days]                  | Variances below this are not findings                        |
| **Risk Score Threshold**         | [Score]                    | Risks below this score are not individually audited          |
| **Field Completeness Threshold** | [X%]                       | Artifacts missing >X% of required fields trigger Missing gap |
| **Maximum Artifact Age**         | [X days]                   | Artifacts older than X days are flagged as stale             |

### 3.4 Governance Levels

| Level                      | In Scope | Standard Reference |
| -------------------------- | -------- | ------------------ |
| Portfolio Board            | Yes / No | [Standard clause]  |
| Program Steering Committee | Yes / No | [Standard clause]  |
| Project Steering Committee | Yes / No | [Standard clause]  |
| PMO Office                 | Yes / No | [Standard clause]  |
| Project Team               | Yes / No | [Standard clause]  |

---

## 4. Propose → Ratify

### 4.1 Machine Proposals

The IEM-PM engine proposed the following based on its analysis. Review each item.

#### Proposed Artifacts (from data discovery)

| Artifact ID | Artifact Name          | Source | Proposal Confidence | Proposed From |
| ----------- | ---------------------- | ------ | ------------------- | ------------- |
| ART-016     | [Discovered file name] | [Path] | High / Medium / Low | Data scan     |
|             |                        |        |                     |               |

#### Proposed Fields (from data discovery)

| Artifact ID | Field Name | Proposed Meaning | Proposed From |
| ----------- | ---------- | ---------------- | ------------- |
|             |            |                  | Data scan     |

#### Proposed Scope (from standards expectations)

| Standard     | Expected Artifact / Process | Found in Data? | Proposed Disposition   |
| ------------ | --------------------------- | -------------- | ---------------------- |
| PMBOK 8 §6.4 | Baseline schedule approval  | Yes / No       | In Scope / Missing gap |
| PMBOK 8 §7.4 | Earned value measurement    | Yes / No       | In Scope / Missing gap |
|              |                             |                |                        |

### 4.2 Human Ratification

By signing below, the ratifier confirms:

1. The Artifact Declaration accurately represents the delivery data available for this audit.
2. The Field Semantics Map correctly defines what each field means for this organization.
3. The Materiality and Scope boundaries are appropriate and derived from authoritative standards.
4. All waivers are documented and approved.
5. Any PROVISIONAL status is acknowledged, and findings will carry the unratified-interpretation caveat.

> **Ratification Statement:**
> "I confirm this Charter accurately describes our delivery data, its meaning, and what matters. I understand that the audit will compare this data against our declared standards, and any variance will be classified as a gap."
>
> **Name:** ****\*\*\*\*****\_****\*\*\*\*****
> **Role:** ****\*\*\*\*****\_\_****\*\*\*\*****
> **Signature:** ****\*\*****\_****\*\*****
> **Date:** ****\*\*\*\*****\_\_****\*\*\*\*****

---

## 5. Anti-Mirror Guard

This Charter enforces the anti-mirror guard:

| Charter Function     | Derived From                                         | Safe?                                                          |
| -------------------- | ---------------------------------------------------- | -------------------------------------------------------------- |
| Artifact Declaration | **Data** — what the organization actually supplied   | ✅ Safe — reading the data to understand the data              |
| Field Semantics Map  | **Data** — what fields exist and what they contain   | ✅ Safe — reading the data to understand the data              |
| Materiality & Scope  | **Standards** — what the standards expect to see     | ✅ Safe — standards define expectations, not observed behavior |
| Waivers              | **Human judgment** — explicit out-of-scope decisions | ✅ Safe — only human-waived items are out of scope             |

**The Guard:** If Materiality and Scope were inferred from what the data contains, the audit could only confirm what was supplied. A **Missing** gap could never surface. Therefore, scope is proposed from the standards' expectations, never from the data alone.

---

## 6. Charter Change Control

Once ratified, this Charter is immutable for the audit run. Changes require:

1. A new Charter version (v1.0.1, v1.1.0, etc.).
2. Re-ratification by the same or higher authority.
3. Re-running Stage 1 (Charter) of the audit.

**Emergency changes:** If new data is discovered mid-audit that invalidates the Charter, the audit halts. The Charter is updated and re-ratified. Findings from the prior run are discarded.

---

## 7. Appendix

### 7.1 Declared Standards

| Standard Name   | Version / Edition | Location in `knowledge/`    | Applicability                     |
| --------------- | ----------------- | --------------------------- | --------------------------------- |
| [e.g., PMBOK]   | 8th Edition       | `knowledge/PMBOK/`          | All projects                      |
| [e.g., Org PMM] | v2.3              | `knowledge/Organizational/` | Overrides PMBOK where conflicting |
|                 |                   |                             |                                   |

### 7.2 Glossary

| Term                | Definition (for this audit) |
| ------------------- | --------------------------- |
| [Org-specific term] | [Definition]                |
|                     |                             |

### 7.3 Assumptions

| #   | Assumption                                     | Impact if Wrong                                  |
| --- | ---------------------------------------------- | ------------------------------------------------ |
| 1   | [e.g., "All schedules use 5-day working week"] | [e.g., "Duration calculations may be incorrect"] |
|     |                                                |                                                  |

### 7.4 Known Limitations

| #   | Limitation                                                 | Mitigation                              |
| --- | ---------------------------------------------------------- | --------------------------------------- |
| 1   | [e.g., "Primavera exports are PDF-only; no XML available"] | [e.g., "Manual field mapping required"] |
|     |                                                            |                                         |
