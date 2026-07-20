# Governance, CI, and Hooks

## Purpose

Set mechanical guardrails so workflow discipline does not depend on agent memory.

## Entry Conditions

- Project kickoff explicitly selected durable workflow governance.
- An accepted Delivery Anchor item or repository governance policy makes a named CI/guardrail the minimum credible proof.
- A PR modifies a guardrail already selected for that anchor item, such as guarded docs, fixtures, CI, lint config, or audit scripts.

A reviewer's generic request for “stronger CI” is a governance follow-up, not an entry condition for the current delivery.

## Document Governance

- Keep docs and code in the same repository and branch timeline.
- Govern only the artifacts the project actually selected for a named risk or durable handoff. Lean contracts and code-native schemas/tests remain valid sources; do not instantiate every possible document to make it governable.
- If durable status is needed, choose one of `workflow-state.json`, feature `status.json`, or `99-进度.md` as the human-maintained navigation source. Other views must be generated or treated as non-authoritative; status is never approval evidence.
- Protect guardrail files too: CI workflows, lint configs, audit scripts, and CODEOWNERS.
- If PR protection is unavailable, use approval tags and diff against the last approved tag as a weaker fallback.

## CI Gates

Add only gates mapped to a Delivery Anchor item or already accepted repository governance policy; every delivery-blocking gate must name that source, a finite command/budget, and its terminal state:

- layer-boundary import checks,
- forbidden raw external-field leaks,
- silent failure scans (`empty catch`, fallback defaults),
- commit order and path purity,
- append-only `fixtures/counterexamples/`,
- red replay for red-test commits,
- contract-vs-code signature comparison,
- pending-question and ambiguity-audit checks,
- regulated or explicitly selected requirement -> behavior -> contract -> test traceability checks,
- optional Markdown/Gherkin parity checks when executable BDD is enabled,
- commit message format,
- status consistency,
- domain/use-case/frontend unit and component tests,
- adapter integration, runtime contract, cross-feature workflow, and browser E2E tests,
- selected property/mutation/fuzz/security/accessibility/visual-regression checks, each with a finite wall-clock/attempted-case scope and deduplicated candidate output,
- risk-triggered matrix checks for required `GAP`/`P:` evidence cells, unknown test IDs, unsupported `PASS` claims, production `N-ID`/wiring gaps, and coverage/evidence disagreement.

## Hooks

Local hooks are early feedback only; CI must repeat the checks.

- `pre-commit`: scan skip/only, empty catch, fallback defaults, counterexample modification, and obvious guarded-path violations.
- `commit-msg`: enforce Conventional Commits and diff/path type match.
- `pre-push`: run fast tests plus selected-status consistency and pending-question scans when those artifacts exist.
- `post-checkout` / `post-merge`: remind agents to re-read the selected status/handoff source when one exists.

## Scheduled Checks

- fixture freshness probes compare external reality with `fixtures/contract/` under a finite request/time limit;
- each scheduled fuzz/property job has a fixed target/invariant, wall-clock or attempted-case limit, and cross-run semantic deduplication;
- each mutation job has a fixed changed-node scope, mutant/time limit, and equivalent-mutant classification.

Scheduled jobs produce candidate issues/evidence only. A seed, survivor, or drift result never appends to the current or a `DELIVERY-DONE` TOS and never reopens a closed delivery. A result may falsify an open compatibility outcome only when it is reproducible and maps to that anchor promise; otherwise handling it requires a newly accepted user/authoritative-source delta with its own finite plan and cumulative admission cap.

## Output

- For kickoff: only the explicitly selected governance configuration, CI gates, hooks, and optional single status source, with reasons recorded in the existing kickoff/architecture surface.
- For an audit: a short report naming each expected gate as present, weakened, or missing, with evidence, plus fixes or a follow-up list.

Configuration is complete when every anchor-linked gate this project selected is enforced by CI (not only by local hooks) and a deliberately failing example is caught. Then return to the router and re-evaluate the Delivery Anchor; do not add another gate from the audit output.

## Stop Conditions

Stop for user confirmation before weakening or removing an accepted gate, and when an anchor-required branch-protection or CODEOWNERS rule is unavailable and the tag-based fallback must be accepted. Missing optional or unanchored governance cannot block `ANCHOR-SATISFIED`.
