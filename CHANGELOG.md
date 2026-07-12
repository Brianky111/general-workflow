# Changelog

Skill package version is independent of the source document version (v3.8).

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
