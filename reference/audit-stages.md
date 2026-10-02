---
Name: Audit State Machine
description: >
  Full stage-by-stage specification (Stage 0-10) of the audit state machine — purpose, preconditions, inputs, activities, decision logic, outputs, failure conditions, and transitions for every stage. Reference for human developers; SKILL.md §5's Thinking Phases is the operational summary the LLM actually follows.
version: 1.8.0
---

# Audit State Machine — Full Stage Specifications

> **Read this file before executing any audit stage.**
> Every stage uses EXACTLY the template below. No exceptions.

## Contents

- [Stage 0 — Baseline](#stage-0--baseline)
- [Stage 1 — Charter](#stage-1--charter)
- [Stage 2 — Define](#stage-2--define)
- [Stage 3 — Measure](#stage-3--measure)
- [Stage 4 — Classify](#stage-4--classify)
- [Stage 5 — Trace](#stage-5--trace)
- [Stage 6 — Engineer & Score](#stage-6--engineer--score)
- [Stage 7 — Synthesize (the Manifest Gate)](#stage-7--synthesize-the-manifest-gate)
- [Stage 8 — Findings JSON (deterministic)](#stage-8--findings-json-deterministic)
- [Stage 9 — Render (deterministic)](#stage-9--render-deterministic)
- [Stage 10 — Final Summary](#stage-10--final-summary)

<!--
  RULE: every stage uses EXACTLY this template. No exceptions.

  ## Stage X — Name
  ### Purpose            (one sentence)
  ### Preconditions      (which transition state must already be set)
  ### Inputs
  ### Activities         (numbered; imperative)
  ### Decision Logic     (if/then rules — where judgment is constrained)
  ### Outputs
  ### Failure Conditions (what triggers a hard stop, and the exact message)
  ### Completion Criteria
  ### Transition         (state emitted)
-->

## Stage 0 — Baseline

### Purpose

Verify the engine is intact, scan `knowledge/`, and build or refresh the local registry — so the audit knows what artifacts should exist and which standards govern them before any data is read.

### Preconditions

None — Stage 0 is the entry point. It runs at the start of every audit.

### Inputs

1. `knowledge/` — the org-supplied standards (the baseline; Contract 1). The only external input.
2. `registries/` — the previously derived registry, **if one exists** (input to the refresh-or-reuse decision only).
3. Engine files (preflight targets, not baseline): `PMO_DATA_CHARTER_template.md`, `AUDIT_MANIFEST_template.md`, `findings.schema.json`, `schema.py`, `manifest_to_findings.py`, `render.py`, `report_template.html`.

### Activities

1. **Preflight** — verify every engine file in Inputs (3) exists. This checks the skill, not the org.
2. **Inventory** — list every document in `knowledge/` (filename, format, size, modified date).
3. **Skeleton scan** — for each document, extract the table of contents / bookmarks / heading structure only. Record: document ID, title, edition, structure map with section numbers and page anchors. Do **not** read body text at this stage.
4. **Derive registry items** — from the skeletons, create or update registry items in Appendix E format: paraphrased checkable criteria + stable citation anchors (section + page). **Never verbatim text** (Principle 3). Depth here is skeleton-level; deep dives happen on demand in Stage 2.
5. **Build the applicability map** — artifact type → governing document(s) and section(s) (e.g., risk register → Standard for Risk Management §4.3, Risk Practice Guide §X2.2). This map is what Stage 1 uses to propose scope and what makes Missing gaps detectable.
6. **Build the folder/category index** — scan `knowledge/`'s actual subfolder structure and record
   it to `knowledge_index.json` (category = whatever top-level folder name exists, with its document
   count and filenames). Never assume a fixed set of category names (`PMI`, `Agile`, `Organizational`,
   ...) — the organization may structure `knowledge/` however it likes, and that structure can change
   between runs. This is the mechanism behind SKILL.md §13.2's reading guide.
7. **Write** the registry files to `registries/` with a derivation timestamp and a fingerprint
   (hash) of each source document; write `knowledge_index.json` to
   `skills/intelligence-engine/knowledge_index.json`.

### Decision Logic

- IF `knowledge/` contains no standards (README only) → `BASELINE_ABSENT`, hard stop (see Failure Conditions).
- IF a registry exists AND every source fingerprint matches the current `knowledge/` contents → **reuse** it; skip Activities 3–6.
- IF documents were added → derive registry entries for the new documents only.
- IF documents were removed or changed → refresh the affected entries; flag orphaned registry items (whose source is gone) and remove them.
- Deep-dive extraction is **never** done in Stage 0 — Stage 2 requests it per governing section. Stage 0 stays fast and shallow.
- A document that cannot be parsed (corrupt, image-only, encrypted) is logged and reported to the user — it is skipped, not guessed at.

### Outputs

Written to `registries/` (local-only, gitignored):

1. **Skeleton map** — every document in `knowledge/` with its structure and anchors.
2. **Registry items** — the checkable criteria (Appendix E format).
3. **Applicability map** — artifact type → governing standards/sections.
4. **Derivation manifest** — timestamp + source fingerprints (drives the reuse decision next run).
5. **Folder/category index** (`knowledge_index.json`) — the actual subfolder structure found this
   run, whatever it's named. Read by SKILL.md §13.2 before deciding what to read next.

### Failure Conditions

- `knowledge/` empty or contains only its README → **HARD STOP**, emit `BASELINE_ABSENT`, print exactly:
  > **BASELINE_ABSENT — no standards found in `knowledge/`.** IEM-PM ships no bundled standard text and never audits from assumption or model memory. Place the organization's real standards (PMI or organizational; PDF/MD) in `skills/intelligence-engine/knowledge/` and re-run. _No baseline, no audit._
- Any engine file missing (preflight) → **HARD STOP**, print:
  > **ENGINE_INCOMPLETE — `<filename>` is missing.** This is a skill-installation problem, not a baseline problem. Reinstall or restore the file, then re-run.
- Every document in `knowledge/` unparseable → **HARD STOP** with the list of failed documents and the reason each failed.

### Completion Criteria

- Every readable document in `knowledge/` appears in the skeleton map.
- Every registry item carries a citation anchor (document ID + section + page) and contains no verbatim standard text.
- The applicability map is non-empty.
- The derivation manifest records a fingerprint for every source document.
- `knowledge_index.json` reflects the actual current subfolder structure — regenerated every run,
  never assumed unchanged from a prior one.

### Transition

→ `BASELINE_READY` (or `BASELINE_ABSENT` + hard stop)

---

## Stage 1 — Charter

### Purpose

Propose the PMO Data Charter (artifacts + field semantics from the **data**; scope from the **standards** — anti-mirror guard) and obtain human ratification — so every later stage interprets the data through one agreed contract, never through guesswork.

### Preconditions

`BASELINE_READY`

### Inputs

1. **The org's delivery data** (the upload) — feeds Charter functions 1–2 (Artifact Declaration, Field Semantics). See §4.2.
2. `PMO_DATA_CHARTER_template.md` — the shape the proposal must fill (Contract 2's template).
3. **Registry + applicability map** from Stage 0 — feed Charter function 3 (Materiality & Scope), which is proposed from the standards' expectations, **never from the data**.

The input split _is_ the anti-mirror guard: input 1 may only inform functions 1–2; input 3 may only inform function 3.

### Activities

1. **Inventory the data** — list every supplied artifact (name, type, format, size, record count where readable). Read to identify, not yet to audit.
2. **Check for a prior audit of this evidence** — this is the one narrow, explicit exception SKILL.md
   Principle 8 (Evidence Isolation) carves out, and only in the form specified here: compute the
   checksum of every supplied artifact and compare it **only** against the checksums already recorded
   in any `reports/` folder's existing Manifests' `## ARTIFACT:` blocks (`**Checksum:**` field) —
   reports now live per-project (each project's own `reports/`, sibling to its `evidence/`), so this
   means checking across every project folder you have visibility into, not one shared location. This
   is a checksum lookup, nothing more: do not open, read, or reason about the *content* of another
   audit's evidence, Charter, or Manifest as part of this check — a match is reported by checksum
   alone. Reading another audit's content here is how unrelated details (a different project's name,
   a different org's vendor list) leak into this run's reasoning; the isolation is the point. If a
   prior audit already covers this same evidence, surface the match (audit ID, date, file) to the
   human **before** drafting a new Charter — do not silently re-derive a Charter and re-run the full
   pipeline against evidence that already has a report. This is a visibility step, not a block: the
   human may still choose to re-audit (e.g. against a different standard baseline), but that should
   be a deliberate choice, not a discovery made by accident after the fact.
3. **Propose Artifact Declaration (function 1)** — from the data: classify each supplied artifact by type (risk register, schedule, status report, …).
4. **Propose Field Semantics Map (function 2)** — from the data: for each significant field, propose its business meaning, flagging every assumption.
5. **Propose Materiality & Scope (function 3)** — from the applicability map: which artifact types, governance levels, thresholds, and time period the _standards_ expect to be in evidence.
6. **Surface candidate Missing gaps** — every artifact the applicability map expects but the upload lacks is listed for the human to **supply, confirm as a finding, or explicitly waive**.
7. **Present the draft Charter** for ratification: the three proposals, all assumptions, and the
   candidate-Missing list, each marked with what it was derived from (data vs. standards). Present
   this as **one** ratification decision, not a multi-round Q&A: for every ambiguity encountered
   while drafting (an inferred organization name, a template row that looks illustrative rather than
   real, how to disposition a candidate-Missing item), propose a reasonable default and flag the
   assumption directly in the Charter text — do not stop to ask a separate clarifying question for
   each one before the human can even reach a ratification decision. The single ratify / edit / "just
   run it" / decline response (Decision Logic) is the resolution mechanism; "edit" is how the human
   overrides any default that's wrong.
8. **Record the outcome and write the Charter** to this project's own `reports/` folder — a sibling
   of its `evidence/` folder (e.g. `Audit/<ProjectName>/reports/`, next to
   `Audit/<ProjectName>/evidence/`; `references/file-naming.md`) — ratified (with ratifier and date)
   or PROVISIONAL.

### Decision Logic

- IF a prior audit of this same evidence (matching checksums) already exists in another project's
  `reports/` folder → present
  it to the human alongside the draft Charter proposal (Activity 2) rather than proceeding silently.
  A different standard baseline, a re-scoped Charter, or evidence that has since changed are all
  legitimate reasons to re-audit — but the human should decide that knowingly, not learn about the
  prior run only after a second full pipeline has already run.
- IF the human **ratifies** → Charter becomes the immutable interpretation contract for the run.
- IF the human **edits** → incorporate the edits and re-present; only the human-approved version is ratified.
- IF the human says **"just run it"** → proceed with a **PROVISIONAL Charter** (§4.2 function 4); the flag is carried in the Charter and every finding in the run inherits the unratified-interpretation caveat.
- IF the human **declines and does not proceed** → hard stop (see Failure Conditions). A declined Charter is not a PROVISIONAL Charter.
- An absence vs. the standards' expectations surfaces as a candidate **Missing** gap for the human to confirm or waive — never inferred "out of scope" from the data alone. Only human-waived items are out of scope.
- After ratification the Charter cannot change mid-run; new data or a scope change means re-entering Stage 1.

### Outputs

Written to this project's own `reports/` folder, a sibling of its `evidence/` folder (see
Activity 8):

1. **The PMO Data Charter** — ratified (ratifier + date) or marked PROVISIONAL.
2. **Candidate Missing gap dispositions** — each standards-expected absence with its outcome: supplied / confirmed (carried into Stage 3 as a finding seed) / waived (with the human's stated reason).

### Failure Conditions

- No delivery data supplied → **HARD STOP**, emit `DATA_ABSENT`, print:
  > **DATA_ABSENT — no delivery data found.** The baseline is ready, but there is nothing to audit against it. Supply the organization's delivery artifacts and re-run.
- Human declines to ratify and does not choose "just run it" → **HARD STOP**, emit `CHARTER_DECLINED`, print:
  > **CHARTER_DECLINED — no ratified Charter.** No ratified Charter, no comparison (Principle 0). Correct the proposal and re-run Stage 1.
- The data is unreadable in its entirety (corrupt, encrypted, unsupported formats) → **HARD STOP** with the list of failed artifacts and the reason each failed.

### Completion Criteria

- Every supplied artifact appears in the Artifact Declaration with a type.
- Every significant field has a semantic definition, with assumptions flagged.
- Every scope and materiality item cites a standards anchor (registry item), not the data.
- Every standards-expected-but-absent artifact has a human disposition: supplied, confirmed, or waived.
- The Charter records its ratification status: ratifier + date, or PROVISIONAL.

### Transition

→ `CHARTER_RATIFIED` (PROVISIONAL is a flag carried inside the Charter, not a separate state; declined = hard stop, no transition)

---

## Stage 2 — Define

### Purpose

Resolve which standards govern each declared artifact; deep-dive those registry sections; request companion data.

### Preconditions

`CHARTER_RATIFIED`

### Inputs

- the outputs defined in stage 1 (The PMO Data Charter + Candidate missing gap dispositions)
- Standards and methodologies in `knowledge/` (baseline)
- the derived registry and applicability map from stage 0
- the projects, programs, portfolios, and PMO artifacts declared in the Charter

### Activities

1. **Resolve artifact → standard mapping** — using Stage 0's applicability map, determine which
   governing standard(s) and section(s) apply to each artifact declared in the ratified Charter.
   Every declared artifact must resolve to at least one governing section, or be flagged as having
   none.
2. **Deep-dive resolved sections** — for each governing section resolved in Activity 1 that is
   still skeleton-level (per `derivation_manifest.json`), read its body text and write or update the
   corresponding registry item in Appendix E format (`references/registry-format.md`), paraphrased
   per Principle 3 — never verbatim. Skip any section whose registry item already exists with a
   matching source fingerprint.
3. **Cross-check against the Field Semantics Map** — compare the resolved mapping to the Charter's
   Field Semantics Map (Contract 2, function 2). Flag any Charter-declared field with no
   corresponding registry criterion, and any registry criterion with no corresponding declared
   field.
4. **Surface companion data requests** — review Stage 1's candidate Missing-gap dispositions. For
   every standards-expected artifact type still unsupplied or unresolved, request the specific
   companion data from the user, naming the artifact type and the standard/section that requires
   it.
5. **Write the Stage 2 output** — record the artifact → standard/section resolution map, the
   updated registry entries, the Field Semantics cross-check flags, and the disposition of every
   companion-data request (supplied / still pending / carried forward) for Stage 3 to consume.

### Decision Logic

- IF an artifact declared in the Charter resolves to **no** governing standard or section in the
  applicability map → flag it for visibility. Not a hard stop — an artifact type the standards
  don't recognize is itself worth noting, not silently passed over.
- IF a resolved governing section already has a registry item AND its fingerprint matches the
  current `knowledge/` contents → reuse it; skip the deep-dive for that section (mirrors Stage 0's
  reuse rule).
- IF a resolved governing section has no registry item, or its fingerprint no longer matches →
  deep-dive it now (Activity 2).
- IF the Field Semantics cross-check finds a Charter-declared field with no corresponding registry
  criterion → note it; not a failure. The field may be operationally meaningful without being
  standards-derived.
- IF the cross-check finds a registry criterion with no corresponding Charter-declared field →
  carry it forward as a priority candidate gap for Stage 3 to evaluate first.
- IF companion data is requested (Activity 4) and the human supplies it before this stage completes
  → incorporate it and re-run Activity 1's resolution for the affected artifact(s).
- IF companion data is requested and the human does not supply it → do **not** hard-stop. Carry the
  unresolved request forward into Stage 3 as a candidate gap, the same way Stage 1 carries forward a
  standards-expected-but-absent artifact rather than inferring it out of scope. Absence is evidence,
  not a blocker, once the evidence-sufficiency gate (Halt Condition 6) has already been passed in
  Stage 1.
- IF **every** declared artifact resolves to no governing standard/section at all (a total mapping
  failure) → HARD STOP (see Failure Conditions). This indicates a genuine Charter/scope mismatch,
  not a normal per-artifact gap.
- IF at least one artifact resolves successfully → proceed to Stage 3 once Activities 1–5 complete,
  regardless of any unresolved companion-data requests.

### Outputs

Registry files updated in `registries/` (same location and format as Stage 0 — local-only,
gitignored):

1. **Deep-dived registry entries** — any registry item touched by Activity 2, now holding full
   checkable criteria rather than a skeleton-level placeholder.

Carried forward as working understanding — not written to disk. No new artifact type is introduced
here: Stage 0's registry and Stage 1's Charter remain the only disk-persisted judgment outputs
before the Stage 7 Manifest gate.

2. **Artifact → standard/section resolution map** — which governing section(s) apply to each
   declared artifact, including any artifact flagged as unresolved (Decision Logic).
3. **Field Semantics cross-check flags** — Charter fields with no registry basis, and registry
   criteria with no Charter field, both carried into Stage 3 as areas warranting attention.
4. **Companion-data request dispositions** — each request from Activity 4, marked supplied / still
   pending / carried forward as a Stage 3 candidate gap.

### Failure Conditions

- Every artifact declared in the Charter resolves to no governing standard or section (Decision
  Logic) → **HARD STOP**, emit `STANDARDS_UNRESOLVED`, print exactly:
  > **STANDARDS_UNRESOLVED — no declared artifact maps to any standard in scope.** The ratified
  > Charter and the standards baseline do not agree on what is being audited. This is a
  > Charter/scope problem, not a per-artifact gap. Re-examine the Charter's declared scope against
  > the standards in `knowledge/`, correct the mismatch, and re-run from Stage 1.
- A governing section resolved in Activity 1 cannot be read for deep-dive (its source document
  became corrupt or unreadable since Stage 0's skeleton scan) → not a hard stop. Log it, skip the
  deep-dive for that section only, and flag it in the Stage 2 output for the human's attention.

### Completion Criteria

- Every artifact declared in the Charter has a recorded resolution outcome — either its governing
  standard(s)/section(s), or an explicit unresolved flag (Decision Logic).
- No registry item needed for a resolved section remains skeleton-level: each is either reused
  (fingerprint match) or freshly deep-dived.
- The Field Semantics cross-check has run, and every flag it raised is recorded for Stage 3.
- Every companion-data request from Activity 4 has a recorded disposition: supplied, still pending,
  or carried forward as a Stage 3 candidate gap.
- At least one artifact resolved to a governing standard — otherwise Failure Conditions applies,
  not completion.

### Transition

→ `INTENT_DEFINED` (unresolved companion-data requests do not block this transition — they carry
forward as Stage 3 candidate gaps; `STANDARDS_UNRESOLVED` is a hard stop, no transition)

---

## Stage 3 — Measure

### Purpose

Evaluate every applicable registry criterion against the delivery evidence; each failure becomes a gap.

### Preconditions

`INTENT_DEFINED`

### Inputs

- The artifact → standard/section resolution map and deep-dived registry entries from Stage 2
  (working understanding, not a file — see Stage 2 Outputs).
- The ratified PMO Data Charter, specifically its Field Semantics Map — required to interpret what
  each field in the evidence actually means before it can be measured.
- The delivery artifacts declared in the Charter, read directly (not just their inventory).
- Stage 2's carried-forward items: unresolved companion-data requests and Field Semantics
  cross-check flags — these are evaluated as candidate gaps in this stage, not dropped.

### Activities

1. **Read the evidence** — read every delivery artifact declared in the Charter, to observe, not
   yet to judge. Do not interpret any field the Charter's Field Semantics Map has not defined.
   For tabular artifacts (spreadsheets, exports), map each value to its header **by column index**,
   not by visual position or memory — a header row and a data row read separately are easy to
   misalign by one column, and a misaligned read produces a confidently wrong number, not an
   obviously wrong one. When a finding's evidence depends on a count of matching rows (e.g. "N rows
   have no schedule data"), enumerate every row against the actual condition rather than sampling or
   estimating — an undercount is a citation error like any other, even though it feels like a detail.
2. **Evaluate each applicable criterion** — for every registry criterion Stage 2 resolved as
   applicable to a given artifact, apply that criterion's `Evaluation Method` (`registry-format.md`,
   Appendix E) against the observed evidence in that artifact.
3. **Run four self-consistency sub-checks within each artifact** — independent of any registry
   criterion: run all four on every artifact; none is optional or criterion-triggered.
   1. **Same-document header/summary vs. body** — where a document states its own summary or
      executive-summary figure for a value, verify it agrees with that same document's detailed
      table/section for the same value.
   2. **Cross-document same-fact restatement** — identify any figure that is stated more than once
      across artifacts (a total that also appears in a summary table, a budget line repeated in a
      detail section, a count restated elsewhere) and verify the restatements agree.
   3. **Enumerated ID-list completeness across artifacts** — for any ID that should carry forward
      between artifacts (risk, change-request, issue, or milestone IDs), verify every ID present in
      its source artifact (e.g., the Risk Register) also appears, or is explicitly accounted for, in
      every downstream artifact that should reference it.
   4. **Narrative facts restated in prose** — verify timestamps, dates, and named events stated as
      prose text (not only tabular figures) agree with every other statement of the same fact,
      whether that other statement is tabular or narrative.

   A mismatch under any of the four is evidence on its own, whether or not any standard's criterion
   happens to cover that field: two "100% field coverage" documents have both concealed exactly this
   kind of internal contradiction in real audits (see `gap-taxonomy.md`'s `Untrusted` type — data
   that conflicts with itself or other data). This raises the floor, not a guarantee — still LLM
   judgment over long documents, not a deterministic parser; running all four reduces the miss rate,
   it does not eliminate it.
4. **Record a raw gap on failure** — where the evidence does not satisfy a criterion, or any of
   Activity 3's four sub-checks finds a disagreement (a figure, an ID, or a narrative fact that
   doesn't match its own restatement), cite the exact evidence (a quote, field value, or explicit
   statement of absence, per Evidence Discipline §6.1) and record one raw gap: which criterion
   failed (or which sub-check found a disagreement, and what disagrees), the citation, and a
   one-line description of the variance. Where the evidence satisfies the criterion and every
   sub-check finds agreement, record nothing — a pass is not a finding.
5. **Resolve Stage 2's carried-forward items** — evaluate every unresolved companion-data request
   and Field Semantics cross-check flag from Stage 2 as its own candidate gap: a genuinely
   standards-required absence becomes a raw gap (Missing-Data Rules, §6.2); anything the standards
   don't actually require is dropped, with the reason recorded.
6. **Do not classify or trace yet** — a raw gap records only the failed criterion, its cited
   evidence, and the variance description. Gap type (Stage 4) and root origin (Stage 5) are not
   assigned here.
7. **Consolidate the raw gap list** — ordered by artifact, then criterion, for Stage 4 to consume.

### Decision Logic

- IF the evidence satisfies a criterion's Evaluation Method → no gap is recorded. A pass is not a
  finding.
- IF the evidence does not satisfy a criterion AND citable evidence exists for the variance (a
  quote, field value, or explicit absence) → record exactly one raw gap.
- IF any of Activity 3's four self-consistency sub-checks finds a disagreement (a repeated figure,
  a cross-document restatement, an ID missing from a downstream artifact, or a narrative fact
  restated inconsistently) → record exactly one raw gap citing both (or all) locations and values,
  regardless of whether any registry criterion covers that field. Marking an artifact's field
  coverage as complete is about presence, not agreement — do not let a "100%" coverage figure stand
  in for having actually reconciled it.
- IF a variance is suspected but no evidence can be cited for it → do **not** record a raw gap
  (§6.1). Note it only as a candidate for the Synthesis narrative in Stage 7 — never in the raw gap
  list.
- IF the same underlying problem recurs across many records of one artifact against one criterion →
  **one** raw gap with multiple evidence bullets, never one gap per row (§6.3 No-Duplicate Rule,
  enforced later by the validator — enforce it here first).
- IF an artifact a criterion applies to cannot be read → do not invent a result. Record the read
  failure itself as the cited evidence for a raw gap (explicit absence of a valid read), rather than
  silently skipping the criterion.
- IF a criterion needs a field the Charter's Field Semantics Map has not defined → do not interpret
  it. This is a Stage 2 omission, not a Stage 3 measurement — flag it back rather than guessing at
  meaning.
- IF a Stage-2 carried-forward item resolves to a genuine standards-required absence → raw gap
  (§6.2). IF it does not (the standard doesn't actually require it) → drop it, with the reason
  recorded in the Stage 3 output.

### Outputs

Carried forward as working understanding — not written to disk. No new artifact type is introduced
here, consistent with Stage 2: the first disk-persisted judgment content after Stage 1's Charter is
Stage 7's Manifest.

1. **The raw gap list** — every variance found, each with its cited evidence and the registry
   criterion it failed. Not yet classified by gap type or root origin.
2. **The criteria-evaluated record** — confirmation of every criterion that was checked and passed
   (no gap), needed later for the evidence/coverage figures Stage 7's Manifest header requires.
3. **Dispositions for every Stage 2 carried-forward item** — resolved into either a raw gap or an
   explicitly recorded reason for dropping it.

### Failure Conditions

This stage introduces no new hard-stop condition. By this point the evidence-sufficiency gate
(Stage 1, Halt Condition 6) and data-readability checks are already satisfied, and Stage 2's own
hard stop (`STANDARDS_UNRESOLVED`) guarantees at least one applicable criterion exists to measure.
Any per-criterion problem discovered here — an unreadable artifact, an undefined field — is handled
by Decision Logic as a raw gap or a flag, not a hard stop. Absence is evidence at this point in the
audit, not a blocker.

### Completion Criteria

- Every registry criterion Stage 2 resolved as applicable has been evaluated — satisfied (no gap)
  or failed (raw gap recorded) — none skipped without a recorded reason.
- Every raw gap carries citable evidence (a quote, field value, or explicit absence); none exist
  without one.
- No two raw gaps share the same criterion + artifact combination for the same underlying problem —
  those are consolidated into one gap with multiple evidence bullets.
- Every item Stage 2 carried forward has a recorded disposition: raw gap, or explicitly dropped with
  a reason.

### Transition

→ `GAPS_MEASURED` — a raw gap list with **zero** entries is a valid, legitimate outcome, not a
failure, if every applicable criterion was genuinely satisfied by the evidence. Do not treat "no
gaps found" as a sign something was skipped.

---

## Stage 4 — Classify

### Purpose

Assign each gap exactly one of the 7 gap types (§7). No overlap, no duplicates.

### Preconditions

`GAPS_MEASURED`

### Inputs

- The raw gap list from Stage 3 — each entry with its cited evidence and the registry criterion it
  failed (working understanding, not a file).
- `references/gap-taxonomy.md` — full definitions, detection logic, examples, misclassification
  traps, and the disambiguation rules for all 7 gap types. Read it before classifying anything.

### Activities

1. **Test in the fixed order, per gap** — for **every** raw gap from Stage 3, independently, apply
   `gap-taxonomy.md`'s classification order (Missing → Ignored → Divergent → Disconnected →
   Untrusted → Underutilized → Misclassified), testing that one gap's Detection steps against the 7
   types in that sequence. Stop testing types **for that gap** once one matches — a gap is exactly
   one type, never more. This does not limit how many gaps get classified: none of Stage 3's raw
   gaps are skipped, deferred, or held back for a later run. Every gap is classified and carried into
   the same Gap Register; the audit reports all of them in one run, ordered by severity (Stage 6) for
   the user to prioritize — it does not surface one gap, wait for a fix, and re-run for the next.
2. **Check against traps and counter-examples** — before finalizing a match, check
   `gap-taxonomy.md`'s Common Misclassification Traps and Counter-examples for that type. Where one
   matches the gap, use the type it names instead of the naive-seeming one.
3. **Split, don't blend** — where a raw gap actually contains two distinct problems (not one
   ambiguous problem), split it into two separate findings, one per gap type — never force one
   finding to carry two types.
4. **Record the assignment** — carry the finding forward with exactly one gap type assigned and its
   Stage 3 evidence unchanged.

### Decision Logic

This is already fully specified in `gap-taxonomy.md` — do not re-derive it here.

- Apply the classification order exactly as written there: Missing → Ignored → Divergent →
  Disconnected → Untrusted → Underutilized → Misclassified. The first type whose Detection steps
  match is the assigned type.
- IF a gap could plausibly fit two types → apply the specific pairwise rule in `gap-taxonomy.md`'s
  "Disambiguation Rules" section (Missing vs. Ignored; Ignored vs. Divergent; Disconnected vs.
  Underutilized; Untrusted vs. Missing; Misclassified vs. Divergent) — the pairwise rule takes
  precedence over the general testing order when both types genuinely apply.
- IF a candidate classification matches a documented Common Misclassification Trap for that type →
  use the trap's stated correct type, not the naive one.
- IF a raw gap actually describes two distinct problems → split it (Activity 3); never assign two
  gap types to one finding (`gap-taxonomy.md`, "What You Must Never Do").
- IF none of the 7 types' Detection steps match → this should not happen for a raw gap that Stage 3
  correctly cited with real evidence. Treat it as a Stage 3 defect — an insufficiently specific raw
  gap — and return it, rather than forcing a classification.

### Outputs

Carried forward as working understanding — not written to disk. No new artifact type is introduced.

1. **Classified gaps** — every raw gap from Stage 3, now with exactly one gap type assigned, split
   into separate findings wherever two distinct problems existed.

### Failure Conditions

- IF Stage 4 receives zero raw gaps from Stage 3 AND Stage 3's criteria-evaluated record (Stage 3
  Output #2) is also empty or missing → this is **not** a legitimate clean-audit outcome — it means
  Stage 3 did not actually evaluate any criteria. **HARD STOP**, emit `EVALUATION_UNVERIFIED`, print
  exactly:
  > **EVALUATION_UNVERIFIED — Stage 3 produced no raw gaps and no record of what was evaluated.**
  > A clean result must show its work: every applicable criterion checked and passed. Zero raw gaps
  > with nothing evaluated means Measure did not run to completion. Return to Stage 3 and confirm
  > every criterion in the Stage 2 resolution map was actually evaluated before re-entering Stage 4.
- IF Stage 4 receives zero raw gaps from Stage 3 BUT Stage 3's criteria-evaluated record is
  populated (criteria were genuinely checked and passed) → this is a legitimate clean audit. Proceed
  with zero classified gaps — not a hard stop. This is the case Stage 3's own Transition note
  describes: "no gaps found" is a valid outcome, not a sign something was skipped.
- Otherwise: no new hard-stop condition. A gap that resists classification is a defect to return to
  Stage 3 (Decision Logic), not a reason to halt the audit.

### Completion Criteria

- Every raw gap from Stage 3 has exactly one gap type assigned — none left unclassified, none
  assigned two types.
- Every classification followed `gap-taxonomy.md`'s testing order and, where applicable, its
  pairwise disambiguation rules — not ad hoc judgment.
- Any raw gap that actually contained two distinct problems has been split into two findings.
- Cited evidence from Stage 3 is preserved unchanged on every classified finding.

### Transition

→ `GAPS_CLASSIFIED`

---

## Stage 5 — Trace

### Purpose

Trace each gap to exactly one of the 7 root origins (§8) — the earliest point the gap entered the system.

### Preconditions

`GAPS_CLASSIFIED`

### Inputs

- The classified gaps from Stage 4 — each with exactly one gap type assigned and its Stage 3
  evidence unchanged (working understanding, not a file).
- `references/root-origins.md` — full definitions, detection logic, examples, misclassification
  traps, the trace order, and the "Earliest Point" rule. Read it before tracing anything.

### Activities

1. **Test in the fixed order, per gap** — for **every** classified gap from Stage 4, independently,
   apply `root-origins.md`'s trace order (Capture → Integration → Definition/Taxonomy → Ownership →
   Process/Cadence → Tooling → Behavior), testing that gap's Detection steps against the 7 origins
   in that sequence. Stop testing origins **for that gap** once one matches — a gap traces to
   exactly one origin, never more. Every classified gap is traced; none are skipped, deferred, or
   held back for a later run.
2. **Trace backward to the earliest structural point** — do not stop at the first plausible cause.
   Apply the Earliest Point rule (`root-origins.md`): ask "why" repeatedly until reaching a
   structural cause with no further structural cause behind it (an unowned meeting is Ownership,
   not "the meeting was cancelled," which is only the symptom). Record the chain, not just the final
   answer, so the trace is auditable.
3. **Check against traps and counter-examples** — before finalizing a match, check
   `root-origins.md`'s Common Misclassification Traps and Counter-examples for that origin. Where
   one matches, use the origin it names instead of the naive-seeming one.
4. **Reconcile against Stage 4's classification** — if tracing reveals the gap's true root cause is
   inconsistent with its assigned gap type (`root-origins.md`'s own counter-examples show this can
   happen — e.g. what looks like Disconnected on the surface is actually Underutilized once traced),
   treat this as a Stage 4 defect: return the gap to Stage 4 for reclassification before tracing it
   further, rather than forcing a root origin onto a gap type that doesn't actually hold.
5. **Split, don't blend** — where a gap's trace reveals two distinct structural failures, split it
   into two separate findings, one per root origin — never assign two root origins to one finding
   (`root-origins.md`, "What You Must Never Do").
6. **Record the assignment** — carry the finding forward with exactly one root origin assigned, its
   Stage 3 evidence and Stage 4 gap type unchanged (except where Activity 4 corrected a genuine
   misclassification).

### Decision Logic

This is already fully specified in `root-origins.md` — do not re-derive it here.

- Apply the trace order exactly as written there: Capture → Integration → Definition/Taxonomy →
  Ownership → Process/Cadence → Tooling → Behavior. The first origin whose Detection steps match is
  the assigned origin.
- IF a gap could plausibly trace to two origins → apply the Earliest Point rule: trace backward
  through the "why" chain until reaching the earliest structural cause; that is the correct origin,
  not the first symptom encountered.
- IF a candidate trace matches a documented Common Misclassification Trap for that origin → use the
  trap's stated correct origin, not the naive one.
- IF "Behavior" is being considered → it requires positive evidence of deliberate choice (admission,
  pattern, workaround, manipulation). Absence of evidence is never Behavior by default — it is
  Capture, Ownership, or Process/Cadence depending on what is actually missing.
- IF "Tooling" is being considered → it requires proof the tool is structurally incapable, not just
  that a configuration or workflow change was never made. A fixable configuration gap is
  Process/Cadence or Behavior, not Tooling.
- IF the trace reveals the gap's Stage 4 classification does not actually hold → return it to
  Stage 4 (Activity 4); do not force a root origin onto an inconsistent gap type.
- IF a gap's trace reveals two distinct structural failures → split it (Activity 5); never assign
  two root origins to one finding.
- IF none of the 7 origins' Detection steps match after the Earliest Point trace → this should not
  happen for a gap correctly classified in Stage 4 with real evidence. Treat it as a Stage 4 defect
  and return it, rather than forcing a trace.

### Outputs

Carried forward as working understanding — not written to disk. No new artifact type is introduced.

1. **Traced gaps** — every classified gap from Stage 4, now with exactly one root origin assigned,
   split into separate findings wherever two distinct structural failures existed, ready for Stage 6
   to engineer a fix and assign severity.

### Failure Conditions

- IF **every** classified gap Stage 5 receives gets returned to Stage 4 under Activity 4 (a 100%
  reconciliation-failure rate, not a few isolated corrections) → this is not normal classification
  noise, it indicates a systemic problem — e.g. Stage 4 applied a stale or wrong taxonomy version, or
  Stage 3's evidence citations are fundamentally malformed. **HARD STOP**, emit
  `SYSTEMIC_MISCLASSIFICATION`, print exactly:
  > **SYSTEMIC_MISCLASSIFICATION — every classified gap failed root-origin reconciliation.** This is
  > not isolated misclassification; it indicates Stage 4 or Stage 3 has a structural defect, not a
  > per-gap error. Do not continue returning gaps one at a time. Halt, re-verify Stage 3's evidence
  > citations and Stage 4's taxonomy application against the current `gap-taxonomy.md`, then re-run
  > from Stage 4.
- Otherwise: no new hard-stop condition. A gap returned to Stage 4 for reclassification (Activity 4)
  is a normal correction, not a reason to halt the audit.

### Completion Criteria

- Every classified gap from Stage 4 has exactly one root origin assigned — none left untraced, none
  assigned two origins.
- Every trace followed `root-origins.md`'s testing order and the Earliest Point rule — none stopped
  at the first symptom encountered.
- Every trace was checked against `root-origins.md`'s misclassification traps, not decided by ad hoc
  judgment.
- Any gap whose trace revealed an inconsistent Stage 4 classification has been returned and
  reclassified, not forced.
- Any gap whose trace revealed two distinct structural failures has been split into two findings.
- Cited evidence and gap type from Stages 3–4 are preserved unchanged on every traced finding,
  except where Activity 4 corrected a genuine misclassification.

### Transition

→ `ROOTS_TRACED` — this stage neither adds nor removes gaps (aside from splits under Activity 5 or
corrections under Activity 4); a traced gap list with zero entries is exactly as legitimate as
Stage 4's zero-gap case, for the same reason.

---

## Stage 6 — Engineer & Score

### Purpose

Engineer the fix-at-source for every finding and assign its severity, using the four-part
diagnostic (Evidence · Impact · Why/Who/Scope · Fix-at-source) and the severity rubric (Appendix D).
The Reporting Integrity Score is **not** computed here — it is computed deterministically by
software in Stage 8 (`scoring.md` §9.2, §9.5); this stage never calculates or estimates it. IEM-PM
does not model organizational maturity (scrapped, not deferred — see `scoring.md` §9.4).

### Preconditions

`ROOTS_TRACED`

### Inputs

- The traced gaps from Stage 5 — each with cited evidence, gap type, and root origin (working
  understanding, not a file).
- `references/severity-matrix.md` (Appendix D) — the three-dimension (Decision Impact × Spread ×
  Persistence) rubric for calibrating severity.
- `scoring.md` §9.1's Severity table (1–5, Cosmetic → Critical) — the field the Manifest, schema, and
  RIS actually consume.
- `assets/AUDIT_MANIFEST_template.md` §10.2.3, the Finding Block Template — the exact fields this
  stage's output must populate: `Impact`, `Severity`, `Recommended Action`, `Intelligence
Dimensions`.

### Activities

1. **Run the four-part diagnostic per gap** — for every traced gap from Stage 5, work through, in
   order:
   - **Evidence** — already established (Stage 3). Do not re-gather; only confirm it is still
     cited.
   - **Impact** — write the narrative impact on delivery capability: what decision, governance
     action, or outcome is distorted, delayed, or put at risk. This becomes the Finding Block's
     `Impact` field.
   - **Why/Who/Scope** — using the Stage 5 root origin as the "why," identify who is accountable or
     affected, and how far the gap spreads (one record, one artifact, one project, one program, one
     portfolio, enterprise-wide). This grounds the Spread and Persistence dimensions in Activity 2
     and directly informs the Recommended Action's target in the next step.
   - **Fix-at-source** — write the Recommended Action: a specific, actionable remediation that
     addresses the Stage 5 root origin, not the symptom. This becomes the Finding Block's
     `Recommended Action` field.
2. **Calibrate severity using the rubric** — score the three dimensions (`severity-matrix.md`):
   Decision Impact (1–4), Spread (1–5, from the Why/Who/Scope step above), Persistence (1–4).
   Multiply for the raw score, band it (Low/Medium/High/Critical), and apply the Critical-floor
   rule.
3. **Bridge the band to the 1–5 field** — the matrix's four bands do not map one-to-one onto the
   Manifest's five-point scale. Use Decision Impact within the band to place it precisely (Decision
   Logic).
4. **Tag Intelligence Dimensions** — from the Impact narrative (step 1), name which of the 7
   Intelligence Indicators (Visibility, Integrity, Connectivity, Governance, Predictability,
   Decision Quality, Continuous Improvement) this finding touches. One or more, comma-separated —
   this becomes the Finding Block's `Intelligence Dimensions` field, and is what Stage 7 draws on
   when writing the portfolio-wide Synthesis narrative per indicator.
5. **Never average, never blend severities** — if the same underlying gap would score differently
   depending on context (e.g. Severity 2 in one project, Severity 4 in another), split it into two
   findings, one per context (`scoring.md` §9.1 Severity Calibration Rules).

### Decision Logic

- **Severity formula** (`severity-matrix.md`): Score = Persistence (1–4) × Spread (1–5) × Decision
  Impact (1–4); range 1–80. Bands: ≤8 Low, 9–24 Medium, 25–48 High, ≥49 Critical. Floor rule:
  Decision Impact = Critical → minimum High band, regardless of score.
- **Band → 1–5 bridge** (not specified in `severity-matrix.md` — resolved here, proposed default,
  not yet confirmed):
  - Low band → **1 (Cosmetic)**, unless Decision Impact ≥ Medium despite the low overall score →
    **2 (Minor)**.
  - Medium band → **2 (Minor)** if Decision Impact ≤ Medium; **3 (Moderate)** if Decision Impact ≥
    High.
  - High band → **4 (Major)**, unless Decision Impact is Low/Medium despite the wide reach →
    **3 (Moderate)**.
  - Critical band → **5 (Critical)**, always.
  - Critical-floor cases (lifted by the matrix's own floor rule) → minimum **4 (Major)**, matching
    the matrix's minimum-High floor.
  - If a finding sits at a band boundary and the exact integer is genuinely ambiguous, flag it —
    don't silently round.
- IF the same underlying gap would score differently in different contexts → split into two
  findings (Activity 5), never average.
- IF Decision Impact cannot be determined from the cited evidence → do not guess. This means the
  Impact narrative (Activity 1) is incomplete — finish it before scoring.
- IF a Recommended Action would only fix the symptom, not the Stage 5 root origin → it is not
  complete; revise it (`AUDIT_MANIFEST_template.md`'s own rule: "Recommended Action must address the
  root origin, not the symptom").

### Outputs

Carried forward as working understanding — not written to disk. No new artifact type is introduced;
Stage 7's Manifest remains the first disk-persisted judgment content since Stage 1's Charter.

1. **Engineered findings** — every traced gap from Stage 5, now carrying an Impact narrative,
   Severity (1–5 integer), a Recommended Action (fix-at-source), and Intelligence Dimensions
   tag(s) — ready for Stage 7 to format into Finding Blocks.

Explicitly **not** an output of this stage: the Reporting Integrity Score. That is Stage 8's job,
computed deterministically by `manifest_to_findings.py` from the findings Stage 7 writes to the
Manifest (`scoring.md` §9.2, §9.5).

### Failure Conditions

No new hard-stop condition. Mirrors Stage 4 and Stage 5's posture: this stage refines judgment, it
does not gate the audit. A Recommended Action that still addresses only the symptom (Decision Logic)
is a defect to revise in place, not a reason to halt.

### Completion Criteria

- Every traced gap from Stage 5 has all four fields this stage owns: `Impact`, `Severity` (1–5
  integer), `Recommended Action`, `Intelligence Dimensions`.
- Every Severity assignment is traceable to a Decision Impact / Spread / Persistence score and band
  (`severity-matrix.md`) — none asserted without calibration.
- Every Recommended Action addresses the Stage 5 root origin, not the symptom.
- No finding's severity was averaged across contexts — genuinely context-dependent gaps were split
  (Activity 5).
- The Reporting Integrity Score has not been calculated anywhere in this stage's output — that
  remains Stage 8's job.

### Transition

→ `SCORED`

---

## Stage 7 — Synthesize (the Manifest Gate)

### Purpose

Write the complete Audit Manifest to disk (§10) — the compaction-survival gate. Everything after this is deterministic.

### Preconditions

`SCORED` — but unlike every other stage in this file, this precondition is not accepted as a bare
flag. Stages 0–6 write nothing to disk except the Charter (Stage 1); everything else exists only in
working memory. If that memory was ever interrupted or compacted between Stage 1 and here, `SCORED`
could be true as a label while the substance behind it is partially gone — and a label alone cannot
prove otherwise. Before writing anything, Stage 7 must verify — not merely assume — that the full
chain actually holds:

`BASELINE_READY` → `CHARTER_RATIFIED` → `INTENT_DEFINED` → `GAPS_MEASURED` → `GAPS_CLASSIFIED` →
`ROOTS_TRACED` → `SCORED`

Concretely, this means every finding about to be written must carry a complete, unbroken chain of
contributions from every stage that touched it — cited evidence (Stage 3), a gap type (Stage 4), a
root origin (Stage 5), and Impact/Severity/Recommended Action/Intelligence Dimensions (Stage 6). See
Activity 1 and Decision Logic below for how this is actually checked, not just asserted. (Stages 1–6
don't need this same treatment on their own Preconditions — they're one continuous, unbroken
reasoning stretch with no disk-persistence boundary between them. Stage 7 is the first checkpoint
since Stage 1, which is exactly why it is the compaction-survival gate.)

### Inputs

- Every finding engineered through Stage 6 — Impact, Severity, Recommended Action, Intelligence
  Dimensions — plus its Stage 3 evidence, Stage 4 gap type, and Stage 5 root origin (the complete
  working understanding accumulated across Stages 3–6; working understanding, not a file).
- The ratified (or PROVISIONAL) PMO Data Charter from Stage 1 — Charter Version and Status for the
  Header Block.
- The artifact inventory (Stage 1) and per-artifact observations (Stage 3's evidence reading) — for
  the Per-Artifact Evidence Log.
- `assets/AUDIT_MANIFEST_template.md` — the exact parser-grade format (Header Block, Per-Artifact
  Evidence Log, Finding Block, Synthesis, Appendix). Read before writing anything (§10.2).
- `references/file-naming.md` (Appendix G) — the output filename convention.

### Activities

1. **Verify the full chain before writing anything** — for every gap in the working understanding,
   confirm it carries: cited evidence (Stage 3), exactly one gap type (Stage 4), exactly one root
   origin (Stage 5), and Impact/Severity/Recommended Action/Intelligence Dimensions (Stage 6). This
   is the substantive check behind the `SCORED` label — nothing before this stage is on disk, so
   this is the only place that label can actually be verified rather than trusted.
2. **Write the Header Block** (§10.2.1) — Audit ID, Charter Version, Standards Baseline, Scope,
   Analyst, Date, Status (RATIFIED / PROVISIONAL), Skill Version (read from `SKILL.md` §13.4, not
   guessed), and Model (what you actually are, per your own system context — write "unknown" rather
   than fabricate this if it's genuinely not available).
3. **Write the Per-Artifact Evidence Log** (§10.2.2) — one `## ARTIFACT:` block per artifact
   declared in the Charter, with observations from Stage 3's evidence reading. For `**Checksum:**`,
   compute a real SHA-256 of the artifact file (e.g. a one-line shell/Python command such as
   `python -c "import hashlib;print(hashlib.sha256(open(path,'rb').read()).hexdigest())"`) — never
   write the literal word "computed" as a placeholder. A fabricated-looking hash string is worse
   than an honest gap: only write a hash you actually computed from the file.
4. **Write the Gap Register** (§10.2.3) — one `### FINDING:` block per engineered finding from
   Stage 6, in the exact format: Gap Type, Root Origin, Standard, Clause, Identifier, Requirement
   Summary, Description (minimum 20 words), Severity, Impact, Recommended Action, Intelligence
   Dimensions, plus at least one evidence bullet. If Severity is 4 or 5, this is also where you
   actually surface the finding to the human operator and record their real answer as Human
   Approved — never write "Yes" on your own authority (§10.3 rule 9). If they approve it, record
   Approved By and Approval Date too; an "Approved" with no accountable name attached is rejected.
5. **Write the Synthesis section** (§10.2.4) — narrative diagnostics for all 7 Intelligence
   Indicators, drawing on the Intelligence Dimensions tags assigned in Stage 6. Qualitative only,
   never scored or graded. A *positive* claim about an artifact (data "traces consistently," figures
   "match," a linkage "holds") is a factual assertion like any other — do not write one unless one of
   Stage 3's Activity 3 sub-checks actually checked that specific figure, ID, or narrative fact.
   Where coverage was checked but reconciliation wasn't, say so precisely ("no discrepancy found in
   the fields checked") rather than a blanket claim of consistency the artifact wasn't actually
   tested against.
6. **Write the Appendix** (§10.2.5) — Schema Version, Total Findings, Artifacts Examined, Standards
   Referenced.
7. **Run Final Validation** — check the completed Manifest against all 10 checks in
   `completion-checklist.md` §12.1 before declaring it done.
8. **Save the Manifest** — to this project's own `reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.md`, a
   sibling of its `evidence/` folder (e.g. `Audit/<ProjectName>/reports/...`; Appendix G,
   `references/file-naming.md`), using this audit's own Date — not wall-clock run time.
9. **Print the Handover Message** (`completion-checklist.md` §12.3) and stop. Do not run scripts,
   calculate the Reporting Integrity Score, or render reports.

### Decision Logic

- IF any finding is missing a link in the chain (no cited evidence, no gap type, no root origin, or
  no Stage 6 fields) → the working memory was not actually intact, regardless of what state was
  believed to hold. This is different from a `completion-checklist.md` §12.1 Manifest-writing defect
  — it is evidence that context was lost somewhere in Stages 0–6, before this stage ever started
  writing.
- IF chain loss is found → there is no saved intermediate state to recover from (nothing was written
  to disk before this stage). Re-enter the earliest stage whose contribution is missing and redo
  that gap's work from the original evidence. Do not guess, average, or fabricate the missing fields
  to complete the Manifest — an invented Severity or Root Origin is worse than an honest re-run.
- IF the missing stage's work cannot be redone in the current session (e.g. the underlying evidence
  artifacts are no longer accessible) → this is a hard stop (see Failure Conditions), not something
  to paper over.
- Once the chain is verified intact: write incrementally or all at once, but never hold a finding in
  memory without recording it (Phase 6 rule). If context is at risk of compaction while writing, save
  progress as you go — the Manifest, once on disk, is the recovery point this stage's name refers to.
- IF Charter Status is PROVISIONAL → every Finding Block must carry the caveat "(Based on unratified
  Charter interpretation.)" (§10.3 rule 8). Not optional, not skippable, no exceptions.
- IF Final Validation (`completion-checklist.md` §12.1) finds any failure → fix the Manifest before
  finishing. Do not hand over a broken Manifest to software (`completion-checklist.md` §12.1's own
  rule).
- IF a Finding Block is missing any of the 8 required fields (§10.3 rule 6) → the Manifest is
  incomplete. Do not write it as done.
- IF two Finding Blocks share the same Gap Type + Root Origin + Artifact + Standard Identifier → this
  should not happen if the No-Duplicate Rule (§6.5) was enforced upstream. If found here, merge them
  into one Finding Block with multiple evidence bullets before writing.
- IF the temptation arises to add an executive summary, JSON blocks, tables for findings, nested
  headings inside a finding, or software-execution notes → do not (§10.4, What Not to Include).
  These are exactly what breaks the regex parser.
- IF the temptation arises to calculate or estimate the Reporting Integrity Score anywhere in the
  Manifest → do not (`scoring.md` §9.2, §9.5). That field does not exist in this document; it is
  computed by Stage 8 from what you write here.

### Outputs

Written to this project's own `reports/` folder (local-only, gitignored, sibling of `evidence/`) —
the first disk-persisted judgment content since Stage 1's Charter:

1. **The Audit Manifest** — `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.md` (Appendix G,
   `references/file-naming.md`), containing all 5 required sections in order (§10.1): Header Block,
   Per-Artifact Evidence Log, Gap Register, Synthesis, Appendix.

This is the **only** file this stage produces (`completion-checklist.md` §12.2's Output Checklist). The matching `.json`,
`.html`, and `.txt` files, sharing the same name stem, are Stage 8/9's job — never written here.

### Failure Conditions

- IF chain-verification (Activity 1) finds a finding missing a required link, AND the missing
  stage's work **can** be redone in the current session (the original evidence and artifacts are
  still accessible) → not a hard stop. Redo that gap's work from the original evidence (Decision
  Logic), then resume.
- IF chain-verification finds a missing link that **cannot** be redone (the underlying evidence is
  no longer accessible, or too much context was lost to reliably reconstruct the missing stage's
  judgment) → **HARD STOP**, emit `CHAIN_INTEGRITY_LOST`, print exactly:
  > **CHAIN_INTEGRITY_LOST — a finding is missing required contributions from an earlier stage, and
  > the evidence needed to redo that work is no longer accessible.** `SCORED` was reached, but the
  > working memory behind it did not survive intact — likely a context interruption between Stage 1
  > and here. Nothing before this stage was ever written to disk, so there is no partial Manifest to
  > salvage. Re-run the audit from Stage 0, keeping delivery evidence accessible throughout the run.
- IF Final Validation (`completion-checklist.md` §12.1) fails on any check, separately from
  chain-verification, and cannot be corrected in place → do not write an incomplete Manifest and
  declare the audit done. Fix it, or if
  genuinely unrecoverable, return to the earliest stage where the missing information should have
  been captured. This is usually a transcription defect in this stage's own writing (Activities
  2–6), not memory loss — corrective, the same posture as Stages 4–6, not automatically
  `CHAIN_INTEGRITY_LOST`.
- No other new hard-stop condition. Once the chain is verified intact, this stage's job is to
  correctly transcribe what Stages 0–6 already established, not to make new
  judgment calls that could fail structurally.

### Completion Criteria

This stage's completion criteria are already fully specified in `completion-checklist.md` §12.1's
10-point Final Validation checklist — do not restate it here; run the Manifest against it directly.
Two additions specific to this stage, not covered by §12.1:

- Chain-verification (Activity 1) ran before writing began, and every finding in the Manifest
  carries a complete, unbroken chain from Stages 3–6 — not merely a `SCORED` label trusted at face
  value.
- The file is written to the correct path and name per Appendix G (`references/file-naming.md`) —
  not an arbitrary filename.
- The Handover Message (`completion-checklist.md` §12.3) has been printed.

### Transition

→ `MANIFEST_WRITTEN`

---

## Stage 8 — Findings JSON _(deterministic)_

### Purpose

Run `manifest_to_findings.py`: Manifest → validator (`schema.py`) → canonical findings JSON. Built
and tested (`scripts/test_pipeline.py`); the LLM never hand-writes the JSON and never runs judgment
here — this stage is pure software.

### Preconditions

`MANIFEST_WRITTEN`

### Inputs

- The Audit Manifest written in Stage 7 — `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.md`.
- Optionally, the ratified Charter path (`--charter`), if the run wants it passed through.

### Activities

1. **Run the script** — `python manifest_to_findings.py --manifest <path to Stage 7's Manifest>`
   (optionally `--output <path>` to override the Appendix G default).
2. **Parse** — the script's `ManifestParser` extracts the Header Block, Per-Artifact Evidence Log,
   Finding Blocks, and Synthesis section via regex.
3. **Validate the parse** — closed-taxonomy match (Gap Type, Root Origin), evidence bullet presence,
   severity range. Failures surface as `E-PARSE-*` codes (`references/error-codes.md`).
4. **Validate the structure** — `schema.py`'s `validate_canonical` / `validate_no_duplicates` /
   `validate_evidence_coverage` run against the parsed result. Failures surface as `E-VALID-*` codes.
5. **Compute the Reporting Integrity Score** — deterministically, from the validated findings
   (Weighted Gap Profile v1.2.0: severity deduction, density deduction, root-cause diversity
   deduction, Missing-gap deduction — `scoring.md` §9.2). This is the **only** place the RIS is
   calculated, anywhere in the pipeline.
6. **Write on success only** — if every check passes, write the canonical findings JSON next to the
   Manifest, in the same project `reports/` folder:
   `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.json` (Appendix G, same stem as the
   Manifest). If any
   check fails, print every error prefixed with its code and exit non-zero — `findings.json` is not
   written.

### Decision Logic

- IF the script exits 0 → `findings.json` is written; proceed to Stage 9.
- IF the script exits non-zero → do **not** hand-write or patch a JSON file, and do not reuse a
  stale one from a prior run. Fix the source of the error and re-run this script from the top.
- IF the error is an `E-PARSE-*` code → the Manifest's format itself is malformed (wrong taxonomy
  wording, missing evidence bullet, bad severity value). Fix the Manifest text — return to Stage 7.
- IF the error is an `E-VALID-*` code → the Manifest's format parsed fine, but its *content*
  violates a structural rule (duplicate finding signature, an evidence bullet citing an artifact ID
  never declared) — trace the defect back to the stage that actually assembled it (Stage 3's
  citation, Stage 4/5's classification), not just Stage 7's transcription.

### Outputs

`<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.json` (Appendix G, same stem as the Manifest,
same project `reports/` folder) — written only on successful validation.

### Failure Conditions

- Validator rejects the Manifest (`E-PARSE-*` or `E-VALID-*`) → **HARD STOP** for this stage, exit
  non-zero, `findings.json` not written. Fix the **Manifest** (or the stage that fed it a defect)
  and re-run. Never patch the JSON directly — the JSON is a derived artifact, not a source of truth.

### Completion Criteria

- The script exited 0.
- `findings.json` exists at the correct Appendix G path, sharing the Manifest's stem.
- No `E-PARSE-*` or `E-VALID-*` errors were printed.
- The Reporting Integrity Score is present in the JSON and was computed here — nowhere earlier in
  the pipeline.

### Transition

→ `JSON_VALIDATED`

---

## Stage 9 — Render _(deterministic)_

### Purpose

Run `render.py`: findings JSON → HTML + TXT. Same JSON in → byte-identical out. Built and tested
(`scripts/test_pipeline.py`); the LLM never edits rendered output and performs no judgment here —
this stage is pure software.

### Preconditions

`JSON_VALIDATED`

### Inputs

- `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.json` from Stage 8.
- `assets/report_template.html` (the default template — `paths.py`'s `DEFAULT_TEMPLATE`; overridable
  via `--template`).

### Activities

1. **Run the script** — `python render.py --canonical <path to Stage 8's findings.json>`
   (optionally `--template` / `--output-html` / `--output-txt` to override the Appendix G defaults).
2. **Compute display aggregates** — severity counts, gap-type counts, root-origin counts, artifact
   count — purely derived from the JSON already validated in Stage 8. No new judgment.
3. **Render the HTML report** — via Jinja2 template substitution against
   `assets/report_template.html`, written next to the input JSON, in the same project `reports/`
   folder: `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.html`.
4. **Render the TXT report** — the 10-section structure (Executive Summary, Audit Scope & Baseline,
   Delivery Evidence Summary, Gap Register, Root Cause Analysis, Intelligence Indicators, Reporting
   Integrity Score, Recommended Actions, Roadmap, Appendix), written to
   `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.txt`.

### Decision Logic

- IF the `--canonical` path does not exist → `E-RENDER-001` (`references/error-codes.md`), hard
  stop, exit 1, nothing written.
- IF the input JSON is present and already schema-valid (guaranteed by Stage 8's gate) → rendering
  cannot meaningfully fail on content grounds. There is no judgment left to exercise in this stage —
  only correct template substitution.
- Re-running this script on the same `findings.json` must produce byte-identical `.html`/`.txt`
  output. If it does not, that is a renderer defect, not a content problem — do not work around it
  by hand-editing the output.

### Outputs

`<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.html` and `.txt` (Appendix G, same stem as the
Manifest and JSON, same project `reports/` folder).

### Failure Conditions

- `--canonical` (the findings JSON) path does not exist → **HARD STOP**, emit `E-RENDER-001`, exit
  1. This should not happen if Stage 8 completed correctly and its output path was passed through
  unchanged.

### Completion Criteria

- Both `.html` and `.txt` files exist at the correct Appendix G path, sharing the Manifest's and
  JSON's stem.
- Re-rendering the same JSON produces byte-identical output — the determinism guarantee this stage's
  Purpose states.

### Transition

→ `REPORTS_RENDERED`

---

## Stage 10 — Final Summary

### Purpose

Print the TXT summary and the output file pointers; confirm the run checklist (§12).

### Preconditions

`REPORTS_RENDERED`

### Inputs

- `<project>/reports/IEMPM_AuditGap_Report_DDMMYY_HHMM.txt` from Stage 9.
- The 4 output file paths sharing this audit's name stem (Appendix G): `.md` (Stage 7), `.json`
  (Stage 8), `.html` and `.txt` (Stage 9).
- `completion-checklist.md` §12.2's Output Checklist — for the confirmation step.

### Activities

1. **Print the rendered TXT report** — relay Stage 9's already-deterministic output to the console.
   Nothing here is new judgment; this stage transcribes, it does not interpret.
2. **List all 4 output file paths** — `.md`, `.json`, `.html`, `.txt`, all sharing one name stem.
3. **Confirm the run checklist** (`completion-checklist.md` §12.2) — exactly one Manifest was written by the LLM (Stage 7);
   exactly one JSON/HTML/TXT triad was produced by software (Stages 8–9), sharing the same stem; no
   extra or missing files.
4. **Stop.** No further stages exist; the audit run is complete.

### Decision Logic

This stage makes no content decisions — it only relays what Stages 7–9 already deterministically
produced.

- IF any of the 4 expected files is missing at this point → that means an earlier stage did not
  actually complete, despite its own Completion Criteria appearing satisfied. Do not fabricate a
  summary from partial output — return to the stage whose file is missing.

### Outputs

Console summary only — evidence count, finding count, gap summary, Reporting Integrity Score, and
the 4 file paths (all values relayed from the already-rendered `.txt`, never recomputed here). No
new file is written.

### Failure Conditions

- Any of the 4 expected files does not exist → do not print a summary. This indicates Stage 7, 8, or
  9 did not actually complete; return to the stage whose output is missing rather than proceeding on
  partial output.

### Completion Criteria

- All 4 files exist at their correct Appendix G paths, sharing one name stem.
- The TXT report's contents were printed to the console.
- The 4 file paths were listed.
- `completion-checklist.md` §12.2's Output Checklist is satisfied exactly: one Manifest, one
  JSON/HTML/TXT triad, nothing extra, nothing missing.

### Transition

→ `REPORTS_EMITTED`
