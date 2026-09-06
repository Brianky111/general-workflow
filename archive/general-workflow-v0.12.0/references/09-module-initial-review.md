# Module Initial Review

## Purpose

Independently decide whether the module makes one currently selected outcome from the original user request or an explicitly accepted delta true through its real production path. CI, the finite `TOS`, and module-review records are subordinate evidence for that anchor outcome.

## Entry Conditions

- A currently incomplete or uncertified original/accepted outcome maps to this module, its production owner/entry, and its observable result.
- A risk-triggered or independently owned module claims green or done, and the independent-review requirement comes from an explicitly accepted risk or repository governance rule for that outcome.
- Target tests pass as supporting evidence, or a known reproducible production-path blocker remains.
- The module has not received independent review evidence.
- The reviewer is independent: never the executor who implemented the module.

## Three Judgments

1. **Anchor-outcome judgment:** first compare the original/accepted outcome directly with the module's real production entry, owner, observable result, and forbidden effects. Then use the finite `TOS` as subordinate evidence. A missing accepted behavior or required seam is `PLANNING-GAP` and uses the one re-freeze correction, never a reviewer-created test. Unsupported `PASS`, wrong-SUT, missing wiring, or weak proof blocks only when it makes the anchor outcome false/unreachable or destroys its minimum credible evidence; naming, trace, matrix, and optional-strength findings are follow-ups.
2. **Anti-hardcoding sample:** only when the accepted risk selected it before review, run the one fixed pre-budgeted sample set. A passing probe is discarded or recorded as evidence, not added as a regression test. A failure enters the bounded counterexample rule only when it reproducibly falsifies the anchor outcome; otherwise it is a follow-up candidate.
3. **Assertion-strength check:** ensure the minimum assertion expresses the accepted observable result. A weaker optional assertion is a follow-up; it is delivery-blocking only when the existing assertion cannot credibly prove the anchor outcome.

## Output

Write a concise anchor-first conclusion in the current handoff, PR, or existing review surface: original/accepted outcome -> real production result -> minimum evidence -> blocking finding or follow-up. Create a dedicated report only for long-running multi-owner, high-risk, or formally audited work.

On pass, record the anchor outcome's real-production result plus `reviewer` and `reviewEvidence` once, mark the independent-review gate closed, then return to the router. Do not mirror the result into both `status.json` and `99-进度.md`. Freeze the first review's complete finding set, containing only delivery-blocking findings; one aggregate repair and one re-review may verify only that set and the selected regression command. It must not choose another sample set or start a new discovery pass. If any frozen finding remains after re-review, mark its owning obligation `BLOCKED` and stop; relabeling a finding creates no new allowance. Governance, naming, trace, and optional-enhancement follow-ups stay outside the repair set and cannot open red work or block `DELIVERY-DONE`.

## Stop Conditions

If the accepted independent-review gate has no evidence, the anchor outcome remains uncertified. Route the same obligation back to `07-red-tests.md` or `08-implementation.md` only for a reproducible production mismatch or loss of the outcome's minimum credible evidence. A finding with no frozen acceptance/risk source, or one limited to governance, naming, traceability, process hygiene, or optional strength, is a follow-up/change candidate, not a new red test and not a completion blocker. After the single bounded re-review closes every delivery-blocking finding, mark the outcome evidence `VERIFIED`, apply `DELIVERY-DONE` when all anchor outcomes are complete, and stop.
