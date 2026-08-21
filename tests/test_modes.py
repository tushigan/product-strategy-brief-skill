import tempfile
import unittest

from scripts.modes.diagnose import DiagnoseMode
from scripts.modes.quick_start import QuickStartMode
from scripts.modes.workshop import WorkshopMode
from scripts.state_manager import StateManager, empty_state


class ModesTest(unittest.TestCase):
    def test_workshop_starts_with_first_brief_question(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            state = manager.ensure("工作坊测试")
            result = WorkshopMode(manager, state).handle("")
            self.assertEqual(result["mode"], "workshop")
            self.assertIn("产品", result["next_question"])

    def test_quick_start_does_not_skip_remaining_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            state = manager.ensure("快速测试")
            mode = QuickStartMode(manager, state)
            result = mode.handle("")
            self.assertEqual(result["mode"], "quick_start")
            for answer in ("产品问题", "开发目标", "目标人群", "便利店", "常温 60 天"):
                result = mode.handle(answer)
            self.assertIn("missing_fields", result)
            self.assertIn("可用产线与关键工艺能力", result["missing_fields"])

    def test_diagnose_reports_missing_brief(self):
        result = DiagnoseMode(empty_state("诊断测试")).run()
        self.assertFalse(result["can_recommend"])
        self.assertGreater(len(result["issues"]), 0)

    def test_workshop_confirmation_changes_state(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            state = manager.ensure("确认测试")
            state["brief"] = {
                "产品问题": "问题",
                "开发目标": "目标",
                "主要渠道或销售场景": "便利店",
                "目标消费者": "上班族",
                "目标保质期要求": "常温 60 天",
                "可用产线与关键工艺能力": "现有平板线",
                "明确禁用或受限工艺": "未经确认的注酱工艺",
                "目标保质期类型": "中保",
            }
            state["three_circle"]["可做"].update({"status": "confirmed", "market_opportunity": "机会"})
            state["three_circle"]["想做"].update({"status": "confirmed", "client_intent": "意愿"})
            state["three_circle"]["能做"].update({"status": "current", "current_capability": "能力"})
            state["three_circle"]["intersection"]["strategy_fit"] = "交集"
            manager.save(state)
            mode = WorkshopMode(manager, state)
            mode.handle("")
            result = mode.handle("确认")
            self.assertEqual(result["status"], "success")
            self.assertEqual(manager.load()["meta"]["status"], "strategy_confirmed")
            self.assertEqual(manager.load()["three_circle"]["intersection"]["status"], "recommended")


if __name__ == "__main__":
    unittest.main()
