# Changelog

## 1.1.1 - 2026-09-07

Closed four routing defects found while auditing the 1.1.0 branch points.

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
