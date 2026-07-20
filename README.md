# General Workflow Skill

This repository develops the `general-workflow` Codex skill: an implementation-forward, evidence-driven workflow for discovering behavior with BDD and delivering vertical features across UI, runtime contracts, backend logic, infrastructure, and E2E acceptance.

The skill helps Codex:

- detect the current workflow stage from repository evidence;
- load only the reference document needed for that stage;
- freeze the smallest sufficient behavior contract, then continue into code in the same run when no material decision is blocked;
- treat documentation as a conditional decision/risk tool rather than a mandatory `00…99` checklist;
- distinguish product/module/feature/use-case/task levels and map one feature across its full-stack code homes;
- turn concise requirements into BDD Rules and concrete Given/When/Then examples, asking only questions that change observable behavior;
- bind existing-code plans and tests to the current production owner, real runtime/composition-root path, and nearest existing test suite;
- use a sparse behavior-to-proof map and behavior-sized red-green-refactor loops, expanding to a full matrix only for named risks;
- reject red tests against test-local surrogates, unregistered `V2` implementations, or parallel test harnesses;
- prove frontend/backend contracts, cross-feature effects, user flows, and final Definition of Done;
- keep the main conversation as the orchestrator while subagents act as scoped executors;
- handle refactors, implementation, review, verification, and change recovery without reading the full source workflow every time.

## Workflow overview

Every request enters through the progress router, which scans repository evidence and first evaluates a positive `READY` predicate. Refactors never become features; similar requirements are triaged (merge / revise / new) before a second behavior source is created:

![请求入口与路由](docs/images/routing-map.svg)

A normal feature request uses the lean incremental pipeline. Raw source, structured behavior, and BDD examples form the default compact contract; one cold read records only actual findings. Once behavior, changed boundaries, the production write seam, and credible verification are clear, planning, red, and implementation can continue in the same run. Blueprint batching is an explicit opt-in for shared high-risk freezes rather than the new-project default:

![单功能主管线](docs/images/feature-pipeline.svg)

Numbered documents (`00-…` to `99-…`) are conditional dashboard slots. Ordinary work does not create empty conflict reports, all-`N/A` matrices, audit reports with no findings, or multiple status mirrors. Dedicated interface, test-matrix, integration, and completeness artifacts appear only when public compatibility, external protocols, migrations, security, concurrency/state-machine risk, cross-owner behavior, audit obligations, or multi-owner handoff justify them.

## Repository layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── 00-progress-router.md
│   ├── 00-orchestration-policy.md
│   ├── 00-pacing-mode.md
│   ├── 00-refactor-intake.md
│   └── ...
├── scripts/
│   └── check_consistency.py
├── 通用开发工作流-v3.8-环节拆分版.md
├── CHANGELOG.md
└── README.md
```

Important distinction:

- `SKILL.md`, `agents/`, and `references/` are the reusable Codex skill package.
- `通用开发工作流-v3.8-环节拆分版.md` is source material for the split references.
- `README.md` documents this repository; it is not required inside the installed skill package.

## Skill behavior

The skill uses progressive disclosure:

1. Start from `SKILL.md`.
2. Always read `references/00-progress-router.md` first.
3. Evaluate whether the compact contract and repository evidence make the work `READY` for code.
4. Load only the reference file needed for the next material decision or execution step.
5. Do not route backward solely because an optional artifact or approval timestamp is absent.

The orchestration model is explicit:

- the current conversation is the orchestrator;
- subagents are executors;
- once a scope is assigned to an executor, the main thread must not implement the same scope in parallel;
- the main thread owns integration, conflict resolution, final verification, and user communication.

## Key references

| File | Purpose |
|---|---|
| `references/00-progress-router.md` | Choose the current workflow stage and next reference. |
| `references/00-orchestration-policy.md` | Define main-thread orchestration and subagent executor boundaries. |
| `references/00-pacing-mode.md` | Default to incremental delivery; opt into blueprint only for justified shared freezes. |
| `references/00-refactor-intake.md` | Establish existing behavior and green-test protection without backfilling workflow docs. |
| `references/03-bdd-example-mapping.md` | Map concise requirements into observable Rules and concrete Examples. |
| `references/05-conflict-scan.md` | Find the real production owner/runtime path and reusable code and tests. |
| `references/06-planning.md` | Build the smallest executable, reuse-first implementation plan. |
| `references/06-test-strategy.md` | Map behavior sparsely to existing test homes and risk-triggered wiring evidence. |
| `references/07-red-tests.md` | Prove an admissible red against the approved production node. |
| `references/08-implementation.md` | Modify the selected production owner and reject shadow implementations. |
| `references/09-review-and-verification.md` | Verify behavior, evidence, ownership, and acceptance. |
| `references/09-feature-completeness.md` | Run a final independent evidence audit for governed or high-risk work. |

## Validate

There is no application build system. Useful checks:

```powershell
Get-ChildItem -Force
Select-String -Path *.md -Pattern '^#{1,4}\s+'
git diff --check
python scripts/check_consistency.py
$env:PYTHONUTF8 = 1   # required on GBK-default Windows: quick_validate.py reads UTF-8 files without declaring an encoding
python "<path-to-skill-creator>\scripts\quick_validate.py" (git rev-parse --show-toplevel)
```

`check_consistency.py` verifies that `references/*.md`, the `SKILL.md` Reference Map, and cross-file mentions stay in sync, that every reference is reachable from the router, and that the READY/document-budget and N-ID/SUT-binding policy anchors remain present across stages. Run it before committing changes to `SKILL.md` or `references/`.

`git diff --check` may print CRLF conversion warnings on this Windows checkout; distinguish those from real whitespace errors.

## Install or sync locally

To use this checkout as the local Codex skill, copy only the skill package files:

Validate the source checkout first (see above), then copy:

```powershell
$src = git rev-parse --show-toplevel
$dst = Join-Path $env:USERPROFILE ".codex\skills\general-workflow"

New-Item -ItemType Directory -Path $dst -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $src "SKILL.md") -Destination (Join-Path $dst "SKILL.md") -Force
robocopy (Join-Path $src "agents") (Join-Path $dst "agents") /MIR
robocopy (Join-Path $src "references") (Join-Path $dst "references") /MIR
```

Note: `/MIR` mirrors — it deletes files in the target that no longer exist in the source, so local patches in the installed copy are overwritten. robocopy exit codes 0-7 all mean success; only >=8 is failure.

Then validate the installed copy:

```powershell
python "<path-to-skill-creator>\scripts\quick_validate.py" $dst
```

## Development notes

- Keep `SKILL.md` concise; move stage details into `references/`.
- Keep references one level deep and directly discoverable from `SKILL.md`.
- Do not duplicate long workflow text across files.
- Treat a Feature as a vertical user capability, not a synonym for one backend folder or one API endpoint.
- Update `agents/openai.yaml` when the trigger behavior or default prompt changes.
- Do not store secrets, credentials, private host details, or project-specific business data in the skill.

## License

MIT — see [LICENSE](LICENSE).
