# Fixtures and Probes

## Purpose

Prevent imagined external data from becoming contracts, mocks, or tests.

## Entry Conditions

- The feature touches an external system, protocol, file format, third-party API, or historical fixture.
- Interface examples or mocks need external data shapes.
- External behavior is uncertain.

## Fixture Areas

All fixture directories live under the feature folder: `docs/features/<feature>/fixtures/`. Other references may use the short form `fixtures/...`; this file owns the authoritative location.

- `docs/features/<feature>/fixtures/contract/`: reviewed probe captures used as contract evidence.
- `docs/features/<feature>/fixtures/counterexamples/`: minimized failing inputs; append-only unless change protocol approves edits.
- `docs/features/<feature>/fixtures/generated/`: refresh reports or reproducible caches; never the only contract source.

## Probe Rules

1. Write a disposable probe to capture real external behavior.
2. Store sanitized output in `fixtures/contract/`.
3. Reference that fixture from interface examples and unit-test mocks.
4. Discard probe code unless the project explicitly keeps it as tooling.
5. If the external behavior later drifts, route to `10-change-protocol.md` level A.

## Prohibitions

- Do not invent external field shapes.
- Do not let raw external fields cross the adapter boundary unless the contract says so.
- Do not update contract fixtures from implementation convenience.
- Do not delete or rewrite counterexamples without a change record.

## Stop Conditions

Stop if real external behavior cannot be captured but the contract depends on it.
