# General Workflow：Greenfield Project Development

这个仓库现在维护的是一套面向**从零开始搭建软件项目**的通用开发工作流。它把架构设计、技术栈搭建、垂直切片、TDD、测试集成、CI/CD、发布运营和复盘串成一条可执行主线。

## 主线

```text
项目画像
  → 需求与目标
  → 场景与验收
  → 范围与非目标
  → 约束、质量属性与风险
  → 架构评估与设计
  → 技术栈、仓库骨架与 CI
  → 第一条垂直切片
  → 红—绿—重构实现
  → 测试、评审与集成
  → 发布、监控与回滚
  → 复盘与下一条切片
```

项目画像不是最终架构；它用于判断流程深度。架构决策要由需求、质量属性、数据和运行边界驱动。第一条垂直切片必须经过真实入口，既验证用户结果，也验证关键架构假设。

## 核心架构问题

架构阶段按证据决定，而不是套固定模板：

- 采用简单单体、模块化单体、应用加 worker、多服务还是事件驱动？
- 代码采用直接分层、纯模块化、模块化加分层，还是有依据的混合结构？
- 哪个模块拥有哪类数据，哪些不变量必须保持？
- 是否需要鉴权、授权、审计、多租户或服务间身份？
- 是否需要异步任务、幂等、重试、死信、补偿或定时调度？
- API/事件采用何种风格，如何版本化并统一错误表达？
- 是否需要事务、缓存、限流、文件、搜索、通知或 feature flag？
- 如何管理配置、秘密、日志、指标、追踪、健康检查和告警？
- 技术栈和目录结构为什么适合当前团队、风险和生命周期？
- 如何构建、迁移、部署、观察、回滚和恢复？

小项目不必强行使用完整分层或微服务；高风险项目即使代码量很小，也不能省略安全、迁移、兼容和恢复判断。

## 仓库结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── references/                         # 当前 Greenfield 主线
│   ├── 00-progress-router.md
│   ├── 00-project-profile.md
│   ├── 00-lean-path.md
│   ├── 01-requirements-and-goals.md
│   ├── 02-scenarios-and-acceptance.md
│   ├── 03-scope-and-nongoals.md
│   ├── 04-constraints-quality-risks.md
│   ├── 05-architecture-design.md
│   ├── 05a-mechanisms-and-contracts.md
│   ├── 06-scaffolding-and-ci.md
│   ├── 07-vertical-slice.md
│   ├── 08-implementation-tdd.md
│   ├── 09-testing-review-integration.md
│   ├── 10-release-operations.md
│   ├── 11-retrospective-evolution.md
│   └── 99-state-and-handoff.md
├── scripts/
│   ├── check_consistency.py            # 校验本仓库自身
│   └── workflow_status.py              # 随 skill 分发，在目标项目里跑
├── archive/general-workflow-v0.12.0/   # 旧版只读参考
├── CHANGELOG.md
└── LICENSE
```

`archive/` 不属于安装包，也不参与当前路由。根目录的 v3.8 源材料已经随旧版一并归档，避免旧流程和新流程同时成为权威。

## 使用方式

1. 先读 `references/00-progress-router.md`。它会先查找状态文件，再建立画像。
2. 建立项目画像，判断当前生命周期阶段、流程档位和路径深度。
3. 每次只读当前阶段需要的一个 reference。
4. 通过阶段门禁后继续下一阶段；只有遇到会改变行为、范围、数据、安全、兼容性、成本或不可逆效果的决策才暂停询问。
5. 在第一条真实垂直切片上验证架构，再进入后续迭代。
6. 每轮结束更新状态文件，让下一次会话可以直接从游标接手。

### 快路径（LEAN）

适用于低风险、单运行单元、单团队、无对外兼容承诺的项目。合并的不只是前四个阶段——LEAN 全程四步：

```text
项目画像 → 一页项目合同 → 轻量架构 → 骨架与第一条路径 → 实现与交付
```

合并的是文档不是决策：真实入口、成功与失败场景、非目标、数据敏感度和一条可跑的验证路径仍然必须有答案。`00-lean-path.md` 里的升级触发一旦成立，立即切回完整路径，已有产出直接搬运。

### 完整与加深路径

STANDARD 逐阶段推进，机制与契约按需加载 `05a-mechanisms-and-contracts.md`。只有在多服务、多客户端、多团队、公共接口、支付/隐私/合规、不可逆迁移、严格性能/可用性或高恢复成本等信号出现时，才升到 HIGH-RISK，增加详细 ADR、合同测试、安全审查、容量测试、迁移演练、灰度发布或独立评审。

### 跨会话接手

项目状态写在目标仓库的 `docs/workflow/` 下，**分片存放**，这样第二个人可以随时插入：

```text
docs/workflow/
  project.md          档位、路径、生命周期、权威来源、已确认决策   ← 罕见变更
  backlog.md          每个 A-ID 归属哪条切片，或未认领/已延后/已取消
  slices/S-01.md      owner、认领、stage、验收状态、证据、写入范围 ← 单一 owner 独占
```

关键是 **`stage` 属于切片而不是项目**：甲在 S-01 上做阶段 8、乙在 S-02 上做阶段 5，一个共享的 `stage` 字段表达不了这件事——那不是合并冲突，是模型缺陷。状态只写在切片文件里，backlog 只记归属，所以最频繁的操作（改状态）永远只碰一个单人独占的文件。

状态是游标和索引，不是第二份真相；与仓库事实冲突时以仓库为准。详见 `references/99-state-and-handoff.md`。

其中的**范围台账**回答“还欠多少、做完了没有”：一行一个 A-ID，状态取 `remaining` / `in-slice` / `delivered` / `deferred` / `dropped`。进入 `delivered` 的唯一条件是通过阶段 9 的 Definition of Done 并填上证据指针；已交付不可退回，要重开必须走变更协议。台账无 `remaining` 且无 `in-slice`，即当前范围交付完毕。

### 一条还是多条切片

阶段 7 同时服务第一条和其后的每一条切片，共用同一套地图和门禁。差别只在选择权重：第一条必须触及一个未验证的架构假设，后续切片改为优先关闭台账里未交付的 Must，架构假设填 `none` 是合法结论。

## 与旧版的关系

旧版是以 feature/change round、Delivery Anchor、TOS 和复杂状态治理为中心的流程，已完整保存在 [`archive/general-workflow-v0.12.0/`](archive/general-workflow-v0.12.0/)。新版本暂时只针对 Greenfield，不删除旧材料，也不让旧材料阻塞新项目的正常开工。

## 校验

两个脚本面向不同对象。修改 `SKILL.md` 或 `references/` 后，在**本仓库**运行：

```bash
python scripts/check_consistency.py
```

`scripts/workflow_status.py` 不校验本仓库，它随 skill 分发，在**使用这套工作流的项目**里运行：

```bash
python workflow_status.py --root . --json
```

它读 `docs/workflow/`，输出每条切片的 owner、stage 和进度、未认领的 A-ID、是否交付完毕；发现 delivered 无证据、backlog 与切片不一致、两条在途切片写入范围重叠、deferred/dropped 无变更记录等问题时退出码非零。这是这套工作流里**唯一一个不靠 agent 自我判定的门禁**。

校验器会检查：

- Reference Map 与实际文件是否一一对应；
- 引用是否可解析、是否能从 router 到达；
- 11 个 Greenfield 阶段和 P0 是否存在并且顺序正确；
- 需求、架构、机制、脚手架、切片、实现、测试、发布、复盘和状态交接的关键门禁是否存在；
- 常驻入口（`SKILL.md` 与 router）和单份 reference 是否超出体积预算——超出说明阶段内容漂回了入口，或某一阶段吞并了相邻阶段；
- 旧版归档是否存在且没有被当前主线引用为必需阶段。

## 许可

MIT，见 [LICENSE](LICENSE)。
