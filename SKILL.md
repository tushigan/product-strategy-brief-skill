---
name: product-strategy-brief
description: "用于预包装食品团队在新品创意前梳理产品开发策略 Brief，或诊断既有策略是否具备市场机会、客户意愿与供应链承接能力。用户输入 /产品开发策略、产品开发策略 Brief、产品策略工作坊或 product-strategy-brief 时使用。"
metadata:
  version: "0.1.2"
  requires:
    bins: ["python3"]
---

# 产品开发策略 Brief

## 用途

这个 Skill 用于产品开发创意之前的策略梳理，不直接替代研发、配方、工业化或法规判断。

顶层原则：

```text
可做 ∩ 想做 ∩ 能做 = 该做的部分
```

## 中文触发别名

用户以 `/产品开发策略` 开头时，视为明确调用本 Skill，效果等同于 `$product-strategy-brief`。将别名之后的内容作为本轮需求；如果用户只输入别名，则进入工作坊模式并提出第一个 Brief 问题。

例如：

```text
/产品开发策略 帮我从零梳理一个常温预包装烘焙新品
```

## 渐进式披露

主入口只负责路由、状态和确认门。执行具体任务时，按 `scripts/router.py` 返回的 `required_references` 读取 `references/` 下对应规则，不要默认读取全部知识。

## 当前支持模式

- `workshop`：从 Brief 逐步梳理三圈交集；
- `diagnose`：诊断 Brief、证据、逻辑和三圈门槛；
- `quick-start`：压缩提问，但不跳过 Brief 和三圈门槛。

`benchmark` 和 `refine` 目前只返回预留状态，不得冒充已实现。

## 命令

```bash
python3 scripts/main.py \
  --input "帮我从零开始做一个预包装烘焙新品策略" \
  --project-path ./项目示例

python3 scripts/main.py \
  --mode diagnose \
  --project-json ./项目示例/project_state.json
```

## 必须遵守

1. Brief 八项最低字段缺失时停止正式策略；
2. 可做、想做、能做任一圈缺证据时标记 `pending`；
3. 趋势信号不能直接写成市场事实；
4. 客户不愿投入或供应链无法承接时，不得因为趋势好就推荐；
5. 动态调研可组合 Tavily、国外网页、官方资料、小红书、抖音、天猫等来源，并记录日期、URL、证据类别和禁止外推范围；
6. 共享记忆只能作为内部案例线索，必须回到原始项目资料核验；
7. 不在状态文件、调研记录或日志中保存 API Key、Token、Cookie、密码或私人账号信息；
8. 用户未确认前，不把交集状态写成正式推荐。

项目需要当前趋势、竞品、价格或平台信号时，先读取 `references/10-动态调研与多来源证据规则.md`，再用 `scripts/research_log.py` 记录来源。需要迭代内部案例时，先读取 `references/09-案例与失败模式索引.md`；共享记忆召回由运行时 Agent 完成，脚本只接收回到原始资料核验后的脱敏案例卡。

## 后续交接

本 Skill 输出 Brief、三圈定位、产品开发策略和开发边界。后续候选方向、正式概念、工业化审查和飞书交付由专门的预包装新品开发流程承接。
