# Project Kickoff

## Purpose

Establish only the project facts needed to deliver the first safe vertical slice. Kickoff must not require a complete governance blueprint before ordinary implementation can begin.

## Entry Conditions

- A new repository is adopting this workflow.
- The requested slice lacks essential architecture, tool, or ownership evidence.
- A project-level risk may require a shared contract, migration, security, or governance baseline.

## Lean Kickoff

Default to incremental lean pacing from `00-pacing-mode.md`. Inspect and reuse repository evidence before creating documents. For the first feature, record only what is needed to run and verify it:

1. runtime/language and the relevant entry points;
2. the smallest truthful layer or vertical-slice boundary;
3. the one-command build/test/check path when available;
4. the durable raw requirement source and its owning feature/module;
5. any blocking shared schema, external system, migration, security, or owner boundary.

Put these facts in the feature's core contract, an existing architecture file, or the repository's normal task/PR location. Do not create `architecture.md`, `glossary.md`, `requirements-index.md`, workflow state, or governance files merely to satisfy a template.

Apply the pre-code budget from `00-feature-grading-and-splitting.md`: at most two new artifacts, 160 nonblank lines, one human pause, and no more than 20% of expected work or 30 minutes. Name the risk exception before exceeding it.

## Risk-Triggered Project Artifacts

Create or extend only what a concrete risk needs:

- `docs/architecture.md` when multiple runtimes, shared state, public contracts, migrations, or cross-owner boundaries need a stable project decision;
- `docs/glossary.md` when inconsistent domain terms could change behavior or data meaning;
- `docs/requirements-index.md` when several owners/features need scope coordination or similarity decisions must survive handoff;
- a project status source when work is blueprint, long-running, paused, audited, or handed between owners;
- governance/CI hooks when security, compliance, release risk, or repeated evidence drift justifies enforcement.

When an architecture artifact is required, keep it focused on layer responsibilities, dependency direction, shared ownership, code homes, and forbidden cross-boundary writes. Add adapters, domain layers, orchestration, or UI layers only when the code actually needs them.

## Decisions

Decide reversible technical defaults without user confirmation. Ask the user only when a decision changes observable behavior, project scope, public compatibility, data meaning, security posture, irreversible migration, or ownership. A clear request to implement plus a faithful lean kickoff is already authorized.

If blueprint mode is proposed, record the exact shared risk and get the one necessary approval through `00-pacing-mode.md`. Do not walk an exhaustive tuning checklist before feature work; tune BDD runners, property/mutation tools, fixture cadence, visual baselines, hooks, status schemas, or parallelism only when the requested slice triggers them.

## Output

- For ordinary work: no dedicated kickoff document; add the minimum project facts to the core contract or existing repository source.
- For a triggered project risk: one focused project artifact containing the decision, evidence, owner, and reevaluation condition.

Then evaluate the feature contract through `00-feature-grading-and-splitting.md`. When READY, continue into planning, tests, and implementation in the same run.

## Stop Conditions

Stop before adopting this workflow when the repository owner has not authorized it. Otherwise stop only for a real project-scope, public-boundary, migration, security, or ownership decision; missing template documents are not blockers.
