# Orchestration Policy

## Purpose

Keep the current conversation as the task orchestrator and use subagents as scoped executors. Avoid the failure mode where the main thread and subagents both implement the same task in parallel.

Also avoid the failure mode where the orchestrator keeps opening new worktrees or executor branches instead of integrating the previous loop.

## Entry Conditions

- A local subagent or multi-agent tool is available.
- The selected workflow stage has non-trivial execution work, separable modules, independent audits, test work, review work, probes, or validation streams.
- The user asks for delegation, parallel work, multi-agent execution, or stronger review.

## Roles

| Role | Owns | Must not do |
|---|---|---|
| Main thread / orchestrator | Stage routing, scope, plan, executor prompts, write-set boundaries, monitoring, integration, conflict resolution, final verification, user communication | Implement the same scope assigned to an executor while that executor is working |
| Executor subagent | Assigned audit, mapping, test, implementation, probe, or review task | Expand scope, edit outside assigned paths, revert other agents, decide final acceptance, communicate completion to the user |

## Execution Modes

Choose the lightest mode that preserves correctness:

| Mode | Use when | Main thread action |
|---|---|---|
| Direct execution | Tiny task, no useful split, local blocker, subagents unavailable, or merge risk exceeds value | Execute locally and record the reason if the task is non-trivial |
| Read-only executor | Requirements audit, code mapping, test review, diff review, risk scan, or external-behavior check | Delegate the investigation, then wait or do only non-overlapping orchestration work |
| Worker executor | A module, layer, test file, probe, or fixture can be edited independently | Assign exact read/write boundaries and pause same-scope implementation locally |
| Adversarial executor | Security, authorization, protocol, migration, concurrency, weak tests, or high-cost failure risk | Ask for counterexamples, missed cases, and evidence gaps; keep final judgment in main thread. For adversarial-tier modules, the attack executor reads only the contract, never the implementation |

Use a role-isolated research/worker/check trio only when independent discovery and review materially reduce risk or when several scopes can truly progress in parallel. Ordinary bounded work may use one worker plus main-thread verification. The same executor never both implements and independently certifies one high-risk scope.

## Session Binding

One session, one scope. A conversation binds to a single feature — or a single executor scope inside it — at a time:

- Claim a scope before editing it. Record the owner in the executor brief and, when the project uses durable ownership tracking, in its one selected status surface; do not mirror the claim into multiple files.
- Do not claim a scope whose owner has fresh evidence (recent commits, CI runs, progress updates); coordinate through the user instead.
- When the user's own request collides with a fresh claim, surface the collision first — owner, evidence freshness, work in progress — before starting; the user may not know the scope is taken.
- Taking over a stale scope requires user confirmation only when ownership is genuinely ambiguous or fresh work may be lost; record the decision in the handoff/status surface in use.
- Switching features mid-session requires closing out first, then re-entering through the router.
- Parallelism across features means parallel sessions, each with its own binding — never one session interleaving several features.

## Worktree and Executor Lifecycle

Treat an executor worktree or branch as a leased workspace for one scope, not as a disposable retry token.

A writable worktree needs an orchestrator-approved inline charter, normally no more than eight lines: purpose plus accepted `AC`/existing ID and `N-ID`; one-sentence objective; exact write set; important read-only and prohibited paths; required red/green/regression or visual evidence; handoff/branch/commit expectation; and merge/no-op/blocked/discard closeout owner. Keep it in the executor prompt, task plan, or existing status surface—never a separate charter document.

Do not open a writable worktree for vague work such as "investigate", "continue", "fix the remaining failures", "clean up the module", or "make progress". Those are read-only discovery or planning tasks until the orchestrator can name the target ID, write set, and evidence. If discovery needs isolation, mark the worktree `review-only` and prohibit code edits.

Before launching a new executor, worktree, or branch for the bound feature:

1. Inspect `git worktree list`, relevant branches/PRs, `git status`, and any selected owner/handoff source.
2. Verify the inline charter. Missing target, write set, evidence, or closeout means read-only discovery or replanning, not a writable executor.
3. Do not replace an active owner or dirty/unmerged/missing-handoff same-scope loop; close it first. Unrelated old worktrees are separate cleanup debt unless paths overlap.

Executor handoff must end in exactly one state:

- `committed`: assigned changes are committed on the executor branch/worktree, with commands, test evidence, changed paths, and remaining risks.
- `no-op`: no file changes were needed, with evidence for why.
- `blocked`: uncommitted or partial paths are listed, the blocking reason is concrete, and the orchestrator decides whether to finish, commit, discard, or ask the user.

Close one loop before opening another. The orchestrator closeout order is:

1. Collect the handoff; inspect Git; integrate or reject code/test/doc changes.
2. Run verification against the integrated runtime path.
3. Update the compact contract/plan only if behavior or scope changed, and update one selected status source when used.
4. Commit, or record evidence-backed no-op/blocker; release, advance, or reassign ownership.
5. Return to `00-progress-router.md` at the meaningful checkpoint.

Do not launch a new same-feature executor/worktree between steps 1 and 7. If several executor results arrive together, integrate them one at a time and rerun the evidence check after each merge.

## Orchestrator Procedure

1. Select the workflow stage first; do not route to orchestration only because tools exist.
2. Decide whether executor help changes correctness, coverage, or throughput.
3. If writable delegation is useful, write the worktree charter first. If the objective cannot be tied to a target ID, write set, and evidence, use read-only discovery instead.
4. If delegating, write a small execution brief:
   - objective;
   - target ID from the approved charter;
   - context manifest for bounded tasks (exact files to load, each with a one-line reason), or a search scope for discovery tasks (paths, globs, or subsystems the executor may search);
   - allowed write paths, or `report only`;
   - prohibited paths and behaviors;
   - required output evidence;
   - handoff location;
   - closeout rule;
   - model tier, when the platform supports it: mechanical or repetitive work → fast cheap tier; standard implementation → default tier; architecture, security, protocol, or adversarial review → strongest tier. Reviewers never below the default tier.
5. Before launching executors, run the worktree/executor lifecycle gate above and close any existing same-feature loop first.
6. After launching executors, do not implement their assigned scope locally. The main thread may:
   - inspect state needed for coordination;
   - prepare or update the compact task plan or selected status/handoff surface;
   - launch additional executors;
   - review executor outputs;
   - integrate non-overlapping results;
   - run final tests and acceptance checks;
   - make tiny integration fixes after executor handoff.
7. If executor output conflicts, the main thread resolves the conflict and may ask a reviewer/adversarial executor for a report. Do not let executors decide final acceptance.

## Executor Prompt Template

```markdown
You are an executor in an orchestrated workflow. The main thread owns scope, integration, and final acceptance.

Task: <one concrete objective>
Target ID: <AC or existing R/EX/P, matrix batch, bug, counterexample, or approved change ID>
Context manifest (bounded tasks — load these and nothing else):
- <file or doc path> — <why this task needs it>
Search scope (discovery tasks — search freely inside, report anything outside):
- <paths, globs, or subsystems>
May edit: <paths or "none, report only">
Must not edit: <paths/behaviors>
Preserve: <contracts, public behavior, tests, data shape>
Evidence required: <red/green command, regression, screenshot, trace, or report>
Handoff: <selected status/handoff surface and commit expectation>
Closeout: <merge/no-op/blocked/discard owner>
Return: <diff summary, commands, evidence, blockers, risks>
```

Bounded (worker/review) executors read only the manifest plus their own write paths. Discovery executors — conflict scans, code mapping, risk scans, anti-hardcoding sampling, adversarial probing — get a declared search scope instead of a closed file list: they search freely inside it and report, rather than act on, anything found outside. Do not paste conversation history into the brief — the manifest or scope carries the context. An executor that finds its manifest or scope insufficient stops and reports what is missing; it does not silently expand its own scope.

## Output

- Orchestration decision: direct / read-only executor / worker executor / adversarial executor.
- Inline worktree charter for any writable worktree/executor, or a statement that the task is read-only discovery.
- Executor briefs and write boundaries, when delegated.
- Worktree/executor closeout status before any new same-feature launch: integrated, no-op, blocked, or unrelated cleanup debt.
- Integration and verification evidence owned by the main thread.
- Direct-execution reason, when the main thread performs non-trivial work without executors.

## Stop Conditions

Stop or re-plan if executor write sets overlap unsafely, an executor needs to change contracts or public behavior, executor reports contradict each other, or the main thread cannot verify executor claims with local evidence.

Stop instead of spawning another worktree if a prior same-feature worktree/branch is dirty, unmerged, lacks a handoff, or has selected-status evidence that has not been reconciled.

Stop instead of spawning a writable worktree if the purpose, target ID, write set, evidence, or closeout rule is missing.
