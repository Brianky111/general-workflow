# Requirements Capture

## Purpose

Preserve the user's original request and convert it into structured, reviewable requirements without inventing design choices.

## Entry Conditions

- The feature has user intent but lacks `00-原始需求.md` or `00-整理后需求.md`.
- The request is scattered across chat, issue text, screenshots, or existing notes.

## Actions

1. Copy the original request into `00-原始需求.md`; append rather than rewrite when possible.
2. Draft `00-整理后需求.md` with:
   - goal and non-goals,
   - actors or users,
   - numbered acceptance scenarios,
   - data or UI terms that need a glossary entry,
   - assumptions separated from confirmed facts.
3. Add numbered acceptance scenarios:
   - `S1`, `S2` for normal paths,
   - `E1`, `E2` for error paths,
   - `B1`, `B2` for boundary cases.
4. Propose standard or lightweight path; read `00-feature-grading-and-splitting.md` if the path or document granularity is unclear.
5. Mark unclear items as questions; do not silently choose product behavior.

## Output

Write concise Chinese requirement docs under `docs/features/<feature>/`.

## Stop Conditions

If requirements contain unresolved intent questions, route to `03-requirements-clarification.md` before writing contracts or tests.

Before human confirmation, route to `03-ambiguity-audit.md`.
