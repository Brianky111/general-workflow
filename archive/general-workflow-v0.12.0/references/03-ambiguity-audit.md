# Ambiguity Audit

## Purpose

Catch material silent assumptions and verify that derived requirements/BDD remain faithful to the Delivery Anchor, using the smallest review that can change a decision. A clean audit is a short evidence note, not a separate report or human gate.

## Entry Conditions

- The core contract is about to be frozen.
- A changed clause affects a named compatibility, migration, security, concurrency/state, or ownership risk.
- A reviewer has a concrete reason to suspect a missing behavior or invented detail.

## Audit Scope

Read the immutable original source, ordered accepted deltas, current effective Anchor projection, and only the shared models or existing-code evidence relevant to the changed boundary. Treat structured requirements and BDD as projections to audit, not sources that may overwrite earlier history. Do not require a full independent pass for ordinary low-risk work.

Use an independent reviewer when public/external compatibility, irreversible migration, security/privacy/compliance, complex concurrency/state, cross-owner shared contracts, or formal audit requires separation of duties. Otherwise the author may perform one labeled cold-read in the same run.

## Targeted Checks

- Every explicit requested behavior is present and no observable behavior was invented.
- Every derived requirement/example maps to the current Delivery Anchor source or accepted delta; earlier sources remain unchanged.
- Each acceptance behavior has a concrete example and credible verification approach.
- Terms, fields, errors, defaults, limits, and forbidden side effects are precise where they affect this change.
- Changed frontend/backend or producer/consumer schemas agree where a shared boundary exists.
- State/event ownership, compatibility, migration, security, concurrency, and recovery are explicit only when triggered by the feature's actual risk.
- No unresolved choice can materially alter user-visible behavior, data meaning, irreversible effects, or ownership.

Check applicable risks; do not write an `N/A` defense for every theoretical category.

## Triage

- Fix projection, document-shape, or wording defects directly when they do not change the current Anchor behavior; never repair them by rewriting an original source or accepted-delta record.
- Record a true missing or contradictory anchored outcome as a specific `request_gap`, then route a blocking choice to `03-requirements-clarification.md` in the single batched pause.
- Record a non-blocking technical assumption in the affected clause only when it constrains implementation.
- Keep a tool/reviewer finding with no Anchor mapping as a follow-up/change candidate. The audit cannot self-accept a new behavior or named risk.

## Output

When clean, add one short note to the core contract, PR/task, or chosen status source:

```text
Ambiguity audit: clean @ <commit/date/source>; no blocking behavior finding.
```

Do not create or attach a separate zero-finding report. When findings exist, record only location, material consequence, and resolution; a dedicated report is justified only by an independent-review or formal-audit risk trigger.

A clean result neither changes the Delivery Anchor nor requires another user confirmation when the projections faithfully restate already authorized work. Apply READY and continue into planning, tests, and implementation in the same run.

## Stop Conditions

Stop only for an unresolved material finding tied to a concrete Anchor `request_gap`. Missing exhaustive category proof, a reviewer/tool suggestion without Anchor authority, or a standalone audit report is not a blocker.
