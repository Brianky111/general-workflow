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
├── scripts/check_consistency.py
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

适用于低风险、单运行单元、单团队、无对外兼容承诺的项目。阶段 1–4 合并成 `00-lean-path.md` 的一页项目合同，主线其余阶段不变：

```text
项目画像 → 一页项目合同 → 轻量架构 → 仓库与 CI → 一条垂直切片 → 测试 → 发布
```

合并的是文档不是决策：真实入口、成功与失败场景、非目标、数据敏感度和一条可跑的验证路径仍然必须有答案。`00-lean-path.md` 里的升级触发一旦成立，立即切回完整路径，已有产出直接搬运。

### 完整与加深路径

STANDARD 逐阶段推进，机制与契约按需加载 `05a-mechanisms-and-contracts.md`。只有在多服务、多客户端、多团队、公共接口、支付/隐私/合规、不可逆迁移、严格性能/可用性或高恢复成本等信号出现时，才升到 HIGH-RISK，增加详细 ADR、合同测试、安全审查、容量测试、迁移演练、灰度发布或独立评审。

### 跨会话接手

项目状态写在目标仓库的 `docs/workflow-state.md`（或根目录 `WORKFLOW-STATE.md`）。它是游标和索引，不是第二份真相：记录当前阶段、路径深度、当前切片、未决决策和证据入口，用指针引用需求、ADR、测试和发布记录的权威位置。与仓库事实冲突时以仓库为准。详见 `references/99-state-and-handoff.md`。

## 与旧版的关系

旧版是以 feature/change round、Delivery Anchor、TOS 和复杂状态治理为中心的流程，已完整保存在 [`archive/general-workflow-v0.12.0/`](archive/general-workflow-v0.12.0/)。新版本暂时只针对 Greenfield，不删除旧材料，也不让旧材料阻塞新项目的正常开工。

## 校验

在修改 `SKILL.md` 或 `references/` 后运行：

```powershell
python scripts/check_consistency.py
git diff --check
```

校验器会检查：

- Reference Map 与实际文件是否一一对应；
- 引用是否可解析、是否能从 router 到达；
- 11 个 Greenfield 阶段和 P0 是否存在并且顺序正确；
- 需求、架构、机制、脚手架、切片、实现、测试、发布、复盘和状态交接的关键门禁是否存在；
- 常驻入口（`SKILL.md` 与 router）和单份 reference 是否超出体积预算——超出说明阶段内容漂回了入口，或某一阶段吞并了相邻阶段；
- 旧版归档是否存在且没有被当前主线引用为必需阶段。

## 许可

MIT，见 [LICENSE](LICENSE)。
