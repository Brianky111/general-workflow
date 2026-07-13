# Business Taxonomy and Code Layout

## Purpose

Arrange requirements physically along the business hierarchy — product, module, feature, use case, sub-feature, task — and give every feature exactly one code home. Physical granularity decreases with depth: directories for modules and features, files for use cases and sub-features, tracked entries for tasks. This keeps navigation obvious as the project grows without creating empty-folder bureaucracy.

## Canonical Layout

```text
docs/
├── architecture.md                  # 产品级：层级地图、代码归宿模板
├── glossary.md
├── domain-models.md
├── requirements-index.md            # 产品级总控台，按模块分节
└── features/
    └── <module>/                    # 大功能模块（订单、支付、退款...）
        ├── 00-模块概述.md            # 模块职责、功能清单、跨功能共享决策
        └── <feature>/               # 功能特性 = 一个需求一套文档
            ├── 00-项目识别.md
            ├── 00-原始需求.md
            ├── 00-整理后需求.md      # 用例索引：编号场景清单
            ├── use-cases/           # 使用场景（触发拆分后，每用例一档）
            │   └── UC1-<slug>.md
            ├── 01-接口.md            # 子功能索引
            ├── interfaces/<sub>.md  # 子功能合同
            ├── 01-代码冲突与重叠.md
            ├── conflicts/<sub>.md
            ├── 02-规划.md            # 任务在此定义为红绿批次
            ├── fixtures/
            ├── status.json          # 任务级状态：modules 条目
            └── 99-进度.md            # 任务级进度：模块小节
```

Every `docs/features/<feature>/` path elsewhere in these references means the feature folder wherever it lives — canonically `docs/features/<module>/<feature>/`. Single-module or tiny projects may flatten to `docs/features/<feature>/`; set the threshold at kickoff.

## Level-by-Level Mapping

| Level | Physical form | Home |
|---|---|---|
| 产品 / 系统 Product | repo-level docs | `architecture.md`, `requirements-index.md`, `glossary.md`, `domain-models.md` |
| 大功能模块 Module | **directory** | `docs/features/<module>/` with `00-模块概述.md`; one roster section in `requirements-index.md` |
| 功能特性 Feature | **directory** | `docs/features/<module>/<feature>/` — the one-requirement-one-doc-set unit |
| 使用场景 Use Case | **file** (split on size) | inline `S/E/B` scenario groups in `00-整理后需求.md`; split into `use-cases/UC<n>-<slug>.md` when triggers fire, with the index keeping one line per scenario ID |
| 子功能 Sub-feature | **file** (split on size) | a module section of `01-接口.md`; split into `interfaces/<sub>.md` per the contract split triggers |
| 具体任务 Task | **entry** | a red/green batch: defined in `02-规划.md`, tracked as a `status.json` module entry and its `99-进度.md` section |

## Use-Case Splitting

Mirror the contract-split idiom: keep use cases inline in `00-整理后需求.md` until a trigger fires, then one file per use case under `use-cases/`:

- more than ~6 scenario groups, or the doc is too long to review in one pass;
- use cases with distinct actors or acceptance rhythms;
- multiple agents drafting or clarifying use cases in parallel.

After splitting, `00-整理后需求.md` stays the index: goals, non-goals, `## 待确认反问`, `## 决策记录`, and the full scenario roster (one line per `S/E/B` ID linking its use-case file). The user confirmation gate still confirms this single roster; detailed steps and data live in the use-case files. Never define the same scenario in two places.

## Placement Rules

- A request that spans business modules, or ships in independently acceptable parts, is not one feature: split it into features under their modules before capture (`00-feature-grading-and-splitting.md`).
- A request that is really a use case or sub-feature of an existing feature is not a new feature: similarity triage merges or revises it (`02-requirements-capture.md`); the triage scan covers `requirements-index.md`, module overviews, and feature scenario rosters.
- A use case that outgrows its feature — its own actors, own acceptance, own release rhythm — is promoted to a feature through similarity triage; record the move in `requirements-index.md`.
- Every feature declares its parent module (`所属模块`) at the head of `00-整理后需求.md` or `00-功能.md`.
- New modules need a `00-模块概述.md` before their first feature folder; keep it to responsibility, feature roster slice, and cross-feature shared decisions.

## Code Layout

Every feature gets exactly one code home, decided at kickoff and recorded in `architecture.md`'s directory-structure section, mirroring the docs tree. Default template for service-style projects — adjust layer names and count per the kickoff four questions; layers follow need, not fashion:

```text
src/features/<feature>/          # 大代码库可同样嵌套 <module>/<feature>
├── api/             # 接收请求、返回结果
├── application/     # 编排流程
├── domain/          # 领域规则与核心业务逻辑
├── infrastructure/  # 平台、数据库实现
├── models/          # 数据结构
└── tests/           # 测试
```

- The code-home name matches the doc-set folder: `docs/features/order/refund/` ↔ `src/features/refund/` (or `src/features/order/refund/` when the codebase nests modules too).
- The contract is the bridge between the two trees: use cases map to contract methods; the plan's method-assignment table maps every method to a concrete path inside the code home.
- Cross-feature shared code lives outside feature homes as a shared kernel declared in `architecture.md`, never copied between features; shared entities stay in `domain-models.md`.

## Output

- `requirements-index.md` grouped by module, with placement decisions (split / merge / promote) recorded.
- Module directories with `00-模块概述.md`; feature folders under their modules.
- The feature code-home template in `architecture.md`.
- The parent-module declaration in each feature's requirement doc.

## Stop Conditions

Stop for the user when a request cannot be placed on one level, when a split or promotion changes review scope, or when a feature needs to deviate from the code-home template.
