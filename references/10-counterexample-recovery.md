# Counterexample Recovery

## Purpose

Turn every reproducible failure into a permanent regression guard.

## Entry Conditions

- Property test records a seed.
- Fuzzing finds an input.
- Mutation testing leaves a surviving mutant.
- Integration scenario fails.
- Production or user bug has reproducible steps.

## Rules

1. Reproducible means mandatory. Do not ignore, retry away, or skip.
2. Minimize the failing input and store it under `fixtures/counterexamples/`.
3. Add a regression test tagged with the counterexample ID.
4. Run red to prove the failure is captured.
5. Fix to green.
6. Keep the counterexample append-only unless a change proposal approves removal or rewrite.

## Escalation

- If the failure violates an implementation detail but the contract is right, use `10-change-protocol.md` level B.
- If the failure proves an invariant or contract is wrong, escalate to level A.
- If the failure is not reproducible and has no seed, record it in the progress observation area. A second similar occurrence upgrades it to mandatory debt.

## Output

The minimized counterexample stored under `fixtures/counterexamples/`, a regression test tagged `反例#N` with red-then-green evidence, and updated status/progress entries. Then return to the router.

## Stop Conditions

Stop if the failure cannot be minimized or reproduced deterministically, or if fixing it would require changing a frozen contract without an approved change proposal.
