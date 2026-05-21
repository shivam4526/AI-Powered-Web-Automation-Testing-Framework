from __future__ import annotations

import os
import re
import subprocess

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import BRAVE_BINARY_PATH


def resolve_driver_version(browser: str) -> str | None:
    explicit_version = os.getenv("CHROMEDRIVER_VERSION")
    if explicit_version:
        return explicit_version

    binary_path = BRAVE_BINARY_PATH if browser == "brave" else None
    if not binary_path:
        return None

    try:
        version_output = subprocess.check_output([binary_path, "--version"], text=True).strip()
        major_match = re.search(r"(\d+)\.", version_output)
        if not major_match:
            return None
        milestone = major_match.group(1)
        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json",
            timeout=20,
        )
        response.raise_for_status()
        milestones = response.json().get("milestones", {})
        version_data = milestones.get(milestone)
        if version_data:
            return version_data.get("version")
    except (OSError, requests.RequestException, subprocess.CalledProcessError):
        return None

    return None


def get_driver(browser="brave", headless=False):
    options = webdriver.ChromeOptions()

    if browser == "brave":
        options.binary_location = BRAVE_BINARY_PATH

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver_version = resolve_driver_version(browser)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version=driver_version).install()),
        options=options,
    )
    return driver
