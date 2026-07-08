# Ambiguity Audit

## Purpose

Catch silent assumptions before human approval.

## Entry Conditions

- Requirements or interface draft is ready for a gate.
- The author claims there are no pending questions.
- A reviewer suspects missing scenarios, undefined terms, or invented details.

## Auditor Setup

Use an independent pass when possible. The auditor should read only the draft documents, upstream docs, glossary, shared models, and raw requirements. Do not give the auditor the author's private reasoning or implementation code.

## Audit Checklist

- Every explicit raw requirement appears in the structured draft.
- Terms are defined and consistent with `glossary.md`.
- Normal, error, and boundary scenario categories are not silently empty.
- Branches are closed: if a case is mentioned, its behavior is specified.
- Vague quantities or degree words are quantified or questioned.
- Defaults, nulls, limits, and extreme inputs are defined.
- Draft statements do not conflict with each other or with shared models.
- Every behavior traces to raw requirements, scenario IDs, or decision records; untraceable behavior becomes a question.

## Triage

- Document defects go back to the drafting agent: missing sections, missing examples, broken template shape.
- True ambiguity goes into `## 待确认反问` with location, options, consequences, and recommendation.

## Output

Attach an audit report with document-position evidence. No evidence means not reviewed.

## Stop Conditions

Do not pass the gate until audit is complete and pending questions are answered or explicitly waived by the human reviewer.
