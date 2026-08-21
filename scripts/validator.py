"""Brief 和三圈定位门禁。"""

from __future__ import annotations

from typing import Any


REQUIRED_BRIEF_FIELDS = (
    "产品问题",
    "开发目标",
    "主要渠道或销售场景",
    "目标消费者",
    "目标保质期要求",
    "可用产线与关键工艺能力",
    "明确禁用或受限工艺",
    "目标保质期类型",
)
VALID_SHELF_LIFE_TYPES = {"短保", "中保", "长保"}
RECOMMENDABLE_CAPABILITY = {"current", "stretch"}


def _brief_from(data: dict[str, Any]) -> dict[str, Any]:
    value = data.get("brief")
    return value if isinstance(value, dict) else data


def validate_brief(data: dict[str, Any]) -> dict[str, Any]:
    brief = _brief_from(data)
    missing: list[str] = []
    invalid: list[str] = []
    warnings: list[str] = []
    for key in REQUIRED_BRIEF_FIELDS:
        value = brief.get(key)
        if not isinstance(value, str) or not value.strip():
            missing.append(key)
    shelf_life = brief.get("目标保质期类型")
    if shelf_life and shelf_life not in VALID_SHELF_LIFE_TYPES:
        invalid.append("目标保质期类型")
    if brief.get("目标保质期要求") and "个月" not in brief["目标保质期要求"] and "天" not in brief["目标保质期要求"]:
        warnings.append("目标保质期要求建议写明具体时长和流通条件")
    return {
        "valid": not missing and not invalid,
        "missing_fields": missing,
        "invalid_fields": invalid,
        "warnings": warnings,
    }


def validate_three_circle(data: dict[str, Any]) -> dict[str, Any]:
    circles = data.get("three_circle") or {}
    market = circles.get("可做") or {}
    client = circles.get("想做") or {}
    capability = circles.get("能做") or {}
    intersection = circles.get("intersection") or {}
    problems: list[str] = []
    if market.get("status") != "confirmed":
        problems.append("可做尚未达到 confirmed")
    if not market.get("evidence_ids"):
        problems.append("可做缺少证据引用")
    if client.get("status") != "confirmed":
        problems.append("想做尚未达到 confirmed")
    if not client.get("evidence_ids"):
        problems.append("想做缺少证据引用")
    if capability.get("status") not in RECOMMENDABLE_CAPABILITY:
        problems.append("能做不是 current 或 stretch")
    if not capability.get("evidence_ids"):
        problems.append("能做缺少证据引用")
    status = intersection.get("status", "pending")
    if status == "recommended" and problems:
        problems.append("交集标记为 recommended，但三圈仍有阻断")
    can_recommend = not problems and status == "recommended"
    return {
        "valid": can_recommend,
        "can_recommend": can_recommend,
        "circle_status": {"可做": market.get("status", "missing"), "想做": client.get("status", "missing"), "能做": capability.get("status", "unknown")},
        "intersection_status": status,
        "blocking_reasons": problems,
        "next_validation": intersection.get("minimum_next_validation", []),
    }


def validate_state(data: dict[str, Any]) -> dict[str, Any]:
    brief_result = validate_brief(data)
    circle_result = validate_three_circle(data)
    return {"valid": brief_result["valid"] and circle_result["valid"], "brief": brief_result, "three_circle": circle_result}
