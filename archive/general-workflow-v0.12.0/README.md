# General Workflow Skill

This repository develops the `general-workflow` Codex skill: an implementation-forward, evidence-driven workflow for framing finite cross-feature solutions, discovering behavior with BDD, and delivering vertical features across UI, runtime contracts, backend logic, infrastructure, and E2E acceptance.

The skill helps Codex:

- preserve the original request plus explicitly accepted deltas as the immutable Delivery Anchor, and decide whether that request is complete before selecting any workflow stage;
- continue only from one named source-backed `request_gap`; unanchored findings, tests, risks, and review suggestions become follow-ups rather than new delivery work;
- run a solution candidate gate before feature-name similarity triage, then frame a goal-bounded solution when one aggregate outcome needs several independently acceptable features, staged cross-feature construction, or aggregate proof, with separate batch-local and aggregate progress while each feature remains the single source of truth for behavior;
- load only the reference document needed for that stage;
- freeze the smallest sufficient behavior contract, then continue into code in the same run when no material decision is blocked;
- treat documentation as a conditional decision/risk tool rather than a mandatory `00…99` checklist;
- distinguish the stable product/module/feature/use-case/task ownership hierarchy from an optional cross-feature solution delivery view, and map one feature across its full-stack code homes;
- preserve one current effective contract per feature while retaining the immutable original-plus-accepted-delta history, instead of concatenating historical snapshots or promoting governance findings into requirements;
- turn concise requirements into BDD Rules and concrete Given/When/Then examples, asking only questions that change observable behavior;
- bind existing-code plans and tests to the current production owner, real runtime/composition-root path, and nearest existing test suite;
- freeze a finite anchor-linked test-obligation set in the sparse behavior-to-proof map, reject unanchored obligations, then consume only valid obligations with behavior-sized red-green-refactor loops;
- declare the Delivery Anchor/current gap once per plan, reuse existing AC/R/EX IDs in rows, and omit unused campaign/counter ledgers on the ordinary path;
- cap property, fuzz, mutation, adversarial, review-sampling, and counterexample admission cumulatively for the accepted delivery, with no reset through rerouting, new executors, or renamed campaigns;
- reject red tests against test-local surrogates, unregistered `V2` implementations, or parallel test harnesses;
- stop immediately when every original/accepted outcome is delivered through the intended production entry and only its minimum anchor-linked proof, writes, wiring, gates, and regression satisfy `DELIVERY-DONE`;
- prove frontend/backend contracts, cross-feature effects, user flows, and final Definition of Done;
- keep the main conversation as the orchestrator while subagents act as scoped executors;
- handle refactors, implementation, review, verification, and change recovery without reading the full source workflow every time.

## Workflow overview

Every request enters through the progress router. The immutable original source plus explicitly accepted deltas form the Delivery Anchor. The router first absorbs existing production evidence and classifies it as `ANCHOR-SATISFIED`, `ANCHOR-UNMET`, or `ANCHOR-BLOCKED`; only `ANCHOR-UNMET` with one concrete `request_gap` may query the stage table or the subordinate positive `READY` predicate. Refactors never become new behavior features; similar requirements are triaged (merge / revise / new) before a second behavior source is created:

![请求入口与路由](docs/images/routing-map.svg)

A normal feature request uses the lean incremental pipeline. Structured behavior and BDD examples are faithful projections of the Delivery Anchor, not new scope authorities; one cold read checks that projection and records only source-backed findings. Once the selected gap's behavior, production write seam, and credible verification are clear, planning declares the Anchor/gap once and freezes a finite Test Obligation Set (`TOS`) whose rows reuse existing acceptance IDs. Ordinary work has no discovery campaign and writes no all-zero budget ledger; campaign IDs and counters appear only when triggered or consumed. Review or tool output may discharge the set but cannot extend it. A candidate changes scope only after an accepted user/authoritative-source delta, while a reproducible production counterexample may enter only when it actually falsifies an anchor outcome and fits the frozen cap. Budgets do not reset on reroute. At every meaningful checkpoint the workflow asks again whether the original request is complete; once it is delivered with minimum credible evidence, it closes once and stops without another review, red test, or discovery pass. Blueprint batching remains explicit opt-in for shared high-risk freezes:

![单功能主管线](docs/images/feature-pipeline.svg)

Before a similarly named request is merged into a feature, the workflow asks whether one feature contract can faithfully own the whole outcome. A common product stem or a platform suffix such as Android, iOS, web, or desktop is only a discovery hint. When an aggregate outcome spans independently acceptable features, modules/applications, staged cross-feature construction, or aggregate proof, the workflow adds a goal-bounded solution frame as an orthogonal delivery view. A durable staged solution uses `00-方案.md`, one `batches/NN-阶段/` directory per batch containing stable `00-施工.md` and mutable batch-local `99-进度.md`, `02-总体验收.md`, and one root aggregate `99-进度.md`; `01-共享边界.md` appears only when needed. Each feature keeps its authoritative behavior contract, production owner, detailed plan, and tests. Work still advances incrementally through exactly one owning feature gap at a time.

Numbered documents (`00-…` to `99-…`) are conditional dashboard slots. Ordinary feature work does not create empty conflict reports, all-`N/A` matrices, audit reports with no findings, or multiple status mirrors. Once staged durable solution coordination is positively identified, its plan, per-batch construction/progress pair, aggregate-acceptance, and root total-progress surfaces are the triggered control set rather than optional feature paperwork. Batch-local status owns work/TOS/evidence and the root status owns transitions/dependencies/totals, so these are scoped authorities rather than duplicate mirrors. Other dedicated artifacts still appear only when their named risks justify them.

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
│   ├── 00-solution-framing.md
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
3. Build the Delivery Anchor from the immutable original source and accepted deltas; evaluate its completion through the real production path before selecting a stage.
4. If `ANCHOR-UNMET`, name one concrete `request_gap`; if no gap exists, close or quarantine the finding instead of continuing.
5. Before feature similarity triage, run the solution candidate gate. If the aggregate outcome needs several independently acceptable feature contributions, staged cross-feature construction, or aggregate proof, use `references/00-solution-framing.md` to map owners, give every batch separate construction and progress sources, maintain root total progress, and define aggregate proof without copying feature truth; then select one owning feature gap.
6. Evaluate whether that gap's compact projection and repository evidence make it `READY` for code.
7. Freeze only anchor-linked test obligations and discovery/admission budgets inside the executable plan.
8. Load only the reference file needed to close the selected gap; every write batch must directly advance its acceptance predicate.
9. Evaluate the Delivery Anchor and `DELIVERY-DONE` before any new red/review/discovery pass, and stop when they hold.
10. Do not route backward solely because an optional artifact, unanchored finding, possible extra edge case, or approval timestamp is absent.

The orchestration model is explicit:

- the current conversation is the orchestrator;
- subagents are executors;
- once a scope is assigned to an executor, the main thread must not implement the same scope in parallel;
- the main thread owns integration, conflict resolution, final verification, and user communication.

## Key references

| File | Purpose |
|---|---|
| `references/00-progress-router.md` | Decide original-request completion first, then choose a subordinate stage only for one anchor gap. |
| `references/00-orchestration-policy.md` | Define main-thread orchestration and subagent executor boundaries. |
| `references/00-pacing-mode.md` | Default to incremental delivery; opt into blueprint only for justified shared freezes. |
| `references/00-solution-framing.md` | Classify solution scope before feature similarity triage, then coordinate per-batch construction/progress and root aggregate progress while preserving one behavior owner per feature. |
| `references/00-refactor-intake.md` | Establish existing behavior and green-test protection without backfilling workflow docs. |
| `references/03-bdd-example-mapping.md` | Map concise requirements into observable Rules and concrete Examples. |
| `references/05-conflict-scan.md` | Find the real production owner/runtime path and reusable code and tests. |
| `references/06-planning.md` | Build the smallest executable, reuse-first plan and freeze its finite test boundary. |
| `references/06-test-strategy.md` | Map a finite obligation set sparsely to existing test homes and budgeted risk evidence. |
| `references/07-red-tests.md` | Consume one frozen pending obligation with an admissible red against the approved production node. |
| `references/08-implementation.md` | Modify the selected production owner and reject shadow implementations. |
| `references/09-review-and-verification.md` | Verify behavior, evidence, ownership, and acceptance. |
| `references/09-feature-completeness.md` | Run a final independent evidence audit for governed or high-risk work. |
| `references/10-counterexample-recovery.md` | Admit and repay one deduplicated counterexample without recursive discovery. |

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

`check_consistency.py` verifies that `references/*.md`, the `SKILL.md` Reference Map, and cross-file mentions stay in sync, that every reference is reachable from the router, and that Delivery-Anchor-first routing, concrete `request_gap` gating, solution/feature ownership separation, current-contract/delta integrity, READY/document-budget, N-ID/SUT-binding, finite anchor-linked TOS, discovery-budget, and `DELIVERY-DONE` stop anchors remain present across stages. Run it before committing changes to `SKILL.md` or `references/`.

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
