# Status and Evidence

## Purpose

Keep handoff state synchronized with real evidence. Status files help navigation but are not the source of truth.

## Entry Conditions

- Router evidence conflicts.
- User asks what remains.
- Work is being handed off between agents.
- Progress/status files are missing or stale.

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

`docs/features/<feature>/status.json` minimum fields:

```json
{
  "schema": 1,
  "feature": "<功能名>",
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
      "next": "<下一步一句话>"
    }
  }
}
```

`99-进度.md` fixed shape per module section:

```markdown
## <模块名>
- 状态：todo / red / green / review / done / blocked
- 负责人：<agent-id 或分支名>
- 合同：<01-接口.md#锚点 或 interfaces/<模块名>.md>
- 红证据：<CI 链接或 commit；无则写“无”>
- 绿证据：<CI 链接或 commit；无则写“无”>
- 阻塞：<待确认反问 / 失败测试 / 外部依赖 / 无>
- 下一步：<一句话>
```

## Consistency Rules

- `pendingQuestions` must equal unresolved `【答复】：` entries.
- `requirementsConfirmedAt` and `contractsFrozenAt` must point to a PR, commit, or approval tag; free-text “confirmed” is not evidence.
- Existing projects must have a conflict report with concrete scan conclusions.
- A module cannot be `done` without contract reference, red evidence, green evidence, and review/integration evidence.
- Status may lag behind reality, but it must not run ahead of evidence.
- Parallel agents edit only their own module section of `99-进度.md`; cross-module status writes must preserve other modules' fields.

## Output

Update `docs/workflow-state.json`, `docs/features/<feature>/status.json`, or `99-进度.md` if the target project uses them; create them from the shapes above when the project adopted this workflow but the files are missing.

## Stop Conditions

Stop if no reliable evidence exists for the claimed stage; report the uncertainty and the safest next verification step.
