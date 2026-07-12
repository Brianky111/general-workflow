# Changelog

Skill package version is independent of the source document version (v3.8).

## 0.5.0 - 2026-07-13

Two more mechanisms adopted from Trellis, adapted to this skill's evidence philosophy.

- Session binding (one session, one scope): a conversation claims a feature or executor scope by writing the `owner` field in `status.json` and `99-进度.md` — repo-visible evidence, not a runtime file; scopes with fresh owner evidence are not claimed; stale takeover needs user confirmation and a handoff note; switching features requires closing out through the router; cross-feature parallelism means parallel sessions (`00-orchestration-policy.md`, `SKILL.md`).
- Role-isolated trio as the default for non-trivial module batches: read-only research executor → worker executor (keeps commit rights — red/green commit order and purity are the anti-cheat audit surface, deliberately unlike Trellis) → independent check executor; findings re-checked after fixes; no executor implements and reviews the same scope; the reviewer is never the implementer (`00-orchestration-policy.md`, `09-module-initial-review.md`).

## 0.4.1 - 2026-07-13

Self-review of the 0.3.x/0.4.0 additions found six issues, two of them regressions of the same classes fixed earlier (over-broad rule, always-true router condition).

- Context manifests now bind bounded (worker/review) executors only; discovery tasks — conflict scans, code mapping, sampling, adversarial probing — get a declared search scope instead of a closed file list (`00-orchestration-policy.md`).
- Visual-track-only features no longer loop at the red-tests router row and can enter implementation without a test phase (`00-progress-router.md`, `08-implementation.md`).
- The similarity-triage question now has a home: hard stop in conversation, parked in `requirements-index.md`'s holding area when the file exists (`02-requirements-capture.md`).
- `99-进度.md` gained the feature-level `## 全局` section the document-set mirror rule assumed (`99-status-and-evidence.md`).
- Lightweight features' merged contract+planning gate is now acknowledged in both gate sections — no double human pass (`04-interface-contract.md`, `06-planning.md`).
- Legacy decision records get `D` IDs on first touch, append-only (`03-requirements-clarification.md`).

## 0.4.0 - 2026-07-13

Five mechanisms adopted from a comparative study of Superpowers, GSD, and Trellis.

- Decision coverage gate (from GSD): answered questions become numbered `D` decisions (`03-requirements-clarification.md`); the ambiguity audit flags decisions with no landing clause (`03-ambiguity-audit.md`); contract clauses cite the `D` IDs they implement (`04-interface-contract.md`); the planning gate blocks on unconsumed decisions like unconsumed `C` conflicts (`06-planning.md`).
- Executor context manifest (from Trellis/GSD): the orchestration brief lists exact files with reasons; executors read only the manifest plus their write paths, never pasted history, and report back instead of browsing when it falls short (`00-orchestration-policy.md`).
- Rationalization table (from Superpowers): seven predictable excuses with rebuttals added to `07-anti-cheat-and-red-replay.md`.
- Model tiering (from Superpowers/GSD): briefs assign a model tier by task nature — cheap for mechanical, default for implementation, strongest for architecture/security/adversarial review; reviewers never below default (`00-orchestration-policy.md`).
- Lessons pass (from Trellis): feature closeout proposes promoting what worked into project-level docs — glossary, architecture, CI gates, tuning checklist (`09-integration-acceptance.md`).

## 0.3.2 - 2026-07-12

Refactors are no longer capturable as features.

- `00-refactor-intake.md`: "Not a Feature" rule — no feature folder, `00-原始需求.md`, or roster entry for a refactor; documentation home is the owning feature's `02-规划.md` preflight (one per affected feature for cross-cutting refactors) or the change protocol. The missing-requirements branch backfills docs for the touched behavior, never records the refactor itself.
- `02-requirements-capture.md`: entry guard — refactor requests route to intake; a backfilled folder is named after the behavior, not the refactor.
- `SKILL.md` / router: the refactor rules state the same invariant.

## 0.3.1 - 2026-07-12

The numbered document set (00-… through 99-…) is now explicitly the user's dashboard.

- `99-status-and-evidence.md`: Document Set Checklist — every numbered doc, the stage that produces it, the user question it answers (需求是否符合预期 / 进度如何 / 还差哪些), and its done-criteria; progress reports go against this checklist, not from memory.
- `SKILL.md`: operating rule for keeping the set complete and current as part of the deliverable; the Default Response Shape now includes document-set status (existing docs, missing docs, next unpassed gate).

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
