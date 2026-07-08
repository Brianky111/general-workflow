# Conflict Scan

## Purpose

Find where the desired contract overlaps, contradicts, or can reuse existing code.

## Entry Conditions

- The project is old or the feature touches existing modules.
- The contract describes behavior that may already exist.

## Actions

1. Search for existing routes, components, services, models, tests, and docs related to the feature.
2. Compare existing behavior against the contract.
3. Classify each finding:
   - reuse as-is,
   - extend existing code,
   - modify existing behavior,
   - refactor before implementation,
   - build from scratch.
4. Check at least:
   - public APIs, commands, events, routes, components, and config entries,
   - data models, persistence, cache, serialization formats,
   - user flows, errors, state machines, permissions, feature flags,
   - external adapters, protocols, fixtures, and test doubles,
   - similar historical features.
5. Note migration risks, compatibility risks, and duplicated concepts.

## Output

Create or update `docs/features/<feature>/01-代码冲突与重叠.md`; use `conflicts/<module>.md` only when the list is large.

Use this item shape:

```markdown
## C1：〈一句话说明冲突或重叠〉
- 需求来源：S1 / E1 / B1 / 决策 D1 / 接口方法 M1
- 涉及现有代码：`<路径>` / `<函数或类>` / `<路由或组件>`
- 当前行为：<现有代码实际做什么>
- 目标行为：<需求或接口要求什么>
- 类型：接口签名冲突 / 数据结构冲突 / 流程冲突 / 命名冲突 / 行为冲突 / 功能重叠 / 架构边界冲突 / 外部协议冲突 / 测试 fixture 冲突
- 风险：<如果处理不好会发生什么>
- 是否阻塞接口确认：是 / 否
- 给主导者的解释：<不用代码术语也能理解的说明>
- 留给规划层：待决策；候选方向可写 2-3 个，但不在本层拍板
```

## Stop Conditions

Stop if an existing behavior conflict requires changing the accepted contract or product intent.
