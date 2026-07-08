# Status and Evidence

## Purpose

Keep handoff state synchronized with real evidence. Status files help navigation but are not the source of truth.

## Entry Conditions

- Router evidence conflicts.
- User asks what remains.
- Work is being handed off between agents.
- Progress/status files are missing or stale.

## Actions

1. Compare status docs with repository facts: files, commits, tests, PRs, and CI.
2. Mark each stage as not started, in progress, blocked, or complete.
3. For every complete claim, attach evidence: path, command, commit, PR, CI link, screenshot, or log summary.
4. Remove or correct unsupported claims.
5. Record blockers as concrete next decisions or commands.

## Consistency Rules

- `pendingQuestions` must equal unresolved `【答复】：` entries.
- `requirementsConfirmedAt` and `contractsFrozenAt` must point to a PR, commit, or approval tag; free-text “confirmed” is not evidence.
- Existing projects must have a conflict report with concrete scan conclusions.
- A module cannot be `done` without contract reference, red evidence, green evidence, and review/integration evidence.
- Status may lag behind reality, but it must not run ahead of evidence.

## Output

Update `docs/workflow-state.json`, `docs/features/<feature>/status.json`, or `99-进度.md` only if those files are part of the target project. For this skill repository, update issue notes or development docs instead.

## Stop Conditions

Stop if no reliable evidence exists for the claimed stage; report the uncertainty and the safest next verification step.
