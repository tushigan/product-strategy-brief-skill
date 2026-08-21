import tempfile
import unittest

from scripts.research_log import CaseIndex, ResearchLog, ResearchRecordError
from scripts.state_manager import StateManager


def valid_source(**overrides):
    source = {
        "source_id": "source-001",
        "question": "消费者是否关注便携早餐",
        "source_type": "xiaohongshu",
        "platform": "示例社交平台",
        "query_date": "2026-08-21",
        "url": "https://example.com/note/1",
        "evidence": "公开页面中出现多个便携早餐使用场景",
        "sample_boundary": "仅为公开可见的少量内容样本",
        "allowed_statement": "可作为消费场景趋势信号",
        "prohibited_extrapolation": "不得外推为全国销量或市场规模",
        "evidence_category": "trend_signal",
    }
    source.update(overrides)
    return source


class ResearchLogTest(unittest.TestCase):
    def test_missing_required_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            log = ResearchLog(StateManager(temp))
            for field in ("source_type", "query_date", "url", "evidence_category", "prohibited_extrapolation"):
                source = valid_source()
                source.pop(field)
                with self.subTest(field=field):
                    with self.assertRaises(ResearchRecordError):
                        log.add_source(source)

    def test_source_id_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            log = ResearchLog(manager)
            first = log.add_source(valid_source())
            second = log.add_source(valid_source(evidence="更新后的页面摘录"))

            self.assertEqual(first["status"], "created")
            self.assertEqual(second["status"], "unchanged")
            self.assertEqual(len(manager.load()["research_sources"]), 1)
            self.assertEqual(manager.load()["research_sources"][0]["evidence"], valid_source()["evidence"])

    def test_credentials_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            log = ResearchLog(StateManager(temp))
            with self.assertRaises(ResearchRecordError):
                log.add_source(valid_source(cookie="private-value"))

    def test_case_index_validates_and_records_versions_without_raw_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            cases = CaseIndex(manager)
            result = cases.add_case(
                {
                    "case_id": "case-001",
                    "title": "脱敏的渠道规格调整案例",
                    "source_reference": "受控项目资料索引",
                    "evidence_level": "verified_primary",
                    "project_stage": "策略确认",
                    "transferable_learning": "先确认渠道约束，再确定产品规格",
                    "non_transferable_boundary": "不能外推到所有品类",
                    "client_use_limit": "仅可使用脱敏方法结论",
                    "introduced_version": "1.0.0",
                    "reviewed_version": "1.0.0",
                }
            )

            self.assertEqual(result["status"], "created")
            state = manager.load()
            self.assertEqual(state["case_index"][0]["version_history"][0]["version"], "1.0.0")
            self.assertNotIn("shared_memory_raw", state["case_index"][0])

    def test_case_index_appends_a_new_review_version(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            cases = CaseIndex(manager)
            base = {
                "case_id": "case-002",
                "title": "脱敏的产品规格案例",
                "source_reference": "受控项目资料索引",
                "evidence_level": "verified_primary",
                "project_stage": "策略确认",
                "transferable_learning": "先判断三圈交集",
                "non_transferable_boundary": "不能外推到其他渠道",
                "client_use_limit": "仅可使用脱敏方法结论",
                "introduced_version": "1.0.0",
                "reviewed_version": "1.0.0",
            }
            cases.add_case(base)
            updated = dict(base, reviewed_version="1.1.0", transferable_learning="先判断三圈交集，再验证最小投入")
            result = cases.add_case(updated)

            self.assertEqual(result["status"], "updated")
            stored = manager.load()["case_index"][0]
            self.assertEqual(stored["reviewed_version"], "1.1.0")
            self.assertEqual([item["version"] for item in stored["version_history"]], ["1.0.0", "1.1.0"])


if __name__ == "__main__":
    unittest.main()
