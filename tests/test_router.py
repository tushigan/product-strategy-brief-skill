import unittest

from scripts.router import detect_mode


class RouterTest(unittest.TestCase):
    def test_workshop_is_default(self):
        self.assertEqual(detect_mode("帮我做一个新品策略")["mode"], "workshop")

    def test_quick_start_keyword(self):
        self.assertEqual(detect_mode("快速给我一个框架")["mode"], "quick_start")

    def test_diagnose_keyword(self):
        self.assertEqual(detect_mode("帮我审一下这个策略")["mode"], "diagnose")

    def test_benchmark_is_reserved(self):
        self.assertEqual(detect_mode("我想对标竞品")["mode"], "benchmark")

    def test_forced_mode_wins(self):
        self.assertEqual(detect_mode("快速做", {"mode": "diagnose"})["mode"], "diagnose")


if __name__ == "__main__":
    unittest.main()

