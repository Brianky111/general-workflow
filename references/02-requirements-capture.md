# Requirements Capture

## Purpose

Preserve the user's original request and convert it into structured, reviewable requirements without inventing design choices.

## Entry Conditions

- The feature has user intent but lacks `00-原始需求.md` or `00-整理后需求.md`.
- The request is scattered across chat, issue text, screenshots, or existing notes.

Refactor, cleanup, or restructure requests are not requirements — route them to `00-refactor-intake.md` instead. Capture here only the existing behavior a refactor must preserve, when that behavior's feature docs are missing; the feature folder is named after the behavior, never after the refactor.

## Similarity Triage

One requirement owns exactly one feature folder and one document set. Before creating any new folder, scan `docs/requirements-index.md`, the module overviews (`00-模块概述.md`), the goals and numbered scenarios of existing feature `00-整理后需求.md` (or `00-功能.md`) files, and the glossary for features that overlap the incoming request. Place the request on the business hierarchy per `00-business-taxonomy.md`: module-sized requests split first; use-case-sized requests merge.

Classify the relationship:

- **New requirement:** no meaningful overlap in actors, scenarios, or data. Create a new feature folder with its first round, `01-初建`.
- **Merge:** the request belongs inside an existing feature's boundary — same behavior area, would share the contract or modules, a separate folder would duplicate docs — and that feature's requirement is **not yet confirmed**. Append the new words to the active round's `00-原始需求.md` and extend its scenarios; do not create a second folder.
- **Revision:** the request changes or extends a requirement that is **already confirmed** (or a frozen contract). Route to `10-change-protocol.md`, which opens a new change round in that feature; never a second feature folder.

When the classification is uncertain, stop and ask the user with this shape — always list the similarity points and argue each option:

```markdown
### 相似需求裁决【<新请求摘要> vs <现有功能名>】
- 相似点：<共同的角色/场景/数据/术语，逐条列出>
- 差异点：<真正不同的地方>
- A. 合并进 <现有功能>——为什么合并：<同一行为边界/共享合同或模块/分开会重复文档>；后果：<扩展该功能的场景与合同，仍是一套文档>
- B. 作为 <现有功能> 的修正——为什么修正：<改变了已确认的意图/与既有场景矛盾>；后果：<走变更协议，等级 A 或 B，重新过关卡>
- C. 立为新需求——理由：<边界独立/可单独验收>；后果：<新建功能目录，冲突扫描须覆盖与 <现有功能> 的重叠>
- 建议：<A/B/C 及理由>
- 【答复】：
```

This question is a hard stop presented in the conversation — no feature folder exists yet to hold it. When the project keeps `docs/requirements-index.md`, park the pending decision in its holding area so the open question survives the session and later agents can find it.

Record the outcome in `docs/requirements-index.md` (merged into X / revision of X / new feature Y) so later agents can trace the mapping.

Hard rules: never let two document sets describe the same behavior, and never silently rewrite an accepted requirement — merges append, revisions go through the change protocol.

## Actions

1. Copy the original request into `00-原始需求.md`; append rather than rewrite when possible.
2. Draft `00-整理后需求.md` with:
   - the parent module (`所属模块`) at the head, per `00-business-taxonomy.md`,
   - goal and non-goals,
   - actors or users,
   - numbered acceptance scenarios,
   - data or UI terms that need a glossary entry,
   - assumptions separated from confirmed facts.
3. Add numbered acceptance scenarios:
   - `S1`, `S2` for normal paths,
   - `E1`, `E2` for error paths,
   - `B1`, `B2` for boundary cases.
   When the scenario list outgrows one review pass, split use cases into `use-cases/UC<n>-<slug>.md` per `00-business-taxonomy.md`, keeping the roster in `00-整理后需求.md` as the index.
4. Propose standard or lightweight path; read `00-feature-grading-and-splitting.md` if the path or document granularity is unclear.
5. Mark unclear items as questions; do not silently choose product behavior.

## Output

Write concise Chinese requirement docs in the feature's active round, `docs/<module>/<feature>/<round>/`.

## Stop Conditions

Close every draft through `03-requirements-clarification.md` — ask-back alignment is mandatory even when no questions were detected — then route to `03-ambiguity-audit.md` before human confirmation.

Do not write contracts or tests while intent questions remain unresolved.
