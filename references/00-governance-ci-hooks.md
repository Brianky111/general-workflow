# Governance, CI, and Hooks

## Purpose

Set mechanical guardrails so workflow discipline does not depend on agent memory.

## Entry Conditions

- Project kickoff is setting workflow infrastructure.
- A review asks whether governance or CI is strong enough.
- A PR modifies guarded docs, fixtures, CI, lint config, or audit scripts.

## Document Governance

- Keep docs and code in the same repository and branch timeline.
- Governed docs include architecture, shared models, requirements, contracts, conflict records, module interfaces, and planning docs.
- State files (`workflow-state.json`, feature `status.json`, `99-进度.md`) are navigation mirrors, not approval evidence.
- Protect guardrail files too: CI workflows, lint configs, audit scripts, and CODEOWNERS.
- If PR protection is unavailable, use approval tags and diff against the last approved tag as a weaker fallback.

## CI Gates

Add gates appropriate to the stack:

- layer-boundary import checks,
- forbidden raw external-field leaks,
- silent failure scans (`empty catch`, fallback defaults),
- commit order and path purity,
- append-only `fixtures/counterexamples/`,
- red replay for red-test commits,
- contract-vs-code signature comparison,
- pending-question and ambiguity-audit checks,
- commit message format,
- status consistency,
- unit/property/integration/visual regression tests.

## Hooks

Local hooks are early feedback only; CI must repeat the checks.

- `pre-commit`: scan skip/only, empty catch, fallback defaults, counterexample modification, and obvious guarded-path violations.
- `commit-msg`: enforce Conventional Commits and diff/path type match.
- `pre-push`: run fast tests, state consistency, and pending-question scans.
- `post-checkout` / `post-merge`: remind agents to re-read state and progress files.

## Scheduled Checks

- fixture freshness probes compare external reality with `fixtures/contract/`,
- nightly fuzz/property testing records seeds,
- mutation testing exposes weak assertions.

## Output

- For kickoff: governance configuration, CI gate definitions, hook scripts, and state files initialized from `99-status-and-evidence.md` shapes, with the chosen gates listed in the kickoff notes.
- For an audit: a short report naming each expected gate as present, weakened, or missing, with evidence, plus fixes or a follow-up list.

Configuration is complete when every gate this project selected is enforced by CI (not only by local hooks) and a deliberately failing example is caught. Then return to the router.

## Stop Conditions

Stop for user confirmation before weakening or removing an existing gate, and when branch protection or CODEOWNERS is unavailable and the tag-based fallback must be accepted.
