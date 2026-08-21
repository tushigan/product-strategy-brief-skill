"""工作坊模式：Brief → 三圈 → 交集。"""

from __future__ import annotations

from typing import Any

from scripts.state_manager import StateManager
from scripts.validator import REQUIRED_BRIEF_FIELDS, validate_brief, validate_three_circle


BRIEF_QUESTIONS = {
    "产品问题": "当前产品、消费者、渠道或货架上要解决的具体问题是什么？",
    "开发目标": "本轮产品开发要建立、改善或验证什么？",
    "主要渠道或销售场景": "主要在哪个渠道销售，或服务什么具体销售场景？",
    "目标消费者": "核心消费者是谁？与产品有关的需求或行为是什么？",
    "目标保质期要求": "目标保质期多长？是常温还是冷藏？主要流通条件是什么？",
    "可用产线与关键工艺能力": "当前已确认的产线、设备和关键工艺能力有哪些？",
    "明确禁用或受限工艺": "明确不能做、尚未确认或需要额外设备的工艺有哪些？",
    "目标保质期类型": "这属于短保、中保还是长保？",
}


def _set_path(data: dict[str, Any], path: tuple[str, ...], value: str) -> None:
    current = data
    for key in path[:-1]:
        current = current.setdefault(key, {})
    current[path[-1]] = value


class WorkshopMode:
    def __init__(self, manager: StateManager, state: dict[str, Any]) -> None:
        self.manager = manager
        self.state = state

    def _next_prompt(self) -> dict[str, str] | None:
        brief = self.state.setdefault("brief", {})
        for key in REQUIRED_BRIEF_FIELDS:
            if not str(brief.get(key, "")).strip():
                return {"target": f"brief.{key}", "question": BRIEF_QUESTIONS[key]}
        circles = self.state.setdefault("three_circle", {})
        if not str(circles.get("可做", {}).get("market_opportunity", "")).strip():
            return {"target": "three_circle.可做.market_opportunity", "question": "可做：市场、消费者、渠道或竞争中，具体机会是什么？请说明证据或当前只是信号。"}
        if not str(circles.get("想做", {}).get("client_intent", "")).strip():
            return {"target": "three_circle.想做.client_intent", "question": "想做：客户为什么想做？这件事对应什么战略重点，愿意投入什么资源？"}
        if not str(circles.get("能做", {}).get("current_capability", "")).strip():
            return {"target": "three_circle.能做.current_capability", "question": "能做：现有产线、设备、供应链能承接到什么程度？需要怎样的‘踮脚’？"}
        if not str(circles.get("intersection", {}).get("strategy_fit", "")).strip():
            return {"target": "three_circle.intersection.strategy_fit", "question": "三圈交集：三圈重叠的部分是什么？为什么它是当前该做的方向？"}
        return None

    def _progress(self) -> float:
        prompt = self._next_prompt()
        if prompt is None:
            return 1.0
        total = len(REQUIRED_BRIEF_FIELDS) + 4
        completed = total
        if prompt["target"].startswith("brief."):
            completed = list(REQUIRED_BRIEF_FIELDS).index(prompt["target"].split(".", 1)[1])
        else:
            completed = len(REQUIRED_BRIEF_FIELDS)
            circles = self.state["three_circle"]
            completed += sum(bool(str(circles.get("可做", {}).get(k, "")).strip()) for k in ("market_opportunity",))
            completed += sum(bool(str(circles.get("想做", {}).get(k, "")).strip()) for k in ("client_intent",))
            completed += sum(bool(str(circles.get("能做", {}).get(k, "")).strip()) for k in ("current_capability",))
            completed += sum(bool(str(circles.get("intersection", {}).get(k, "")).strip()) for k in ("strategy_fit",))
        return round(completed / total, 2)

    def handle(self, user_input: str) -> dict[str, Any]:
        pending = self.state.setdefault("meta", {}).get("pending_question")
        if pending and user_input.strip():
            answer = user_input.strip()
            if pending["target"] == "confirmation":
                if any(token in answer for token in ("确认", "可以", "准确", "按这个", "推进")):
                    circle_result = validate_three_circle(self.state)
                    if circle_result["blocking_reasons"]:
                        self.state["meta"]["status"] = "pending"
                        self.state["meta"]["pending_question"] = {"target": "confirmation", "question": "三圈仍有阻断，不能确认正式策略。请先补齐或修正阻断项。"}
                        self.manager.save(self.state)
                        return self._response("当前不能进入正式策略确认。", self.state["meta"]["pending_question"]["question"])
                    self.state["three_circle"]["intersection"]["status"] = "recommended"
                    self.state["meta"]["status"] = "strategy_confirmed"
                    self.state["meta"].pop("pending_question", None)
                    self.manager.save(self.state)
                    self.manager.add_history("strategy_confirmed", "用户确认三圈交集", mode="workshop")
                    return {"status": "success", "mode": "workshop", "message": "三圈交集已确认，可进入产品开发策略整理。", "progress": 1.0, "project_json_path": str(self.manager.json_path)}
                return self._response("还没有记录确认。", "如果三圈交集准确，请回复“确认”或“按这个推进”；如果不准确，请指出需要修改的圈。")
            _set_path(self.state, tuple(pending["target"].split(".")), answer)
            if pending["target"] == "three_circle.可做.market_opportunity":
                self.state["three_circle"]["可做"]["status"] = "confirmed"
                self._add_evidence_reference("可做", "market")
            elif pending["target"] == "three_circle.想做.client_intent":
                self.state["three_circle"]["想做"]["status"] = "confirmed"
                self._add_evidence_reference("想做", "intent")
            elif pending["target"] == "three_circle.能做.current_capability":
                text = answer.lower()
                self.state["three_circle"]["能做"]["status"] = "stretch" if any(x in text for x in ("踮", "调整", "改造", "新增")) else "current"
                self._add_evidence_reference("能做", "capability")
            self.state["meta"].pop("pending_question", None)
            self.manager.save(self.state)
            self.manager.add_history("workshop_answer", pending["target"], mode="workshop")
        prompt = self._next_prompt()
        if prompt is None:
            circle_result = validate_three_circle(self.state)
            self.state["meta"]["status"] = "pending_confirmation"
            self.state["meta"]["pending_question"] = {"target": "confirmation", "question": "三圈交集已形成。是否确认按当前交集进入策略确认？"}
            self.state["three_circle"]["intersection"]["status"] = "pending" if not circle_result["can_recommend"] else "conditional"
            self.manager.save(self.state)
            return self._response("完成信息采集，请确认是否按当前三圈交集推进。", self.state["meta"]["pending_question"]["question"])
        self.state["meta"]["pending_question"] = prompt
        self.state["meta"]["current_mode"] = "workshop"
        self.state["meta"]["status"] = "in_progress"
        self.manager.save(self.state)
        return self._response("我们按三圈定位逐步梳理。", prompt["question"])

    def _add_evidence_reference(self, circle_name: str, prefix: str) -> None:
        circle = self.state["three_circle"][circle_name]
        evidence_ids = circle.setdefault("evidence_ids", [])
        evidence_id = f"workshop-{prefix}-{len(evidence_ids) + 1:03d}"
        if evidence_id not in evidence_ids:
            evidence_ids.append(evidence_id)

    def _response(self, message: str, question: str) -> dict[str, Any]:
        return {
            "status": "continue",
            "mode": "workshop",
            "message": message,
            "next_question": question,
            "progress": self._progress(),
            "project_json_path": str(self.manager.json_path),
        }
