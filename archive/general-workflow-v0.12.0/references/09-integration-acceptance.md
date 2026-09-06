# Integration Acceptance

## Purpose

Verify that one currently selected outcome from the original user request or an explicitly accepted delta works through the real vertical production slice and its declared cross-feature effects. Integration obligations and matrices are subordinate evidence for that anchor outcome.

When `00-solution-framing.md` is active, keep two judgments distinct: each owning feature contribution passes its own production behavior/proof, while the solution passes only after the declared cross-feature assembly and aggregate evidence succeed. Do not copy feature contracts into the integration record or use another owner's open contribution to erase a feature's already supported completion unless its accepted result or only credible production proof depends on that contribution.

## Entry Conditions

- A currently incomplete or uncertified original/accepted outcome depends on a recorded connection, persistence truth, cross-owner effect, public contract, or critical UI path, and its authoritative acceptance ID and real user/runtime entry are known.
- Target tests are green or a known reproducible blocker remains; a frozen integration obligation identifies the minimum real-layer evidence for that outcome rather than defining a separate scope.

## Actions

1. Start from the anchor outcome's real user/API/event entry and run the relevant production slice together. Judge its observable result and forbidden effects first; then use assigned real-layer obligations to explain the evidence. Remove or bypass only mocks that hide the required seam, and do not assemble unrelated layers for broader exploration.
2. Validate producer/consumer fields, units, casing, enums, errors, and events only when the frozen contract/risk set assigns that boundary.
3. Execute only the acceptance behaviors assigned to contract, wiring/feature integration, cross-feature, persistence, or E2E obligations in the finite frozen `TOS`; each must map to the current original/accepted outcome. Do not replay unrelated or theoretical examples solely for document completeness.
4. Report each using its authoritative acceptance ID: `<AC or existing ID> -> pass/fail -> evidence + likely broken production node/boundary`.
5. For UI flows, drive behavior from the user's entry point. Exercise only applicable states named by the frozen contract/risk obligations; the generic loading/empty/success/validation/permission/network/server/retry/disabled/duplicate-submit list is a selection aid, not an instruction to create them all.
6. When persistence truth is assigned, reload or start a new session after success to prove state is persisted/system truth, not only frontend memory.
7. Exercise only declared cross-feature effects and assigned event-idempotency risks; verify downstream effects through the owning feature rather than direct database reach-through.
8. For a framed solution, record each result under its owning feature reference and record only the cross-feature seam/aggregate outcome at solution level. Leave an unfinished owned behavior with that feature; leave an independently blocked contribution as the solution's aggregate gap.
9. Include dependency failure, retry/duplicate delivery, or concurrency paths only when the original/accepted outcome or its accepted risk selected them; a matrix entry alone cannot expand the outcome.
10. Automate a passing integration/E2E scenario only when that automation is already a frozen obligation. Otherwise retain the current evidence and record optional automation as a follow-up; do not open a post-implementation red loop.
11. Provide screenshot, trace, recording, preview link, or direct human walkthrough for UI; run selected accessibility checks and record visual baselines only after human approval.

## Output

Record the anchor outcome, real production entry/result, environment, and subordinate per-scenario evidence in CI, the current handoff/PR, or an existing acceptance surface. Create `09-集成验收.md` only for an explicitly governed round, durable multi-owner handoff, or accepted high-risk need. Resolve planned proof to supported evidence; never use a bare checkmark.

When the triggered integration evidence is green, return to the router. Ordinary work may close after review and regression evidence; a framed solution closes only when all required feature contributions and its finite aggregate proof are supported. Read `09-feature-completeness.md` only when a governed/high-risk final independent audit is actually triggered.

## Stop Conditions

A finding moves an existing obligation to `GAP` only when it is reproducible through the real production slice and actually falsifies the anchor outcome, or when it destroys that outcome's minimum credible persistence/wiring/cross-feature evidence. Freeze that complete delivery-blocking failed-scenario set, allow one aggregate repair, then run one integration recheck over exactly that set. If any frozen scenario remains red, its obligation is `BLOCKED`; relabeling the failure cannot start another cycle. Missing optional risk proof, governance/naming/trace defects, extra automation, and theoretical scenarios are follow-ups and cannot open red work or block `DELIVERY-DONE`. An unassigned reproducible failure is only a bounded counterexample candidate when it maps to the same accepted outcome; otherwise quarantine it. Do not substitute mocked page success for required persistence, production wiring, or cross-feature evidence. When assigned obligations pass, mark them `VERIFIED`, stop integration, record that the anchor outcome succeeds in production, and evaluate `DELIVERY-DONE`.
