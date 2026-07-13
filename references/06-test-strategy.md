# Test Strategy and Feature Test Matrix

## Purpose

Prove that each requirement is protected at the cheapest trustworthy layer and that the assembled vertical feature works. Use the Feature Test Matrix as the feature-level coverage map; passing unit tests or reporting a coverage percentage alone never proves completeness.

## Contents

- Confidence Ladder
- Feature Test Matrix templates
- Build Procedure
- Matrix Gate and output

## Entry Conditions

- The behavior contract and conflict scan exist.
- A plan draft exists or test scope must be decided before the planning gate.
- `02-测试矩阵.md` is missing, stale, or does not include frontend, contract, cross-feature, or assembly risks that apply.

## Confidence Ladder

Choose only the layers needed for the risk; do not duplicate every scenario at every layer.

| Layer | Primary question |
|---|---|
| Static checks | Does it compile, type-check, lint, and respect layer boundaries? |
| Domain unit | Is one business rule, value object, calculation, or state transition legal? |
| Use-case unit | Is the flow ordered correctly, with the right result and side effects? |
| Frontend logic/component/page | Does the UI expose the right states and respond as a user would expect? |
| Adapter/repository integration | Do persistence, mappers, SDK adapters, and real schemas agree? |
| Contract | Do producer and consumer agree on fields, units, casing, enums, errors, and events? |
| Feature integration | Do this feature's UI/client/application/domain/adapter modules run together correctly? |
| Cross-feature workflow | Do owned events and downstream effects connect without hidden database coupling? |
| E2E acceptance | Can a user complete the critical path through real UI/API/persistence and still see truth after reload? |
| Risk checks | Do adversarial, security, concurrency, performance, accessibility, and visual checks cover the selected risks? |

## Feature Test Matrix

Treat `02-测试矩阵.md` as a feature-level artifact, not a list of test filenames. It contains two linked tables:

1. **Coverage view:** one row per acceptance scenario or invariant, showing which test layer protects it.
2. **Evidence register:** one row per test ID, showing where and how that test runs and where its evidence lives.

### Cell notation

- `P:T-UC-S1` — planned test with a stable test ID.
- `PASS:T-UC-S1@<evidence>` — executed test with evidence.
- `N/A:<reason>` — the layer is intentionally not needed.
- `GAP:<reason>` — required coverage is missing and blocks the planning or completion gate.

Never use a bare checkmark: it cannot identify the test or prove that it ran. Never leave a cell blank.

### Coverage view template

```markdown
| 场景/不变量 | 用户可见结果与失败底线 | 风险标签 | Domain | Use Case | 前端 | Adapter/Repository | 契约 | Feature 集成 | 跨 Feature | E2E | 对抗/非功能 | 总状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 正常提交 | 显示成功；刷新后仍正确 | UI, 契约, 持久化 | P:T-D-S1 | P:T-UC-S1 | P:T-FE-S1 | P:T-DB-S1 | P:T-CT-S1 | P:T-INT-S1 | N/A:无下游 | P:T-E2E-S1 | N/A:普通风险 | planned |
| E1 非法状态 | 明确拒绝；不得写库或调用外部依赖 | 状态, 副作用 | P:T-D-E1 | P:T-UC-E1 | P:T-FE-E1 | N/A:调用前拒绝 | P:T-CT-E1 | P:T-INT-E1 | N/A:无事件 | N/A:边界下沉 | P:T-MUT-E1 | planned |
| E2 依赖超时 | 显示可重试错误；不得报告成功 | 依赖故障, 恢复 | N/A:无领域规则 | P:T-UC-E2 | P:T-FE-E2 | P:T-AD-E2 | P:T-CT-E2 | P:T-INT-E2 | N/A:无完成事件 | N/A:Feature 集成覆盖 | P:T-FAULT-E2 | planned |
| B1 重复提交 | 只产生一次业务结果 | 并发, 幂等 | P:T-D-B1 | P:T-UC-B1 | P:T-FE-B1 | P:T-DB-B1 | P:T-CT-B1 | P:T-INT-B1 | N/A:无下游 | P:T-E2E-B1 | P:T-CONC-B1 | planned |
| S2 完成后更新关联功能 | 下游最终状态正确且重复事件无副作用 | 跨功能, 事件, 幂等 | P:T-EVT-S2 | P:T-PUB-S2 | P:T-FE-S2 | P:T-OUTBOX-S2 | P:T-EVENT-S2 | P:T-INT-S2 | P:T-XF-S2 | P:T-E2E-S2 | P:T-DUP-S2 | planned |
```

The example is structural. Replace its generic behaviors and test IDs with the feature's accepted `S/E/B/P` roster. Do not copy layers that are genuinely absent; use an explained `N/A`.

### Evidence register template

```markdown
| 测试 ID | 覆盖场景 | 类型/层级 | 测试文件 | 命令与环境 | Fixture/seed | 关键断言 | 负责人 | 状态与证据 |
|---|---|---|---|---|---|---|---|---|
| T-UC-S1 | S1 | Use Case unit | `<path>` | `<command>` | `<factory/fake>` | 结果正确；保存一次 | `<owner>` | planned |
| T-E2E-S1 | S1 | Browser E2E | `<path>` | `<command + env>` | `<seed>` | 成功后刷新仍正确 | `<owner>` | planned |
```

## Build Procedure

1. Create one coverage row for every numbered acceptance scenario and invariant. Include applicable tags such as `权限`, `状态`, `并发/幂等`, `依赖故障`, `恢复`, `UI`, and `跨功能`.
2. Write the user-visible result and failure bottom line before assigning tests. Failure rows must name forbidden side effects, not only the expected error.
3. Assign the lowest layer that can prove the rule precisely, then add a higher layer only when a connection itself can fail.
4. Give every planned test a stable ID and add it to the evidence register. One test may cover multiple rows, but every relationship remains explicit.
5. Require at least one feature-integration check for every vertical feature. Shared frontend/backend schemas require contract coverage; multi-feature events require cross-feature workflow checks; user-critical paths require E2E.
6. Keep detailed boundaries low in the pyramid and only representative critical paths in E2E. Use `N/A:<reason>` instead of duplicating a case at every layer.
7. For UI scope, cover applicable loading, empty, success, validation, permission, network/server error, retry, disabled/in-flight, and duplicate-submit states. Separate behavior, accessibility, and visual evidence.
8. For use cases, verify query/input, result, required side effects, and absence of forbidden side effects on failure. Assert call order only when order changes correctness.
9. Prefer a Fake for reusable stateful collaborators, a Stub for a fixed response, and a Mock/spy only for an important interaction.
10. Select adversarial checks by risk: malformed input, authorization bypass, illegal transition, timeout/unknown response, duplicate callback, concurrency/idempotency, property tests, mutation tests, security, performance, accessibility, and visual regression.

## Matrix Gate

The matrix is ready for planning approval only when:

- every accepted scenario/invariant has exactly one coverage row;
- every row has a precise rule layer or an explained reason why only assembly behavior exists;
- every connection risk has contract, adapter, cross-feature, integration, or E2E coverage;
- every user-critical flow has E2E acceptance;
- every failure row proves forbidden side effects remain absent;
- every planned test ID exists in the evidence register with path, command/environment, owner, and key assertion;
- no cell is blank and no `GAP` remains.

Planning freezes required coverage and ownership, not evidence cells. During TDD and verification, update `P:` to `PASS:` plus evidence. Adding stronger coverage is allowed; weakening required coverage reopens the planning/change gate.

## Output

Create or update `docs/<module>/<feature>/<round>/02-测试矩阵.md` with the coverage view and evidence register. Lightweight features may keep both tables as clearly named sections of `00-功能.md`; the coverage questions do not weaken. Link each row to requirement IDs, contract clauses, plan batches, and later evidence.

Return to `06-planning.md` for the planning gate after the matrix is complete.

## Stop Conditions

Do not approve the plan while the Matrix Gate fails. Do not mark the feature complete while a required cell is still `P:`, `GAP`, blank, or backed only by an unsupported checkmark.
