# Changelog

## 1.5.1 - 2026-09-08

Strengthened requirement coverage, verification, and handoff; closed six review
findings in completion and the status gate.

- Define completion boundaries from the original request and accepted changes in
  the existing Goal/LEAN contract before decomposition. Map every promised outcome
  to acceptance and verify the full result again at integration and closeout.
  MVP deletion analysis cannot silently defer explicit commitments; ledger
  completion does not prove that the original requirement was fully decomposed.

- Added module-scoped `AGENTS.md` guidance to slice preparation, implementation,
  and review. Read applicable instructions before editing, create local guidance
  only for distinct module rules, and update it when verified boundaries,
  entrypoints, or validation commands change. P0 returns also recheck affected guidance.
- Connected BDD scenario semantics to TDD evidence in the existing acceptance
  mapping. Review actual assertions, production wiring, test execution, and
  available Red/Green evidence without copying requirements into agent documents
  or treating a checklist as proof of passing tests.
- Added a P0 return path when decomposition exposes ambiguous intent,
  conflicting core goals, or invalid project assumptions. Resolve intent from
  existing decisions or a targeted user question, update affected contracts and
  acceptance, then revalidate the earliest affected gates. LEAN uses the same
  return path; local requirement or assertion issues stay in stages 1–4.
- Centralized completion rules in the handoff reference. Claiming all IDs no
  longer satisfies stage 7; passing stage 9 completes acceptance scope only.
  Closeout also requires the delivery target already requested by the user,
  including release and observation when those are in scope.
- Added `acceptance_source` to project state, pointing directly to the current
  version's authoritative Markdown acceptance table, with an optional exact
  heading. The gate rejects missing, extra, duplicate, or unreadable IDs instead
  of deriving the expected set from backlog. Undefined draft scope is incomplete.
- Added `delivery_target` as a pointer to the authorized handoff endpoint. Existing
  projects fill these fields from their current contract and request, preserving
  IDs and evidence. The script does not verify source authenticity or release results.
- Resolved write scopes relative to the project, including dot segments,
  existing links, and Windows case normalization. Reject unsupported globs and
  paths outside the project; require valid owners, claim dates, and write scopes
  on live slices, with at most one live slice per owner.
- Invoke the installed skill's script by absolute path with an explicit target
  `--root`. Missing partial state now fails; uninitialized projects remain usable,
  and both cases preserve JSON output and cannot report completion.
- Added consumer-project CLI regression tests for completion, source coverage,
  path conflicts, ownership, and invocation outside the skill and project folders.

## 1.5.0 - 2026-09-08

Made the workflow safe for a second person to join at any moment, which meant
sharding the state and shipping the first gate an agent cannot talk itself past.

- Split the single state file into `docs/workflow/`: `project.md` for what
  rarely changes, `backlog.md` for which slice owns each acceptance id, and one
  file per slice for the rest. A slice is the natural unit of ownership -- no
  one claims half a slice -- so status updates, the most frequent write, only
  ever touch a file with a single owner.
- Moved `stage` from the project to the slice. Two people working two slices
  are genuinely at two different stages; a shared field cannot express that,
  and merging it is not a resolution because both values are correct. This is
  a modelling fix, not a merge workaround.
- `backlog.md` records assignment only, never status, so the two never disagree.
- Added claim rules: claiming edits the file you are claiming, so it cannot
  conflict; do not take a slice whose owner has fresh evidence; check
  `write_scope` against in-flight slices before starting, because overlapping
  scopes collide in code rather than on paper; hold one slice at a time.
- Added `scripts/workflow_status.py`, shipped to projects using the workflow.
  It reports slice owners, stages, unclaimed ids and whether scope is complete,
  and exits non-zero on delivered-without-evidence, backlog/slice disagreement,
  an id in two slices, overlapping write scopes, deferred or dropped without a
  change record, and owner set without a claim date. Sharding makes it
  necessary -- "how much is still owed" no longer fits in one file -- and it is
  the only gate here that does not rely on an agent judging itself.
- Same layout for solo projects. A conditional guarantee of "anyone can join"
  is not a guarantee, and the migration would land exactly when someone is
  trying to join.

## 1.4.0 - 2026-09-07

Pulled the test-first discipline forward from implementation to requirements,
without restoring the archived obligation-set machinery that did it before.

- Stage 2 scenarios must now be written in executable shape: a concrete
  entrypoint, concrete input values, a concrete assertion, the forbidden
  effect, and the seam the assertion needs. A scenario you cannot turn into a
  failing assertion is an unfinished requirement, not a testing problem. The
  assertions are not run yet -- the scaffold arrives at stage 6 -- but they
  become stage 8's red tests unchanged.
- The seam column is the new link between requirements and module boundaries.
  Naming what a test must double is a boundary decision made against observed
  behavior rather than imagined layering.
- Stage 5 takes the union of those seams as input to module boundaries, and
  states the limit: seams fix the outer edges, domain modelling fills the
  inside. Letting acceptance tests drive internal layering produces modules
  that mirror test cases instead of domain boundaries.
- Stage 3 decides the MVP by deletion -- "remove this row; is the desired
  outcome still observable?" -- rather than by Must/Should/Could judgement,
  with security and data-integrity boundaries as the stated exception. Where
  deletion and the priority label disagree, deletion wins.
- The LEAN contract template carries the same seam column and deletion rule.

## 1.3.1 - 2026-09-07

First forward test: a LEAN internal CLI taken from profile to delivered
acceptance. Six defects surfaced; five are closed here.

- The fast-path gate required "a verification path you can run" and the ledger
  required a change record for deferred and dropped rows, but the one-page
  contract template had a field for neither. Both fields added -- a gate that
  asks for something the template cannot hold is not a gate.
- Restored the constraint-conflict check the merge had dropped. The full path
  gates on "conflicts between quality goals are explicitly recorded"; nothing
  carried it into the fast path, so the test run wrote a contract requiring
  both "never send dependency lists to third parties" and "look up known
  vulnerabilities" and no check caught it until the architecture stage. The new
  sixth minimum also requires re-checking after a resolution, because the first
  fix attempted (cutting vulnerability scanning) did not remove the conflict.
- Narrowed the fast-path entry condition from "privacy" to "personal privacy or
  regulatory compliance". Internal secrets are not by themselves an escalation
  reason, only sending them to a third party is -- the old wording would have
  pushed most internal tools onto the eleven-stage path.
- Said which gate governs after a merge: the merged stages' own gates remain
  the floor, and the fast path's boundary list is a waiver list against them.
- Defined "real entrypoint" to include calling the composition root in-process,
  so a subprocess is not mistaken for a higher standard.

Not fixed, needs a decision: a LEAN run still reads 66% of the document set
(66.6 KB of 100.5 KB), because 00-lean-path.md says what is relaxed rather than
what to do, so stages 6 through 10 still get read in full.

## 1.3.0 - 2026-09-07

A subtraction pass. Nothing was added: six places said the same thing twice,
and the fast path had only been made fast in its front half.

- Cut the return table from stage 11. The router's stage table, stage 11's own
  observation classification, and that table were three statements of one
  mapping; the classification list survives and now names files rather than
  bare stage numbers. Removed check_return_table with it -- a guard that keeps
  two copies in sync is worth less than not having two copies.
- Compressed SKILL.md's twelve principles to six. Ten of the twelve were
  restated by the stage document that owns them; what remains is what has to
  be true before you know which stage you are in.
- Replaced the six prose completion conditions in SKILL.md with the ledger
  test: no remaining and no in-slice rows. Stages 9 and 10 own the gates that
  move rows, so the entry file no longer summarizes them.
- Merged the back half of the LEAN path. It collapsed stages 1-4 but left six
  stages standing behind them; LEAN is now four steps, with the clean-clone
  check and one CI pipeline as its single non-negotiable gate.
- Cut stage 9's CI layering block (a restatement of the 运行时机 column in its
  own table), stage 8's scope firewall (owned by stage 3), and stage 5's
  decision-order list (a prose table of contents for its own sections).
- Narrowed stage 5's deployment section to the four decisions that constrain
  the data model and contracts; the execution checklist belongs to stage 10.
- Tightened the size budgets to lock the reduction in: SKILL.md 8000, any
  single reference 13000.

## 1.2.0 - 2026-09-07

Made the line past the first slice as well specified as the line up to it.
Surveyed how the highest-starred agent workflow projects track outstanding
scope -- superpowers, spec-kit, OpenSpec, BMAD-METHOD, and claude-task-master
-- and adopted the two conventions they share.

- Generalized `07-vertical-slice.md` from the first slice to every slice. The
  map and the gates are shared; only the selection weights differ, and the
  document now states that difference in a table. An architecture hypothesis of
  `none` is a legitimate result for a later slice rather than a blank to fill.
  None of the surveyed projects keeps a separate document for the first
  iteration, and neither does this one now.
- Added a scope ledger to the state file: one row per A-ID with a status of
  remaining, in-slice, delivered, deferred, or dropped, plus an evidence
  pointer. It holds identifiers and pointers only, never scenario text.
- A row reaches `delivered` only by passing the stage 9 Definition of Done with
  an evidence pointer filled in, and `delivered` is monotonic -- reopening
  scope goes through the change protocol in stage 3 rather than editing the
  ledger backwards. Both rules come from the survey: BMAD refuses status moves
  that go backwards, and OpenSpec makes delivery a move between directories so
  a status field cannot drift from reality.
- "Current scope is delivered" now has one authoritative answer: no remaining
  and no in-slice rows. Stage 11 selects the next slice from the remaining
  rows and reports what is left in its closeout.

## 1.1.1 - 2026-09-07

Closed five routing defects found while auditing the 1.1.0 branch points.

- The LEAN row in the router's stage table stated a mode ("tier is LEAN"), not
  an unmet fact, so it matched for the whole life of a LEAN project and routed
  finished work back to the project contract. It now states the deficiency, and
  the table says explicitly that satisfied rows are skipped.
- The profile gate hardcoded stage 1 as its successor, so a project whose tier
  was just set to LEAN could not reach the fast path by following the profile
  document's own gate. The gate now branches on tier.
- The retrospective's return table still sent mechanism failures to stage 5
  after mechanisms moved to 05a, and wrote "07/08" as bare numbers rather than
  resolvable links. Both fixed, plus a row for fast-path escalation.
- The state cursor was only mentioned at end of round, while stages may advance
  several at a time. Cursor advance is now part of the shared stage gate, so it
  applies at every gate rather than once per conversation.
- The fast path emitted only A-IDs while stages 5, 7, and 9 name R-ID and Q-ID
  in their entry conditions, so a LEAN project reached stage 5 against a gate it
  could never satisfy. `00-lean-path.md` now maps must entries to R-ID and
  quality_targets to Q-ID, and names the two cases that must escalate instead.
- Added check_return_table to check_consistency.py: every reference the router
  can route into must also appear in the retrospective's return table, so the
  two routing tables cannot drift apart again.

## 1.1.0 - 2026-09-06

Tuned the Greenfield main line for how it actually gets executed: less constant
cost, fewer load spikes, a real fast path, and state that survives a session
boundary. No change to the eleven-stage lifecycle or to the Greenfield-only
scope.

- Added `references/00-lean-path.md`: LEAN projects merge stages 1-4 into a
  single project contract with explicit minimums and escalation triggers, so
  the fast path is executable instead of a paragraph in the router.
- Split `references/05-architecture-design.md` (16.7 KB) into shape/boundary/
  data/stack/deployment decisions plus `05a-mechanisms-and-contracts.md` for
  auth, async, transactions, API/event contracts, and observability. The
  mechanisms file loads only when the architecture stage marks an item as
  required or risk-triggered.
- Added `references/99-state-and-handoff.md`: a cursor-and-index state file in
  the target repository, with read/verify rules on session start and update
  rules on session end. It holds pointers, never copies; repository facts win
  on conflict.
- Removed the architecture, implementation, and verification checklists that
  `SKILL.md` restated from stages 5, 8, and 9, keeping only cross-stage policy.
  The anti-fake-green rule moved into the evidence principle rather than being
  dropped.
- Routed the new entry points: the router now looks for the state file first,
  branches on path depth, and lists the mechanisms document as its own row.
- Added size budgets to `check_consistency.py` for the always-loaded entry path
  and for any single reference, so stage detail cannot drift back into
  `SKILL.md` unnoticed. Reference names may now carry a letter suffix (`05a`).

## 1.0.0 - 2026-09-04

Reframed the skill around Greenfield project delivery, using the supplied `project-dev-workflow` package as the baseline and expanding it for architecture-led development.

- Added a project-profile entry point that evaluates product shape, runtime units, data, team, lifecycle, and risk before selecting architecture depth.
- Added explicit stages for requirements/goals, scenarios/acceptance, scope/non-goals, constraints/quality attributes, architecture decisions, scaffolding/CI, vertical slicing, implementation, testing/integration, release/operations, and retrospective evolution.
- Expanded architecture guidance to cover system shape, direct layering vs modular vs hybrid organization, data ownership and invariants, authentication/authorization, asynchronous work, API/error conventions, observability, deployment, migration, and rollback.
- Made the first vertical slice an architecture-validation path rather than only a feature list.
- Kept behavior-sized red/green/refactor, layered testing, CI/CD, migration, secrets, monitoring, and rollback guidance from the reference package.
- Archived the previous feature/change-oriented workflow under `archive/general-workflow-v0.12.0/`; archived material is reference-only.
- Replaced the old consistency checks with checks for the Greenfield stage graph, reference reachability, architecture decision coverage, release/operations coverage, and archive separation.
