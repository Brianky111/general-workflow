# Anti-Cheat and Red Replay

## Purpose

Make test-first history auditable instead of relying on agent claims.

## Entry Conditions

- The disputed red/TDD evidence is the predeclared minimum proof for the currently selected anchor-linked `request_gap`; otherwise record the concern as governance/follow-up without selecting this stage.
- Red evidence is being accepted or committed.
- Implementation changes tests or fixtures.
- A reviewer suspects tests were added after implementation or weakened.

## Evidence Discipline

- Capture the admissible failing command/output before changing production behavior. A separate red commit is required only when repository policy, CI red replay, formal audit, or the user's requested history demands it; otherwise a timestamped local/CI/executor transcript is sufficient.
- Evidence order applies per frozen test obligation; do not use one early trivial red to excuse later implementation-first batches.
- A red change may touch tests and minimal test-support assets, but not production behavior. Counterexample fixtures remain append-only.
- Implementation must not rewrite the accepted assertion or fixture to obtain green. When separate commits are used, keep production behavior out of the red commit and test weakening out of the implementation commit.
- Pure refactor evidence keeps public behavior and the protection suite unchanged throughout.

## Red Admissibility

A red commit is admissible only when its evidence names the Delivery Anchor item/current `request_gap` and a matching `PENDING` obligation or same-key `GAP` with unused aggregate-repair allowance from the frozen `TOS`, plus its accepted behavior, stable `N-ID`, production owner/entry, nearest existing test home/reuse assets, baseline, and expected failure. An obligation without that anchor reference is `INVALID-OBLIGATION` and cannot enter replay/red. The test must exercise the planned production SUT; unit tests record its runtime reachability, and wiring tests enter through the real production route, registry, export, or composition root. A directly constructed test-only graph is not wiring proof.

`NEW`/`REPLACEMENT` additionally requires approved reuse rejection evidence, a planned non-test incoming edge, and wiring coverage. Side-by-side work also requires a tested selection point and retirement condition.

## Red Replay

CI or the reviewer should replay each recorded red evidence point; when a separate red commit exists, check it out, otherwise use the preserved pre-implementation diff/command context:

1. reproduce the recorded baseline;
2. verify that the test resolves the declared `N-ID` and real production entry rather than a wrong SUT, test-local business implementation, or unregistered parallel replacement;
3. verify that the established test home/runner/reuse assets were used, or that new test infrastructure has explicit conflict/plan approval;
4. run the newly added or marked red case and confirm failure for the expected behavior reason, such as `尚未实现` or the target defect, while existing tests do not crash for unrelated reasons;
5. for `NEW`/`REPLACEMENT`, verify the planned wiring test uses the real composition root and would fail if the production registration/route edge were absent.

## Prohibitions

- Do not write implementation first and backfill tests.
- Do not cross hard stops: unanswered questions or unfrozen contracts block later artifacts.
- Do not weaken tests by deleting assertions, loosening expectations, adding `skip`/`only`, or changing expected values to match wrong code.
- Do not hardcode against known test inputs.
- Do not hide failure with fallback defaults, swallowed exceptions, or test-environment branches.
- Do not create or target a parallel SUT, test-local business implementation, second runner, or unapproved harness merely to manufacture a red result.
- Do not invent another obligation, sample, seed, mutant, or proof layer because the frozen test is already green or the first red is invalid.

## Rationalization Table

Excuses are predictable; rebut them before they win. Following the letter of a rule while violating its spirit is still a violation.

| Excuse | Rebuttal |
|---|---|
| Too simple to need a test | Simplicity does not waive an executable obligation already frozen in the `TOS`; equally, this slogan cannot create a test for behavior outside that set |
| Writing the test afterwards is the same | A test written after passes immediately, and an immediate pass proves nothing; if a frozen obligation is `UNEXPECTED-GREEN` on the real owner, close it as existing evidence or correct an already-contracted distinction once—never invent another behavior or SUT to force red |
| We already had one red commit for the feature | TDD evidence is per frozen obligation; each later `PENDING` obligation needs its own expected red before green, but exhaustion of the set ends red work |
| Deleting hours of work is wasteful | Sunk-cost fallacy; code that never went red-then-green is a liability, not an asset |
| It's just a refactor, this tiny behavior tweak is fine | Changed behavior is not a refactor; route to the change protocol |
| This case is flaky, skip it for now | Do not silently skip a frozen obligation; use its declared retry/budget rule, then stop and report `BLOCKED` rather than searching for another test |
| The failure is intermittent, rerunning fixes it | Preserve the evidence; only a distinct deterministic in-scope failure admitted within the frozen counterexample budget enters recovery, while nondeterministic evidence stops or becomes a follow-up |
| Merge first, backfill evidence later | Status must never run ahead of evidence; without evidence it is not done |

## Invalid Red Recovery

Faithful `UNEXPECTED-GREEN` is existing proof, not an invalid red: record `EXISTING-PASS` evidence and move the same obligation to `VERIFIED` without implementation, then re-evaluate whether its anchor outcome and any explicitly requested write are already complete; never seek another red merely to preserve TDD form. A discovery/setup failure, wrong SUT, stale `N-ID`, unregistered parallel implementation, unapproved harness, or an assertion that fails to express the frozen distinction is invalid; record `superseded-invalid:<test-id>`, stop implementation, and consume the obligation's one mapping/setup correction through `05-conflict-scan.md`, planning, or the test mapping. Any later invalid red for that anchor-linked obligation is `ANCHOR-BLOCKED`, regardless of category. Preserve the accepted behavior and failure bottom line; replacing the invalid target once under this audit trail is not test weakening, but changing identifiers or classifications does not create another allowance.

## Legal Paths After Failure

Only after red admissibility is proven are two paths valid:

1. fix the implementation for the declared `N-ID`,
2. use `10-change-protocol.md` to change the contract.

## Output

An audit conclusion with evidence order (and commit order/path purity when separate commits are required), red admissibility (`N-ID`, production entry, test home/reuse assets, baseline), replay result, wiring proof when required, and any invalid/violating evidence with the rule each one breaks. Then return to the router.

## Stop Conditions

Stop and report `ANCHOR-BLOCKED` only when a confirmed violation (implementation-first history, weakened tests, hardcoded answers, parallel/wrong SUT, unapproved harness, invalid red followed by implementation, bypassed stops, or any second invalid red after the obligation's one correction) destroys the predeclared minimum credible proof for the named anchor item. If the concern is unanchored process hygiene and the original outcome still has trustworthy production evidence, record governance/follow-up and do not open another red target or block completion.
