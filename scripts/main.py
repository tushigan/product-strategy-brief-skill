"""Skill 命令行入口。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.modes.diagnose import DiagnoseMode
from scripts.modes.quick_start import QuickStartMode
from scripts.modes.workshop import WorkshopMode
from scripts.router import RESERVED_MODES, detect_mode
from scripts.state_manager import StateManager


def run(user_input: str, project_path: str | None = None, project_json: str | None = None, mode: str | None = None) -> dict[str, Any]:
    if project_json:
        json_path = Path(project_json).expanduser().resolve()
        manager = StateManager(json_path.parent, filename=json_path.name)
    else:
        manager = StateManager(project_path or Path.cwd())
    has_existing_project = manager.json_path.exists()
    state = manager.ensure()
    context = {
        "mode": mode,
        "has_existing_project": has_existing_project,
        "project_status": state.get("meta", {}).get("status"),
        "last_mode": state.get("meta", {}).get("current_mode"),
    }
    route = detect_mode(user_input, context)
    selected = route["mode"]
    if selected in RESERVED_MODES:
        return {"status": "reserved", "mode": selected, "message": f"{selected} 模式已预留，当前版本先支持工作坊、诊断和快速启动。", "required_references": route["required_references"]}
    if selected == "diagnose":
        result = DiagnoseMode(state).run()
    elif selected == "quick_start":
        result = QuickStartMode(manager, state).handle(user_input)
    else:
        result = WorkshopMode(manager, state).handle(user_input)
    result["route_reason"] = route["reason"]
    result["required_references"] = route["required_references"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="产品开发策略 Brief Skill")
    parser.add_argument("--input", default="", help="本轮用户输入")
    parser.add_argument("--project-path", help="项目状态保存目录")
    parser.add_argument("--project-json", help="已有 project_state.json 路径")
    parser.add_argument("--mode", choices=("workshop", "diagnose", "quick-start", "benchmark", "refine"))
    args = parser.parse_args()
    result = run(args.input, args.project_path, args.project_json, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
