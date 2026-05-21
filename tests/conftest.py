from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import BASE_URL, BROWSER, HEADLESS
from utils.driver_factory import get_driver
from utils.logger import get_logger
from utils.reporting import build_dashboard
from utils.screenshot import take_screenshot


logger = get_logger("pytest")


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=BROWSER)
    parser.addoption("--headless", action="store_true", default=HEADLESS)


def wait_for_server(url: str, timeout: int = 20) -> None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException:
            time.sleep(0.5)
    raise RuntimeError(f"Application did not start at {url}")


@pytest.fixture(scope="session", autouse=True)
def app_server():
    logger.info("Starting local Flask server for test session")
    process = subprocess.Popen(
        [str(Path(".venv/bin/python")), "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wait_for_server(BASE_URL)
    yield
    process.terminate()
    process.wait(timeout=10)
    logger.info("Stopped local Flask server")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    logger.info("Launching Selenium driver | browser=%s | headless=%s", browser, headless)
    driver_instance = get_driver(browser=browser, headless=headless)
    yield driver_instance
    driver_instance.quit()
    logger.info("Closed Selenium driver")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "driver" in item.fixturenames:
        driver_instance = item.funcargs["driver"]
        screenshot_name = item.name.replace("/", "_")
        logger.error("Test failed. Capturing screenshot for %s", screenshot_name)
        take_screenshot(driver_instance, screenshot_name)


def pytest_sessionfinish(session, exitstatus):
    logger.info("PyTest finished with exit status %s", exitstatus)
    build_dashboard()
