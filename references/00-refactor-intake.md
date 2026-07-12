# Refactor Intake

## Purpose

Prevent refactor requests from skipping product intent. Reconfirm requirements and contracts before code changes, then classify whether the work can stay behavior-preserving.

## Entry Conditions

- The user asks to refactor, clean up, rewrite, restructure, simplify, `重构`, or `整理`.
- Planning selects `refactor before implementation`.
- A refactor commit or work batch is about to start.

## Requirements Recertification

Before touching code, re-read the smallest current evidence set:

- project docs: `docs/architecture.md`, `docs/glossary.md`, `docs/requirements-index.md`;
- target feature docs: `00-原始需求.md`, `00-整理后需求.md`, `01-接口.md`, `interfaces/*.md`, `01-代码冲突与重叠.md`, `conflicts/*.md`, `02-规划.md`, or `00-功能.md` for lightweight features (its sections replace the separate requirement/contract/plan docs);
- state and evidence: `status.json`, `99-进度.md`, `docs/workflow-state.json`, tests, recent diffs, PR notes, CI, and review comments.

Verify that `requirementsConfirmedAt` and `contractsFrozenAt`, when present, point to a PR, commit, tag, or other concrete approval evidence. Status text alone is not enough.

## Classification

Classify the requested work before implementation:

- **Pure refactor:** no change to public signatures, data semantics, persisted shape, user-visible text, error behavior, protocol behavior, authorization behavior, or scenario outcomes. Tests and contracts stay unchanged. Do not write new red tests for a pure refactor: proceed to `08-implementation.md` with the existing green tests as protection evidence.
- **Behavior-affecting refactor:** any of the above might change, or layer/module boundaries need to move. Route to `10-change-protocol.md` level A before coding.
- **Missing or stale requirements:** accepted requirements, contracts, or plan cannot be found or do not match the code being touched. Route to `02-requirements-capture.md`, `04-interface-contract.md`, `06-planning.md`, or `99-status-and-evidence.md` before coding.

Every refactor target must trace to a requirement scenario, contract method/invariant, documented conflict, or explicit planning item. Do not justify refactor solely from code aesthetics.

In a repository that never adopted this workflow (no workflow docs exist), do not create workflow docs uninvited: treat the current public interfaces, observed behavior, and green test suite as the protection contract, state that substitution in the report, and require the protection suite to stay green throughout. If no protection tests exist for the touched behavior, add characterization tests first or stop and ask the user.

## Plan Update

Add or update a refactor preflight section in `02-规划.md`:

```markdown
## 重构复核

| 项 | 证据 | 结论 |
|---|---|---|
| 需求复核 | `<文档/PR/commit/tag>` | <已确认 / 缺失 / 需变更> |
| 合同复核 | `<接口/不变量/场景>` | <保持不变 / 需变更协议> |
| 保护行为 | S1/E1/P1... | <测试或人工证据> |
| 重构边界 | `<模块/文件>` | <可改 / 禁改> |
| 回滚方式 | `<命令/分支/开关>` | <说明> |
```

If no implementation plan exists, route to `06-planning.md` and create it before writing code.

If local subagent tools are available and the refactor is non-trivial, read `00-orchestration-policy.md` after the refactor classification. The main thread remains the orchestrator; executors perform assigned audits, mappings, tests, or module edits.

## Output

- Updated `02-规划.md` refactor preflight, or a route to the missing prerequisite stage.
- Pure-refactor / behavior-affecting / missing-prerequisite classification.
- Updated status/progress evidence if the target project uses those files.
- Exact tests, CI, diffs, or review reports used as evidence.

## Stop Conditions

Stop before coding if accepted requirements or contracts cannot be recertified, behavior might change without a level-A proposal, public signatures or tests would need edits, or independent review reports contradict the refactor classification.
