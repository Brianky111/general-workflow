# Solution Framing and Feature Ownership

## Purpose

Frame a finite, goal-bounded delivery that needs several independently acceptable feature contributions, staged cross-feature construction, or aggregate proof without turning the solution into a second behavior source. Keep the stable product/module/feature hierarchy as the ownership view; use a solution only as a cross-feature delivery, sequencing, progress, and aggregate-acceptance view derived from the same Delivery Anchor.

## Contents

- Solution candidate gate and non-entry tests
- Solution/feature ownership rules
- Durable staged construction surface
- Incremental execution and change routing
- Completion and stop conditions

## Solution Candidate Gate

Run this gate before feature similarity triage whenever a request names or appears to describe an application, client, platform, migration, rollout, program, or other aggregate delivery. Classify from observable scope and acceptance topology, not from naming similarity:

```text
Can one independently acceptable user-visible feature contract own the whole request
without hiding another distinct capability, owner/source, construction dependency,
or aggregate acceptance result?
  yes -> reject solution framing; continue to feature similarity triage
  no  -> frame or update a solution before routing each behavior to its owning feature
```

Use solution framing when any one of these is true:

- the finite aggregate outcome needs two or more independently acceptable feature contributions, even when one team owns all of them;
- the delivery crosses stable module, application, client, runtime, or release ownership;
- ordered construction stages coordinate contributions from several feature contracts or shared foundations;
- shared integration, migration, release, rollback, or end-to-end proof cannot be owned faithfully by one feature.

A shared repository/product stem or a platform suffix such as `Android`, `iOS`, `web`, or `desktop` is not evidence that the request belongs inside the similarly named feature. For example, `btw-client-Android` is a solution candidate when it delivers an Android client through several independently acceptable capabilities or construction stages; an Android-specific change to one existing capability remains that feature's merge or revision.

Do not trigger a solution merely because one vertical feature touches UI, API, domain, persistence, infrastructure, several code directories, or several implementation tasks. Code breadth, multiple test types, an internal red/green micro-batch sequence, or a desire for a roadmap does not create a solution. A solution construction batch coordinates feature-owned contributions; it is not a renamed feature task or change round.

If the request is only a broad authorization such as “continue,” “finish the area,” or “fix everything,” first capture a finite observable outcome, non-goals, and minimum proof through `02-requirements-capture.md`; a vague work authorization is not a finite aggregate outcome.

## Two Orthogonal Views

- **Ownership view:** product → module → feature → use case/sub-feature → task. Keep behavior, public/data semantics, production owners, and tests in the one authoritative feature contract.
- **Delivery view:** solution → referenced participating features/current accepted deltas → aggregate integration and closeout. A solution may cross modules, and one feature may participate in several solutions.

Do not rename a stable module as a solution, move feature truth under a solution directory, or treat a change round as a child feature. Modules persist as responsibility domains; solutions end when their finite aggregate outcome is delivered; rounds are optional history/approval boundaries.

## Durable Staged Construction Surface

Keep a one-session, non-staged aggregate fix in an existing durable issue or plan when no handoff or persistent progress view is needed. Create or reuse `docs/solutions/<solution>/` when the solution spans multiple construction stages, sessions, owners, or releases; when the repository already uses `docs/solutions/`; or when the user requests staged construction or total-progress records.

Use this control surface:

```text
docs/solutions/<solution>/
├── 00-方案.md                 # Anchor、总体结果/非目标、参与 feature、依赖与阶段账本
├── 01-共享边界.md             # 条件式：共享合同/事件/模型/兼容与 owner
├── 02-总体验收.md             # solution 级装配、迁移、发布/回滚、E2E 与关闭判据
├── batches/
│   ├── 01-<施工阶段>.md       # 该阶段的贡献引用、施工顺序、证据与阶段进度
│   └── NN-<施工阶段>.md
└── 99-进度.md                 # 唯一人工维护的 solution 总进度与当前 aggregate gap
```

`00-方案.md`, `02-总体验收.md`, at least one executable stage document, and `99-进度.md` form the core durable solution surface. Create `01-共享边界.md` only when two or more contributions consume a shared contract, event, model, compatibility rule, migration boundary, or other cross-feature decision. Do not create empty placeholders.

Define the finite stage ledger in `00-方案.md` and create one `batches/NN-<stage>.md` for each planned construction stage once its objective and dependencies are known. Keep detailed feature requirements, BDD, code plans, and test obligations in their owning feature sources; solution batch documents contain links and coordination facts only. This shallow staged plan does not authorize blueprinting every child feature's implementation before its turn.

Each stage document records only:

```text
Stage outcome / status: PENDING | IN_PROGRESS | BLOCKED | DONE
Anchor-linked aggregate gap: <one gap this stage advances>
Prerequisites and participating feature refs: <current owner/source links>
Construction order and handoffs: <contribution-level sequence; no copied feature plan>
Aggregate/write boundary: <shared integration or allowed coordination writes>
Required stage evidence: <feature evidence refs + assembly/contract/runtime proof>
Progress checkpoint: <completed/required contributions, blocker, next action>
Closeout: <evidence refs and dependency unlocked>
```

Treat `99-进度.md` as the single aggregate progress authority. It summarizes, but never overrides, batch and feature evidence. Record completed/total required stages and aggregate gates; if a percentage is useful, declare a stable evidence-based formula instead of averaging subjective feature percentages. Update it at a stage transition, handoff, blocker, aggregate verification, or closeout—not after every feature micro-step.

## Compact Solution Frame

Whether stored in `00-方案.md` or an existing durable issue, record only:

```text
Delivery Anchor: <original source + accepted delta refs>
Aggregate outcome / non-goals: <finite observable result and exclusions>
Participating features:
  <feature ref> -> <owned contribution> -> <owner/current source>
Shared boundaries: <contract/model/event owner; consumers only reference it>
Dependency order / first vertical result: <smallest end-to-end sequence>
Construction stages: <finite ordered/parallel batch ledger + status/doc ref>
Aggregate proof: <cross-feature assembly, migration, release, rollback, E2E>
Completion: <required feature contributions + aggregate evidence>
Current aggregate gap: <one anchor-linked gap or none>
```

The frame may summarize contribution state, but must link rather than copy feature requirements, BDD examples, interface clauses, plans, test matrices, or status. A solution status is an aggregate projection and cannot override production, evidence, or an owning feature's current contract.

## Ownership and Completion Rules

1. Assign every behavior and boundary clause to exactly one feature owner. Let the solution own only the aggregate goal, feature/owner map, cross-feature dependency and construction-stage order, aggregate progress, shared rollout/rollback decisions, and aggregate acceptance.
2. Keep one current effective contract per feature. Preserve original sources and accepted deltas as history; consolidate their effect semantically into that contract without concatenating complete old snapshots.
3. Distinguish contribution completion from solution completion. A feature is complete when its accepted owned behavior works through its intended production entry with its minimum proof. A solution is complete only when every required feature contribution is complete and the declared cross-feature assembly/aggregate proof passes.
4. Do not mark an otherwise complete feature incomplete solely because another independently acceptable contribution remains, unless that contribution is part of the feature's own accepted result or only credible production proof. Otherwise record the dependency as the solution's aggregate gap. Conversely, do not hide an unfinished owned behavior inside solution status.
5. Keep shared models, events, and public contracts under one declared owner. Consumers cite that source; the solution records the producer/consumer relationship without restating the schema.

## Incremental Execution

After the minimal frame is sufficient to choose ownership and aggregate proof:

1. Select the first dependency-ordered user-visible vertical result.
2. Select exactly one owning feature and one anchor-linked `request_gap`.
3. Run that feature through its current contract, code-reality scan, executable plan, finite `TOS`, implementation, and verification.
4. Update the active solution batch at a stage checkpoint and `99-进度.md` only at a stage transition, material dependency change, handoff, blocker, aggregate verification, or closeout.
5. Return to the Delivery Anchor before choosing another feature; do not blueprint every child feature in detail before the first implementation unless `00-pacing-mode.md` explicitly selects a justified blueprint.

## Change Routing

- If a finding reproducibly falsifies an existing accepted outcome, repair the owning feature's same obligation; do not create a solution requirement or new round.
- If the user or authoritative source accepts changed behavior/public/data semantics, append one delta through `10-change-protocol.md` and update the owning feature's affected clauses. Update the solution only when its aggregate outcome, non-goals, participant map, stage/dependency order, rollout, or aggregate proof changes.
- If a finding only proposes stronger internal robustness or optional assurance, quarantine it as a follow-up. A review, test, tool, or executor cannot convert it into a child feature or solution blocker.
- Open a governed round only for the triggers in `00-business-taxonomy.md`; never use repeated full snapshots to represent ordinary accepted deltas.

## Output

- No solution artifact for ordinary single-feature work.
- For a non-staged one-session aggregate delivery, one compact solution frame plus references to authoritative feature contracts.
- For a durable or staged solution, the core solution control surface: `00-方案.md`, `batches/NN-<stage>.md`, `02-总体验收.md`, and the single aggregate `99-进度.md`; add `01-共享边界.md` only when triggered.
- One selected owning feature and `request_gap` for immediate execution, not a fully expanded plan for every participant.

## Stop Conditions

Stop for user input only when competing feature placements change observable behavior, public/data ownership, compatibility, irreversible effects, or accepted scope. Otherwise record the smallest faithful owner map and continue. When every required feature contribution and the finite aggregate proof pass, close the solution once; do not keep it open for optional hardening, unrelated feature backlog, or stronger evidence not declared by the Delivery Anchor.
