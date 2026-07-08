# Planning

## Purpose

Convert the contract and conflict scan into an implementation plan that preserves test-first discipline.

## Entry Conditions

- Contract exists.
- Conflict scan is complete or explicitly not applicable.
- No actionable implementation plan exists.

## Actions

1. Choose implementation strategy for each module: reuse, extend, modify, refactor, or create.
   - from scratch,
   - modify existing code,
   - reuse and extend,
   - refactor before implementing,
   - strangler/side-by-side replacement.
2. Define validation strength:
   - standard: normal unit/integration coverage,
   - enhanced: boundary/property/regression coverage,
   - adversarial: fuzzing, mutation, or external-protocol probes.
3. Identify test files to add before implementation.
4. List expected evidence: commands, screenshots, CI, probes, or logs.
5. Keep the plan small enough for one agent to execute or split by module.

## Required Tables

Consume every `C` conflict ID:

```markdown
| 冲突编号 | 处理方式 | 涉及代码 | 保留什么 | 替换/新增什么 | 测试覆盖 | 风险与回滚 |
|---|---|---|---|---|---|---|
| C1 | 修改现有代码 / 复用扩展 / 从零实现 / 延后并说明原因 | `<路径>` | <旧行为> | <目标改动> | S1/E1/P1 | <说明> |
```

Map every method to a layer/module, then walk one numbered scenario through the layers. If layer boundaries need to change, route to `10-change-protocol.md` as a level-A change.

## Validation Strength Triggers

Read `00-feature-grading-and-splitting.md` for feature-level path. At module level, choose at least enhanced validation if any trigger applies:

- three or more freely combinable input parameters,
- high-cost or irreversible decisions,
- external input parsing or protocol adaptation,
- state machine or concurrency logic.

## Output

Create or update `docs/features/<feature>/02-规划.md`.

## Stop Conditions

Stop if the plan requires scope expansion, architectural tradeoffs, or contract changes.
