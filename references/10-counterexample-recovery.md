# Counterexample Recovery

## Purpose

Turn every reproducible failure into a permanent regression guard.

## Entry Conditions

- Property test records a seed.
- Fuzzing finds an input.
- Mutation testing leaves a surviving mutant.
- Integration scenario fails.
- Completeness audit finds a reproducible contract, connection, persistence, UI-state, or cross-feature failure.
- Production or user bug has reproducible steps.
- The failure is inside the accepted feature scope or directly blocks proving current feature evidence.

## Rules

1. Reproducible means mandatory. Do not ignore, retry away, or skip.
2. Minimize the failing input and store it under `fixtures/counterexamples/`.
3. Add a regression test tagged with the counterexample ID.
4. Run red to prove the failure is captured.
5. Fix to green.
6. Keep the counterexample append-only unless a change proposal approves removal or rewrite.
7. If the failure belongs to another feature or system and does not block current evidence, do not fix it here. Record it as an out-of-scope finding and return to the current router path.

## Escalation

- If the failure violates an implementation detail inside current scope but the contract is right, use `10-change-protocol.md` level B.
- If the failure proves an invariant or contract is wrong, escalate to level A.
- If the failure is not reproducible and has no seed, record it in the current handoff or the one selected status source only when useful. A second similar occurrence upgrades it to mandatory debt.

## Output

The minimized counterexample under the project's existing fixture convention, a regression test tagged `反例#N` with red-then-green evidence, and one update in the selected status/handoff source only when a pause, handoff, or closeout trigger exists. Ordinary single-owner work does not create or synchronize status/progress files. Then return to the router.

## Stop Conditions

Stop if the failure cannot be minimized or reproduced deterministically, or if fixing it would require changing a frozen contract without an accepted delta under `10-change-protocol.md`.
