import os


BROWSER = os.getenv("BROWSER", "brave")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
BRAVE_BINARY_PATH = os.getenv(
    "BRAVE_BINARY_PATH",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
)
