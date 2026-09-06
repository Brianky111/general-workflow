# Changelog

## 1.0.0 - 2026-09-04

Reframed the skill around Greenfield project delivery, using the supplied `project-dev-workflow` package as the baseline and expanding it for architecture-led development.

- Added a project-profile entry point that evaluates product shape, runtime units, data, team, lifecycle, and risk before selecting architecture depth.
- Added explicit stages for requirements/goals, scenarios/acceptance, scope/non-goals, constraints/quality attributes, architecture decisions, scaffolding/CI, vertical slicing, implementation, testing/integration, release/operations, and retrospective evolution.
- Expanded architecture guidance to cover system shape, direct layering vs modular vs hybrid organization, data ownership and invariants, authentication/authorization, asynchronous work, API/error conventions, observability, deployment, migration, and rollback.
- Made the first vertical slice an architecture-validation path rather than only a feature list.
- Kept behavior-sized red/green/refactor, layered testing, CI/CD, migration, secrets, monitoring, and rollback guidance from the reference package.
- Archived the previous feature/change-oriented workflow under `archive/general-workflow-v0.12.0/`; archived material is reference-only.
- Replaced the old consistency checks with checks for the Greenfield stage graph, reference reachability, architecture decision coverage, release/operations coverage, and archive separation.
