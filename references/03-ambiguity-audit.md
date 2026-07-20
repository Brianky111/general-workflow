# Ambiguity Audit

## Purpose

Catch material silent assumptions with the smallest review that can change a decision. A clean audit is a short evidence note, not a separate report or human gate.

## Entry Conditions

- The core contract is about to be frozen.
- A changed clause affects a named compatibility, migration, security, concurrency/state, or ownership risk.
- A reviewer has a concrete reason to suspect a missing behavior or invented detail.

## Audit Scope

Read the durable raw source, structured requirement, BDD examples, and only the shared models or existing-code evidence relevant to the changed boundary. Do not require a full independent pass for ordinary low-risk work.

Use an independent reviewer when public/external compatibility, irreversible migration, security/privacy/compliance, complex concurrency/state, cross-owner shared contracts, or formal audit requires separation of duties. Otherwise the author may perform one labeled cold-read in the same run.

## Targeted Checks

- Every explicit requested behavior is present and no observable behavior was invented.
- Each acceptance behavior has a concrete example and credible verification approach.
- Terms, fields, errors, defaults, limits, and forbidden side effects are precise where they affect this change.
- Changed frontend/backend or producer/consumer schemas agree where a shared boundary exists.
- State/event ownership, compatibility, migration, security, concurrency, and recovery are explicit only when triggered by the feature's actual risk.
- No unresolved choice can materially alter user-visible behavior, data meaning, irreversible effects, or ownership.

Check applicable risks; do not write an `N/A` defense for every theoretical category.

## Triage

- Fix document-shape or wording defects directly when they do not change behavior.
- Route a true blocking choice to `03-requirements-clarification.md` in the single batched pause.
- Record a non-blocking technical assumption in the affected clause only when it constrains implementation.

## Output

When clean, add one short note to the core contract, PR/task, or chosen status source:

```text
Ambiguity audit: clean @ <commit/date/source>; no blocking behavior finding.
```

Do not create or attach a separate zero-finding report. When findings exist, record only location, material consequence, and resolution; a dedicated report is justified only by an independent-review or formal-audit risk trigger.

A clean result does not require another user confirmation when the contract faithfully restates already authorized work. Apply READY and continue into planning, tests, and implementation in the same run.

## Stop Conditions

Stop only for an unresolved material finding. Missing exhaustive category proof or a standalone audit report is not a blocker.
