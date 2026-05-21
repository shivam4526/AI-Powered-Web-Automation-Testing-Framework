from __future__ import annotations

import json
from pathlib import Path


def build_dashboard(report_dir: str = "reports") -> Path:
    report_path = Path(report_dir)
    dashboard_path = report_path / "dashboard.html"
    ai_cases_path = report_path / "ai_generated_cases.json"
    ai_summary_path = report_path / "ai_execution_summary.json"
    log_path = report_path / "logs" / "test_execution.log"
    screenshots_dir = report_path / "screenshots"

    ai_cases = []
    if ai_cases_path.exists():
        ai_cases = json.loads(ai_cases_path.read_text())

    ai_summary = {}
    if ai_summary_path.exists():
        ai_summary = json.loads(ai_summary_path.read_text())

    screenshots = sorted(p.name for p in screenshots_dir.glob("*.png")) if screenshots_dir.exists() else []
    log_excerpt = ""
    if log_path.exists():
        lines = log_path.read_text().splitlines()
        log_excerpt = "\n".join(lines[-20:])

    dashboard_path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f7f8fa; color: #1f2937; }}
        .card {{ background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 10px 30px rgba(0,0,0,0.06); }}
        code, pre {{ background: #111827; color: #f9fafb; padding: 0.2rem 0.4rem; border-radius: 6px; }}
        pre {{ padding: 1rem; white-space: pre-wrap; }}
        ul {{ padding-left: 1.1rem; }}
    </style>
</head>
<body>
    <h1>Automation Results Dashboard</h1>
    <div class="card">
        <h2>Generated Artifacts</h2>
        <ul>
            <li>PyTest HTML report: <code>reports/report.html</code></li>
            <li>Allure results folder: <code>reports/allure-results</code></li>
            <li>AI test cases: <code>reports/ai_generated_cases.json</code></li>
            <li>Execution log: <code>reports/logs/test_execution.log</code></li>
        </ul>
    </div>
    <div class="card">
        <h2>Autonomous Execution Summary</h2>
        <pre>{json.dumps(ai_summary, indent=2) if ai_summary else "Run run_autonomous_ai_testing.py to generate and execute tests automatically."}</pre>
    </div>
    <div class="card">
        <h2>AI Test Cases</h2>
        <pre>{json.dumps(ai_cases, indent=2)}</pre>
    </div>
    <div class="card">
        <h2>Failure Screenshots</h2>
        <pre>{json.dumps(screenshots, indent=2)}</pre>
    </div>
    <div class="card">
        <h2>Recent Execution Logs</h2>
        <pre>{log_excerpt or "No log entries yet."}</pre>
    </div>
</body>
</html>""",
        encoding="utf-8",
    )
    return dashboard_path
