# BDD Example Mapping

## Purpose

Turn structured requirements into shared, concrete behavior examples before interface design. BDD decides what observable behavior means; TDD later decides how to implement and prove it.

## Contents

- Position and Three Lenses
- Actions and artifact shape
- BDD Gate
- Output and stop conditions

## Entry Conditions

- `00-整理后需求.md` has a goal, actors, and an initial `S/E/B` scenario roster.
- The standard path lacks `00-行为示例.md`, or requirement answers made it stale.
- A level-A change alters a rule, example, actor outcome, or failure bottom line.

Lightweight features keep a minimal `## BDD 行为示例` section inside `00-功能.md`. Pure refactors and level-B/C work reuse accepted examples unless they expose a behavior gap.

## Position in the Workflow

```text
Requirements Capture
→ BDD Example Mapping
→ Requirements Clarification
→ refresh stale examples
→ Ambiguity Audit
→ human requirement/behavior confirmation
→ Interface Contract
```

## Three Lenses

Evaluate every map through three explicit lenses:

- **Business/user:** goal, rule, value, and observable outcome.
- **Development/system:** state, trigger, ownership boundary, and feasibility questions without choosing implementation.
- **Test/risk:** counterexamples, forbidden side effects, boundaries, permissions, concurrency, recovery, and ambiguity.

When three people are unavailable, perform three labeled passes. The user still owns product behavior decisions; the agent owns technical choices after behavior is settled.

## Actions

1. Restate the Feature goal and actors; do not introduce behavior absent from raw requirements or recorded decisions.
2. Extract rules as `R1`, `R2`... Each rule states one observable business truth and cites source `S/E/B/D` IDs.
3. Add concrete examples as `EX1`, `EX2`... under each rule. Use Given/When/Then:
   - **Given:** relevant preconditions and state, never an action sequence.
   - **When:** one business trigger or user action.
   - **Then:** observable outcome, including persistence or downstream results when relevant.
   - **And / failure bottom line:** required side effects and effects that must not occur.
4. Cover only applicable categories, but never omit one silently: normal, alternative, error, boundary, permission, illegal state, duplicate/concurrent, dependency failure, retry/recovery, refresh/persistence, UI state, and cross-feature event outcomes.
5. Capture unknown behavior in `## 待确认反问` using the existing question template and exact `【答复】：` marker. Do not hide a question inside an example.
6. Maintain a trace table from every requirement scenario to its rule/example IDs and back. One scenario may need several examples; every example must cite its source.
7. Keep examples technology-neutral. Do not mention controllers, SQL, React state, selectors, queues, class names, or mock calls unless the technology itself is user-visible behavior.
8. Use Markdown examples by default. Generate `.feature` files only when kickoff selected an executable BDD runner; the Markdown map remains the reviewed source or a generated/index view, never a competing truth.

## Artifact Shape

```markdown
# Feature：<功能名> 行为示例

## Example Map
| Rule | 业务规则 | 来源 | Examples | Questions | 状态 |
|---|---|---|---|---|---|
| R1 | <可观察规则> | S1 / E1 / D1 | EX1, EX2 | Q1 | draft |

## R1：<规则名>

### EX1：<正常或代表性示例>
- Given：<相关前置状态>
- And：<补充状态，可选>
- When：<一个业务动作>
- Then：<主要可观察结果>
- And：<持久化、UI 或下游结果，可选>
- 失败底线：<不得发生的副作用；成功示例可写 N/A>
- 来源：S1 / D1
- 后续追踪：合同待定；测试矩阵待定

## 场景追踪
| Requirement scenario | Rule / Examples | 覆盖结论 |
|---|---|---|
| S1 | R1 / EX1 | covered |

## 待确认反问
### Q1【R1/EX2】<行为问题>
- A. <答案与后果>
- B. <答案与后果>
- 建议：<选项与理由>
- 【答复】：

## 决策记录
```

For large features, keep `00-行为示例.md` as the Rule/Example index and place detailed examples in the owning `use-cases/UC<n>-<slug>.md`; never define the same example twice.

## BDD Gate

The map is ready for ambiguity audit only when:

- every accepted `S/E/B` scenario maps to at least one `R/EX` and every example traces back;
- rules are observable and examples use concrete data or state, not vague adjectives;
- applicable failure, permission, boundary, concurrency, recovery, persistence, UI, and cross-feature categories are covered or explicitly `N/A` with a reason;
- failure examples name forbidden side effects;
- Given/When/Then contains no hidden implementation design;
- contradictions are resolved and `## 待确认反问` is empty.

After `03-ambiguity-audit.md` passes, the user confirms the requirement scenario roster and behavior examples together. Record that approval as `behaviorExamplesConfirmedAt`; it freezes the accepted `R/EX` behavior before interface design.

## Output

Create or update `docs/<module>/<feature>/<round>/00-行为示例.md`, or the named lightweight section. Route through `03-requirements-clarification.md`; if answers change a rule/example, refresh this map, then run `03-ambiguity-audit.md` and the combined human requirement/behavior gate.

## Stop Conditions

Do not write interface contracts while a behavior question, contradiction, unmapped scenario, failed audit, or unapproved example remains. Do not turn a technical implementation preference into a business rule.
