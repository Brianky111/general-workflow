# Fixtures and Probes

## Purpose

Prevent imagined external data from becoming contracts, mocks, or tests.

## Entry Conditions

- `ANCHOR-UNMET` names an original/accepted outcome whose completion cannot be judged without one specific external fact; general curiosity about an external system is not an entry condition.
- The feature touches an external system, protocol, file format, third-party API, or historical fixture.
- Interface examples or mocks need external data shapes.
- External behavior is uncertain.

## Fixture Areas

All fixture directories live at feature level, outside change rounds: `docs/<module>/<feature>/fixtures/`. Tests and CI reference these paths across rounds, so they never move when a round is archived. Other references may use the short form `fixtures/...`; this file owns the authoritative location.

- `docs/<module>/<feature>/fixtures/contract/`: reviewed probe captures used as contract evidence.
- `docs/<module>/<feature>/fixtures/counterexamples/`: admitted, deduplicated minimized failing inputs; append-only unless change protocol approves edits. Candidate/duplicate discovery output does not have to become a fixture.
- `docs/<module>/<feature>/fixtures/generated/`: refresh reports or reproducible caches; never the only contract source.

## Probe Rules

1. Before running anything, freeze one inline probe campaign: Delivery Anchor item/current `request_gap`, stable probe ID, exact external question/target, request or attempted-case limit, wall-clock limit, expected capture, and allowed sanitization. Keep it in the compact contract/task; do not create a probe-plan document.
2. Treat pre-contract probes as cumulative campaigns for the accepted delivery. Run only frozen probe IDs once; rerouting, another script/executor/session, or a renamed endpoint/question cannot reset or append budget.
3. Write the smallest disposable probe and capture only the evidence needed for that frozen question. Store reviewed sanitized output in `fixtures/contract/` when it becomes contract evidence; duplicate/nearby responses do not create fixtures, tests, or another probe.
4. Reference the selected fixture from interface examples and unit-test mocks, then discard probe code unless the project explicitly keeps it as bounded tooling.
5. A normal request/time limit with sufficient anchor evidence records `DISCOVERY-CLOSED`. If minimum external evidence for the named anchor item is still unavailable at the limit, stop as `ANCHOR-BLOCKED`; do not broaden the query or start a sibling probe.
6. If external behavior later drifts and the current anchor promised compatibility, treat the result as evidence that the same outcome is unmet. Otherwise it is a change candidate requiring acceptance through `10-change-protocol.md`. A scheduled or post-closeout probe result never appends to or reopens a `DELIVERY-DONE` TOS by itself.

## Prohibitions

- Do not invent external field shapes.
- Do not let raw external fields cross the adapter boundary unless the contract says so.
- Do not update contract fixtures from implementation convenience.
- Do not delete or rewrite counterexamples without a change record.
- Do not use the probe exception to launch exploratory crawling, fuzzing, nearby-input sampling, or repeated external checks outside the frozen probe ID and limits.

## Stop Conditions

Stop if the anchor reference/question/scope/limits are missing, real external behavior cannot be captured within the frozen request/time budget but the selected anchor outcome depends on it, or another probe would be needed after the delivery's probe list is closed. Report the exact `request_gap`; do not manufacture a contract or reset the campaign. If no anchor outcome depends on the probe, reject it as optional discovery rather than blocking delivery.
