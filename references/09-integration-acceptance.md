# Integration Acceptance

## Purpose

Verify the real vertical feature slice and its cross-feature effects after modules pass review.

## Entry Conditions

- All feature modules have green tests and initial review evidence.
- End-to-end or user-visible behavior has not been verified.

## Actions

1. Remove or bypass mocks where practical; run frontend, runtime contract, backend, persistence/adapters, and downstream handlers together.
2. Validate producer/consumer schemas at runtime: fields, units, casing, enums, errors, and events.
3. Execute every numbered acceptance scenario and every Feature Test Matrix cell assigned to contract, feature integration, cross-feature, or E2E coverage.
4. Report each as `S1 -> pass/fail -> details + likely broken layer/module + suspected contract`.
5. For UI flows, drive behavior from the user's entry point. Exercise applicable loading, empty, success, validation, permission, network/server error, retry, disabled/in-flight, and duplicate-submit states.
6. Reload or start a new session after success to prove state is persisted/system truth, not only frontend memory.
7. Exercise declared cross-feature effects and event idempotency; verify downstream state/notification/accounting/etc. through the owning feature rather than direct database reach-through.
8. Include dependency failure, retry/duplicate delivery, or concurrency paths selected in the test matrix.
9. Turn passing stable scenarios into automated integration/E2E regression where feasible. Keep detailed edge cases at lower layers.
10. Provide screenshot, trace, recording, preview link, or direct human walkthrough for UI; run selected accessibility checks and record visual baselines only after human approval.

## Output

Create or update `09-集成验收.md` with real-layer environment details, per-scenario results, contract/cross-feature evidence, persistence-after-reload evidence, and UI/human acceptance evidence where applicable. Resolve test IDs through the evidence register and replace only verified `P:` cells with `PASS:<test-id>@<evidence>`; never write a bare checkmark.

All integration scenarios green is necessary but not terminal. Return to the router and read `09-feature-completeness.md` for the final Definition of Done audit. That audit owns archiving and the lessons pass.

## Stop Conditions

Any missing scenario or assigned matrix row is a coverage gap. Any red scenario routes back to the stage that owns the defect. Do not substitute mocked page success for real persistence or cross-feature evidence.
