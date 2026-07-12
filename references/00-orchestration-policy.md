# Orchestration Policy

## Purpose

Keep the current conversation as the task orchestrator and use subagents as scoped executors. Avoid the failure mode where the main thread and subagents both implement the same task in parallel.

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

## Orchestrator Procedure

1. Select the workflow stage first; do not route to orchestration only because tools exist.
2. Decide whether executor help changes correctness, coverage, or throughput.
3. If delegating, write a small execution brief:
   - objective;
   - context manifest: the exact files to load, each with a one-line reason;
   - allowed write paths, or `report only`;
   - prohibited paths and behaviors;
   - required output evidence;
   - handoff location;
   - model tier, when the platform supports it: mechanical or repetitive work → fast cheap tier; standard implementation → default tier; architecture, security, protocol, or adversarial review → strongest tier. Reviewers never below the default tier.
4. After launching executors, do not implement their assigned scope locally. The main thread may:
   - inspect state needed for coordination;
   - prepare or update orchestration docs;
   - launch additional executors;
   - review executor outputs;
   - integrate non-overlapping results;
   - run final tests and acceptance checks;
   - make tiny integration fixes after executor handoff.
5. If executor output conflicts, the main thread resolves the conflict and may ask a reviewer/adversarial executor for a report. Do not let executors decide final acceptance.

## Executor Prompt Template

```markdown
You are an executor in an orchestrated workflow. The main thread owns scope, integration, and final acceptance.

Task: <one concrete objective>
Context manifest (load these and nothing else):
- <file or doc path> — <why this task needs it>
- <file or doc path> — <why this task needs it>
May edit: <paths or "none, report only">
Must not edit: <paths/behaviors>
Preserve: <contracts, public behavior, tests, data shape>
Return: <diff summary, commands, evidence, blockers, risks>
```

Executors read only the manifest plus their own write paths. Do not paste conversation history into the brief — the manifest files carry the context. If an executor finds the manifest insufficient, it stops and reports what is missing; it does not browse the repository on its own.

## Output

- Orchestration decision: direct / read-only executor / worker executor / adversarial executor.
- Executor briefs and write boundaries, when delegated.
- Integration and verification evidence owned by the main thread.
- Direct-execution reason, when the main thread performs non-trivial work without executors.

## Stop Conditions

Stop or re-plan if executor write sets overlap unsafely, an executor needs to change contracts or public behavior, executor reports contradict each other, or the main thread cannot verify executor claims with local evidence.
