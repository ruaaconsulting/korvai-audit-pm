---
Name: Root Origin Taxonomy
description:
  > The Seven Root Origin Taxonomy — full definitions, detection logic, examples,
  and disambiguation rules for tracing PMO delivery gaps to their earliest
  structural cause. Read during Stage 5 (Trace) before assigning any root origin.
version: 1.0.0
---

## The Seven Root Origins (closed) (Tells why it is wrong?)

> Every gap traces to exactly one of seven origins. No overlap. No duplicates.
> Trace order: Capture → Integration → Definition / Taxonomy → Ownership →
> Process / Cadence → Tooling → Behavior. Test in this sequence.
> Stop at the first match.

| Root Origin           | Definition                                                              |
| --------------------- | ----------------------------------------------------------------------- |
| Capture               | The data was never captured at the source                               |
| Integration           | The data exists but does not flow between tools/processes               |
| Definition / Taxonomy | The data is captured but defined incorrectly or classified wrongly      |
| Ownership             | No accountable owner for the data or process                            |
| Process / Cadence     | The process exists but timing, sequence, or governance cadence is wrong |
| Tooling               | The tool cannot support the required standard                           |
| Behavior              | People bypass, ignore, or manipulate the process                        |

## Master Disambiguation Example — The Late Status Report

The same symptom: the monthly status report is consistently late.

| Situation                                                                                                                                              | Earliest Structural Point                       | Root Origin                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Nobody is assigned to write the report. It happens when someone remembers.                                                                             | No accountable role                             | **Ownership**                                                                                                                                                      |
| The report writer is assigned, but the deadline is "end of month" with no specific date.                                                               | Process is ambiguous                            | **Process / Cadence**                                                                                                                                              |
| The report writer is assigned, the deadline is the 25th, but they are waiting for data from Finance that never arrives on time.                        | Data exists in Finance but does not flow to PMO | **Integration**                                                                                                                                                    |
| Finance provides the data, but it arrives as a PDF screenshot of a dashboard that cannot be verified or reused.                                        | Data is present but unverifiable                | **Untrusted** (gap type) → trace to **Definition / Taxonomy** if the format requirement is undefined, or **Integration** if the format is defined but not enforced |
| The PMO tool auto-generates the report on the 25th, but the export format is corrupted and unusable.                                                   | Tool failure                                    | **Tooling**                                                                                                                                                        |
| The report writer has the data, the tool works, the deadline is clear — but they consistently start writing on the 28th and backdate it.               | Deliberate bypass                               | **Behavior**                                                                                                                                                       |
| The report is not late because it was never required in the first place. The standard expects it, but the organization never established the practice. | Data never captured                             | **Capture**                                                                                                                                                        |

---

# Root Origin Analysis

---

## 1 Capture — The data was never captured at the source

### Definition

The required information exists in the real world — work is happening, decisions are made, risks materialize — but it was never recorded in any system, artifact, or log. The gap entered the system at the **moment of absence**: the data should have been captured but wasn't.

### Detection

> Step 1: Confirm the real-world event or state EXISTS. (If the event itself did not happen, there is no gap — the standard may be inapplicable.)
> Step 2: Search all declared artifacts and systems for any record of the event/state. Search by function, not by name.
> Step 3: If zero records exist across all artifacts → **Capture**.
> Step 4: If partial records exist (some events captured, others not) → assess whether the capture process is intermittent or selective. Intermittent capture may indicate Ownership or Process, not pure Capture. Pure Capture means the capture mechanism itself is absent.
> Step 5: Distinguish from Behavior: Capture means there was no mechanism or expectation to record. Behavior means there was a mechanism but someone chose not to use it.

### Examples

**Example 1 — Risk Never Logged (from Master Table):**
A project team identifies a supplier delay risk in a weekly standup. The risk is discussed, mitigations are agreed verbally, but no entry is made in the RAID log. The risk exists in reality. No artifact captures it.
→ **Capture.** The capture mechanism (risk logging process) either does not exist or is not known to the team.

**Example 2 — Baseline Never Established:**
The project charter approves a $2M budget and a 6-month timeline. Work begins. Six months later, there is no baseline document, no approved schedule baseline, no signed scope statement. The baseline should have been captured at kickoff. It was not.
→ **Capture.**

**Example 3 — Decision Never Recorded:**
The steering committee approves a scope change in a meeting. Minutes are not taken. The decision is communicated verbally to the project manager. No change log entry is created. No formal approval document exists. The decision happened. It was never captured.
→ **Capture.**

**Counter-example — NOT Capture:**
The risk register exists. The project manager chooses not to log "small risks" because "they're not worth the paperwork." The mechanism exists. The choice is deliberate.
→ **NOT Capture.** The data was not captured because of a human choice. → **Behavior.**

### Common Misclassification Traps

| Trap                                           | Why It's Wrong                                                                                                                                                                                                                  | Correct Origin                                                          |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| "The field is blank" → Capture                 | Blank fields in an existing record mean the capture mechanism exists but was not used.                                                                                                                                          | **Behavior** or **Process / Cadence**                                   |
| "The template exists but is empty" → Capture   | The template is a capture mechanism. Its emptiness means the mechanism was not used.                                                                                                                                            | **Ownership** (nobody filled it) or **Behavior** (someone chose not to) |
| "We didn't know we needed to log it" → Capture | If the standard and Charter both require it, ignorance is not Capture. Capture means the mechanism is structurally absent. Ignorance of a known requirement is Behavior or Training (not a root origin — falls under Behavior). | **Behavior**                                                            |

---

## 2 Integration — The data exists but does not flow

### Definition

The information is captured correctly in one artifact or system. But it never reaches the downstream consumer — the next process, the next team, the next tool, or the governance forum that needs it. The gap entered the system at the **handoff point**.

### Detection

> Step 1: Confirm the data EXISTS in the source artifact/system. (If not → Capture.)
> Step 2: Identify the expected consumer per the standard. Which process, artifact, person, or system should receive this data next?
> Step 3: Check the consumer's evidence. Is the data present? Is it referenced? Is it used?
> Step 4: If the data is absent in the consumer but present in the source → **Integration**.
> Step 5: Determine the nature of the break:
>
> - No integration mechanism exists (no API, no export, no manual process) → Integration at the structural level.
> - Integration mechanism exists but is broken (API down, export failed, email bounced) → may be Tooling if the mechanism is the tool's fault, or Process if the failure is undetected.

### Examples

**Example 1 — Schedule to Portfolio Dashboard (from Master Table):**
The project schedule (MS Project) contains current baseline and actual dates. The portfolio dashboard (Power BI) shows last month's dates. The project manager says "I update the schedule every week." The portfolio manager says "I pull from the data warehouse." The data warehouse has not refreshed in 6 weeks. The data exists in the source. It does not reach the consumer.
→ **Integration.**

**Example 2 — Risk Mitigation to Change Control:**
A risk mitigation plan requires a scope change. The risk register shows the mitigation as "approved." The change log contains no corresponding change request. The risk data exists. The change process never received it.
→ **Integration.**

**Example 3 — Lessons Learned to New Project Charters:**
The lessons learned register contains 14 entries. Three new projects started this quarter. None of the new project charters reference any lesson learned. The PMO says "we email the register to PMs at kickoff." No PM recalls receiving it. The data exists. The transfer mechanism (email) is unreliable and unverified.
→ **Integration.**

**Counter-example — NOT Integration:**
The risk register exists. The issue log exists. Each issue has a `source_risk_id` field populated. The project manager reviews linked issues during risk reviews. However, the steering committee never discusses risks or issues.
→ **NOT Integration.** The data is connected. It is not used. → **Underutilized** (gap type) → trace to **Behavior** or **Process / Cadence** (if the steering agenda omits risk review).

### Common Misclassification Traps

| Trap                                                 | Why It's Wrong                                                                                                                                                        | Correct Origin                                 |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| "The tool doesn't sync" → Integration                | If the tool lacks sync capability entirely → the tool is structurally incapable.                                                                                      | **Tooling**                                    |
| "They forgot to send it" → Integration               | One-time human error is Behavior. Systematic forgetting is Ownership or Process.                                                                                      | **Behavior** or **Ownership**                  |
| "The data is in two different formats" → Integration | Format mismatch is a Definition / Taxonomy problem if the standard defines the format. If the standard does not define it → gap is in the standard, not the delivery. | **Definition / Taxonomy** or **Not a finding** |

---

## 3 Definition / Taxonomy — The data is captured but defined incorrectly

### Definition

The field exists. The record exists. The data is populated. But its meaning, classification, unit, scale, or relationship is wrong — causing downstream misinterpretation, wrong routing, or invisible reporting. The gap entered the system at the **point of definition**.

### Detection

> Step 1: Confirm the data EXISTS and is populated. (If not → Capture.)
> Step 2: Examine the definition, taxonomy, or classification applied. Does it match the standard's definition?
> Step 3: Check for downstream effects. Is the misdefinition causing wrong process routing, incorrect metrics, or governance blind spots?
> Step 4: If the data is present but defined/classified in a way that breaks standard intent → **Definition / Taxonomy**.
> Step 5: Distinguish from Misclassified (gap type): Definition / Taxonomy is the root origin — the structural point where the wrong definition was established. Misclassified is the gap type — the observable symptom.

### Examples

**Example 1 — "Percent Complete" Means Different Things:**
The Charter does not define `percent_complete`. Three project managers interpret it differently: one uses physical % complete, one uses duration % complete, one uses effort % complete. The field exists in all schedules. The data is populated. The definitions are incompatible. Portfolio rollup is meaningless.
→ **Definition / Taxonomy.** The gap entered when the field was left undefined (or defined ambiguously) in the Charter or standard.

**Example 2 — Program Classified as Project:**
A $5M strategic initiative is classified in the portfolio system as a "project." It receives project governance (monthly PM review) instead of program governance (quarterly board review, benefits management). The artifact exists. The classification is wrong.
→ **Definition / Taxonomy.**

**Example 3 — "High" Priority Has No Definition:**
The issue log uses priority levels: Low, Medium, High, Critical. There is no definition of what "High" means. One team uses High for "affects one user." Another uses High for "affects all users and has regulatory impact." The field exists. The taxonomy is undefined. Governance cannot prioritize consistently.
→ **Definition / Taxonomy.**

**Counter-example — NOT Definition / Taxonomy:**
The Charter clearly defines `percent_complete` as "physical % complete." The project manager uses "duration % complete" because "it's easier." The definition exists and is clear. The user chose to ignore it.
→ **NOT Definition / Taxonomy.** The definition is correct. The application is wrong. → **Behavior.**

### Common Misclassification Traps

| Trap                                                           | Why It's Wrong                                                                                                                                                                                                                                        | Correct Origin                                      |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| "They don't know what the field means" → Definition / Taxonomy | If the field is undefined in the Charter/standard → yes. If it is defined but the user was never trained → the definition exists but was not communicated. This is Process (training is part of process) or Behavior (user did not read the Charter). | **Process / Cadence** or **Behavior**               |
| "The data is wrong" → Definition / Taxonomy                    | Wrong data values are not definition errors. If the definition is clear but the value is incorrect → the gap is in capture, behavior, or process.                                                                                                     | **Capture**, **Behavior**, or **Process / Cadence** |
| "They use a different scale" → Definition / Taxonomy           | If the standard mandates a 5×5 scale and the org uses 3×3 without defining it → yes. If the org has a documented, approved 3×3 definition that replaces the 5×5 → not a gap.                                                                          | **Not a finding** or **Divergent** (if unapproved)  |

---

## 4 Ownership — No accountable owner

### Definition

The process, data, artifact, or decision has no named owner. Or the named owner lacks authority, capacity, or accountability to perform the role. The gap entered the system at the **organizational design point** — where accountability should have been assigned but wasn't.

### Detection

> Step 1: Identify the required process, data, or artifact per the standard.
> Step 2: Search the Charter, org chart, RACI, or governance documents for an assigned owner.
> Step 3: If no owner is named → **Ownership**.
> Step 4: If an owner is named, verify they have the authority and capacity to perform the role:
>
> - Do they have decision rights? (Authority)
> - Do they have time/resource? (Capacity)
> - Are they evaluated on this outcome? (Accountability)
>   Step 5: If the owner lacks any of the three → **Ownership** (the assignment is structural but ineffective).
>   Step 6: Distinguish from Behavior: Ownership means nobody is structurally accountable. Behavior means someone is accountable but chooses not to perform.

### Examples

**Example 1 — Risk Register Has No Owner:**
The RAID log exists. It is updated sporadically. The Charter does not assign a risk owner role. The project manager says "the team owns it." The team says "the PM owns it." No individual is named. No one is accountable for completeness, accuracy, or timeliness.
→ **Ownership.**

**Example 2 — Governance Role Is Vacant:**
The PMO charter assigns portfolio governance to the "Chief Portfolio Officer." That role has been vacant for 8 months. An interim director covers it "when they have time." Portfolio decisions are deferred or made ad-hoc. The role exists on paper. It is not staffed.
→ **Ownership.**

**Example 3 — Baseline Approval Has No Authority:**
The standard requires baseline approval by the project sponsor. The Charter names a "project sponsor" who is a junior manager with no budget authority. They sign the baseline, but the signature has no organizational weight. The baseline can be overridden by any senior stakeholder. The owner is named. They lack authority.
→ **Ownership.**

**Counter-example — NOT Ownership:**
The Charter assigns risk ownership to the project manager. The project manager is competent, has authority, and is accountable. They simply do not update the risk register because "I have more urgent priorities."
→ **NOT Ownership.** The owner exists and is capable. They choose not to perform. → **Behavior.**

### Common Misclassification Traps

| Trap                                     | Why It's Wrong                                                                                                                                                                                        | Correct Origin                                                                           |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| "The PM is too busy" → Ownership         | Being busy is a capacity issue, but if the PM is the named owner and has authority/accountability → the structural assignment is correct. The failure is behavioral or process-related (overloading). | **Behavior** or **Process / Cadence**                                                    |
| "The team should own it" → Ownership     | "The team" is not an accountable owner. If the Charter says "the team" → that is an Ownership gap (no individual). If the Charter names an individual → not Ownership.                                | **Ownership** (if "the team" is the assignment) or **Behavior** (if individual is named) |
| "The owner left the company" → Ownership | If the role is vacant and no replacement is assigned → yes. If a replacement was assigned but is ineffective → assess authority/capacity/accountability.                                              | **Ownership** (if vacant) or **Behavior** (if ineffective but structurally sound)        |

---

## 5 Process / Cadence — The process exists but timing is wrong

### Definition

The required activity happens. The process is documented. But the timing, sequence, frequency, or governance checkpoint is incorrect — causing the right work to produce the wrong outcome at the wrong time. The gap entered the system at the **process design point**.

### Detection

> Step 1: Confirm the process EXISTS and is documented. (If not → Capture or Definition / Taxonomy.)
> Step 2: Confirm the process IS BEING PERFORMED. (If not → Ignored or Behavior.)
> Step 3: Compare the actual timing/sequence/frequency against the standard's requirement.
> Step 4: If the process happens but at the wrong time, in the wrong order, or without required checkpoints → **Process / Cadence**.
> Step 5: Assess whether the wrong cadence is documented (a wrong process) or executed (a right process done wrong). Documented wrong = Process / Cadence. Executed wrong = Behavior.

### Examples

**Example 1 — Steering Committees Quarterly Instead of Monthly:**
The governance framework requires monthly steering committees for all projects >$500K. The organization holds them quarterly. The meetings happen. The process exists. The cadence is wrong. The standard is clear. No waiver exists.
→ **Process / Cadence.**

**Example 2 — Lessons Learned at Closure Only:**
The standard requires lessons learned at stage gates and project closure. The organization collects them only at closure. Early lessons are lost. Late lessons are too late to help. The process exists. The sequence is wrong.
→ **Process / Cadence.**

**Example 3 — Budget Approved After Spend:**
The financial process requires budget approval before expenditure. Evidence shows purchase orders are raised and approved after goods are received. The process exists (approval happens). The sequence is inverted. The standard requires "before." The practice is "after."
→ **Process / Cadence.**

**Counter-example — NOT Process / Cadence:**
The standard requires monthly steering committees. The project manager holds them monthly but backdates the minutes to meet the deadline. The cadence is correct. The execution is fraudulent.
→ **NOT Process / Cadence.** The process timing is right. The human behavior is wrong. → **Behavior.**

### Common Misclassification Traps

| Trap                                                         | Why It's Wrong                                                                                                                                                                           | Correct Origin                            |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| "They skip the gate review" → Process / Cadence              | Skipping is not a timing error — it is non-performance.                                                                                                                                  | **Ignored** or **Behavior**               |
| "The process takes too long" → Process / Cadence             | Duration is a capacity or tooling issue, not necessarily a cadence design flaw. If the process steps are correct but the tool is slow → Tooling. If the owner is overloaded → Ownership. | **Tooling** or **Ownership**              |
| "They do it differently in each project" → Process / Cadence | Inconsistent execution of a standard process is Behavior (if the process is documented) or Definition / Taxonomy (if the process is ambiguous).                                          | **Behavior** or **Definition / Taxonomy** |

---

## 6 Tooling — The tool cannot support the standard

### Definition

The standard requires a capability that the current tool, system, or platform cannot provide. Or the tool is configured in a way that structurally prevents compliance. The gap entered the system at the **tool selection or configuration point**.

### Detection

> Step 1: Identify the standard's requirement. What capability, field, workflow, calculation, or report does it mandate?
> Step 2: Examine the current tool. Does it natively support this requirement?
> Step 3: If the tool cannot support the requirement even with configuration, customization, or workaround → **Tooling**.
> Step 4: If the tool CAN support it but is configured wrong → assess: is the configuration error documented (Process) or accidental (Behavior)? Only if the tool is structurally incapable → Tooling.
> Step 5: Distinguish from Integration: Tooling means the tool lacks capability. Integration means the tool has capability but does not connect to another tool.

### Examples

**Example 1 — Portfolio Tool Cannot Calculate Earned Value:**
The standard requires earned value management (EVM) for all strategic programs. The portfolio management tool (Smartsheet) does not support BCWS, BCWP, or SPI calculation. The organization uses percent complete instead. The tool is structurally incapable of EVM.
→ **Tooling.**

**Example 2 — Jira Workflow Has No CAB Approval Status:**
The standard requires all changes to pass through a Change Advisory Board (CAB). The Jira workflow has statuses: Open, In Progress, Done. There is no "Pending CAB Approval" status. Changes move from Open to Done without governance checkpoint. The workflow cannot enforce the standard.
→ **Tooling.**

**Example 3 — Scheduling Tool Does Not Lock Baselines:**
The standard requires baseline lock after approval. The scheduling tool (Excel) has no baseline protection mechanism. Any user can edit any date at any time. The tool is incapable of enforcing baseline integrity.
→ **Tooling.**

**Counter-example — NOT Tooling:**
The portfolio tool supports EVM natively. The EVM module was not enabled during implementation. The tool CAN do it. It was not configured.
→ **NOT Tooling.** The tool is capable. The configuration was omitted. → **Process / Cadence** (configuration is part of implementation process) or **Behavior** (someone chose not to enable it).

### Common Misclassification Traps

| Trap                                   | Why It's Wrong                                                                                                   | Correct Origin                               |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| "The tool is slow" → Tooling           | Performance is not a capability gap. Slow tools cause Behavior (workarounds) or Underutilization.                | **Behavior** or **Underutilized** (gap type) |
| "The export format is wrong" → Tooling | If the tool supports multiple formats but the wrong one was selected → configuration error.                      | **Process / Cadence** or **Behavior**        |
| "We need a better tool" → Tooling      | "Need" is not evidence. You must prove the current tool is structurally incapable of the standard's requirement. | **Prove incapability, or → Behavior**        |

---

## 7 Behavior — People bypass, ignore, or manipulate the process

### Definition

The standard is clear. The process is documented. The tool works. The owner is assigned. But individuals or teams deliberately choose not to follow the process — and there is evidence of this choice. The gap entered the system at the **human decision point**.

### Detection

> Step 1: Verify the standard EXISTS. (If not → Capture.)
> Step 2: Verify the process IS DOCUMENTED. (If not → Definition / Taxonomy or Process / Cadence.)
> Step 3: Verify the tool WORKS. (If not → Tooling.)
> Step 4: Verify the owner IS ASSIGNED AND CAPABLE. (If not → Ownership.)
> Step 5: Verify the process TIMING/SEQUENCE IS CORRECT. (If not → Process / Cadence.)
> Step 6: If all of the above are correct, but the practice still deviates → **Behavior**. You must find evidence of deliberate choice: admission, pattern, workaround, or manipulation.
> Step 7: Distinguish from Ignored: Ignored means the standard exists but the practice is not performed. Behavior means the practice is performed but in a way that bypasses or manipulates the standard.

### Examples

**Example 1 — Backdated Status Reports:**
The reporting process requires weekly status reports by Friday 5 PM. The project manager consistently writes the report on Monday morning and changes the file date to Friday. They admit "I don't have time on Fridays." The standard is clear. The process is documented. The tool works. The owner is assigned. The timing is correct. The PM deliberately bypasses it.
→ **Behavior.**

**Example 2 — Shadow Spreadsheets:**
The standard requires all financial tracking in the corporate ERP. The project team maintains a shadow Excel file "because ERP is too slow." The ERP works. The process is documented. The team chooses to bypass it. The shadow file is evidence of deliberate workaround.
→ **Behavior.**

**Example 3 — Risk Downgrading:**
The standard requires risks with probability=5 and impact=4 to be escalated to the portfolio level. The project manager rates them probability=3, impact=3 to keep them at project level. The risk register shows the downgraded values. The PM admits "I don't want portfolio attention." The standard is clear. The tool enforces the scale. The PM manipulates the data.
→ **Behavior.**

**Counter-example — NOT Behavior:**
The project manager does not update the risk register because they were never told it was their responsibility. The Charter does not assign risk ownership. The PMO handbook mentions risk management but does not name a role.
→ **NOT Behavior.** There is no evidence of deliberate choice. The PM is unaware of accountability. → **Ownership** (no assigned owner) or **Process / Cadence** (training/onboarding gap).

### Common Misclassification Traps

| Trap                                     | Why It's Wrong                                                                                              | Correct Origin                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| "They didn't know" → Behavior            | Ignorance is not deliberate choice. If the standard was not communicated → Process or Definition.           | **Process / Cadence** or **Definition / Taxonomy**                   |
| "They made a mistake" → Behavior         | One-time errors are not Behavior. Behavior requires a pattern or admission of deliberate choice.            | **Process / Cadence** (if process allows error) or **Not a finding** |
| "They don't like the process" → Behavior | Dislike alone is not evidence. You need evidence of action: workaround, bypass, manipulation, or admission. | **Prove with evidence, or → Not a finding**                          |

---

## Final Trace Order (For the Entire Document)

When tracing any gap, test in this order. Stop at the first match.

1. **Capture** — Was the data ever captured at all?
2. **Integration** — Does the data exist in the source but not reach the consumer?
3. **Definition / Taxonomy** — Is the data captured but defined/classified incorrectly?
4. **Ownership** — Is there an accountable owner with authority, capacity, and accountability?
5. **Process / Cadence** — Does the process exist but with wrong timing, sequence, or frequency?
6. **Tooling** — Is the tool structurally incapable of supporting the standard?
7. **Behavior** — Do people deliberately bypass, ignore, or manipulate the process?

This order prevents the most common errors: calling "uncommunicated process" Behavior, calling "overloaded owner" Ownership, or calling "slow tool" Tooling.

## The "Earliest Point" Rule

Trace backward from the symptom until you hit a structural cause. Then stop.

Example chain:

- Symptom: Steering pack shows outdated risk data.
- Why? Risk register was not updated before the pack was produced.
- Why? Risk review meeting was cancelled.
- Why? No one was assigned to convene it.
- **Root Origin: Ownership** (no accountable owner for risk review cadence).

Do not stop at "Process / Cadence" (meeting was cancelled) if the cancellation happened because no one owned the meeting. Go to the earliest structural point.

## What You Must Never Do

- Never assign two root origins to one finding. If two structural failures exist, they are two separate findings.
- Never assign "Behavior" without evidence of deliberate choice. Absence is not behavior — absence is Capture.
- Never assign "Tooling" if a configuration change or workflow fix would solve it. Tooling means the tool is structurally incapable.
- Never trace to a symptom. "Report is late" is a symptom. "No one owns the report deadline" is Ownership. "Deadline is not in the process" is Process / Cadence.
