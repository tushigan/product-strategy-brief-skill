"""项目 JSON 状态的原子读写和历史记录。"""

from __future__ import annotations

import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def empty_state(project_name: str = "未命名项目") -> dict[str, Any]:
    return {
        "meta": {
            "project_id": str(uuid4()),
            "project_name": project_name,
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "current_mode": "workshop",
            "status": "draft",
            "knowledge_version": "kb-v1"
        },
        "brief": {
            "产品问题": "",
            "开发目标": "",
            "主要渠道或销售场景": "",
            "目标消费者": "",
            "目标保质期要求": "",
            "可用产线与关键工艺能力": "",
            "明确禁用或受限工艺": "",
            "目标保质期类型": ""
        },
        "strategy": {},
        "three_circle": {
            "可做": {"status": "missing", "evidence_ids": [], "assumptions": [], "gaps": []},
            "想做": {"status": "missing", "evidence_ids": [], "gaps": []},
            "能做": {"status": "unknown", "evidence_ids": [], "gaps": []},
            "intersection": {
                "status": "pending",
                "strategy_fit": "",
                "trade_offs": [],
                "minimum_next_validation": [],
                "decision_reason": ""
            }
        },
        "outputs": {"lark_doc_url": "", "generated_at": ""},
        "research_sources": [],
        "case_index": [],
        "history": []
    }


class StateManager:
    """以项目目录下的 project_state.json 作为唯一状态文件。"""

    def __init__(self, project_path: str | Path, filename: str = "project_state.json") -> None:
        self.project_path = Path(project_path).expanduser().resolve()
        self.json_path = self.project_path / filename

    def load(self) -> dict[str, Any] | None:
        if not self.json_path.exists():
            return None
        with self.json_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def ensure(self, project_name: str = "未命名项目") -> dict[str, Any]:
        state = self.load()
        if state is None:
            state = empty_state(project_name)
            self.save(state)
        return state

    def save(self, data: dict[str, Any]) -> Path:
        self.project_path.mkdir(parents=True, exist_ok=True)
        payload = copy.deepcopy(data)
        payload.setdefault("meta", {})["updated_at"] = utc_now()
        fd, temp_name = tempfile.mkstemp(prefix=".project_state.", suffix=".tmp", dir=self.project_path)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.json_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return self.json_path

    def add_history(self, action: str, summary: str, *, mode: str | None = None) -> dict[str, Any]:
        state = self.ensure()
        event = {"timestamp": utc_now(), "action": action, "summary": summary}
        if mode:
            event["mode"] = mode
        state.setdefault("history", []).append(event)
        self.save(state)
        return event
