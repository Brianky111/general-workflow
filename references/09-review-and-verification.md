# Review and Verification

## Purpose

Verify that the implementation satisfies the contract and did not weaken workflow guarantees.

## Entry Conditions

- Implementation exists.
- Target tests are green or there is a known blocker.

## Actions

1. Re-run target tests and the broadest practical regression command.
2. Compare implementation to the raw/structured source, authoritative acceptance/BDD IDs, changed contract clauses, invariants, and every assigned sparse/risk-triggered proof. Reject changed Given/When/Then meaning, unknown test IDs, bare checkmarks, filler `N/A` columns, missing triggered coverage, or unsupported `PASS` claims.
3. Inspect diffs for test weakening, skipped cases, silent fallback, and unrelated scope.
4. Compare changed paths against the approved topology, scope firewall, and worktree charter. Reject opportunistic repairs, unrelated cleanup, edits to paths marked read-only/out-of-scope, or commits whose purpose cannot be tied to the charter target ID unless the plan or change protocol was updated first.
5. Trace every changed production path, new public symbol, and test ID to the same stable `N-ID`. Verify the recorded production owner/entry, nearest existing test home/reuse assets, and non-test incoming edges; reject code reachable only from tests.
6. For existing-code work, verify the current owner was modified or extended by default. A `NEW`/`REPLACEMENT` must have concrete reuse rejection evidence and no unapproved parallel SUT/harness; side-by-side work must exercise its selection point and retirement condition.
7. Verify wiring through the real production route, registry, export, or composition root, not a directly constructed test-only graph. For `NEW`/`REPLACEMENT`, confirm the wiring test would fail if its production registration/route edge were removed or disabled.
8. For refactors, verify public signatures, data semantics, error behavior, protocol behavior, authorization behavior, and user-visible outcomes did not drift unless `10-change-protocol.md` approved it.
9. For orchestrated work, verify the main thread acted as orchestrator: executor scopes were explicit, the main thread did not implement the same delegated scope concurrently, and final acceptance is based on local evidence.
10. Verify module ownership, integration boundaries, and that no executor overwrote another executor's scope or progress evidence.
11. If an independently owned, high-risk, or governed module claims done, read `09-module-initial-review.md`; ordinary single-owner work uses this review directly.
12. Verify runtime contract schemas and ownership boundaries across frontend/backend, service/service, or event producer/consumer edges.
13. Read `09-integration-acceptance.md` only when a connection, persistence, cross-owner, public-contract, or critical UI risk needs real-layer evidence.
14. For UI work, inspect visible output and applicable loading/empty/success/validation/permission/network/server/retry/disabled states.
15. At the planned review/closeout sync, reconcile batched `P:` to `PASS:` updates with exact commands and evidence. Do not require per-command or per-micro-step document churn, but do not mark complete before evidence is synchronized.

## Output

Review notes keyed by `N-ID`, verification/wiring evidence, synchronized sparse-map/risk-matrix status, and any follow-up fixes.

## Stop Conditions

Do not mark complete if required evidence is missing or unsynchronized, tests are skipped without approval, sparse/risk coverage or contract coverage is incomplete, an `N-ID` is missing or changed, a production node is test-only/unwired, `NEW`/`REPLACEMENT` lacks reuse rejection evidence or a non-test incoming edge, side-by-side selection/retirement is unverified, a parallel SUT/harness is unapproved, UI or runtime-contract states are unverified, refactor recertification is missing, executor claims cannot be verified, orchestrated work blurred main-thread and executor ownership, the worktree/commit lacks a concrete charter, or the diff repaired out-of-scope bugs without an approved route.
