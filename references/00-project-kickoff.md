# Project Kickoff

## Purpose

Initialize the project-level documents and guardrails before feature work begins.

## Entry Conditions

- A new repository is adopting this workflow.
- `docs/architecture.md`, `docs/glossary.md`, governance, CI, or state files are absent.

## Actions

1. Create `docs/architecture.md` with:
   - layer map: layer name, one-line responsibility, forbidden actions,
   - dependency direction: lower layers must not know higher layers,
   - vertical feature-slice map across frontend, shared contracts, backend, adapters, and E2E where applicable,
   - directory tree with one-line purpose per directory.
2. Decide layers by need, not by template. Ask:
   - Is there an external system or third-party API? Add an adapter layer.
   - Are there pure business rules independent of UI/external systems? Add a core layer.
   - Are there multi-step flows? Add an orchestration layer that orders calls but does not make domain judgments.
   - Is there a human interface? Add a frontend layer that displays and forwards, not owns business rules.
3. Write project examples for four architecture tests:
   - platform replacement test for adapter boundaries,
   - paper-calculation test for core logic,
   - script test for orchestration order,
   - loud-failure questions for error handling.
4. Initialize `docs/glossary.md`.
5. Initialize `docs/requirements-index.md` as the project-level feature roster, grouped by business module per `00-business-taxonomy.md`: scope, grading, status, and a holding area for out-of-scope ideas.
6. Decide the vertical-slice code-home template and record it in `architecture.md`: one feature identity across each touched runtime, using the full-stack example in `00-business-taxonomy.md` when applicable. Do not create a generic backend `models/` drawer; assign each model to its owning layer.
7. Read `00-pacing-mode.md` to choose blueprint or incremental pacing and record it in `docs/workflow-state.json`.
8. Read `00-governance-ci-hooks.md` to set document governance, CI gates, hooks, and status files (state-file shapes live in `99-status-and-evidence.md`).
9. Walk the tuning checklist below with the user and record the answers in kickoff notes or `architecture.md`.

## Tuning Checklist

Instantiate these project-level parameters before feature work; unanswered items become silent defaults later:

- [ ] layers: add/remove/rename per the four architecture questions
- [ ] vertical feature-slice template: frontend, shared runtime contracts, backend layers, adapters, E2E home, and shared-kernel ownership
- [ ] module grouping: which business modules structure the roster and the `docs/<module>/` directories, and the threshold below which a tiny project may flatten
- [ ] change-round convention: round slug naming, and which level-B/C work may stay inside the active round instead of opening one
- [ ] use-case split threshold: when scenario groups move from `00-整理后需求.md` into `use-cases/*.md` files
- [ ] BDD form: Markdown Example Mapping by default; whether an executable Gherkin runner is justified, where `.feature` files live, and which artifact is authoritative
- [ ] BDD depth: standard-path Rule/Example requirements and the minimum inline form for lightweight features
- [ ] pacing mode: blueprint or incremental this cycle; blueprint scope goes to `requirements-index.md`
- [ ] project identification criteria: what counts as new project / old project / new module in old project
- [ ] glossary: seed the domain terms
- [ ] forbidden-words list: raw external-field blacklist when external systems exist
- [ ] test framework and one-command run (Vitest / Jest / pytest ...)
- [ ] frontend test stack: logic/component/page tests, browser E2E, accessibility, and visual-regression tools when UI exists
- [ ] contract-test mechanism: shared runtime schema, OpenAPI validation, or consumer-driven contracts
- [ ] property-testing and combination tools (fast-check / hypothesis; PICT or equivalent)
- [ ] CI platform and gate scripts (PR gates, red-replay marking, commit-scope audit, status consistency, scheduled jobs)
- [ ] governance switches: CODEOWNERS / branch protection, or the tag-based fallback
- [ ] validation-strength thresholds: instantiate "high-cost decisions" as a concrete project list
- [ ] feature Definition of Done: select the applicable checklist and evidence forms from `09-feature-completeness.md`
- [ ] examples: fill every template placeholder with this project's domain content
- [ ] mutation testing: schedule and survival-rate requirement
- [ ] nightly fuzz budget: duration or iterations
- [ ] lightweight-path criteria: what counts as lightweight here
- [ ] raw-requirement preservation: how user words/attachments enter `00-原始需求.md`; append-only or not
- [ ] conflict-scan scope: which directories, entries, historical features, tests, and configs old-project scans must cover
- [ ] implementation-strategy decision template: criteria for from-scratch / modify existing / reuse-and-extend / refactor-then-implement / strangler replacement
- [ ] contract split thresholds: when `01-接口.md` splits into `interfaces/<module>.md` and when `conflicts/<module>.md` splits alongside (module count, line count, parallelism, external protocol, reuse)
- [ ] fixture freshness cadence: per external-system change speed
- [ ] visual-track form: screenshots / local preview / recording; visual-regression baseline management
- [ ] question-answer channel: batch in-doc, PR comments, or chat-then-write-back — pick one and fix it
- [ ] hooks policy: enable `core.hooksPath scripts/hooks` or not; which checks warn vs block
- [ ] state-file policy: enable `workflow-state.json` / `status.json` or not; schema fields, status enums, and evidence-link format
- [ ] parallelism: single serial agent, or multi-agent per module after freeze
- [ ] initial-review strictness: small projects may drop the anti-hardcoding sample, never the evidence rule

## Output

Project-level kickoff docs and guardrails, the recorded pacing mode, and the tuning checklist answers. Architecture approval freezes layer boundaries; later architecture changes use `10-change-protocol.md` level A. Then return to the router.

## Stop Conditions

Stop for human review when layer boundaries, dependency directions, or external-system responsibilities are not obvious, and before adopting this workflow in a repository whose owner has not confirmed it.
