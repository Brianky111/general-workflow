# Solution Framing and Feature Ownership

## Purpose

Frame a finite, goal-bounded delivery that needs several independently owned features without turning the solution into a second behavior source. Keep the stable product/module/feature hierarchy as the ownership view; use a solution only as a cross-feature delivery, sequencing, and aggregate-acceptance view derived from the same Delivery Anchor.

## Contents

- Entry and non-entry tests
- Solution/feature ownership rules
- Compact solution frame
- Incremental execution and change routing
- Completion and stop conditions

## Entry Test

Use solution framing only when an accepted aggregate outcome needs two or more independently acceptable or independently owned feature contributions, crosses module ownership, or needs shared integration/release/rollback proof that no single feature can own faithfully.

Do not trigger it merely because one vertical feature touches UI, API, domain, persistence, infrastructure, or several code directories. Code breadth, theoretical future reuse, multiple test types, or a desire for a roadmap does not make a solution layer necessary.

If the request is only a broad authorization such as “continue,” “finish the area,” or “fix everything,” first capture a finite observable outcome, non-goals, and minimum proof through `02-requirements-capture.md`; a vague work authorization is not a finite aggregate outcome.

## Two Orthogonal Views

- **Ownership view:** product → module → feature → use case/sub-feature → task. Keep behavior, public/data semantics, production owners, and tests in the one authoritative feature contract.
- **Delivery view:** solution → referenced participating features/current accepted deltas → aggregate integration and closeout. A solution may cross modules, and one feature may participate in several solutions.

Do not rename a stable module as a solution, move feature truth under a solution directory, or treat a change round as a child feature. Modules persist as responsibility domains; solutions end when their finite aggregate outcome is delivered; rounds are optional history/approval boundaries.

## Compact Solution Frame

Prefer the existing issue, plan, or one compact artifact. Create `docs/solutions/<solution>/00-方案.md` or an equivalent status surface only when durable multi-owner handoff, long-running coordination, aggregate audit, or release governance justifies it. Do not create a mandatory solution directory.

Record only:

```text
Delivery Anchor: <original source + accepted delta refs>
Aggregate outcome / non-goals: <finite observable result and exclusions>
Participating features:
  <feature ref> -> <owned contribution> -> <owner/current source>
Shared boundaries: <contract/model/event owner; consumers only reference it>
Dependency order / first vertical result: <smallest end-to-end sequence>
Aggregate proof: <cross-feature assembly, migration, release, rollback, E2E>
Completion: <required feature contributions + aggregate evidence>
Current aggregate gap: <one anchor-linked gap or none>
```

The frame may summarize contribution state, but must link rather than copy feature requirements, BDD examples, interface clauses, plans, test matrices, or status. A solution status is an aggregate projection and cannot override production, evidence, or an owning feature's current contract.

## Ownership and Completion Rules

1. Assign every behavior and boundary clause to exactly one feature owner. Let the solution own only the aggregate goal, feature/owner map, cross-feature dependency order, shared rollout/rollback decisions, and aggregate acceptance.
2. Keep one current effective contract per feature. Preserve original sources and accepted deltas as history; consolidate their effect semantically into that contract without concatenating complete old snapshots.
3. Distinguish contribution completion from solution completion. A feature is complete when its accepted owned behavior works through its intended production entry with its minimum proof. A solution is complete only when every required feature contribution is complete and the declared cross-feature assembly/aggregate proof passes.
4. Do not mark an otherwise complete feature incomplete solely because another independently owned contribution remains, unless that contribution is part of the feature's own accepted result or only credible production proof. Otherwise record the dependency as the solution's aggregate gap. Conversely, do not hide an unfinished owned behavior inside solution status.
5. Keep shared models, events, and public contracts under one declared owner. Consumers cite that source; the solution records the producer/consumer relationship without restating the schema.

## Incremental Execution

After the minimal frame is sufficient to choose ownership and aggregate proof:

1. Select the first dependency-ordered user-visible vertical result.
2. Select exactly one owning feature and one anchor-linked `request_gap`.
3. Run that feature through its current contract, code-reality scan, executable plan, finite `TOS`, implementation, and verification.
4. Update the solution surface only at a material dependency change, multi-owner handoff, aggregate verification, or closeout.
5. Return to the Delivery Anchor before choosing another feature; do not blueprint every child feature in detail before the first implementation unless `00-pacing-mode.md` explicitly selects a justified blueprint.

## Change Routing

- If a finding reproducibly falsifies an existing accepted outcome, repair the owning feature's same obligation; do not create a solution requirement or new round.
- If the user or authoritative source accepts changed behavior/public/data semantics, append one delta through `10-change-protocol.md` and update the owning feature's affected clauses. Update the solution only when its aggregate outcome, non-goals, participant map, dependency order, rollout, or aggregate proof changes.
- If a finding only proposes stronger internal robustness or optional assurance, quarantine it as a follow-up. A review, test, tool, or executor cannot convert it into a child feature or solution blocker.
- Open a governed round only for the triggers in `00-business-taxonomy.md`; never use repeated full snapshots to represent ordinary accepted deltas.

## Output

- No solution artifact for ordinary single-feature work.
- Otherwise, one compact solution frame plus references to the existing authoritative feature contracts.
- One selected owning feature and `request_gap` for immediate execution, not a fully expanded plan for every participant.

## Stop Conditions

Stop for user input only when competing feature placements change observable behavior, public/data ownership, compatibility, irreversible effects, or accepted scope. Otherwise record the smallest faithful owner map and continue. When every required feature contribution and the finite aggregate proof pass, close the solution once; do not keep it open for optional hardening, unrelated feature backlog, or stronger evidence not declared by the Delivery Anchor.
