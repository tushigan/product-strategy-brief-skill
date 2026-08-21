import json
import tempfile
import unittest
from pathlib import Path

from scripts.state_manager import StateManager, empty_state


class StateManagerTest(unittest.TestCase):
    def test_save_is_loadable_and_updates_timestamp(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            state = empty_state("测试项目")
            path = manager.save(state)
            self.assertTrue(path.exists())
            loaded = manager.load()
            self.assertEqual(loaded["meta"]["project_name"], "测试项目")
            self.assertTrue(loaded["meta"]["updated_at"])

    def test_add_history_is_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = StateManager(temp)
            manager.ensure("历史测试")
            event = manager.add_history("brief_check", "完成 Brief 检查", mode="workshop")
            loaded = manager.load()
            self.assertEqual(loaded["history"][0]["action"], event["action"])
            self.assertEqual(loaded["history"][0]["mode"], "workshop")


if __name__ == "__main__":
    unittest.main()

