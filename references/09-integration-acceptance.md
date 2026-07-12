# Integration Acceptance

## Purpose

Verify the feature as a whole after modules pass review.

## Entry Conditions

- All feature modules have green tests and initial review evidence.
- End-to-end or user-visible behavior has not been verified.

## Actions

1. Remove or bypass mocks where practical; run real layers together.
2. Execute every numbered acceptance scenario.
3. Report each as `S1 -> pass/fail -> details + likely broken layer/module + suspected contract`.
4. If a scenario passes, turn it into automated integration/E2E regression where feasible.
5. For UI, provide screenshot, recording, preview link, or direct human walkthrough.
6. Record visual baselines after human approval for visual-regression checks.

## Output

Integration report, scenario regression evidence, and UI/human acceptance evidence where applicable.

All scenarios green plus human-eye acceptance means the feature is complete: update `status.json` and `99-进度.md`, confirm the passed scenarios are captured as automated regression in CI where feasible (visual-track scenarios record visual baselines instead), report completion to the user with the evidence summary, and stop. This is the workflow's terminal state.

## Stop Conditions

Any missing scenario ID is a coverage gap. Any red scenario routes back to the stage that owns the defect.
