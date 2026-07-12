# Changelog

Skill package version is independent of the source document version (v3.8).

## 0.3.0 - 2026-07-12

New mechanism (extends beyond the v3.8 source document): one-requirement-one-doc-set as an explicit organizing instinct, plus similarity triage for incoming requests.

- `SKILL.md`: operating rule — every incoming request lands in exactly one document set (new folder, merge into an unconfirmed sibling, or change-protocol revision of a confirmed one); splitting inside a folder is fine, a second folder for the same behavior never is.
- `02-requirements-capture.md`: Similarity Triage section — scan `requirements-index.md` and existing feature goals/scenarios before creating any folder; classify new/merge/revision; when uncertain, stop and ask the user with a fixed shape (similarity points, the case for merging, the case for revising, plus a new-feature option); record the outcome in `requirements-index.md`.
- `00-progress-router.md`: similarity-triage routing row and tie breaker.
- `10-change-protocol.md`: entry condition for triage-classified revisions.

## 0.2.2 - 2026-07-12

Forward-tested the installed skill with Codex CLI on three live scenarios (mid-workflow takeover, refactor in a plain repo, trivial task in a bare repo). Triggering, stage routing, progressive loading (3 files per run), gate discipline, and the kickoff guard all behaved as designed.

- `00-refactor-intake.md`: codified the fallback the refactor scenario exposed — in repositories that never adopted this workflow, treat current public interfaces, observed behavior, and green tests as the protection contract instead of routing to requirements capture; add characterization tests or stop when no protection exists.

## 0.2.1 - 2026-07-12

Round-2 review of the 0.2.0 changes themselves (adversarial diff review plus fidelity spot checks).

- Router: pacing-mode row gained a completion predicate (it was always-true in blueprint mode); governance-audit row narrowed to guardrail-weakening changes (it previously matched every document PR); closeout row defers regression capture to the integration report.
- `00-pacing-mode.md`: re-entry exit added (recorded mode no longer loops back into mode selection); blueprint batches skip grading; conflict reports also cover new modules in old projects; state-file-less projects record mode in kickoff notes.
- `06-planning.md`: planning gate routes pure refactors to implementation, not red tests; stubs generate for new methods/modules only and never overwrite existing code. `04-interface-contract.md` now defers the stub instruction to planning.
- `03-requirements-clarification.md`: questions go into the document being closed out (requirement, contract, or `00-功能.md`), not always `00-整理后需求.md`; self-proof rule moved to Hard Stop. `02-requirements-capture.md` closes every draft through clarification unconditionally.
- `01-project-identification.md`: classification tokens aligned with `status.json`'s `projectType` enum.
- `00-project-kickoff.md`: restored the implementation-strategy-template checklist item; split-threshold and state-file items complete again.
- `08-implementation.md`: pure refactors keep the protection suite green throughout (no red phase).
- `10-change-protocol.md`: restored the probe exception and level B's merge-on-green-CI rule.
- README: documented `PYTHONUTF8=1` for `quick_validate.py` on GBK-default Windows.

## 0.2.0 - 2026-07-12

Fixes from a multi-dimension review (trigger metadata, router state machine, source-document fidelity, engineering hygiene).

### Trigger metadata

- `SKILL.md` description no longer binds triggering to "Codex"; covers new-project kickoff and lists Chinese/English trigger phrases.
- `agents/openai.yaml` short_description now names the domain.

### Router state machine

- Added a terminal "feature closeout" row; the table previously had no match for a successfully finished feature.
- Pure refactor now routes to implementation with existing green tests as protection; it previously dead-ended at red tests, which pure refactors cannot and must not write.
- Fixtures and conflict-scan rows gained completion predicates (they were always-true for old projects, causing circular routing).
- Governance audit is now routable for existing projects, not only via kickoff.
- Lightweight features' merged `00-功能.md` is recognized by the router, interface contract, and refactor intake.
- Kickoff requires user confirmation before bootstrapping governance in a repository with no workflow docs.
- Evidence scan now covers `interfaces/*.md`, `conflicts/*.md`, `domain-models.md`, and the `mode` field.
- New operating rule: after completing a stage's Output, return to the router.

### Source-document fidelity

- New `references/00-pacing-mode.md`: blueprint vs incremental pacing, batch gates, cross-contract consistency check, consolidated question list, probe-first discipline.
- `06-planning.md`: restored the visual track and the standard/enhanced/adversarial tier definitions (pairwise/PICT tables; contract-only attack agent with three-way independence; mutation threshold), and the planning gate (human review, then freeze, then stub generation).
- `04-interface-contract.md`: ambiguity audit is unconditional before the contract gate; merge preconditions, six-question review checklist, and stub generation restored.
- `05-conflict-scan.md`: scan no longer decides implementation strategy (that belongs to planning); added the `## 总结` section and hard rules.
- `03-requirements-clarification.md`: ask-back alignment is a mandatory closing step; fixed `## 待确认反问` / `## 决策记录` section names and the `【答复】：` marker.
- `99-status-and-evidence.md`: added `workflow-state.json` / `status.json` minimum schemas and the `99-进度.md` module-section shape; removed dev-repo-specific instructions.
- `00-project-kickoff.md`: added `requirements-index.md` creation, pacing-mode selection, and the project tuning checklist.
- `04-fixtures-and-probes.md`: fixture paths rooted at `docs/features/<feature>/fixtures/`.
- `01-project-identification.md`: fixed Chinese section names for `00-项目识别.md`.
- `00-feature-grading-and-splitting.md`: "stages 0-5" replaced with concrete reference files; added Output.
- Added Output/Stop Conditions to `00-governance-ci-hooks.md`, `07-anti-cheat-and-red-replay.md`, `10-counterexample-recovery.md`; review/acceptance stages now update status files on pass, and integration acceptance defines the terminal state.

### Engineering

- New `scripts/check_consistency.py`: verifies references ↔ Reference Map ↔ mention links and router reachability.
- README install/validate commands are machine-portable; documented robocopy `/MIR` semantics and exit codes.
- AGENTS.md no longer claims the checkout has no Git history.

## 0.1.0 - 2026-07-09

Initial split of 通用开发工作流 v3.8 into a progressive-disclosure skill package.
