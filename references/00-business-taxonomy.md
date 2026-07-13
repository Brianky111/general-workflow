# Business Taxonomy and Code Layout

## Purpose

Arrange requirements physically along the business hierarchy — product, module, feature, use case, sub-feature, task — and give every feature exactly one code home. Each add/remove/modify round on a feature gets its own numbered document set, archived on completion, so the feature's history stays navigable and the active work is always one directory.

## Canonical Layout

```text
docs/
├── architecture.md                  # 产品级：层级地图、代码归宿模板
├── glossary.md
├── domain-models.md
├── requirements-index.md            # 产品级总控台，按模块分节
└── <module>/                        # 大功能模块（目录内有 00-模块概述.md 即为模块目录）
    ├── 00-模块概述.md                # 模块职责、功能清单、跨功能共享决策
    └── <feature>/                   # 功能特性
        ├── status.json              # 功能级：activeRound、最新冻结引用、模块状态
        ├── fixtures/                # 功能级、跨轮共享：contract / counterexamples / generated
        ├── <NN>-<round>/            # 变更轮：01-初建、02-<变更slug>…（进行中的一轮）
        │   ├── 00-项目识别.md
        │   ├── 00-原始需求.md
        │   ├── 00-整理后需求.md      # 用例索引：编号场景清单
        │   ├── use-cases/           # 使用场景（触发拆分后，每用例一档）
        │   ├── 01-接口.md            # 子功能索引（每轮为完整合同，非增量）
        │   ├── interfaces/<sub>.md  # 子功能合同
        │   ├── 01-代码冲突与重叠.md
        │   ├── conflicts/<sub>.md
        │   ├── 02-规划.md            # 任务在此定义为红绿批次
        │   └── 99-进度.md            # 任务级进度：模块小节
        └── archive/
            └── <NN>-<round>/        # 验收通过后整轮移入
```

Path convention: round documents are written as `docs/<module>/<feature>/<round>/...` throughout these references, where `<round>` always means the feature's **active round**. `fixtures/` and `status.json` sit at feature level across rounds. Single-module or tiny projects may flatten the module level; set thresholds at kickoff.

## Change Rounds

- Every add/remove/modify of a feature opens a new round directory `<NN>-<round>` (two-digit sequence plus a short slug; the first is `01-初建`) holding its own numbered doc set. One round, one doc set — the one-requirement-one-doc-set instinct applied per change.
- Rounds apply to requirement/contract-level work: the initial build, level-A changes, and similarity-triage revisions. Level B (bug fix / counterexample repayment) and level C (display tweaks) stay inside the active round — or, when no round is active, record into feature-level `fixtures/counterexamples/` and `status.json` without opening one.
- Each round's `01-接口.md` is the **complete** contract after the change, never a delta: the newest archived round always holds the feature's current truth. A new round starts by copying the previous round's contract forward and revising it under the change protocol.
- On integration acceptance (terminal state), move the round directory into `archive/` and update `status.json`'s `activeRound` to empty. Archived rounds are read-only history; corrections open a new round.
- `fixtures/` never moves with a round: counterexamples are append-only permanent regression assets, and tests reference their paths across rounds.

## Level-by-Level Mapping

| Level | Physical form | Home |
|---|---|---|
| 产品 / 系统 Product | repo-level docs | `architecture.md`, `requirements-index.md`, `glossary.md`, `domain-models.md` |
| 大功能模块 Module | **directory** | `docs/<module>/` with `00-模块概述.md`; one roster section in `requirements-index.md` |
| 功能特性 Feature | **directory** | `docs/<module>/<feature>/` — feature-level `status.json` and `fixtures/`, plus change rounds |
| 变更轮 Round | **directory** | `docs/<module>/<feature>/<NN>-<round>/` — one doc set per add/remove/modify; archived on completion |
| 使用场景 Use Case | **file** (split on size) | inline `S/E/B` scenario groups in the round's `00-整理后需求.md`; split into `use-cases/UC<n>-<slug>.md` when triggers fire, with the index keeping one line per scenario ID |
| 子功能 Sub-feature | **file** (split on size) | a module section of the round's `01-接口.md`; split into `interfaces/<sub>.md` per the contract split triggers |
| 具体任务 Task | **entry** | a red/green batch: defined in `02-规划.md`, tracked as a `status.json` module entry and its `99-进度.md` section |

## Use-Case Splitting

Mirror the contract-split idiom: keep use cases inline in `00-整理后需求.md` until a trigger fires, then one file per use case under `use-cases/`:

- more than ~6 scenario groups, or the doc is too long to review in one pass;
- use cases with distinct actors or acceptance rhythms;
- multiple agents drafting or clarifying use cases in parallel.

After splitting, `00-整理后需求.md` stays the index: goals, non-goals, `## 待确认反问`, `## 决策记录`, and the full scenario roster (one line per `S/E/B` ID linking its use-case file). The user confirmation gate still confirms this single roster; detailed steps and data live in the use-case files. Never define the same scenario in two places.

## Placement Rules

- A request that spans business modules, or ships in independently acceptable parts, is not one feature: split it into features under their modules before capture (`00-feature-grading-and-splitting.md`).
- A request that is really a use case or sub-feature of an existing feature is not a new feature: similarity triage merges it into the active round, or opens a revision round on the confirmed feature (`02-requirements-capture.md`); the triage scan covers `requirements-index.md`, module overviews, and the newest round of each feature.
- A use case that outgrows its feature — its own actors, own acceptance, own release rhythm — is promoted to a feature through similarity triage; record the move in `requirements-index.md`.
- Every round declares its parent module (`所属模块`) and, for revision rounds, the previous round it supersedes, at the head of `00-整理后需求.md` or `00-功能.md`.
- New modules need a `00-模块概述.md` before their first feature folder; keep it to responsibility, feature roster slice, and cross-feature shared decisions.

## Code Layout

Every feature gets exactly one code home, decided at kickoff and recorded in `architecture.md`'s directory-structure section, mirroring the docs tree. Code is not archived per round — the code home always reflects the newest accepted contract; rounds version the documents, git versions the code. Default template for service-style projects — adjust layer names and count per the kickoff four questions; layers follow need, not fashion:

```text
src/<module>/<feature>/          # 与文档树同构：模块目录下一功能一归宿
├── api/             # 接收请求、返回结果
├── application/     # 编排流程
├── domain/          # 领域规则与核心业务逻辑
├── infrastructure/  # 平台、数据库实现
├── models/          # 数据结构
└── tests/           # 测试
```

- The two trees stay isomorphic: `docs/<module>/<feature>/` ↔ `src/<module>/<feature>/`, same module and feature names on both sides. A project that flattens the docs tree flattens the code tree the same way (`src/<feature>/`).
- The contract is the bridge between the two trees: use cases map to contract methods; the plan's method-assignment table maps every method to a concrete path inside the code home.
- Cross-feature shared code lives outside feature homes as a shared kernel declared in `architecture.md`, never copied between features; shared entities stay in `domain-models.md`.

## Output

- `requirements-index.md` grouped by module, with placement decisions (split / merge / promote) recorded.
- Module directories with `00-模块概述.md`; feature folders under their modules; one active round directory per feature under change.
- Archived rounds under `archive/` after acceptance; `status.json` tracking `activeRound`.
- The feature code-home template in `architecture.md`.

## Stop Conditions

Stop for the user when a request cannot be placed on one level, when a split or promotion changes review scope, when a feature needs to deviate from the code-home template, or before archiving a round whose acceptance evidence is incomplete.
