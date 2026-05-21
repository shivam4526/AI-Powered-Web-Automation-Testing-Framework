from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ai_test_generator import discover_application_capabilities, save_cases


def build_summary(stdout: str, generated_files: list[str]) -> dict:
    passed = 0
    failed = 0
    errors = 0
    collected = 0

    match = re.search(r"(\d+)\s+passed", stdout)
    if match:
        passed = int(match.group(1))

    match = re.search(r"(\d+)\s+failed", stdout)
    if match:
        failed = int(match.group(1))

    match = re.search(r"(\d+)\s+errors?", stdout)
    if match:
        errors = int(match.group(1))

    if passed or failed or errors:
        collected = passed + failed + errors

    return {
        "application": discover_application_capabilities(),
        "generated_test_files": generated_files,
        "result_summary": {
            "collected": collected,
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
    }


def main() -> int:
    save_cases()
    generated_files = [
        "tests/generated/test_ai_generated_api.py",
        "tests/generated/test_ai_generated_ui.py",
    ]

    command = [
        str(Path(".venv/bin/pytest")),
        *generated_files,
        "--browser=brave",
        "--headless",
        "--html=reports/report.html",
        "--self-contained-html",
        "--alluredir=reports/allure-results",
    ]

    env = os.environ.copy()
    env.setdefault("HEADLESS", "true")
    env.setdefault(
        "BRAVE_BINARY_PATH",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    )

    completed = subprocess.run(command, text=True, capture_output=True, env=env)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)

    summary_path = Path("reports/ai_execution_summary.json")
    summary_path.write_text(
        json.dumps(build_summary(completed.stdout + completed.stderr, generated_files), indent=2),
        encoding="utf-8",
    )
    print(f"\nSaved autonomous execution summary to {summary_path}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
