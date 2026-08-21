import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MainEntrypointTest(unittest.TestCase):
    def test_direct_script_execution_creates_project_state(self):
        repository_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(repository_root / "scripts" / "main.py"),
                    "--input",
                    "我想快速做一个预包装烘焙新品策略",
                    "--project-path",
                    temp,
                ],
                cwd=repository_root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["mode"], "quick_start")
            self.assertTrue((Path(temp) / "project_state.json").exists())

    def test_project_json_uses_the_exact_filename(self):
        repository_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            custom_json = Path(temp) / "自定义策略状态.json"
            custom_json.write_text(
                json.dumps(
                    {
                        "meta": {"status": "draft", "current_mode": "workshop"},
                        "brief": {},
                        "three_circle": {},
                        "outputs": {},
                        "research_sources": [],
                        "case_index": [],
                        "history": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(repository_root / "scripts" / "main.py"),
                    "--mode",
                    "diagnose",
                    "--project-json",
                    str(custom_json),
                ],
                cwd=repository_root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(custom_json.exists())
            self.assertFalse((Path(temp) / "project_state.json").exists())


if __name__ == "__main__":
    unittest.main()
