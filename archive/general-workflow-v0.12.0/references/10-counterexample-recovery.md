# Counterexample Recovery

## Purpose

Repay one admitted, distinct, reproducible production failure that actually falsifies a Delivery Anchor outcome with a bounded regression guard. Counterexample recovery consumes a finite anchor-linked obligation; it is not an engine for recursively discovering more failures.

## Entry Conditions

- A production/user report or a pre-budgeted property, fuzz, mutation, integration, review, or completeness pass exposes a candidate.
- The candidate reproduces deterministically against the real production `N-ID`, cites an original/accepted outcome or non-goal, and actually falsifies it or destroys its only credible proof.
- It is semantically distinct from existing obligations and regression tests by acceptance/invariant, failure bottom line, and root-cause family.
- The accepted delivery's cumulative integer `counterexample_admission_cap` has room, and the orchestrator has admitted this candidate as one finite obligation without resetting the cap.

## Rules

1. Fingerprint the candidate by authoritative acceptance/invariant, observable failure bottom line, real `N-ID`, and root-cause family. Different seeds, inputs, stack traces, or mutant IDs with the same semantics are duplicates, not new obligations.
2. If an existing test/obligation already fails for and preserves that semantic defect, reuse it. Attach one minimized fixture/seed when useful; do not add another regression test or red micro-batch.
3. Otherwise admit at most one representative regression obligation for the distinct anchor-falsifying failure, and only while the delivery-level absolute cap has room. Reaching the cap records `DISCOVERY-CLOSED` and stops further admission; continue already admitted obligations. A known additional reproducible anchor-falsifying blocker makes completion `ANCHOR-BLOCKED`, but cap exhaustion alone does not.
4. Minimize only enough to make the admitted failure deterministic and understandable. Store the admitted sanitized input under the project's existing `fixtures/counterexamples/` convention when a fixture adds durable value.
5. Add the smallest regression test tagged with the existing counterexample/source ID, run red once to prove capture through the real production owner, make one bounded repair pass, and run one green/regression recheck. If it still fails, mark the obligation `BLOCKED` regardless of the new label or failure category; do not open another recovery generation. On pass, mark it `VERIFIED`.
6. Keep an admitted counterexample fixture append-only unless an accepted change approves removal or rewrite. Candidate logs, duplicate seeds, and equivalent mutants need not become permanent fixtures.
7. Recovery never launches another property/fuzz/mutation/adversarial discovery pass, never samples “nearby” inputs, and never creates a child counterexample from its own red/green output. The current delivery may not renew its campaign list or cap. Only a later accepted user/authoritative-source delta may create a new delivery with a new finite budget after current closeout; verified drift covered by an existing compatibility promise is evidence against that same anchor item, while unrelated drift remains a change candidate. An agent, reviewer, tool, or executor cannot authorize either expansion.
8. If the finding does not satisfy the anchor-falsification test, record one out-of-scope/follow-up candidate and return to the current anchor decision without a test. If no anchor gap remains, close the delivery.

## Escalation

- If the Delivery Anchor is right and the admitted failure exposes an implementation defect, repay the one same-anchor obligation without reopening unaffected planning.
- If the finding suggests the accepted outcome itself should change, stop recovery and treat it as a change candidate; only an accepted delta through `10-change-protocol.md` defines a finite replacement obligation set.
- If the failure is nondeterministic, cannot identify an oracle, is an equivalent mutant, or cannot be reproduced against the real owner, it is not an admissible red. Preserve useful evidence as a blocker/follow-up; repeated observation alone does not authorize endless retries.

## Output

One deduplicated admitted counterexample obligation, an optional minimized fixture under the project's existing convention, a regression test tagged with its existing source ID and red-then-green evidence, and one update in the selected status/handoff source only when a pause, handoff, or closeout trigger exists. Ordinary single-owner work does not create or synchronize status/progress files. Close the obligation, return to the router, and do not restart discovery.

## Stop Conditions

Stop without recovery if the finding cannot be reproduced deterministically against the real owner, has no trustworthy oracle, does not falsify an anchor item, duplicates existing protection, is equivalent/out of scope, or requires changing the anchor without an accepted delta under `10-change-protocol.md`; these close as no-op/follow-up evidence and cannot block completion. Any second invalid red after the admitted obligation's one correction is `ANCHOR-BLOCKED`. Reaching the admission cap closes discovery and preserves already admitted work; only minimum anchor evidence that could not be produced or a known unadmitted anchor-falsifying blocker is `ANCHOR-BLOCKED`. After the admitted obligation is `VERIFIED`, evaluate the Delivery Anchor and `DELIVERY-DONE`; do not search for another counterexample.
