# Requirements Clarification

## Purpose

Expose ambiguity before contracts or implementation begin.

## Entry Conditions

- `00-整理后需求.md` contains assumptions, TBD markers, contradictory scenarios, or user-facing behavior that is not decided.
- A requirement or contract draft is being closed out. Ask-back alignment is a mandatory closing step for every draft, not a fallback for detected problems: declaring "no questions" requires per-category self-proof (normal/error/boundary scenarios, field meanings, failure semantics — why each has nothing left to ask), which the user may reject.

## Actions

1. Write questions into the `## 待确认反问` section of `00-整理后需求.md`, numbered Q1, Q2..., ordered by how blocking they are, grouped by scenario, field, or workflow step.
2. Ask only intent-level questions; do not outsource implementation design to the user. Technical choices are the agent's, recorded in `## 决策记录`.
3. For each question, explain the risk of leaving it unresolved.
4. For each question, provide 2-3 candidate answers, consequences, and one recommendation.
5. After answers arrive, write them back into the body, then move each answered question with its conclusion into the `## 决策记录` section (with date/source) so later agents and the change protocol can cite it.
6. If an answer creates new scenarios, add them to the numbered S/E/B lists.

## Question Template

```markdown
### Q1【场景/字段编号】〈一句话点出模糊点〉
- A. 〈候选答案〉——〈后果〉
- B. 〈候选答案〉——〈后果〉
- 建议：〈A 或 B〉——〈理由〉
- 【答复】：
```

## Hard Stop

After writing a pending-question list, stop the current run. Do not continue to interface, planning, tests, or implementation until answers are recorded and the pending list is cleared.

## Output

Update `00-整理后需求.md` with:

- the `## 待确认反问` section (pending questions with the `【答复】：` marker; consistency checks count unresolved `【答复】：` entries, so keep the marker exact),
- the `## 决策记录` section (answered questions and agent-made technical decisions),
- revised acceptance scenarios.

## Stop Conditions

Do not proceed to interface contracts while required intent questions remain unanswered.
