# Business Taxonomy and Code Layout

## Purpose

Use the stable business hierarchy — product, module, feature, use case, sub-feature, task — only to clarify ownership, acceptance, or independent delivery. Treat a goal-bounded cross-feature solution as an orthogonal delivery view rather than another permanent containment level. Map behavior to the repository's existing vertical slice and avoid creating folders, rounds, or duplicate code homes solely to satisfy a taxonomy.

## Contents

- Lean layout, optional solution delivery view, governed layout, and change rounds
- Level mapping and use-case splitting
- Placement rules
- Vertical feature slice and code layout
- Output and stop conditions

## Lean Layout

Prefer the repository's existing task/spec and code layout. When a durable feature document is useful, the ordinary shape may be only:

```text
docs/<module>/<feature>/00-功能.md   # source link + concise requirements + inline BDD + compact plan/evidence
```

When a finite accepted outcome genuinely needs independently owned feature contributions, keep a compact solution frame in the existing issue/plan or, when durable coordination is triggered, one optional `docs/solutions/<solution>/00-方案.md`. It references feature contracts and never contains copies of them.

Add `fixtures/`, interface/conflict appendices, a test matrix, round directories, archives, or one status source only when their named risk trigger in `00-feature-grading-and-splitting.md` applies. The following is an expanded governed layout, not a required template:

## Expanded Governed Layout

```text
docs/
├── solutions/                       # 可选：有终点的跨功能交付视图，不是功能真源
│   └── <solution>/
│       └── 00-方案.md                # 锚点、功能/owner映射、依赖、总体证据与关闭条件
├── architecture.md                  # 产品级：层级地图、代码归宿模板
├── glossary.md
├── domain-models.md
├── requirements-index.md            # 产品级总控台，按模块分节
└── <module>/                        # 大功能模块（目录内有 00-模块概述.md 即为模块目录）
    ├── 00-模块概述.md                # 模块职责、功能清单、跨功能共享决策
    └── <feature>/                   # 功能特性
        ├── status.json              # 可选：多 owner / 长期 handoff 时选用的唯一状态源
        ├── fixtures/                # 功能级、跨轮共享：contract / counterexamples / generated
        ├── <NN>-<round>/            # 变更轮：01-初建、02-<变更slug>…（进行中的一轮）
        │   ├── 00-项目识别.md
        │   ├── 00-原始需求.md
        │   ├── 00-整理后需求.md      # 用例索引：编号场景清单
        │   ├── 00-行为示例.md        # BDD Rule / Example / Question 与 Given-When-Then
        │   ├── use-cases/           # 使用场景（触发拆分后，每用例一档）
        │   ├── 01-接口.md            # 可选：风险触发的接口 delta 或所需完整快照
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

Path convention: where a project already uses rounds, references write them as `docs/<module>/<feature>/<round>/...`, with `<round>` meaning the active governed round. Projects on the lean path may use their existing issue/spec location or one compact feature file and omit rounds, fixtures, and status files entirely.

## Solution Delivery View

A solution is a finite coordination projection of the Delivery Anchor for an aggregate outcome that cannot be faithfully owned or accepted by one feature. It may cross stable modules and may reference a feature that also participates in other solutions. A module remains a long-lived responsibility domain; a feature remains the single behavior owner; a round remains optional version/audit history.

Use `00-solution-framing.md` only when independently owned feature contributions, cross-module sequencing, or aggregate integration/release/rollback proof is materially required. Let the solution own the aggregate outcome/non-goals, participating feature/owner map, dependencies, shared rollout decisions, and aggregate acceptance. Let every feature retain its one current effective behavior contract, public/data semantics, production owner, plan, and tests.

Do not nest or duplicate feature contracts under the solution, copy shared schemas into it, or keep a completed feature open solely because another independent contribution remains. Do not hide unfinished feature behavior in aggregate status. Ordinary single-feature vertical work needs no solution artifact.

## Change Rounds

- Do not open a round for every change. Default to a delta in the existing authoritative issue/contract. Open a governed round only for a public compatibility snapshot, formal audit/regulatory history, irreversible migration, or long-running independent-owner approval boundary.
- Bug fixes, counterexample repayment, display tweaks, and ordinary behavior changes stay in the current source of truth. Do not create `fixtures/` or `status.json` if the project does not already need them.
- A round records changed acceptance clauses, BDD examples, boundary deltas, and evidence. Copy a complete post-change contract only when tooling, external consumers, or formal audit requires one authoritative snapshot; otherwise never copy unchanged prose forward.
- When governed rounds are used, archive one only after its required risk evidence passes and clear `activeRound` in the one selected status source. Archived rounds are read-only history; later changes create a delta or another governed round according to the same triggers.
- `fixtures/` never moves with a round: counterexamples are append-only permanent regression assets, and tests reference their paths across rounds.

## Level-by-Level Mapping

| Level | Physical form | Home |
|---|---|---|
| 产品 / 系统 Product | repo-level docs | `architecture.md`, `requirements-index.md`, `glossary.md`, `domain-models.md` |
| 总体解决方案 Solution | optional cross-feature delivery view | existing issue/plan or one compact `docs/solutions/<solution>/00-方案.md`; references owning features and aggregate proof |
| 大功能模块 Module | **directory** | `docs/<module>/` with `00-模块概述.md`; one roster section in `requirements-index.md` |
| 功能特性 Feature | existing issue/spec or optional directory | one authoritative compact contract; add status/fixtures/rounds only when triggered |
| 变更轮 Round | optional directory | only for governed history or independent approval; stores a delta unless a full snapshot is required |
| 使用场景 Use Case | inline section or split file | lean `AC`/Given-When-Then examples; preserve existing S/E/B or R/EX IDs rather than adding a parallel scheme |
| 子功能 Sub-feature | existing code/contract section | split only for independent ownership, compatibility, or review boundaries |
| 具体任务 Task | plan/handoff entry | behavior-sized red/green/refactor batch bound to `N-ID`, an existing test home, and evidence; durable status is optional and singular |

## Use-Case Splitting

Mirror the contract-split idiom: keep use cases inline in `00-整理后需求.md` until a trigger fires, then one file per use case under `use-cases/`:

- more than ~6 scenario groups, or the doc is too long to review in one pass;
- use cases with distinct actors or acceptance rhythms;
- independent owners need separate approval or handoff boundaries.

After splitting, keep one authoritative index and link detailed scenarios/examples from it; never copy them. Ask for confirmation only when the split introduces a material ownership or behavior decision.

## Placement Rules

- If one accepted aggregate outcome requires independently owned feature contributions, frame the minimal solution/owner/dependency/aggregate-proof view through `00-solution-framing.md`, then place each behavior in exactly one owning feature. Do not use the solution as a second contract.
- A request that spans business modules, or ships in independently acceptable parts, is not one feature: split it into features under their modules before capture (`00-feature-grading-and-splitting.md`).
- A request that is really a use case or sub-feature of an existing feature is not a new feature: similarity triage merges it into the authoritative compact contract or records a revision delta (`02-requirements-capture.md`).
- A use case that outgrows its feature — its own actors, acceptance, owner, and release rhythm — may be promoted through similarity triage; record the move only in the roster/status source the project already uses.
- When rounds are used, declare the parent module and prior authoritative reference at the head of the compact contract.
- Create `00-模块概述.md` only when several features need a durable shared ownership or cross-feature decision source; a new code directory alone does not require one.

## Vertical Feature Slice and Code Layout

A Feature is a user-understandable capability, not a backend folder. Give it one logical boundary and one declared home per touched application/runtime. Code is not archived per round — code homes reflect the newest accepted contract; rounds version documents and Git versions code.

For a brand-new full-stack project, the following may be a useful logical shape. In an existing repository, extend its current owners, registrations, conventions, and test homes instead of creating a parallel feature tree:

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
- The compact contract bridges the slice. The plan maps each changed acceptance behavior to a stable production `N-ID`, exact existing/new path, nearest test home, and sparse proof; expand layer-by-layer traceability only for a named risk.
- Keep dependency direction explicit: UI calls application-facing contracts; application orchestrates; domain owns legal business states; infrastructure implements ports. Neither domain nor application imports UI frameworks, ORM clients, or vendor SDKs.
- Cross-feature shared code lives outside feature homes as a shared kernel declared in `architecture.md`, never copied between features. Shared domain definitions live in `domain-models.md`; shared runtime schemas have one code owner.

## Output

- A concise placement decision in the existing task/contract when hierarchy affects scope.
- The repository's actual production/test anchors and ownership, not a template-generated parallel tree.
- Optional module overviews, rounds, archives, fixtures, or one status source only when their risk/governance trigger applies.

## Stop Conditions

Stop for the user only when competing placements change observable scope, ownership, public compatibility, or independent acceptance, or before archiving a governed round whose required risk evidence is incomplete. Otherwise choose the smallest faithful placement and continue.
