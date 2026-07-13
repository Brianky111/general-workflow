# Pacing Mode

## Purpose

Choose the project-level pacing before any feature work: blueprint (freeze all contracts first, then implement in parallel) or incremental (one feature loop at a time). The stages are the same in both modes; only the ordering and gate grouping differ.

## Entry Conditions

- Project kickoff is underway and no pacing mode is recorded.
- `docs/workflow-state.json` has no `mode` field, or its value conflicts with how work is actually proceeding.
- `mode` is `blueprint` and the agent is about to do feature-level work.

## Mode Selection

- **Blueprint mode:** default for new projects and major versions. Freeze every contract before any implementation.
- **Incremental mode:** default for additions and fixes on top of a shipped blueprint. Lightweight-path features and level B/C changes always belong here.

Record the decision in `docs/workflow-state.json` as `"mode": "blueprint" | "incremental"` (projects that disabled state files record it in kickoff notes or `architecture.md` instead), and scope the blueprint in `docs/requirements-index.md` (in-scope features plus a holding area for out-of-scope ideas). The user confirms mode and scope.

## Blueprint Mode Rules

Blueprint mode is a staged bulldozer, not a per-feature pipeline. Each stage completes for **all** in-scope features and passes a batch review gate before the next stage starts:

1. **Requirements batch:** run the requirements stages for every feature, producing each feature's `00-项目识别.md`, `00-原始需求.md`, `00-整理后需求.md`, plus the `requirements-index.md` roster. After all drafts, the ambiguity audit cold-reads the whole set; genuine ambiguities and drafter-reported questions merge into **one consolidated question list grouped by feature**, answered by the user in one pass → requirements batch gate.
2. **Interface batch:** run the contract stage for every feature (old projects and new modules in old projects also produce `01-代码冲突与重叠.md`). Shared entities live once in `domain-models.md`. After all drafts, the ambiguity audit also runs a **cross-contract consistency check**: same-named fields mean the same thing (against the glossary and shared models), runtime schemas agree across producers/consumers, event/state ownership has no gaps or duplicate owners, no methods conflict, and no feature edits shared models locally. → interface batch gate; passing it freezes **all contracts at once**.
3. **Global planning and test strategy:** run the implementation plan and `02-测试矩阵.md` for every feature in one pass, including contract, cross-feature, UI, and E2E assembly coverage → planning batch gate.
4. Only then do implementation, review, integration, and completeness audit open, with multiple agents working in parallel by feature and module; each feature still passes its own integration and Definition of Done gates.

Standing disciplines:

- Every external touchpoint must have probe-captured fixtures **before** the interface batch gate. Signing contracts against an imagined external world is blueprint mode's biggest risk.
- Blueprint batches skip feature grading: the batch advances all features together, and the lightweight path exists only in incremental mode.
- Blueprint mode trades later change cost for contract consistency and batch review efficiency; the later a design error is found, the more level-A changes it causes. Note this tradeoff when proposing the mode.

## Incremental Mode Rules

Run the single-feature loop: each feature passes stages from identification through completeness acceptance on its own. Document granularity is identical to blueprint mode (one folder per feature); only the gate grouping differs.

## Re-entry

When the mode is already recorded, this file only tells you which gate applies; do not redo mode selection. In incremental mode, return to the router and proceed stage by stage. In blueprint mode, identify the current batch (requirements, interface, or planning): if the batch gate covering the work at hand has passed, return to the router and select the feature-level stage; if not, continue the batch and its gate before any later-stage work.

## Output

- `docs/workflow-state.json` with the recorded `mode`.
- For blueprint mode: `docs/requirements-index.md` scope roster and the current batch stage noted in status files.
- User confirmation of mode and scope.

## Stop Conditions

Stop for user confirmation before recording or changing the mode, before expanding blueprint scope mid-batch, and before starting any implementation while a blueprint batch gate is unpassed.
