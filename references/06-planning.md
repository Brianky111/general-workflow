# Planning

## Purpose

Convert a ready compact contract and code-reality scan into the smallest executable, reuse-first code and verification plan. Planning exists to start safe implementation, not to create a second specification.

## Entry Conditions

- The raw/structured/BDD bundle is ready under `00-progress-router.md`; any material public/runtime boundary delta is explicit.
- For existing-code work, `05-conflict-scan.md` has identified the current production owner, runtime/composition-root path, nearest existing test home, and reuse candidates.
- No executable plan yet binds the changed behavior to those code and test anchors.

## Actions

1. Read only the accepted compact contract, relevant boundary delta, code-reality/reuse map, and current Git/test evidence. Do not restate all upstream prose.
2. Carry the same stable `N-ID` from the reuse map into the plan. For each changed behavior, name the current production owner, real runtime/registration path, nearest existing test home, reusable helpers/fixtures/fakes, exact write file or symbol, and verification command.
3. Default existing-code work to `MODIFY_EXISTING` or `REUSE_EXTEND`. `NEW`, `REPLACEMENT`, or `SIDE_BY_SIDE` requires:
   - the evaluated reuse candidates and concrete rejection evidence;
   - the non-test caller, registration, route, export, or composition-root edge that will reach the new node;
   - a wiring/assembly check through the real production selection path;
   - for side-by-side work, the selection rule, coexistence invariant, rollback, and old-owner retirement condition.
4. Keep one active default production owner per business responsibility. A cleaner name or easier unit test is not evidence for a second service/model/parser/client/store/harness.
5. Add a scope firewall only for actual neighbors: exact write set, important read-only context, prohibited paths, and discovered out-of-scope failures. Existing-code write sets should name files or symbols; a broad directory glob is not sufficient unless every intended new node is listed.
6. If refactor is requested or needed to expose a test seam, read `00-refactor-intake.md`. Prefer a characterization test and the smallest behavior-preserving seam refactor over creating a parallel implementation.
7. Map each changed behavior to the cheapest trustworthy test in the existing suite. Add a real wiring/contract/integration check only when the connection itself can fail. Read `06-test-strategy.md` only when a named risk requires expanded coverage; do not build a full matrix for ordinary work.
8. Split implementation into behavior-sized red -> green -> refactor batches, but keep the plan compact. Several ready batches may run continuously in the same execution turn.
9. List the concrete commands or visual/runtime evidence that will prove target behavior, production wiring, and the relevant regression slice.
10. If local subagent tools materially improve the work, read `00-orchestration-policy.md`. A writable executor/worktree gets a concise charter with objective, target ID, exact write set, evidence, handoff, and closeout; the main thread does not implement that same scope.

## Minimum Executable Plan

Use one sparse table or equivalent bullets. Do not create separate conflict, topology, scope, and test tables when one row carries the needed facts.

```markdown
| Behavior | N-ID / kind | Current owner and production path | Existing test home / reused assets | Action and exact write set | Red / verification | Wiring or risk evidence |
|---|---|---|---|---|---|---|
| R1/EX1 | N1 / EXISTING | `<route> -> <owner>` | `<nearby-test>` / `<fixture>` | MODIFY_EXISTING `<file#symbol>` | `<target command>` | `<real-entry check or N/A:no connection change>` |
```

For a real conflict or side-by-side replacement, append only the selected resolution and rollback/retirement facts; do not first write several candidate tables and defer the choice to another document.

When orchestration is used, the charter may be a plan row or an executor prompt rather than a separate artifact:

```markdown
| Executor role | Purpose | Target ID / N-ID | May edit | Must not edit | Required evidence | Handoff/status location | Closeout |
|---|---|---|---|---|---|---|---|
| <role> | <feature batch / bug fix / counterexample / review-only> | <behavior + production node> | <paths> | <paths/contracts/tests> | <commands/report> | <selected status surface or handoff message> | <merge/no-op/blocked/discard owner> |
```

Vague goals such as "investigate", "continue", "fix failures", or "clean up" are read-only discovery, not writable charters.

## Validation Strength Triggers

Read `00-feature-grading-and-splitting.md` for the lean budget and expansion rules. Add focused property, pairwise, mutation, adversarial, contract, or E2E evidence only for the risk it addresses. Typical triggers include:

- three or more freely combinable input parameters,
- high-cost or irreversible decisions,
- external input parsing or protocol adaptation,
- state machine or concurrency logic.

The agent selects proportionate validation and proceeds. Ask the user only when validation cost or a safety tradeoff changes accepted scope or delivery expectations.

## Output

Record the minimum executable plan in the current task plan, handoff, or owning compact feature document. Create `02-规划.md` only when the repository already governs it, several owners need a durable handoff, or a named risk justifies it. Create a separate `02-测试矩阵.md` only when `06-test-strategy.md`'s expansion triggers apply.

## Execution Gate

The plan is executable when every changed behavior has a production `N-ID`, real runtime path, existing test home or justified new test location, exact action/write set, target verification, and any required wiring evidence. All discovered conflicts must have one selected handling; all writable executor charters must be concrete.

If the user authorized implementation and no material behavior, compatibility, safety, or scope choice remains, freeze the compact plan in place and start `07-red-tests.md` or `08-implementation.md` in the same run. Do not ask for a second planning approval, pre-generate parallel stubs, or wait for optional document/status completeness. A new production node begins in the red/green batch only after its `NEW/REPLACEMENT` evidence above is satisfied.

Strengthen verification freely when evidence exposes risk. Weakening accepted behavior or a material contract routes to `10-change-protocol.md`; correcting a wrong SUT or unexpectedly green plan routes back to the code-reality map without inventing a new implementation.

## Stop Conditions

Stop only when the compact contract is not ready, no real production/test anchor can be established, a `NEW/REPLACEMENT` node lacks reuse-rejection or runtime wiring evidence, a writable executor lacks a concrete charter, an out-of-scope repair is being pulled in, or the plan requires an unresolved behavior/compatibility/safety/scope decision. Do not stop merely because a plan file, full matrix, approval timestamp, or status mirror is absent.
