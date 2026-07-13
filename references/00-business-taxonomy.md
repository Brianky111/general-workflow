# Business Taxonomy and Code Layout

## Purpose

Arrange requirements physically along the business hierarchy — product, module, feature, use case, sub-feature, task — and map every feature to one explicit vertical slice across the applications it touches. Each add/remove/modify round on a feature gets its own numbered document set, archived on completion, so the feature's history stays navigable and the active work is always one directory.

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
        │   ├── 02-测试矩阵.md        # Feature Test Matrix 覆盖图 + 证据登记表
        │   ├── 09-集成验收.md        # 真实纵向切片与跨功能验收
        │   ├── 09-完整性审计.md      # Definition of Done 终审
        │   └── 99-进度.md            # 任务级进度：模块小节
        └── archive/
            └── <NN>-<round>/        # 验收通过后整轮移入
```

Path convention: round documents are written as `docs/<module>/<feature>/<round>/...` throughout these references, where `<round>` always means the feature's **active round**. `fixtures/` and `status.json` sit at feature level across rounds. Single-module or tiny projects may flatten the module level; set thresholds at kickoff.

## Change Rounds

- Every add/remove/modify of a feature opens a new round directory `<NN>-<round>` (two-digit sequence plus a short slug; the first is `01-初建`) holding its own numbered doc set. One round, one doc set — the one-requirement-one-doc-set instinct applied per change.
- Rounds apply to requirement/contract-level work: the initial build, level-A changes, and similarity-triage revisions. Level B (bug fix / counterexample repayment) and level C (display tweaks) stay inside the active round — or, when no round is active, record into feature-level `fixtures/counterexamples/` and `status.json` without opening one.
- Each round's `01-接口.md` is the **complete** contract after the change, never a delta: the newest archived round always holds the feature's current truth. A new round starts by copying the previous round's contract forward and revising it under the change protocol.
- On feature-completeness acceptance (terminal state), move the round directory into `archive/` and update `status.json`'s `activeRound` to empty. Archived rounds are read-only history; corrections open a new round.
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
| 具体任务 Task | **entry** | a behavior-sized red/green/refactor batch: defined in `02-规划.md`, covered in `02-测试矩阵.md`, and tracked in `status.json` plus `99-进度.md` |

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

## Vertical Feature Slice and Code Layout

A Feature is a user-understandable capability, not a backend folder. Give it one logical boundary and one declared home per touched application/runtime. Code is not archived per round — code homes reflect the newest accepted contract; rounds version documents and Git versions code.

For a full-stack project, prefer this logical shape and adapt paths to the repository:

```text
apps/
├── web/src/<module>/<feature>/
│   ├── api/             # typed client; transport only
│   ├── model/           # frontend state, hooks, view-model types
│   ├── ui/              # user-facing components and states
│   ├── pages/           # route/page composition
│   └── tests/           # logic, component, and page integration tests
└── api/src/<module>/<feature>/
    ├── api/             # inbound protocol, DTOs, presenters
    ├── application/     # use cases, commands/results, ports
    ├── domain/          # entities, value objects, policies, events
    ├── infrastructure/  # persistence, SDK, messaging adapters
    └── tests/           # domain, use-case, and adapter tests

packages/contracts/<module>/<feature>/  # runtime schemas/events shared across boundaries
tests/e2e/<module>/<feature>/            # critical real user paths
```

Backend `models/` is not a generic drawer. Put transport DTOs in `api/`, commands/results in `application/`, entities/value objects in `domain/`, persistence/external records in `infrastructure/`, and shared wire schemas in `packages/contracts/` or the repository's equivalent. A small or single-runtime project may collapse directories, but it still records where each concern lives.

- Keep the docs feature path stable while code spans several declared homes: `docs/<module>/<feature>/` ↔ the same `<module>/<feature>` identity in web, API, contracts, and E2E trees.
- The contract bridges the slice: use cases map to UI flows, schemas, API/event methods, domain rules, adapters, and downstream feature effects. The plan maps each contract clause to a concrete path and test-matrix row.
- Keep dependency direction explicit: UI calls application-facing contracts; application orchestrates; domain owns legal business states; infrastructure implements ports. Neither domain nor application imports UI frameworks, ORM clients, or vendor SDKs.
- Cross-feature shared code lives outside feature homes as a shared kernel declared in `architecture.md`, never copied between features. Shared domain definitions live in `domain-models.md`; shared runtime schemas have one code owner.

## Output

- `requirements-index.md` grouped by module, with placement decisions (split / merge / promote) recorded.
- Module directories with `00-模块概述.md`; feature folders under their modules; one active round directory per feature under change.
- Archived rounds under `archive/` after completeness acceptance; `status.json` tracking `activeRound`.
- The vertical-slice code-home map in `architecture.md`, including frontend, contracts, backend, adapters, and E2E locations when applicable.

## Stop Conditions

Stop for the user when a request cannot be placed on one level, when a split or promotion changes review scope, when a feature needs an undeclared runtime/code home, or before archiving a round whose completeness evidence is incomplete.
