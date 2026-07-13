# Status and Evidence

## Purpose

Keep handoff state synchronized with real evidence. Status files help navigation but are not the source of truth.

## Entry Conditions

- Router evidence conflicts.
- User asks whether the requirement matches their expectations, how far the work has progressed, or what is still missing.
- Work is being handed off between agents.
- Progress/status files are missing or stale.

## Document Set Checklist

One change round owns one numbered document set; the checklist applies to the feature's active round, and archived rounds hold completed sets. The numbers are the user's dashboard: each document answers one question the user cares about, and the missing ones are exactly "还差哪些". Report progress against this checklist, not from memory.

| Document | Produced by | Answers for the user | Done when |
|---|---|---|---|
| `00-项目识别.md` | Project identification | 这是新项目还是改旧项目，判断有没有依据 | Four fixed sections filled |
| `00-原始需求.md` | Requirements capture | 我的原话有没有被完整封存、未被改写 | Raw words preserved, append-only |
| `00-整理后需求.md` (+ `use-cases/*.md` after splitting) | Capture + clarification | 需求是否符合我的预期（编号场景 = 我的意图） | Questions answered, user confirmed, `requirementsConfirmedAt` set |
| `01-接口.md` / `interfaces/*.md` | Interface contract | 行为合同是不是我要的行为 | Ambiguity audit attached, user approved, `contractsFrozenAt` set |
| `01-代码冲突与重叠.md` / `conflicts/*.md` | Conflict scan (old projects) | 与现有代码的冲突讲清楚了没有 | `## 总结` filled, every C-ID concrete |
| `fixtures/` | Probes | 外部数据是真的还是编的 | Contract examples trace to probe captures |
| `02-规划.md` | Planning | 怎么实现、冲突怎么处理、验证多严 | Every C-ID consumed, user approved the plan gate |
| tests + implementation | Red tests + implementation | 做出来的东西有没有证据 | Red-then-green evidence in CI |
| review + integration reports | Module review + acceptance | 有没有人独立查过、整体跑通没有 | Reports with evidence, scenarios green, human-eye pass |
| `99-进度.md` + `status.json` | Every stage | 进度如何、还差哪些、卡在哪 | Mirrors the rows above with evidence links |

Lightweight features merge the requirement, contract, and plan rows into sections of `00-功能.md`; the questions and done-criteria stay the same.

When reporting, list each row as present / in progress / missing, name the next unpassed gate, and mirror the missing list in `99-进度.md`.

## Actions

1. Compare status docs with repository facts: files, commits, tests, PRs, and CI.
2. Mark each stage as not started, in progress, blocked, or complete.
3. For every complete claim, attach evidence: path, command, commit, PR, CI link, screenshot, or log summary.
4. Remove or correct unsupported claims.
5. Record blockers as concrete next decisions or commands.

## File Shapes

State files must not contain secrets, account credentials, tokens, or full sensitive external responses; only paths, commits, PR/CI links, short summaries, and shareable status.

`docs/workflow-state.json` minimum fields:

```json
{
  "schema": 1,
  "mode": "blueprint|incremental",
  "currentGate": "kickoff|identification|requirements|interfaces|planning|implementation|review|integration|done|blocked",
  "inScopeFeatures": ["<功能名>"],
  "lastApprovedRef": "<main-sha-or-approved-tag>",
  "pendingQuestions": 0
}
```

`docs/<module>/<feature>/status.json` minimum fields (feature level, spans rounds):

```json
{
  "schema": 1,
  "feature": "<功能名>",
  "activeRound": "<NN>-<round>，无进行中轮次则为空",
  "projectType": "new|existing|new-module-in-existing",
  "phase": "identification|requirements|interfaces|planning|red|green|review|integration|done|blocked",
  "gate": "open|waiting-human|approved|blocked",
  "pendingQuestions": 0,
  "requirementsConfirmedAt": "<pr-or-tag-or-main-sha>",
  "contractsFrozenAt": "<pr-or-tag-or-main-sha>",
  "conflictReport": "01-代码冲突与重叠.md",
  "modules": {
    "<模块名>": {
      "owner": "<agent-id-or-branch>",
      "status": "todo|red|green|review|done|blocked",
      "contract": "01-接口.md#<模块名>",
      "redEvidence": "<ci-run-or-commit>",
      "greenEvidence": "<ci-run-or-commit>",
      "reviewer": "<agent-id, optional until review>",
      "reviewEvidence": "<report-path-or-ci, optional until review>",
      "next": "<下一步一句话>"
    }
  }
}
```

`99-进度.md` opens with a feature-level summary, then one fixed-shape section per module:

```markdown
## 全局
- 阶段：<当前阶段>
- 文档集缺失：<对照文档集清单列出，无则写“无”>
- 阻塞：<待确认反问 / 外部依赖 / 无>
- 下一步：<一句话>

## <模块名>
- 状态：todo / red / green / review / done / blocked
- 负责人：<agent-id 或分支名>
- 合同：<01-接口.md#锚点 或 interfaces/<模块名>.md>
- 红证据：<CI 链接或 commit；无则写“无”>
- 绿证据：<CI 链接或 commit；无则写“无”>
- 审查：<初审报告或 CI 链接；无则写“无”>
- 阻塞：<待确认反问 / 失败测试 / 外部依赖 / 无>
- 下一步：<一句话>
```

## Consistency Rules

- `pendingQuestions` must equal unresolved `【答复】：` entries.
- `requirementsConfirmedAt` and `contractsFrozenAt` must point to a PR, commit, or approval tag; free-text “confirmed” is not evidence.
- Existing projects must have a conflict report with concrete scan conclusions.
- A module cannot be `done` without contract reference, red evidence, green evidence, and `reviewEvidence` pointing to a review report or CI run.
- `reviewer`, when present, must differ from the module's `owner`: the reviewer is never the implementer.
- `activeRound`, when set, must point to an existing round directory; archived rounds are read-only history — corrections open a new round.
- Status may lag behind reality, but it must not run ahead of evidence.
- Parallel agents edit only their own module section of `99-进度.md`; cross-module status writes must preserve other modules' fields.

## Output

Update `docs/workflow-state.json`, `docs/<module>/<feature>/status.json`, or the active round's `99-进度.md` if the target project uses them; create them from the shapes above when the project adopted this workflow but the files are missing.

## Stop Conditions

Stop if no reliable evidence exists for the claimed stage; report the uncertainty and the safest next verification step.
