# Integration Acceptance

## Purpose

Verify the real vertical feature slice and its cross-feature effects after modules pass review.

## Entry Conditions

- Target tests are green, and a recorded connection, persistence, cross-owner, public-contract, or critical UI risk still needs real-layer evidence.

## Actions

1. Remove or bypass mocks where practical; run frontend, runtime contract, backend, persistence/adapters, and downstream handlers together.
2. Validate producer/consumer schemas at runtime: fields, units, casing, enums, errors, and events.
3. Execute the acceptance behaviors assigned to contract, wiring/feature integration, cross-feature, persistence, or E2E proof in the sparse/risk-triggered verification map; do not replay unrelated examples solely for document completeness.
4. Report each using its authoritative acceptance ID: `<AC or existing ID> -> pass/fail -> evidence + likely broken production node/boundary`.
5. For UI flows, drive behavior from the user's entry point. Exercise applicable loading, empty, success, validation, permission, network/server error, retry, disabled/in-flight, and duplicate-submit states.
6. Reload or start a new session after success to prove state is persisted/system truth, not only frontend memory.
7. Exercise declared cross-feature effects and event idempotency; verify downstream state/notification/accounting/etc. through the owning feature rather than direct database reach-through.
8. Include dependency failure, retry/duplicate delivery, or concurrency paths selected in the test matrix.
9. Turn passing stable scenarios into automated integration/E2E regression where feasible. Keep detailed edge cases at lower layers.
10. Provide screenshot, trace, recording, preview link, or direct human walkthrough for UI; run selected accessibility checks and record visual baselines only after human approval.

## Output

Record real-layer environment details and per-scenario evidence in CI, the current handoff/PR, or an existing acceptance surface. Create `09-集成验收.md` only for a governed round, durable multi-owner handoff, or named high-risk acceptance need. Resolve planned proof to supported evidence; never use a bare checkmark.

When the triggered integration evidence is green, return to the router. Ordinary work may close after review and regression evidence; read `09-feature-completeness.md` only when a governed/high-risk final independent audit is actually triggered.

## Stop Conditions

Any missing assigned risk proof is a coverage gap. Any red scenario routes back to the stage that owns the defect. Do not substitute mocked page success for real persistence, production wiring, or cross-feature evidence. Unassigned theoretical scenarios do not require `N/A` rows.
