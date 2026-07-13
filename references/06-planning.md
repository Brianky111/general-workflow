# Planning

## Purpose

Convert the contract and conflict scan into an implementation plan that preserves test-first discipline.

## Entry Conditions

- Contract exists.
- Conflict scan is complete or explicitly not applicable.
- No actionable implementation plan exists.

## Actions

1. Re-read accepted requirements, contracts, conflict scan, and status evidence before choosing strategy. Do not plan from code shape alone.
2. If any module might need refactor, or the user asked for refactor/cleanup/rewrite/restructure/simplification, read `00-refactor-intake.md` and add the refactor preflight before coding.
3. Choose the implementation strategy for each module, with stated reasons:
   - from scratch,
   - modify existing code,
   - reuse and extend,
   - refactor before implementing,
   - strangler/side-by-side replacement.
4. Assign each module a track, then a tier for red/green modules. The agent proposes tier and reasons; the user confirms or overrides at the planning gate:
   - **Visual track:** pure presentation (layout, styling, interaction feel). No filler snapshot tests; deliver screenshots or previews, pass human-eye acceptance at integration, then record the visual regression baseline.
   - **Red/green standard tier:** example-based red/green tests covering numbered S/E/B scenarios.
   - **Red/green enhanced tier:** standard, plus property tests targeting `P` invariants, plus a pairwise combination table (PICT-style generation from the parameter matrix, covering all two-parameter interactions).
   - **Red/green adversarial tier:** enhanced, plus an independent attack agent that reads only the contract, never the implementation (three-way independence between test writer, implementer, and attacker), plus a mutation-testing pass threshold.
5. Identify test files to add before implementation.
6. List expected evidence: commands, screenshots, CI, probes, or logs.
7. If local subagent tools are available and the work is non-trivial, read `00-orchestration-policy.md` and design executor scopes. The main thread remains the orchestrator and must not implement a scope assigned to an executor.

## Required Tables

Consume every `C` conflict ID:

```markdown
| 冲突编号 | 处理方式 | 涉及代码 | 保留什么 | 替换/新增什么 | 测试覆盖 | 风险与回滚 |
|---|---|---|---|---|---|---|
| C1 | 修改现有代码 / 复用扩展 / 从零实现 / 延后并说明原因 | `<路径>` | <旧行为> | <目标改动> | S1/E1/P1 | <说明> |
```

Map every method to a layer/module and to its concrete path inside the feature's code home (the template recorded in `architecture.md`; see `00-business-taxonomy.md`), then walk one numbered scenario through the layers. If layer boundaries need to change, route to `10-change-protocol.md` as a level-A change.

When orchestration is used, include an executor split table:

```markdown
| Executor role | Module or scope | May edit | Must not edit | Required evidence | Handoff/status location |
|---|---|---|---|---|---|
| <role> | <module> | <paths> | <paths/contracts/tests> | <commands/report> | `99-进度.md#...` |
```

If the main thread executes a non-trivial plan directly, record why delegation is unavailable, unsafe, or lower value than direct execution.

## Validation Strength Triggers

Read `00-feature-grading-and-splitting.md` for feature-level path. At module level, choose at least enhanced validation if any trigger applies:

- three or more freely combinable input parameters,
- high-cost or irreversible decisions,
- external input parsing or protocol adaptation,
- state machine or concurrency logic.

## Output

Create or update the active round's `docs/<module>/<feature>/<round>/02-规划.md` (or the plan section of `00-功能.md` for lightweight features), written in Chinese.

## Planning Gate

The plan is a document-PR human gate. After the plan doc is complete, stop and ask the user to review the conflict-handling table, implementation strategy decisions, layer walkthrough, and track/tier assignments. Do not write tests or implementation in the same run.

The gate also checks decision coverage: every `D` decision recorded in the requirement and contract docs must be traceable to a contract clause or a plan item. An unconsumed behavior-affecting decision pushes the plan back, the same way an unconsumed `C` conflict ID does.

For lightweight features this gate merges with the contract gate into the single `00-功能.md` document-PR review; do not run a second human pass.

Once approved, the plan freezes. Generate code stubs from the frozen contracts for new methods and modules only (signatures plus Chinese comments plus `throw new Error('尚未实现')`); never overwrite existing implementations. CI compares doc and stub signatures. Then route to `07-red-tests.md`; batches classified as pure refactor by `00-refactor-intake.md` route to `08-implementation.md` instead. Modules may now be implemented in parallel by executors.

## Stop Conditions

Stop if requirements/contracts cannot be recertified, if the plan requires scope expansion, architectural tradeoffs, or contract changes, and always at the planning gate before any test or implementation work.
