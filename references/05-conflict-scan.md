# Code Reality, Reuse, and Conflict Scan

## Purpose

Bind the compact contract to the code and test paths that the running system actually uses. Find reuse and real conflicts before planning; do not create a report merely because the repository already exists.

## Entry Conditions

- Existing code may already own or partially implement the behavior.
- Planning does not yet name the current production owner, real runtime path, nearest existing test home, and reuse assets.

## Actions

1. Search for existing routes, components, services, models, tests, and docs related to the feature. Record the searched code homes and queries; "nothing reusable found" without reproducible search evidence is not a result.
2. Compare existing behavior against the contract.
3. For each real finding, record the difference between current and target behavior and select the smallest reversible handling when evidence makes it clear. Carry a material behavior/compatibility choice to `06-planning.md` or the user; do not manufacture 2-3 candidates only to defer an ordinary internal decision.
4. Check at least:
   - public APIs, commands, events, routes, components, and config entries,
   - data models, persistence, cache, serialization formats,
   - frontend stores/query caches, runtime schemas, generated clients, and page state handling,
   - user flows, errors, state machines, permissions, feature flags,
   - cross-feature calls, event handlers, ownership boundaries, and duplicate/idempotent processing,
   - external adapters, protocols, fixtures, and test doubles,
   - similar historical features.
5. Note migration risks, compatibility risks, and duplicated concepts.
6. Assign a stable `N-ID` to every relevant production topology node and keep that ID through planning, tests, implementation, and review. Record the current production owner, the real runtime/assembly entry, non-test incoming edges, and whether the node is existing, proposed-new, or proposed-replacement.
7. For each target responsibility, name the nearest existing implementation, test home, runner, fixtures/factories, and other reuse assets. Existing-code work defaults to modifying or extending the existing owner; collect concrete reuse rejection evidence before proposing `NEW` or `REPLACEMENT`.
8. Produce a code topology sketch for the feature slice: entry points, state owners, shared contracts/schemas, adapters, persistence, cross-feature calls, and test seams. Mark which nodes are in scope, read-only context, or out of scope.
9. For a proposed `NEW` or `REPLACEMENT`, identify its planned non-test incoming edge and wiring verification. For side-by-side replacement, also identify the runtime selection point and retirement condition; unresolved fields are `GAP` and block planning.
10. If the scan finds unrelated bugs, failing tests, dead code, or design smells, do not turn them into work. Record them as out-of-scope findings unless they contradict or block the accepted contract.

## Output

For ordinary work, put the `N-ID` reuse map directly in the minimum executable plan from `06-planning.md` or the current handoff. Create `01-代码冲突与重叠.md` or a focused conflict appendix only when there is a concrete legacy conflict, uncertain migration/cutover, independent owner handoff, or formal traceability need. No conflict means a concise scan result, not an empty report.

Use one minimum reuse map:

```markdown
| N-ID | Production owner / kind | 真实运行/装配入口与非测试入边 | 最近既有测试归宿/复用资产 | 匹配点/缺口/搜索证据 | 计划动作与作用域 |
|---|---|---|---|---|---|
| N1 | `<symbol>` / EXISTING, NEW, or REPLACEMENT | `<route/DI/root -> owner>` | `<test>` + runner/fixture/helper | <可复用什么；为何不足> | MODIFY/EXTEND/NEW/REPLACE；可改/只读/不碰 |
```

For a real conflict, append one selected-resolution row. `NEW`/`REPLACEMENT` records 复用否决证据 and a non-test edge/wiring check; side-by-side records its 选择点和退场条件:

```markdown
| C-ID | Acceptance / N-ID | Current -> target | Selected handling and reuse evidence | Runtime/wiring or cutover evidence | Risk/rollback |
|---|---|---|---|---|---|
| C1 | AC1 / N1 | <差异> | <修改/复用/替换及证据> | <真实入口验证；side-by-side 切换/退场> | <风险/回滚> |
```

Add an OOS row only for an actual neighboring finding:

```markdown
| OOS ID | Finding | Why outside this contract | Blocks current evidence? | Follow-up |
|---|---|---|---|---|
| OOS1 | <bug/failure/smell> | <scope reason> | yes/no | <issue/handoff> |
```

## Hard Rules

- Repository age alone never requires a conflict report; the code-reality/reuse evidence may live in the executable plan.
- Every conflict item must point at concrete code locations.
- Never recycle an `N-ID`; later artifacts must reference the same ID for the same production responsibility.
- Planning must not start for existing-code work until the topology section names the intended write paths, current production owner and entry, nearest existing test home/reuse assets, and important read-only/out-of-scope neighbors.
- Existing-code work defaults to modifying or extending the existing owner. `NEW` or `REPLACEMENT` is not plan-ready without reuse rejection evidence, a planned non-test incoming edge, and wiring verification; side-by-side work additionally requires a selection point and retirement condition.
- Do not introduce a parallel SUT, runner, harness, fixture system, or helper library merely to manufacture a red test. Treat unavoidable new test infrastructure as a conflict that needs evidence and an explicit executable-plan decision.
- Conflicts discovered later must update the owning reuse map or focused appendix before planning consumes them; do not create a new document solely for synchronization.
- Out-of-scope findings are not implementation permission. They need a user request, accepted change proposal, or proof that they directly block current evidence.

## Stop Conditions

Stop if an existing behavior conflict requires changing the accepted contract or product intent, or if a proposed `NEW`/`REPLACEMENT` lacks reuse rejection evidence, a non-test incoming edge, wiring verification, or required side-by-side selection and retirement conditions.
