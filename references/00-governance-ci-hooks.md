# Governance, CI, and Hooks

## Purpose

Set mechanical guardrails so workflow discipline does not depend on agent memory.

## Entry Conditions

- Project kickoff explicitly selected durable workflow governance.
- A review asks whether governance or CI is strong enough.
- A PR modifies guarded docs, fixtures, CI, lint config, or audit scripts.

## Document Governance

- Keep docs and code in the same repository and branch timeline.
- Govern only the artifacts the project actually selected for a named risk or durable handoff. Lean contracts and code-native schemas/tests remain valid sources; do not instantiate every possible document to make it governable.
- If durable status is needed, choose one of `workflow-state.json`, feature `status.json`, or `99-进度.md` as the human-maintained navigation source. Other views must be generated or treated as non-authoritative; status is never approval evidence.
- Protect guardrail files too: CI workflows, lint configs, audit scripts, and CODEOWNERS.
- If PR protection is unavailable, use approval tags and diff against the last approved tag as a weaker fallback.

## CI Gates

Add only gates appropriate to the stack and recorded risks:

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
- selected property/mutation/fuzz/security/accessibility/visual-regression checks,
- risk-triggered matrix checks for required `GAP`/planned cells, unknown test IDs, unsupported PASS claims, production `N-ID`/wiring gaps, and coverage/evidence disagreement.

## Hooks

Local hooks are early feedback only; CI must repeat the checks.

- `pre-commit`: scan skip/only, empty catch, fallback defaults, counterexample modification, and obvious guarded-path violations.
- `commit-msg`: enforce Conventional Commits and diff/path type match.
- `pre-push`: run fast tests plus selected-status consistency and pending-question scans when those artifacts exist.
- `post-checkout` / `post-merge`: remind agents to re-read the selected status/handoff source when one exists.

## Scheduled Checks

- fixture freshness probes compare external reality with `fixtures/contract/`,
- nightly fuzz/property testing records seeds,
- mutation testing exposes weak assertions.

## Output

- For kickoff: only the explicitly selected governance configuration, CI gates, hooks, and optional single status source, with reasons recorded in the existing kickoff/architecture surface.
- For an audit: a short report naming each expected gate as present, weakened, or missing, with evidence, plus fixes or a follow-up list.

Configuration is complete when every gate this project selected is enforced by CI (not only by local hooks) and a deliberately failing example is caught. Then return to the router.

## Stop Conditions

Stop for user confirmation before weakening or removing an existing gate, and when branch protection or CODEOWNERS is unavailable and the tag-based fallback must be accepted.
