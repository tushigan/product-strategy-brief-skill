"""快速启动模式：少问，但不绕过门槛。"""

from __future__ import annotations

from typing import Any

from scripts.state_manager import StateManager


QUICK_QUESTIONS = (
    ("产品问题", "一句话说明当前产品或渠道要解决的问题？"),
    ("开发目标", "这轮开发最想验证或改善什么？"),
    ("目标消费者", "最核心的消费者是谁？"),
    ("主要渠道或销售场景", "准备在哪个渠道或场景销售？"),
    ("目标保质期要求", "目标保质期和主要流通条件是什么？"),
)


class QuickStartMode:
    def __init__(self, manager: StateManager, state: dict[str, Any]) -> None:
        self.manager = manager
        self.state = state

    def handle(self, user_input: str) -> dict[str, Any]:
        meta = self.state.setdefault("meta", {})
        pending = meta.get("pending_quick_question")
        if pending and user_input.strip():
            self.state.setdefault("brief", {})[pending["key"]] = user_input.strip()
            meta.pop("pending_quick_question", None)
            self.manager.save(self.state)
        answered = self.state.setdefault("quick_answers", {})
        next_item = next(((key, question) for key, question in QUICK_QUESTIONS if not str(answered.get(key, self.state.get("brief", {}).get(key, ""))).strip()), None)
        if next_item is None:
            missing = [key for key in ("目标保质期类型", "可用产线与关键工艺能力", "明确禁用或受限工艺") if not str(self.state.get("brief", {}).get(key, "")).strip()]
            self.state["meta"]["status"] = "pending" if missing else "in_progress"
            self.manager.save(self.state)
            return {"status": "continue", "mode": "quick_start", "message": "快速信息已收集，但仍需补齐必要门槛。", "missing_fields": missing, "progress": 1.0 if not missing else 0.7, "project_json_path": str(self.manager.json_path)}
        key, question = next_item
        meta["pending_quick_question"] = {"key": key, "question": question}
        meta["current_mode"] = "quick_start"
        meta["status"] = "in_progress"
        self.manager.save(self.state)
        return {"status": "continue", "mode": "quick_start", "message": "快速启动只压缩提问，不跳过 Brief 门槛。", "next_question": question, "progress": round(len([k for k, _ in QUICK_QUESTIONS if str(self.state.get("brief", {}).get(k, "")).strip()]) / len(QUICK_QUESTIONS), 2), "project_json_path": str(self.manager.json_path)}

