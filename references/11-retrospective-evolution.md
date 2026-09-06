# 复盘、架构演化与下一条切片

发布不是流程终点。复盘用真实用户结果、质量指标、故障、成本和维护信号检验此前的需求与架构假设，再决定继续、修复、暂停、取消或回到更早阶段。

## 目的与入口

目的：把运行反馈转化为有边界的下一步，而不是凭个人偏好自动重构或无限扩展范围。

入口：

- 10-release-operations.md 已有发布版本、观察窗口和运行证据；
- 关键指标、日志、告警、用户反馈、故障和成本数据可访问；
- 当前版本的遗留风险和非目标已列出。

## 复盘问题

按四组证据检查：

### 用户与业务

- 主要用户是否到达真实入口并完成 A-ID？
- 成功率、采用率、完成时间和业务指标相对基线如何？
- 哪些非目标被用户误解为承诺，是否需要澄清范围？
- 新反馈是当前缺陷、真正的新需求还是使用教育问题？

### 质量与运营

- Q-ID 的延迟、可用性、错误率、恢复、成本和安全目标是否达到？
- 告警是否及时、可行动，runbook 是否真的可执行？
- 是否出现重复副作用、数据漂移、迁移/回滚困难或值班负担？
- 第三方依赖、容量和账单是否改变了原有假设？

### 架构假设

- 第一条垂直切片验证的 H-ID 是否成立？
- 模块边界是否出现循环、跨表写入或责任模糊？
- 运行单元是否需要独立扩缩容、发布或故障隔离？
- API/事件版本、数据一致性、缓存和异步机制是否符合实际负载？
- ADR 的驱动、代价和重评条件是否仍然有效？

### 团队与交付

- setup、CI/CD、测试和诊断路径是否可由团队其他成员重复？
- 哪些工作是流程摩擦，哪些是必要控制？
- 维护成本、依赖升级和所有权是否清楚？

## 证据与决策表

~~~markdown
| observation | source | impact | decision | owner | trigger/date |
| --- | --- | --- | --- | --- | --- |
| p95 above Q-01 after canary | dashboard/run | latency risk | run capacity experiment | ops | 2026-09-10 |
~~~

将每个观察分类为：

- 当前范围缺陷：回到需求/场景或实现修复；
- 已接受风险：继续观察并记录阈值；
- 新需求：回到 01/03，重新定义结果和范围；
- 架构假设失效：回到 04/05，先做实验和 ADR；
- 仅优化建议：进入后续队列，不阻塞已完成版本。

## 架构演化规则

只有真实指标、故障、需求变化、合规要求或维护成本触发时才启动重构/拆分。演化提案至少写：

- 触发证据和受影响的 A/R/Q/ADR；
- 当前方案的具体瓶颈和替代候选；
- 数据迁移、兼容、发布和回滚影响；
- 先做的最小实验或垂直切片；
- 成功阈值、停止条件和所有者。

不要因为“代码不够优雅”“别的团队都用微服务”或一次低概率理论风险自动重构。若架构仍满足目标，保留简单方案并记录重新评估条件。

## 下一条垂直切片

下一条切片按以下优先级选择：

1. 直接改善未达到的核心用户结果；
2. 关闭最高风险且最有信息量的未知；
3. 修复属于当前范围的可复现缺陷；
4. 为已确认的后续目标建立可复用边界。

沿用 07-vertical-slice.md 的地图和门禁；不要预先为所有未来功能设计完整架构。

## 回流条件

| 证据 | 回到 |
| --- | --- |
| 用户问题/结果改变 | 01-requirements-and-goals.md |
| 场景或权限边界新增/冲突 | 02-scenarios-and-acceptance.md |
| 版本承诺或非目标改变 | 03-scope-and-nongoals.md |
| 新质量风险/未知 | 04-constraints-quality-risks.md |
| 形态、模块边界、数据所有权或技术栈不再成立 | 05-architecture-design.md |
| 鉴权、异步、事务/缓存或对外契约不再成立 | 05a-mechanisms-and-contracts.md |
| 工具链/环境不可重复 | 06-scaffolding-and-ci.md |
| 新行为准备实现 | 07-vertical-slice.md → 08-implementation-tdd.md |
| 证据不足但范围不变 | 09-testing-review-integration.md |
| 新发布/恢复风险 | 10-release-operations.md |
| 快路径的升级触发成立 | 00-lean-path.md 的升级触发表所指阶段 |

## Closeout 模板

~~~markdown
# Iteration Review
- version/commit: <released version>
- observation_window: <time range>
- user_result: <what happened>
- quality_result: <Q-ID vs target>
- incidents_and_cost: <summary>
- architecture_assumptions: <confirmed/refuted>
- accepted_risks: <owner + trigger>
- next_slice: <one bounded outcome>
- return_stage: <if any>
- decision: continue | fix | pause | cancel
~~~

## 复盘门禁

完成复盘后：

- 已发布版本的结果、指标、故障和成本有证据；
- ADR、风险和非目标已更新或明确仍有效；
- 下一步只有一个有边界的动作/切片；
- 需要回流时指出具体阶段和原因；
- 没有把“更多覆盖率/更多抽象”自动变成新任务；
- 若用户没有新目标且系统满足约束，记录继续观察并结束本轮。
