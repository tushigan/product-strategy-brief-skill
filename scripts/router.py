"""自然语言模式路由。"""

from __future__ import annotations

from typing import Any


SUPPORTED_MODES = {"workshop", "diagnose", "quick_start"}
RESERVED_MODES = {"benchmark", "refine"}
MODE_REFERENCES = {
    "workshop": ["00-知识基座说明.md", "01-知识路由表.md", "02-三圈定位总则.md"],
    "diagnose": ["00-知识基座说明.md", "01-知识路由表.md", "02-三圈定位总则.md", "08-策略诊断与评分标准.md"],
    "quick_start": ["00-知识基座说明.md", "01-知识路由表.md", "02-三圈定位总则.md", "06-三圈交集与策略取舍.md"],
    "benchmark": ["02-三圈定位总则.md", "03-可做：市场机会与趋势.md", "06-三圈交集与策略取舍.md", "10-动态调研与多来源证据规则.md"],
    "refine": ["02-三圈定位总则.md"],
}

KEYWORDS = {
    "benchmark": ("对标", "竞品", "标杆", "参考案例", "学习某"),
    "diagnose": ("审一下", "审核", "诊断", "评估", "检查", "遗漏", "逻辑通"),
    "quick_start": ("快速", "赶时间", "明天要", "先出个框架", "简版", "80分"),
    "refine": ("优化", "深化", "迭代", "改进", "这部分不好"),
    "workshop": ("从零", "没有思路", "共创", "一步步", "引导"),
}


def detect_mode(user_input: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    forced = context.get("mode")
    if forced:
        mode = forced.replace("-", "_")
        if mode in SUPPORTED_MODES or mode in RESERVED_MODES:
            return {"mode": mode, "reason": "用户显式指定模式", "required_references": MODE_REFERENCES[mode]}
    text = (user_input or "").strip()
    for mode in ("benchmark", "diagnose", "quick_start", "refine", "workshop"):
        if any(keyword in text for keyword in KEYWORDS[mode]):
            return {"mode": mode, "reason": f"命中{mode}意图关键词", "required_references": MODE_REFERENCES[mode]}
    if context.get("has_existing_project") and context.get("project_status") == "completed":
        return {"mode": "diagnose", "reason": "已有 completed 项目，默认先做诊断", "required_references": MODE_REFERENCES["diagnose"]}
    return {"mode": "workshop", "reason": "未命中其他意图，默认进入工作坊", "required_references": MODE_REFERENCES["workshop"]}

