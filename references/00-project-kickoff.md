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
5. Read `00-governance-ci-hooks.md` to set document governance, CI gates, hooks, and status files.

## Output

Project-level kickoff docs and guardrails. Architecture approval freezes layer boundaries; later architecture changes use `10-change-protocol.md` level A.

## Stop Conditions

Stop for human review when layer boundaries, dependency directions, or external-system responsibilities are not obvious.
