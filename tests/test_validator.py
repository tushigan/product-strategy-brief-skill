import unittest

from scripts.state_manager import empty_state
from scripts.validator import validate_brief, validate_state, validate_three_circle


def complete_brief():
    return {
        "产品问题": "目标渠道缺少适合通勤早餐的预包装产品",
        "开发目标": "验证一款可稳定流通的早餐场景产品",
        "主要渠道或销售场景": "便利店早餐货架和办公室通勤",
        "目标消费者": "工作日早晨没有完整早餐时间的上班族",
        "目标保质期要求": "常温流通 60 天",
        "可用产线与关键工艺能力": "现有平板线和基础包装线，具体夹心能力待核实",
        "明确禁用或受限工艺": "未经确认的在线注酱工艺暂不采用",
        "目标保质期类型": "中保",
    }


class ValidatorTest(unittest.TestCase):
    def test_missing_brief_is_invalid(self):
        result = validate_brief({"产品问题": "只有这一项"})
        self.assertFalse(result["valid"])
        self.assertIn("开发目标", result["missing_fields"])

    def test_invalid_shelf_life_type_is_rejected(self):
        brief = complete_brief()
        brief["目标保质期类型"] = "超长保"
        result = validate_brief(brief)
        self.assertFalse(result["valid"])
        self.assertIn("目标保质期类型", result["invalid_fields"])

    def test_three_circle_requires_intersection(self):
        state = empty_state("三圈测试")
        state["three_circle"]["可做"]["status"] = "confirmed"
        state["three_circle"]["想做"]["status"] = "confirmed"
        state["three_circle"]["能做"]["status"] = "stretch"
        state["three_circle"]["intersection"]["status"] = "pending"
        result = validate_three_circle(state)
        self.assertFalse(result["can_recommend"])

    def test_three_circle_recommended_when_all_gates_pass(self):
        state = empty_state("推荐测试")
        state["brief"] = complete_brief()
        state["three_circle"]["可做"]["status"] = "confirmed"
        state["three_circle"]["想做"]["status"] = "confirmed"
        state["three_circle"]["能做"]["status"] = "current"
        state["three_circle"]["intersection"]["status"] = "recommended"
        result = validate_state(state)
        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
