# Status and Evidence

## Purpose

Keep durable handoff claims aligned with Git, tests, CI, PRs, and runtime evidence without turning status bookkeeping into a prerequisite for implementation.

## Default Rule

Ordinary single-owner work needs no dedicated status document. Use the repository's task/PR plus Git and test evidence, and update status only at:

1. a real human pause for a blocking decision;
2. an owner or executor handoff;
3. closeout.

Do not update status after every internal workflow stage. Do not create or hand-maintain equivalent `workflow-state.json`, feature `status.json`, and `99-进度.md` mirrors in parallel. If durable status is triggered, choose one manual authority per scope; other views at that same scope must be generated or treated as non-authoritative. A durable solution may have one batch-local authority per batch plus one non-overlapping aggregate authority.

## Status Triggers

Use a dedicated status/evidence source only when one applies:

- work pauses across sessions with a real blocker;
- multiple owners, executors, worktrees, or teams require handoff and closeout;
- a goal-bounded solution needs durable aggregate state across independently acceptable feature contributions or staged construction batches;
- blueprint coordination holds several features behind a shared dependency;
- migration, security, compliance, or formal audit requires durable approval/evidence state;
- the user explicitly requires a persistent status artifact.

Repository age, a missing template file, or an ordinary single-agent feature is not a trigger.

## Conditional Artifact Ledger

Track only artifacts required by the feature's chosen path:

| Artifact | Default | Triggered when | Done when |
|---|---|---|---|
| Durable raw source / Delivery Anchor | Core | Always link the original source and any ordered accepted deltas | Immutable source history remains accessible; current Anchor state is clear |
| Structured requirement + BDD | Core | Ordinary feature contract | Faithfully project the current Anchor state; observable behavior is READY and frozen |
| Dedicated interface contract | Conditional | Public/external compatibility, migration, security, complex state/concurrency, or cross-owner boundary | Triggered risk is explicit and accepted |
| Conflict appendix | Conditional | A concrete legacy overlap or uncertain migration boundary exists | Actual locations and chosen handling are recorded |
| Fixtures/probes | Conditional | External behavior cannot be trusted from documentation alone | Examples trace to captured evidence |
| Feature Test Matrix | Conditional | Multi-layer/cross-owner risk, adversarial verification, or formal traceability needs a durable matrix | Required rows point to supported evidence |
| Dedicated status source | Conditional | A status trigger above exists | Current pause/handoff/closeout is evidenced |
| Tests + implementation | Delivery evidence | The accepted behaviors are implemented | Commands/CI/runtime evidence support the claim |

Do not report an untriggered artifact as “missing.” The complete lean contract is the durable source plus structured requirement and BDD examples; risk-triggered artifacts extend it rather than redefining completeness.

## Source Selection

Prefer an already durable issue, PR, or project tracker. For ordinary work, otherwise choose exactly one:

- `99-进度.md` for a human-readable multi-owner handoff;
- feature `status.json` when automation consumes structured state;
- a compact project status source for a blueprint or regulated cross-feature baseline.

For a durable staged solution, choose the scoped hierarchy defined below: one `batches/NN-<stage>/99-进度.md` for each batch and one root `docs/solutions/<solution>/99-进度.md` for aggregate-only state. Record each authority once. Legacy repositories may retain other files, but do not manually synchronize equivalent fields across them. Reconcile or retire stale mirrors at the next handoff/closeout instead of blocking current implementation solely to refresh them.

## Minimal Status Shape

Keep the chosen source concise:

```markdown
## 状态
- Delivery Anchor：<original source + ordered accepted delta refs；current state>
- Anchor state / request_gap：<SATISFIED / UNMET + concrete existing ID or clause / BLOCKED + exact reason>
- 下一步：<一个直接关闭该 gap 的动作；SATISFIED/BLOCKED 时为 stop>
- 证据：<production path + test/CI/commit/截图/日志摘要>
- 有限测试义务：<VERIFIED/total；仅在测试适用且需要 handoff/closeout 时>
- 当前负责人：<仅在有 owner/handoff 时>
```

Add the following sections only when their condition applies. Omit them entirely rather than filling empty placeholders.

## Durable Solution Progress

For a durable staged solution, give every batch its own `batches/NN-<stage>/99-进度.md`. It is the only manually maintained status for that batch; the batch's stable construction contract stays in `00-施工.md`, while feature contracts/status own feature behavior and evidence.

Use this batch-local shape:

```markdown
## Batch 状态
- Batch：<NN + name>
- Batch state / selected gap：<PENDING / IN_PROGRESS + one gap / BLOCKED + reason / DONE>
- 工作进度：<completed required work items>/<total required work items>
- 当前负责人 / handoff：<owner or none>
- 下一步：<one batch-closing action, or stop>

## 贡献与证据
| Work / contribution / TOS / gate ref | 状态 | 证据 | blocker / next |
|---|---|---|---|
| <owning source ref> | PENDING / RED / GREEN / VERIFIED / BLOCKED | <evidence ref> | <concise result> |

## Batch 关闭
- Exit criteria：<from 00-施工.md>
- Closeout / dependency unlocked：<evidence-backed result or pending>
```

Use the root `docs/solutions/<solution>/99-进度.md` as the only manually maintained aggregate status. It links batch-local progress and owns dependency transitions, total progress, aggregate gates, current aggregate gap, and solution closeout. It never owns or copies the batch's work-item/TOS detail.

Use this aggregate shape:

```markdown
## 总状态
- Delivery Anchor：<source + accepted deltas>
- Solution state / aggregate gap：<UNMET + one gap / BLOCKED + reason / SATISFIED>
- 总进度：<completed required stages>/<total required stages>；aggregate gates <verified>/<total>
- 当前施工阶段：<batch ref + status>
- 下一步：<one action that advances the aggregate gap, or stop>

## 施工阶段
| 阶段 | Batch progress source | 状态 | 阶段证据摘要 | 解锁/阻塞 |
|---|---|---|---|---|
| <batch plan ref> | <batch 99 ref> | PENDING / IN_PROGRESS / BLOCKED / DONE | <evidence refs> | <dependency result> |

## 总体验收
| Aggregate gate | 状态 | 证据 |
|---|---|---|
| <assembly/migration/release/rollback/E2E gate> | PENDING / VERIFIED / BLOCKED | <ref> |
```

Use counts as the default progress record at both scopes. Publish a percentage only when the owning `00-施工.md` or root `00-方案.md` declares a stable formula; never average subjective feature percentages. Update batch progress at meaningful work/evidence checkpoints. Update root progress only at a batch state/dependency transition, an aggregate-affecting blocker, aggregate verification, or closeout. A batch-local state may be summarized in the root table, but its detailed work/TOS rows exist only in the batch-local file.

## Conditional Scope Firewall

Add a scope firewall when existing-code work has nearby behavior, failures, or shared paths that could be accidentally pulled into the change:

```markdown
| 路径/发现 | 本轮处理 | 与核心合同的关系 | 证据/后续去向 |
|---|---|---|---|
| <path or finding> | 改 / 只读 / 不碰 / blocker | <AC/合同边界> | <test/OOS/change source> |
```

Only accepted behavior, a concrete blocking dependency, or an approved change grants write scope. The firewall does not require an empty table for isolated work.

## Conditional Worktree Charter and Closeout

For a writable executor/worktree or multi-owner scope, record before edits:

- purpose and target behavior/bug ID;
- allowed and forbidden write paths;
- required verification evidence;
- handoff location;
- closeout result: committed, no-op, blocked, discarded, or integrated.

At handoff or closeout, reconcile branch/worktree facts before assigning the same scope again: integrate or explicitly reject document/status changes, integrate or record code/test results, update the one authoritative status source, and release or advance the owner. Do not open another same-scope writable loop while dirty/unmerged work, an unsupported PASS claim, or an unreconciled handoff remains.

This section is not required for single-owner local work or read-only discovery.

## Conditional Out-of-Scope Findings

Record an OOS item only when an actual neighboring bug, failing test, dead code, or design problem is discovered:

```markdown
| OOS ID | 发现 | 为什么不在本轮修 | 是否阻塞核心合同证据 | 后续去向 |
|---|---|---|---|---|
| OOS1 | <finding> | <scope reason> | 是 / 否 | <issue/change/holding area> |
```

An OOS finding is not implementation permission. It remains read-only unless the user accepts it, a change delta adds it, or evidence proves it directly blocks the current contract. Do not add an empty OOS field when nothing was found.

## Evidence Rules

- Treat the immutable original source plus ordered explicitly accepted deltas as the Delivery Anchor. Requirements, BDD, plans, tests, reviews, and status are projections/evidence; none may rewrite Anchor history or self-accept a scope expansion.
- A batch-local solution status references each owning feature's current contract and evidence and owns only that batch's work/evidence projection, blocker, handoff, and closeout. The root solution status owns only batch transitions, aggregate dependencies, proof, total progress, and solution closeout. Neither can copy or override feature behavior/status, and the root cannot replace batch-local progress.
- At every triggered status update, record the current Anchor state and one concrete `request_gap` first. Use `none` only when the anchored outcome, authorized writes, required production/gates, and known blockers support it; a vague “continue testing/review” is not a gap.
- Prefer repository facts over manual status prose.
- Every complete claim points to a path, command, commit, PR/CI result, screenshot, trace, or concise log evidence.
- Status may lag while work is active, but it must never run ahead of evidence.
- A blocking question identifies the exact decision and affected acceptance/contract boundary; an empty `【答复】：` marker exists only for a real pending question.
- A risk-triggered matrix cannot claim PASS without supporting evidence; untriggered matrix cells do not exist and need no `N/A` entries.
- When test work applies, completion names the finite frozen `TOS` total and shows every obligation `VERIFIED`; `PASS`/`EXISTING-PASS`/`ACCEPTED-NONTEST` remain evidence kinds. Status cannot add obligations or treat an unbounded discovery pass as pending work.
- Record `planning_gap_refreeze_used`, invalid-red correction, aggregate repair/recheck, review/adjudication slots, probe/discovery campaign state, or admission-cap counters only when triggered, overridden, or consumed, in the existing plan/TOS row or handoff. Never create an all-zero ledger; once used, a reroute or session change cannot reset it, and the use must be persisted before a pause or owner/session handoff.
- A reviewer must be independent only when the named risk or governance requires separation of duties.
- If rounds are used for audit or multi-owner history, archived rounds remain read-only; ordinary revisions use a delta and do not require a new full round.
- Parallel owners update only their own scope in the chosen status source; cross-scope edits preserve other owners' evidence.

## Actions

At a triggered update point:

1. Reconcile the Delivery Anchor's current effective state from the immutable original source and ordered accepted deltas; record the exact `request_gap` or evidence-backed `none` before any stage/test status.
2. Compare that state and the chosen status source with Git, worktrees, tests, CI, PRs, and runtime evidence.
3. Correct unsupported claims without rewriting Anchor history or promoting tool/reviewer findings into scope.
4. Record only the current blocker, handoff, checkpoint, or closeout plus its next action; update the owning batch-local status first, then refresh the root only when aggregate state changes. When applicable, include the frozen obligation count and any exhausted budget without reopening discovery.
5. Include scope firewall, worktree closeout, or OOS sections only when their conditions apply.
6. Keep the update within the document budget from `00-feature-grading-and-splitting.md`, or name the audit/coordination exception.

## Output

- Ordinary active work: no status-file write.
- Human pause: one concise blocker update in the chosen durable source.
- Batch checkpoint/handoff: one update in the owning batch-local `99-进度.md`, including a conditional worktree charter when applicable; refresh the root only for a state/dependency transition.
- Batch closeout: close the batch-local progress, then update the root aggregate transition once.
- Solution closeout: one final evidence-backed root update after every required batch and aggregate gate closes.

## Stop Conditions

Stop when the Anchor state or concrete `request_gap` cannot be established, when a claimed pause/handoff/completion has no reliable evidence, or when the claimed test boundary is not finite. Report the uncertainty and smallest verification step tied to the existing Anchor/obligation set. A tool/reviewer finding with no Anchor mapping cannot keep status active. When `DELIVERY-DONE` is evidenced, write one closeout and stop. Record `request_gap: none` in that closeout; status synchronization must not launch another review/test pass. Missing untriggered documents or stale non-authoritative mirrors do not block READY or implementation.
