# Requirements Clarification

## Purpose

Expose ambiguity before contracts or implementation begin.

## Entry Conditions

- `00-整理后需求.md` contains assumptions, TBD markers, contradictory scenarios, or user-facing behavior that is not decided.

## Actions

1. Group questions by scenario, field, or workflow step.
2. Ask only intent-level questions; do not outsource implementation design to the user.
3. For each question, explain the risk of leaving it unresolved.
4. For each question, provide 2-3 candidate answers, consequences, and one recommendation.
5. Record answers in a decision log with date/source.
6. Update structured requirements after answers arrive.

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

- pending questions,
- decision records,
- revised acceptance scenarios.

## Stop Conditions

Do not proceed to interface contracts while required intent questions remain unanswered.
