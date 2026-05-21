from pathlib import Path


def take_screenshot(driver, name):
    screenshots_dir = Path("reports/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(screenshots_dir / f"{name}.png"))
