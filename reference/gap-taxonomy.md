---
name: gap-taxonomy
description: The Seven Gap Taxonomy — full definitions, detection logic, examples, and disambiguation rules for classifying PMO delivery gaps. Read during Stage 4 (Classify) before assigning any gap type.
version: 1.0.0
---

## The Seven Gap Taxonomy (closed) (Tells what is wrong?)

> Every finding belongs to exactly one of seven types. No overlap. No duplicates.
> Classification order: Missing → Ignored → Divergent → Disconnected →
> Untrusted → Underutilized → Misclassified. Test in this sequence.
> Stop at the first match.

| Gap           | Meaning                                 |
| ------------- | --------------------------------------- |
| Missing       | Required information absent             |
| Ignored       | Standard exists but not followed        |
| Disconnected  | Information exists but is isolated      |
| Untrusted     | Evidence cannot be verified             |
| Underutilized | Data collected but unused               |
| Misclassified | Wrong classification or taxonomy        |
| Divergent     | Delivery differs from required standard |

## Master Disambiguation Example — The Risk Register

The same artifact, the same standard, the same organization.
Only the problem changes.

A standard defines what SHOULD exist. If the delivery evidence doesn't have what the standard requires, that's a gap.

| Situation                                                         | Does it "not satisfy the standards"? | Gap Type          |
| ----------------------------------------------------------------- | ------------------------------------ | ----------------- |
| The Risk Register **doesn't exist at all**                        | Yes                                  | **Missing**       |
| The Risk Register exists but **nobody updates it**                | Yes                                  | **Ignored**       |
| The Risk Register exists but **isn't connected to governance**    | Yes                                  | **Disconnected**  |
| The Risk Register exists but **the data can't be verified**       | Yes                                  | **Untrusted**     |
| The Risk Register exists, is updated, but **nobody reads it**     | Yes                                  | **Underutilized** |
| The Risk Register exists but **risks are categorized wrong**      | Yes                                  | **Misclassified** |
| The Risk Register exists but **uses a 3×3 matrix instead of 5×5** | Yes                                  | **Divergent**     |

# Gap Classification

---

## 1 Missing — required information absent

### Definition

Missing means the required information does not exist. Not "exists but is wrong." Not "exists but is ignored." Does. Not. Exist.

### Detection

> Step 1: Check all the organization's delivery evidence
> Step 2: Review that with declared project management standards
> Step 3: Search by **Function** not by name (An org might call it a "Threat Log" instead of "Risk Register" — that's NOT Missing.)
> Step 4: If zero instances → check the Charter. Was it waived by the human?
> Step 5: If waived → out of scope, not a finding. If confirmed → Missing.

### Examples

**Example 1 — Risk Register (from Master Table):**
The Standard for Risk Management §3.2 requires a Risk Register.
A search of all declared artifacts finds zero instances.
No document, no system record, no spreadsheet, no field set functions as a risk register. The human confirmed this absence during Charter ratification.
→ **Missing.** The required artifact does not exist.

**Example 2 — Lessons Learned Register:**
PMBOK 8 expects lessons learned to be captured and maintained.
The organization has no lessons learned repository, no template, no log, and no process for capturing lessons.
→ **Missing.**

**Counter-example — NOT Missing:**
The standard expects a "Decision Log." The org has no document called "Decision Log." However, decisions are recorded in Steering Committee Minutes under "Resolutions." The artifact functionally exists under a different name.
→ **NOT Missing.** Possibly Disconnected or Misclassified — but not Missing.

### Common Misclassification Traps

| Trap                                                       | Why It's Wrong                                           | Correct Type                                             |
| ---------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| "The risk register is 8 months out of date" → Missing      | The register EXISTS. It's stale, not absent.             | **Ignored**                                              |
| "We track risks in Jira tickets, not a register" → Missing | The risk information EXISTS in a different format.       | **Not Missing** (possibly Disconnected or Misclassified) |
| "The template exists but nobody uses it" → Missing         | The template EXISTS. The practice of using it is absent. | **Ignored**                                              |

---

## 2 Ignored — standard exists but not followed

### Definition

The standard/rule/policy/process EXISTS. The practice does not follow it. Not performed. Not enforced. Not applied. Not maintained."Does. Exist. Not. Followed."

### Detection

> Step 1: Confirm the standard/rule/policy EXISTS in the organization's baseline or knowledge base.(If it doesn't exist → this is Missing, not Ignored. Go back to §7.1.)

> Step 2: Compare the registry criterion's expected evidence (from the applicability map, Stage 0) against the delivery evidence declared in the Charter. What artifact does the standard expect? Does ANY instance of it exist?

> Step 3: Examine the delivery evidence for conformance.

    - Is the practice being performed?
    - Is the output being produced?
    - Is the cadence being met?
    - Is the content meeting the standard?

> Step 4: If the practice DEVIATES from the rule:

    - Check for a documented tailoring decision or approved waiver.
        - If a valid waiver/tailoring EXISTS → NOT Ignored.
    - Governed deviation. Record as a tailoring note.
        - If NO waiver/tailoring exists → Ignored.

> Step 5: Assess the PATTERN:

- Isolated (one project, one cycle) → lower Persistence.
- Systematic (across projects, across cycles) → higher Persistence and Spread.

### Examples

**Example 1 — Risk Register (from Master Table):**
The Risk Register exists. It was created 14 months ago at project kickoff. It contains 6 risks, all dated to the initial workshop. No new risks have been added. No risk reviews have been recorded. No status updates appear in any of the last 8 reporting cycles. The register exists but has not been maintained.
→ **Ignored.** The standard requires ongoing maintenance.
The practice does not follow it.

**Example 2-: Weekly Status Report **
The Reporting Policy requires weekly status reports by Friday 5 PM. The policy exists. The template exists. Over 12 weeks, 4 reports are missing and 5 are late. The standard exists. The cadence is not followed.
→ **Ignored.**

**Example 3-: Project management Plan**
The PMBOK 8 standard expects a full Project Management Plan. The org's PMO Policy (§2.1) states: "Small projects (<$100K) shall use a Lightweight Brief in lieu of a full plan." Small projects use the Brief. This is a documented, approved tailoring decision.
→ **NOT Ignored**. Governed deviation. Not a finding.

### Common Misclassification Traps

| Trap                                                                     | Why It's Wrong                                                                                                                                                                                                                                                 | Correct Type                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| "Nobody follows the change control process" → Ignored (without checking) | First check: does the process document EXIST? If not → Missing.                                                                                                                                                                                                | **Depends on existence**                                    |
| "Teams use their own format instead of the template" → Ignored           | The critical distinction from Divergent: Ignored means the practice is NOT PERFORMED (the action doesn't happen). Divergent means the practice IS PERFORMED but produces a DIFFERENT RESULT than the standard requires. Test: Is the action being done at all? | If NO → Ignored. If YES but the output differs → Divergent. |
| "The governance board meets but skips risk review" → Ignored             | Correct — the specific required practice within the meeting is not performed.                                                                                                                                                                                  | **Ignored** ✅                                              |

---

## 3. Disconnected — Information exists but is isolated

### Definition

The data exists. It is captured correctly. But it lives in a silo — it does not reach the process, person, or system that needs it to make a decision or take action. The gap is not absence; it is broken flow.

### Detection

> Step 1: Confirm the data EXISTS in the source artifact. (If not → Missing. Go back to §1.)
> Step 2: Identify the downstream consumer of this data per the standard. Who or what needs this information next?
> Step 3: Check whether the data appears in the consumer's artifact, system, or process.
> Step 4: If the data is present in the source but absent in the consumer → Disconnected.
> Step 5: Assess the scope of disconnection:

- One artifact to one consumer → isolated.
- Multiple artifacts with no cross-references → systemic.

### Examples

**Example 1 — Risk Register to Issues (from Master Table):**
The RAID log contains 23 active risks with clear owners and mitigation plans. The Issue Log contains 8 issues, none of which reference a risk ID. The standard requires that issues triggered by risks be linked to their originating risk for traceability. The risk data exists. The issue data exists. The link does not.
→ Disconnected.

**Example 2 — Schedule to Financial Forecast:**
The project schedule shows a 6-week delay on a critical path task. The financial forecast (monthly) still assumes original delivery dates. No variance alert was sent from scheduling to finance. The schedule data exists. The forecast artifact exists. The connection does not.
→ Disconnected.

**Example 3 — Lessons Learned to New Projects:**
The Lessons Learned register contains 14 entries from completed projects. Three new projects started in the last quarter. None of the project charters reference any lesson learned. The register exists. The new projects exist. The transfer does not.
→ Disconnected.

**Counter-example — NOT Disconnected:**
The risk register exists. The issue log exists. Each issue has a source_risk_id field populated. However, the project manager never reviews linked issues during risk reviews.
→ NOT Disconnected. The data is connected. It is not used. → Underutilized.

### Common Misclassification Traps

| Trap                                                | Why It's Wrong                                                                                                                           | Correct Type                                           |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| "The risk register isn't updated" → Disconnected    | The register exists but is stale. The problem is maintenance, not flow.                                                                  | **Ignored**                                            |
| "Nobody reads the linked issues" → Disconnected     | The link exists. The problem is usage, not connectivity.                                                                                 | **Underutilized**                                      |
| "The data is in two different tools" → Disconnected | Two tools alone do not mean disconnected. If an integration (API, export, manual transfer) exists and functions, it is not Disconnected. | **Not a gap, or Tooling if the integration is broken** |

---

## 4 Untrusted — Evidence cannot be verified

### Definition

The data is present. It is populated. But its source is unknown, its calculation is unverifiable, it contradicts other evidence, or its provenance is questionable. You cannot rely on it for decision-making — not because it is missing, but because it is suspect.

### Detection

> Step 1: Confirm the data EXISTS. (If not → Missing.)
> Step 2: Check for provenance. Can you trace this data point back to its source?
> Step 3: Check for consistency. Does this data match other evidence of the same fact?
> Step 4: Check for methodology. Is the calculation, derivation, or measurement method documented and standard-compliant?
> Step 5: If any check fails → Untrusted. Record the specific reason: unverifiable source, internal contradiction, or undocumented calculation.

### Examples

**Example 1 — SPI Without Earned Value (from Master Table):**
The status report states SPI = 0.95. The schedule file shows percent complete = 45%, but there is no earned value calculation, no BCWS, no BCWP. The SPI figure appears without methodology. When asked, the project manager says "I estimate it." The number exists. It cannot be verified.
→ Untrusted.

**Example 2 — Conflicting Budget Figures:**
The monthly financial report (ART-005) shows project spend at $1.2M. The steering pack (ART-003) shows $1.4M for the same project, same month. Both are "official" sources. Neither explains the $200K variance. The data exists in both places. It contradicts.
→ Untrusted.

**Example 3 — Backdated Status Reports:**
The status report is dated 2026-07-26. The file metadata shows it was created on 2026-08-02. The project manager admits it was written after the fact. The report exists. Its timestamp is a lie. The evidence is present but its provenance is corrupt.
→ Untrusted.

**Counter-example — NOT Untrusted:**
The risk register shows probability = 4, impact = 3. The project manager cannot explain why 4 and 3 were chosen — "it felt right." The data is subjective, but it is consistently recorded and the scale is defined in the Charter. Subjective judgment is not Untrusted unless it contradicts or is unverifiable.
→ NOT Untrusted. Possibly Misclassified if the scale is wrong, or Ignored if the assessment process is skipped — but not Untrusted.

### Common Misclassification Traps

| Trap                                       | Why It's Wrong                                                                                                                                                                        | Correct Type                |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| "The data is wrong" → Untrusted            | Untrusted is about _verifiability_, not accuracy. If the data is provably wrong (e.g., 2+2=5) but the source and method are clear → the gap is in the process or behavior, not trust. | **Ignored** or **Behavior** |
| "The field is blank sometimes" → Untrusted | Blank fields are absence, not suspect data.                                                                                                                                           | **Missing** or **Ignored**  |
| "I don't like the RAG status" → Untrusted  | Personal disagreement is not evidence of untrustworthiness. You need a concrete contradiction or provenance failure.                                                                  | **Not a finding**           |

---

## 5 Underutilized — Data collected but unused

### Definition

The data exists. It is complete. It is accurate. But there is no evidence that anyone uses it to make decisions, steer governance, or control delivery. The organization collects intelligence but acts as if it does not exist. The gap is waste, not absence.

### Detection

> Step 1: Confirm the data EXISTS and is populated. (If not → Missing.)
> Step 2: Identify the decision or process that this data is supposed to support. What action should this data trigger?
> Step 3: Examine the downstream evidence. Are decisions, reports, or actions informed by this data?
> Step 4: If the data is present but never referenced, never acted upon, or never influences outcomes → Underutilized.
> Step 5: Distinguish from Disconnected: in Disconnected, the data does not reach the consumer. In Underutilized, the data reaches the consumer but the consumer does nothing with it.

### Examples

**Example 1 — RAID Log Nobody Reads (from Master Table):**
The RAID log contains 47 risks, all current, with owners, probabilities, impacts, and mitigations. The last 6 steering packs contain zero references to any risk. The project manager says "I update it every week." When asked if the steering committee reviews it, the PM says "They have the link." The data exists. It is maintained. It is never used in governance.
→ Underutilized.

**Example 2 — Schedule Updates Without Reforecasting:**
The schedule is updated weekly. Baseline vs. actual variance is calculated. But the forecast finish date has not changed in 4 months despite consistent negative variance. The schedule data exists. The variance is known. No one uses it to reforecast.
→ Underutilized.

**Example 3 — Lessons Learned in a Drawer:**
The Lessons Learned register has 50+ entries from 10 projects. No project charter references them. No kickoff agenda includes them. No PMO report aggregates them. The data exists. It is never consumed.
→ Underutilized.

**Counter-example — NOT Underutilized:**
The risk register is updated weekly. The steering pack references the top 5 risks every month. However, the risk-based decisions are always "continue monitoring" — no mitigations are approved. The data IS used (it is reviewed and referenced). The governance decision is weak, but that is a governance/behavior issue, not underutilization of data.
→ NOT Underutilized. Possibly Behavior (governance avoids action) or Ignored (mitigation process not followed).

### Common Misclassification Traps

| Trap                                                       | Why It's Wrong                                                    | Correct Type         |
| ---------------------------------------------------------- | ----------------------------------------------------------------- | -------------------- |
| "The data is old" → Underutilized                          | Stale data is Ignored (not maintained), not Underutilized.        | **Ignored**          |
| "The data doesn't reach the dashboard" → Underutilized     | If the data is blocked from reaching the consumer → flow problem. | **Disconnected**     |
| "They have the report but don't act on it" → Underutilized | Correct — if the data is received but not acted upon.             | **Underutilized** ✅ |

---

## 6 Misclassified — Wrong classification or taxonomy

### Definition

The data exists. It is in the right place. But it is labeled, categorized, or typed incorrectly — causing it to be routed to the wrong process, measured by the wrong metric, or invisible to the right governance. The gap is semantic error, not absence or disuse.

### Detection

> Step 1: Confirm the data EXISTS. (If not → Missing.)
> Step 2: Examine the taxonomy, classification, or typing applied to the data. Does it match the standard's definitions?
> Step 3: Check downstream effects. Is the misclassification causing wrong process routing, wrong metrics, or governance blind spots?
> Step 4: If the data is present but categorized in a way that breaks standard intent → Misclassified.
> Step 5: Distinguish from Divergent: Misclassified means the practice is correct but the label is wrong. Divergent means the practice itself is wrong.

### Examples

**Example 1 — Risks Categorized as Issues (from Master Table):**
The issue log contains 15 entries. 8 of them describe uncertain future events with probability and impact ("supplier might miss deadline," "regulatory change possible"). These are risks by standard definition. They are logged as issues. Because they are issues, they bypass risk review, have no mitigation plans, and do not appear in the risk dashboard. The data exists. The taxonomy is wrong.
→ Misclassified.

**Example 2 — Strategic Initiative in Operational Portfolio:**
A $5M digital transformation initiative is classified in the "Business as Usual" portfolio alongside IT support tickets. It receives operational governance (monthly review) instead of strategic governance (quarterly board review). The initiative exists. The portfolio assignment is wrong.
→ Misclassified.

**Example 3 — Defects as Change Requests:**
The change log contains 23 "changes" that are actually software defects reported by users. Because they are changes, they go through the CAB (taking 2 weeks) instead of the defect triage process (taking 2 days). The data exists. The routing is broken by taxonomy.
→ Misclassified.

**Counter-example — NOT Misclassified:**
The project uses a 3×3 risk matrix instead of the standard 5×5. The risks are correctly identified and categorized within the 3×3. The practice itself deviates from the standard.
→ NOT Misclassified. The taxonomy is internally consistent. The deviation is in the methodology → Divergent.

### Common Misclassification Traps

| Trap                                                               | Why It's Wrong                                                                                                                                       | Correct Type                      |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| "They use the wrong template" → Misclassified                      | Template choice is a process/tooling decision, not a taxonomy error.                                                                                 | **Divergent** or **Tooling**      |
| "The priority is wrong" → Misclassified                            | Priority is a judgment call within a taxonomy. If the taxonomy itself is correct but the value is debatable → not a gap, or Behavior if manipulated. | **Behavior** or **Not a finding** |
| "They call it a program but it's really a project" → Misclassified | Correct — the label contradicts the standard definition.                                                                                             | **Misclassified** ✅              |

---

## 7 Divergent — Delivery differs from required standard

### Definition

The organization follows a practice that contradicts the standard. There is no documented tailoring, no approved waiver, no exception. The practice is different and ungoverned. This is the gap of unauthorized deviation.

### Detection

> Step 1: Confirm the standard EXISTS and is applicable. (If not → Missing or out of scope.)
> Step 2: Confirm the practice IS BEING PERFORMED. (If not → Ignored.)
> Step 3: Compare the practice against the standard's requirement. Is the output, timing, method, or governance different?
> Step 4: Check for documented approval. Is there a tailoring decision, waiver, or exception record?
> Step 5: If the practice differs AND there is no documented approval → Divergent.
> Step 6: Assess scope: one project or systemic? Systemic divergence suggests organizational behavior or broken governance.

### Examples

**Example 1 — 3×3 Risk Matrix (from Master Table):**
The Standard for Risk Management §4.2 requires a 5×5 probability-impact matrix. The organization uses a 3×3 matrix in all projects. The matrix is documented in the PMO handbook. There is no tailoring decision, no waiver, no board approval. The practice exists. It contradicts the standard. It is ungoverned.
→ Divergent.

**Example 2 — Steering Committees Quarterly Instead of Monthly:**
The governance framework (§3.1) mandates monthly steering committees for all projects >$500K. All 12 projects in scope show quarterly meetings. The quarterly cadence is consistent across the portfolio. No exception log exists. No tailoring register mentions this change.
→ Divergent.

**Example 3 — Earned Value Replaced by Percent Complete:**
The standard mandates earned value management (EVM) for all strategic programs. All programs use "percent complete" reported by project managers without BCWS, BCWP, or ACWP. The PMO says "EVM is too complex." No approved alternative methodology exists. The practice is different and ungoverned.
→ Divergent.

**Counter-example — NOT Divergent:**
The standard requires monthly steering committees. The project has a documented, board-approved waiver: "Steering committee frequency reduced to quarterly due to project stability and low risk profile. Approved by Portfolio Director on 2026-01-15." The practice differs. It is governed.
→ NOT Divergent. Not a finding. Governed deviation.

### Common Misclassification Traps

| Trap                                                    | Why It's Wrong                                                                                                                                                  | Correct Type                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| "They don't follow the standard" → Divergent            | First check: is the practice being performed at all? If not → Ignored.                                                                                          | **Ignored**                            |
| "They use a different tool" → Divergent                 | If the tool is approved and the output meets the standard → not a gap. If the tool prevents compliance → Tooling.                                               | **Tooling** or **Not a finding**       |
| "The result is different from the template" → Divergent | If the template is wrong but the practice meets the standard's intent → not Divergent. Divergent requires contradiction of the standard, not just the template. | **Not a finding** or **Misclassified** |

---

## Disambiguation Rules

When a gap seems to fit multiple types, apply these rules in order:

1. **Missing vs. Ignored:** If the artifact/field does not exist at all → **Missing**. If it exists but the practice is bypassed → **Ignored**.
2. **Ignored vs. Divergent:** If the standard is known but deliberately not followed → **Ignored**. If the practice is different but there is no evidence the standard was known → **Divergent**.
3. **Disconnected vs. Underutilized:** If the data exists but is not linked to other processes → **Disconnected**. If the data is linked but not acted upon → **Underutilized**.
4. **Untrusted vs. Missing:** If the data is present but suspicious → **Untrusted**. If the data is simply not there → **Missing**.
5. **Misclassified vs. Divergent:** If the practice is correct but labeled wrong → **Misclassified**. If the practice itself is wrong → **Divergent**.

## What You Must Never Do

- Never assign two gap types to one finding. Split the finding if two distinct problems exist.
- Never classify a gap as "Other" or "N/A." The seven types cover all variances.
- Never use "Missing" for data that exists but is blank in some rows — that is **Untrusted** (data quality) or **Ignored** (process not enforced), depending on why it is blank.
