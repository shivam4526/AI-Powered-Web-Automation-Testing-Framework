# AI-Powered Web Application with Integrated Automation Testing Framework

This project bundles a Flask e-commerce demo app with a Selenium, PyTest, and API automation framework that runs on Brave Browser through ChromeDriver. It also includes an autonomous AI-style test engine that generates runnable tests by itself and then executes them.

## Features

- Login and logout
- Product listing and search
- Add to cart and mock checkout
- UI automation on Brave Browser
- API testing with `requests`
- AI-style generated test cases
- Autonomous generation of runnable PyTest files
- One-command AI generation + execution flow
- PyTest HTML and Allure reporting
- Execution logs and screenshots on failure
- GitHub Actions CI with headless Brave support

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai_test_generator.py
python app.py
```

Open `http://127.0.0.1:5000`.

## Demo Credentials

- Username: `demouser`
- Password: `Password123`

## Run Tests on Brave

```bash
pytest --browser=brave --html=reports/report.html --self-contained-html --alluredir=reports/allure-results
```

## Run Autonomous AI Test Generation And Execution

```bash
python run_autonomous_ai_testing.py
```

This command will:

- inspect the application routes and capabilities
- generate AI-designed test cases
- write runnable tests into `tests/generated/`
- execute those generated tests on Brave in headless mode
- save a machine-readable result summary to `reports/ai_execution_summary.json`

## Headless Mode

```bash
HEADLESS=true pytest --browser=brave --headless --html=reports/report.html --self-contained-html --alluredir=reports/allure-results
```

## Outputs

- HTML report: `reports/report.html`
- Allure results: `reports/allure-results/`
- AI cases: `reports/ai_generated_cases.json`
- AI execution summary: `reports/ai_execution_summary.json`
- Logs: `reports/logs/test_execution.log`
- Screenshots: `reports/screenshots/`
- Dashboard: `reports/dashboard.html`
