# Review and Verification

## Purpose

Decide whether the currently selected outcome from the original user request or an explicitly accepted delta is complete through the real production path. Tests, the finite `TOS`, matrices, charters, and workflow records are subordinate evidence for that anchor outcome; they do not define a separate delivery scope.

## Entry Conditions

- One currently selected outcome from the original user request or an explicitly accepted delta is implemented but not yet certified complete, and its authoritative acceptance ID, observable result, forbidden effects, production owner, and real runtime entry are known.
- The implementation exists on that production path. Target tests, the finite frozen `TOS`, and selected review/regression commands are known as supporting evidence, not as the reason the outcome exists.

## Actions

1. Compare the authoritative original/accepted outcome directly with the running production path before inspecting workflow bookkeeping. Enter through the real user, API, event, command, or composition-root entry and judge the observable result plus material forbidden effects. A reproducible mismatch, unreachable intended owner, or test-only implementation is delivery-blocking; a process note that does not change this judgment is not.
2. Re-run only the target tests and regression command selected as the minimum credible evidence for that outcome; “broader is possible” is not permission to expand the command or test set during review.
3. Then compare the frozen authoritative acceptance/risk source IDs to the entire `TOS`, and compare each relevant row to production evidence. A missing accepted behavior or required seam is `PLANNING-GAP`, not a reviewer-created test or theoretical follow-up; stop before testing and use the single re-freeze correction rule. Unknown test IDs, bare checkmarks, filler `N/A` columns, naming/trace defects, or unsupported `PASS` claims are governance findings unless they hide or destroy the minimum credible evidence for the anchor outcome.
4. Inspect diffs for changed Given/When/Then meaning, test weakening, skipped minimum evidence, silent fallback, and unrelated scope. Treat one as delivery-blocking only when it reproducibly falsifies the anchor outcome or makes its minimum proof untrustworthy.
5. Compare changed paths against the approved topology, scope firewall, and worktree charter. Opportunistic repairs, unrelated cleanup, read-only-path edits, charter defects, or unapproved process deviations are follow-ups unless they changed the anchor outcome, left required code unintegrated, or destroyed its trustworthy evidence.
6. Trace every changed production path, new public symbol, and test ID to the same stable `N-ID`. Verify the production owner/entry, nearest existing test home/reuse assets, and non-test incoming edges; code reachable only from tests cannot prove the anchor outcome.
7. For existing-code work, verify the current owner was modified or extended by default. A `NEW`/`REPLACEMENT` must have concrete reuse rejection evidence and no unapproved parallel SUT/harness; side-by-side work must exercise its selection point and retirement condition when those facts are required to make the accepted outcome real.
8. Verify wiring through the real production route, registry, export, or composition root, not a directly constructed test-only graph. For `NEW`/`REPLACEMENT`, confirm the wiring evidence would expose a missing production registration/route edge.
9. For refactors, verify public signatures, data semantics, error behavior, protocol behavior, authorization behavior, and user-visible outcomes did not drift unless `10-change-protocol.md` approved it.
10. For orchestrated work, record scope overlap, charter, ownership, or status-process defects as governance follow-ups. They block this delivery only when code is unintegrated/conflicting or local evidence can no longer establish the anchor outcome.
11. If an explicitly accepted risk or repository governance rule requires independent module review for this outcome, read `09-module-initial-review.md`; ordinary single-owner work uses this review directly.
12. Verify runtime contract schemas and ownership only for changed or accepted-risk-assigned frontend/backend, service/service, or event producer/consumer boundaries.
13. Read `09-integration-acceptance.md` only when the anchor outcome depends on a connection, persistence truth, cross-owner effect, public contract, or critical UI path that still lacks minimum real-layer evidence.
14. For UI work, inspect visible output and only the states required by the original/accepted outcome; do not turn theoretically possible UI states into new acceptance tests.
15. At the planned review/closeout sync, reconcile batched `P:` to `PASS:` evidence. Synchronization defects are follow-ups unless they leave the anchor outcome without trustworthy evidence.
16. Review can find a gap in a frozen obligation; it cannot create a new obligation. Move the same key from `GREEN/VERIFIED` to `GAP`, then `REPAIRING`, only when a reproducible finding actually falsifies the anchor outcome or destroys its minimum credible evidence. A style preference, naming/trace defect, charter/process issue, theoretical edge, extra layer, optional enhancement, or concern with no frozen source is a follow-up/OOS candidate and cannot open red work or block `DELIVERY-DONE` unless an explicitly accepted delta changes the outcome.
17. Perform one review pass and freeze only its complete delivery-blocking finding set. After one aggregate repair, perform one verification pass over exactly that set and the selected regression command; do not restart sampling, adversarial discovery, or “find more tests.” If any frozen finding remains, mark its owning obligation `BLOCKED` and stop. A new label or failure bottom line cannot open another repair/review allowance. Follow-ups stay outside this repair set.
18. On pass, record that the anchor outcome succeeds through the production path, move its reviewed `GREEN`/repaired obligations to `VERIFIED`, and record the review gate closed once. Return to the router; do not run a second clean review for extra confidence.

## Output

An anchor-first conclusion keyed by the original/accepted outcome and production `N-ID`, followed by its subordinate verification/wiring evidence, any bounded repair to existing obligations, and governance/naming/optional-enhancement follow-ups that did not expand the current test set.

## Stop Conditions

Do not mark the anchor outcome complete when a reproducible production-path failure contradicts its observable result/forbidden effects, required code is test-only or unwired, or the minimum credible evidence assigned to that outcome is missing, weakened, skipped, or untrustworthy. A naming/trace/status defect, unknown test ID, optional coverage gap, charter/worktree bookkeeping issue, orchestration-process violation, style concern, or unrelated repair is a governance/follow-up finding unless it causes one of those delivery failures; it cannot open a new red test or block `DELIVERY-DONE`. When the original/accepted outcome succeeds in production and its minimum evidence passes, mark its obligations `VERIFIED`, apply `DELIVERY-DONE` when the remaining anchor outcomes are also complete, and stop.
