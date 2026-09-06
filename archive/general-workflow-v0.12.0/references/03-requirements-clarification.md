# Requirements Clarification

## Purpose

Ask the user only for decisions that materially affect observable behavior or a named high-risk boundary. Clarification is an exception path, not a mandatory closing ritual for every draft.

## Entry Conditions

- Two or more plausible interpretations would produce different user-visible outcomes.
- A choice affects external compatibility, data meaning, security, an irreversible effect, or cross-owner responsibility.
- Raw sources or accepted examples directly contradict one another.

TBD markers about internal naming, code shape, libraries, test placement, or another reversible technical choice do not enter this stage; decide them as implementation choices.

## Blocking Test

Before asking, state which acceptance behavior or risk changes under each answer. If the result, contract, safety, or ownership remains the same, the question is non-blocking: choose the simplest reversible option, record it only if useful, and continue.

Do not ask the user to confirm a faithful restatement of work they already authorized. Do not require per-category proof that there are no questions.

## Actions

1. Batch all currently known blockers into the single allowed pre-code human pause; normally ask no more than three highest-impact questions.
2. For each question, cite the affected acceptance ID or contract boundary, give 2–3 materially different answers and consequences, and recommend one.
3. Ask in the conversation. Persist the question only when work will pause, hand off, or requires audit history; use the one chosen contract/status source rather than copying it across files.
4. After the answer, update only the affected requirement, BDD example, or risk-specific contract clause. Preserve a concise decision record when later code or audit must cite it.
5. Re-run the targeted ambiguity check for the changed clause, then return to the READY check. Do not restart every earlier stage.

## Question Template

```markdown
### Q1【AC/合同边界】<真正阻塞的行为问题>
- A. <可观察结果与后果>
- B. <可观察结果与后果>
- 建议：<选项与理由>
- 【答复】：
```

Use the exact `【答复】：` marker only for a genuinely pending human decision. Do not leave empty markers as template placeholders.

## Output

- No output when no blocking question exists.
- When blocked, one batched question list in the conversation and, only if persistence is needed, in the core contract or one chosen status source.
- After resolution, the smallest affected contract/example update and an optional concise decision ID.

Clarification work counts against the default limit of one human pause and the document/time budget in `00-feature-grading-and-splitting.md`.

## Stop Conditions

Stop only while a real blocking question remains unanswered. Non-blocking uncertainty never prevents planning, tests, or implementation.
