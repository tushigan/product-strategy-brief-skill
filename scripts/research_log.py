"""项目级调研证据与脱敏内部案例索引。"""

from __future__ import annotations

import copy
from datetime import date
from typing import Any
from urllib.parse import urlparse

from scripts.state_manager import StateManager, utc_now


SOURCE_TYPES = {"tavily", "foreign_web", "official", "xiaohongshu", "douyin", "tmall", "other"}
EVIDENCE_CATEGORIES = {"fact", "trend_signal", "competitive_observation", "hypothesis"}
SENSITIVE_KEYS = {"api_key", "apikey", "token", "password", "secret", "cookie", "client_secret"}
SOURCE_REQUIRED_FIELDS = {
    "source_id",
    "question",
    "source_type",
    "platform",
    "query_date",
    "url",
    "evidence",
    "sample_boundary",
    "allowed_statement",
    "prohibited_extrapolation",
    "evidence_category",
}
CASE_REQUIRED_FIELDS = {
    "case_id",
    "title",
    "source_reference",
    "evidence_level",
    "project_stage",
    "transferable_learning",
    "non_transferable_boundary",
    "client_use_limit",
    "introduced_version",
    "reviewed_version",
}


class ResearchRecordError(ValueError):
    """调研记录或案例卡不符合公开安全与证据规则。"""


def _find_sensitive_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in SENSITIVE_KEYS:
                return str(key)
            found = _find_sensitive_key(nested)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_sensitive_key(item)
            if found:
                return found
    return None


def _require_fields(record: dict[str, Any], fields: set[str]) -> None:
    missing = sorted(field for field in fields if not str(record.get(field, "")).strip())
    if missing:
        raise ResearchRecordError(f"缺少必填字段：{', '.join(missing)}")


class ResearchLog:
    def __init__(self, manager: StateManager) -> None:
        self.manager = manager

    def add_source(self, source: dict[str, Any]) -> dict[str, Any]:
        _require_fields(source, SOURCE_REQUIRED_FIELDS)
        sensitive_key = _find_sensitive_key(source)
        if sensitive_key:
            raise ResearchRecordError(f"调研记录不得保存敏感字段：{sensitive_key}")
        if source["source_type"] not in SOURCE_TYPES:
            raise ResearchRecordError(f"不支持的来源类型：{source['source_type']}")
        if source["evidence_category"] not in EVIDENCE_CATEGORIES:
            raise ResearchRecordError(f"不支持的证据类别：{source['evidence_category']}")
        try:
            date.fromisoformat(source["query_date"])
        except (TypeError, ValueError) as error:
            raise ResearchRecordError("query_date 必须使用 YYYY-MM-DD") from error
        parsed_url = urlparse(source["url"])
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ResearchRecordError("url 必须是有效的 http 或 https 地址")

        state = self.manager.ensure()
        sources = state.setdefault("research_sources", [])
        if any(item.get("source_id") == source["source_id"] for item in sources):
            return {"status": "unchanged", "source_id": source["source_id"]}

        stored = copy.deepcopy(source)
        stored["recorded_at"] = utc_now()
        sources.append(stored)
        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "action": "research_source_added",
                "summary": f"新增调研来源 {source['source_id']}",
            }
        )
        self.manager.save(state)
        return {"status": "created", "source_id": source["source_id"]}


class CaseIndex:
    """只保存已核验案例卡的脱敏索引，不保存共享记忆原文。"""

    def __init__(self, manager: StateManager) -> None:
        self.manager = manager

    def add_case(self, case: dict[str, Any]) -> dict[str, Any]:
        _require_fields(case, CASE_REQUIRED_FIELDS)
        sensitive_key = _find_sensitive_key(case)
        if sensitive_key:
            raise ResearchRecordError(f"案例索引不得保存敏感字段：{sensitive_key}")
        if any(key in case for key in ("shared_memory_raw", "raw_memory", "customer_name")):
            raise ResearchRecordError("案例索引不得保存共享记忆原文或真实客户名称")

        state = self.manager.ensure()
        case_index = state.setdefault("case_index", [])
        existing = next((item for item in case_index if item.get("case_id") == case["case_id"]), None)
        if existing:
            if existing.get("reviewed_version") == case["reviewed_version"]:
                return {"status": "unchanged", "case_id": case["case_id"]}
            version_history = existing.get("version_history", [])
            existing.update(copy.deepcopy(case))
            existing["version_history"] = version_history + [
                {
                    "version": case["reviewed_version"],
                    "reviewed_at": utc_now(),
                    "source_status": "verified_reference_only",
                }
            ]
            state.setdefault("history", []).append(
                {
                    "timestamp": utc_now(),
                    "action": "case_index_updated",
                    "summary": f"更新脱敏案例索引 {case['case_id']} 至 {case['reviewed_version']}",
                }
            )
            self.manager.save(state)
            return {"status": "updated", "case_id": case["case_id"]}

        stored = copy.deepcopy(case)
        stored["version_history"] = [
            {
                "version": case["reviewed_version"],
                "reviewed_at": utc_now(),
                "source_status": "verified_reference_only",
            }
        ]
        case_index.append(stored)
        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "action": "case_index_added",
                "summary": f"新增脱敏案例索引 {case['case_id']}",
            }
        )
        self.manager.save(state)
        return {"status": "created", "case_id": case["case_id"]}
