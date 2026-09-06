# Planning

## Purpose

Convert a ready compact contract and code-reality scan into the smallest executable, reuse-first code and verification plan. Planning exists to start safe implementation, not to create a second specification.

## Entry Conditions

- The raw/structured/BDD bundle is ready under `00-progress-router.md`; any material public/runtime boundary delta is explicit.
- The Delivery Anchor is known: the original durable user request plus only user- or authoritative-source-accepted deltas. One still-unmet clause is selected as the current `request_gap`, using its existing `AC`/`R`/`EX`/contract ID or an exact source quotation when no ID exists.
- For existing-code work, `05-conflict-scan.md` has identified the current production owner, runtime/composition-root path, nearest existing test home, and reuse candidates.
- No executable plan yet binds the changed behavior to those code and test anchors.

## Completion-First Anchor

The Delivery Anchor defines what completion means and does not drift when code, tests, reviews, or tools expose new ideas. Preserve the original request and accepted deltas as an append-only source chain; never rewrite the original source. A test, reviewer, executor, repository smell, or discovery result may report a candidate, but only the user or an authoritative product/contract source may accept a behavior or risk delta.

Select exactly one current `request_gap`: an existing acceptance/invariant/non-goal/write outcome from that source chain that is not yet evidenced as complete. Declare the Delivery Anchor source and current gap **once at the plan header**, then let rows inherit that context through existing `AC`/`R`/`EX`/contract or obligation IDs. Do not repeat the full source reference in every row and do not create a Delivery-Anchor, gap, plan, or trace ID namespace. When the gap closes, return to the anchor, recompute what remains, and select the next unmet clause; implementation output cannot invent the next gap.

## Actions

1. Read only the Delivery Anchor source chain, accepted compact contract, relevant boundary delta, code-reality/reuse map, and current Git/test evidence. Identify the selected `request_gap` before choosing a write or test. Do not restate all upstream prose.
2. Put the Delivery Anchor reference and selected `request_gap` once above the executable rows. Carry only the existing acceptance/obligation ID and stable `N-ID` into each row. For each changed behavior, name the current production owner, real runtime/registration path, nearest existing test home, reusable helpers/fixtures/fakes, exact write file or symbol, and verification command.
3. Default existing-code work to `MODIFY_EXISTING` or `REUSE_EXTEND`. `NEW`, `REPLACEMENT`, or `SIDE_BY_SIDE` requires:
   - the evaluated reuse candidates and concrete rejection evidence;
   - the non-test caller, registration, route, export, or composition-root edge that will reach the new node;
   - a wiring/assembly check through the real production selection path;
   - for side-by-side work, the selection rule, coexistence invariant, rollback, and old-owner retirement condition.
4. Keep one active default production owner per business responsibility. A cleaner name or easier unit test is not evidence for a second service/model/parser/client/store/harness.
5. Add a scope firewall only for actual neighbors: exact write set, important read-only context, prohibited paths, and discovered out-of-scope failures. Existing-code write sets should name files or symbols; a broad directory glob is not sufficient unless every intended new node is listed.
6. If refactor is requested or needed to expose a test seam, read `00-refactor-intake.md`. Prefer a characterization test and the smallest behavior-preserving seam refactor over creating a parallel implementation.
7. Map each distinct changed behavior/invariant to one cheapest trustworthy rule obligation in the existing suite. Add at most one focused wiring/contract/integration obligation for each named seam that can independently fail. Equivalent examples share a parameterized test or fixture instead of becoming separate micro-batches. Read `06-test-strategy.md` only when a named risk requires expanded coverage; do not build a full matrix for ordinary work.
8. Freeze a finite Test Obligation Set (`TOS`) in the same sparse plan. Each entry inherits the one plan-level Anchor/gap and uses the existing acceptance/invariant/counterexample ID plus proof kind, production/test anchors, and terminal evidence expected. The router's default one-correction/one-repair limits apply without per-row bookkeeping; record only an override or an allowance actually consumed. Mark each active item `PENDING` or already evidenced item `VERIFIED`. Record `EXISTING-PASS` or `ACCEPTED-NONTEST` as an evidence kind, never as a terminal state. Do not create a separate TOS artifact or ID namespace.
9. Ordinary work implicitly uses `counterexample_admission_cap=1` and an empty discovery-campaign set that is closed by default; do not write a budget ledger for unused defaults. Only when a probe, pairwise/generated-case, property, fuzz, mutation, adversarial, or anti-hardcoding campaign is actually triggered, freeze its ID, invariant/scope, command/configuration, wall-clock or attempted-case/mutant/request limit, and cap consumption. Record the counterexample cap only when it is overridden or consumed. Limits are cumulative across reroutes, executors, and sessions; unique seeds alone are not a stopping counter, and the same delivery cannot reset, append, or rename a campaign. Without these triggered limits, that discovery pass is not executable.
10. Split implementation into obligation-sized red -> green -> refactor batches. Each write batch reuses the current gap's existing acceptance/obligation ID, and its planned production effect must directly make that gap's acceptance predicate true; prerequisite-only cleanup is not a separately completable batch. Several ready batches may run continuously in the same execution turn, but only until the frozen `TOS` is exhausted.
11. List the concrete commands or visual/runtime evidence that will prove target behavior, production wiring, and the relevant regression slice.
12. If local subagent tools materially improve the work, read `00-orchestration-policy.md`. A writable executor/worktree gets a concise charter with objective, assigned obligation keys, exact write set, evidence, handoff, and closeout; the main thread does not implement that same scope.

## Minimum Executable Plan

Use one sparse table or equivalent bullets. Do not create separate conflict, topology, scope, and test tables when one row carries the needed facts.

```markdown
Delivery Anchor: <original source + accepted delta refs>
Current request_gap: <existing AC/R/EX/contract ID or exact source clause>

| Behavior | Finite obligation / state | N-ID / kind | Current owner and production path | Existing test home / reused assets | Action and exact write set | Red / verification | Wiring or risk evidence |
|---|---|---|---|---|---|---|---|
| R1/EX1 | `R1/EX1:rule` / PENDING | N1 / EXISTING | `<route> -> <owner>` | `<nearby-test>` / `<fixture>` | MODIFY_EXISTING `<file#symbol>` to close R1/EX1 | `<target command>` | `<real-entry check or N/A:no connection change>` |
```

For a real conflict or side-by-side replacement, append only the selected resolution and rollback/retirement facts; do not first write several candidate tables and defer the choice to another document.

When orchestration is used, the charter may be a plan row or an executor prompt rather than a separate artifact:

```markdown
| Executor role | Purpose | Existing AC/obligation / target N-ID | May edit | Must not edit | Required evidence | Handoff/status location | Closeout |
|---|---|---|---|---|---|---|---|
| <role> | <feature batch / bug fix / counterexample / review-only> | <existing behavior/obligation ID + production node; inherits plan gap> | <paths> | <paths/contracts/tests> | <commands/report proving the gap closed> | <selected status surface or handoff message> | <merge/no-op/blocked/discard owner> |
```

Vague goals such as "investigate", "continue", "fix failures", or "clean up" are read-only discovery, not writable charters.

Do not create an all-zero delivery-boundary line. The fixed defaults in this skill are implicit. Add one compact line beside the table or in a handoff only when a campaign is triggered, an allowance/cap is consumed, or an accepted risk overrides a default; update that line in place rather than creating another tracking document.

## Finite Test Boundary

The frozen `TOS` is the complete current-work test boundary, not a starter list. Tests, reviewers, executors, coverage reports, and discovery tools may discharge an obligation or report a candidate; they cannot add one themselves. After freeze, append only:

1. the finite verification delta from an accepted behavior/contract change;
2. a focused obligation for a named-risk expansion accepted by the user or an authoritative product/contract source;
3. at most one representative regression obligation for a distinct, reproducible, in-scope counterexample admitted within the discovery pass's absolute cap.

An obligation that cannot trace through its existing acceptance/obligation ID to the plan-level Delivery Anchor and selected `request_gap`, or whose proof cannot close that gap, is `INVALID-OBLIGATION`. This is a plan-admissibility finding, not a TOS state: it never enters red, never counts as `PENDING`/`GAP`/`BLOCKED`, and cannot prevent completion of the Delivery Anchor. If the inherited mapping was merely omitted, use the single `PLANNING-GAP` re-freeze correction to attach the existing clause without creating a key. If no faithful mapping exists, preserve the finding as a candidate/follow-up and exclude it from the delivery boundary.

If an existing test already proves the obligation, record evidence kind `EXISTING-PASS` and mark the obligation `VERIFIED` without manufacturing red. If several inputs share the same behavior and failure bottom line, parameterize or attach the minimized fixture/seed to the existing obligation. A review suggestion with no frozen acceptance/risk source becomes a follow-up. Reaching a normal discovery limit records `DISCOVERY-CLOSED`; only required evidence that could not be produced or a known unadmitted in-scope blocker becomes `BLOCKED`.

If required proof discovered later cannot map to a frozen obligation, do not let a reviewer or test author add it. Mark `PLANNING-GAP` and stop before testing. The orchestrator gets at most one explicit re-freeze correction when the proof cites an acceptance/risk source that was already frozen; a second omission is `BLOCKED`. Genuinely new behavior/risk requires an accepted change delta.

## Validation Strength Triggers

Read `00-feature-grading-and-splitting.md` for the lean budget and expansion rules. Add focused property, pairwise, mutation, adversarial, contract, or E2E evidence only for the risk it addresses. Typical triggers include:

- three or more freely combinable input parameters,
- high-cost or irreversible decisions,
- external input parsing or protocol adaptation,
- state machine or concurrency logic.

The agent selects proportionate validation and proceeds. Ask the user only when validation cost or a safety tradeoff changes accepted scope or delivery expectations.

Materialize pairwise/combinatorial cases into the frozen `TOS` before execution, or assign their generator one frozen bounded campaign ID. Do not keep generating combinations after freeze outside those two finite paths. A campaign that exhausts its declared finite input scope before a numeric/time ceiling also records `DISCOVERY-CLOSED`.

## Output

Record the minimum executable plan in the current task plan, handoff, or owning compact feature document. Create `02-规划.md` only when the repository already governs it, several owners need a durable handoff, or a named risk justifies it. Create a separate `02-测试矩阵.md` only when `06-test-strategy.md`'s expansion triggers apply.

## Execution Gate

The plan is executable when the Delivery Anchor and selected `request_gap` are declared once; every row, obligation, and write batch traces to them through an existing ID; every write directly closes the gap; every changed behavior has a production `N-ID`, real runtime path, existing test home or justified new test location, exact action/write set, target verification, and any required wiring evidence; the finite `TOS` is enumerated and frozen; and every actually triggered campaign has cumulative stopping/admission budgets. No `INVALID-OBLIGATION` is executable or counted against completion. Unused default counters/campaigns are not recorded. All discovered conflicts must have one selected handling; all writable executor charters must be concrete.

If the user authorized implementation and no material behavior, compatibility, safety, or scope choice remains, freeze the compact plan in place and start `07-red-tests.md` or `08-implementation.md` in the same run. Do not ask for a second planning approval, pre-generate parallel stubs, or wait for optional document/status completeness. A new production node begins in the red/green batch only after its `NEW/REPLACEMENT` evidence above is satisfied.

Strengthen an existing obligation's assertion or SUT binding when evidence shows it is weak, but do not add proof kinds or examples outside the frozen `TOS`. A material behavior/contract change or risk expansion must come from the user or an accepted authoritative product/contract source before `10-change-protocol.md` produces a finite TOS delta; external drift outside an existing promise is only a candidate until accepted. An agent/reviewer/tool cannot self-accept it. Correcting a wrong SUT or unexpectedly green plan stays on the same obligation without inventing a new implementation or test target.

## Stop Conditions

Stop when the compact contract is not ready, the Delivery Anchor has no selectable unmet `request_gap` but completion evidence is still contradictory, no real production/test anchor can be established, the `TOS`, same-failure repair loop, or discovery campaign is unbounded, required evidence cannot be produced within the cumulative budget, a known in-scope blocker remains unadmitted, a one-time `PLANNING-GAP` correction reveals another omission, a `NEW/REPLACEMENT` node lacks reuse-rejection or runtime wiring evidence, a writable executor lacks a concrete charter, an out-of-scope repair is being pulled in, or the plan requires an unresolved behavior/compatibility/safety/scope decision. Reject an `INVALID-OBLIGATION` and select from the real remaining anchor gaps; the invalid item itself is not a delivery blocker. Normal budget exhaustion closes discovery and does not block already admitted obligations. When every anchor gap is closed, every valid frozen obligation is `VERIFIED`, and the required write/runtime/regression/gate evidence satisfies `DELIVERY-DONE` in `00-progress-router.md`, stop. Do not stop merely because a plan file, full matrix, approval timestamp, or status mirror is absent.
