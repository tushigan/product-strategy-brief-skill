"""诊断模式。"""

from __future__ import annotations

from typing import Any

from scripts.validator import validate_brief, validate_three_circle


class DiagnoseMode:
    def __init__(self, state: dict[str, Any]) -> None:
        self.state = state

    def run(self) -> dict[str, Any]:
        brief = validate_brief(self.state)
        circles = validate_three_circle(self.state)
        issues: list[dict[str, str]] = []
        for field in brief["missing_fields"]:
            issues.append({"severity": "high", "section": "brief", "issue": f"缺少 Brief 字段：{field}", "suggestion": "先补齐该字段，再进入策略判断"})
        for field in brief["invalid_fields"]:
            issues.append({"severity": "high", "section": "brief", "issue": f"Brief 字段不合法：{field}", "suggestion": "按固定枚举或具体时长重新填写"})
        for reason in circles["blocking_reasons"]:
            issues.append({"severity": "high", "section": "three_circle", "issue": reason, "suggestion": "补充该圈证据或调整方向"})
        score = max(0, 100 - len(brief["missing_fields"]) * 10 - len(brief["invalid_fields"]) * 15 - len(circles["blocking_reasons"]) * 15)
        return {
            "status": "success",
            "mode": "diagnose",
            "overall_score": score,
            "can_recommend": circles["can_recommend"] and brief["valid"],
            "issues": issues,
            "strengths": ["Brief 八项完整" if brief["valid"] else "尚未满足 Brief 最低门槛", "三圈交集成立" if circles["can_recommend"] else "三圈交集尚未成立"],
            "next_steps": [issue["suggestion"] for issue in issues] or ["进入用户确认门"],
        }

