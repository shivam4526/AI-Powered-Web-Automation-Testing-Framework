from __future__ import annotations

import json
from pprint import pformat
from pathlib import Path

from app.main import app


GENERATED_DIR = Path("tests/generated")


def discover_application_capabilities() -> dict:
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda item: item.rule):
        routes.append(
            {
                "path": rule.rule,
                "methods": sorted(method for method in rule.methods if method not in {"HEAD", "OPTIONS"}),
                "endpoint": rule.endpoint,
            }
        )

    return {
        "app_name": "AI Commerce Demo",
        "base_url": "http://127.0.0.1:5000",
        "routes": routes,
        "credentials": {"username": "demouser", "password": "Password123"},
        "ui_capabilities": ["login", "search", "add_to_cart", "checkout"],
    }


def generate_cases() -> list[dict]:
    app_context = discover_application_capabilities()
    return [
        {
            "id": "api_login_positive",
            "layer": "api",
            "feature": "login",
            "type": "positive",
            "title": "AI generated API test: valid user can log in",
            "route": "/login",
            "input": app_context["credentials"],
            "expected_status": 200,
            "expected_key": "message",
            "expected_value": "Login successful",
        },
        {
            "id": "api_products_requires_auth",
            "layer": "api",
            "feature": "products",
            "type": "negative",
            "title": "AI generated API test: products endpoint rejects anonymous access",
            "route": "/products",
            "expected_status": 401,
            "expected_key": "error",
            "expected_value": "Authentication required",
        },
        {
            "id": "api_checkout_positive",
            "layer": "api",
            "feature": "checkout",
            "type": "positive",
            "title": "AI generated API test: logged in user can add product and checkout",
            "route": "/checkout",
            "setup": {"login": True, "add_to_cart": {"product_id": 1, "quantity": 1}},
            "expected_status": 200,
            "expected_key": "message",
            "expected_value": "Checkout complete",
        },
        {
            "id": "ui_login_positive",
            "layer": "ui",
            "feature": "login",
            "type": "positive",
            "title": "AI generated UI test: valid login updates the session banner",
            "input": app_context["credentials"],
            "expected_text": "Logged in as demouser",
        },
        {
            "id": "ui_search_product",
            "layer": "ui",
            "feature": "search",
            "type": "positive",
            "title": "AI generated UI test: searching for Laptop narrows products to one card",
            "search_term": "Laptop",
            "expected_count": 1,
        },
        {
            "id": "ui_add_to_cart",
            "layer": "ui",
            "feature": "cart",
            "type": "positive",
            "title": "AI generated UI test: adding a product creates a cart item",
            "expected_min_cart_items": 1,
        },
        {
            "id": "ui_checkout",
            "layer": "ui",
            "feature": "checkout",
            "type": "positive",
            "title": "AI generated UI test: checkout displays the completion message",
            "expected_text": "Checkout complete",
        },
    ]


def render_generated_api_tests(api_cases: list[dict]) -> str:
    return f"""import pytest
import requests


CASES = {pformat(api_cases, width=100)}


def _login(session, base_url, credentials):
    response = session.post(f"{{base_url}}/login", json=credentials, timeout=5)
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.generated
@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_ai_generated_api_cases(base_url, case):
    if case["id"] == "api_login_positive":
        response = requests.post(f"{{base_url}}/login", json=case["input"], timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    if case["id"] == "api_products_requires_auth":
        response = requests.get(f"{{base_url}}{{case['route']}}", timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    if case["id"] == "api_checkout_positive":
        session = requests.Session()
        _login(session, base_url, {{"username": "demouser", "password": "Password123"}})
        setup = case["setup"]["add_to_cart"]
        add_response = session.post(f"{{base_url}}/cart", json=setup, timeout=5)
        assert add_response.status_code == 200
        response = session.post(f"{{base_url}}{{case['route']}}", timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    raise AssertionError(f"Unhandled API case: {{case['id']}}")
"""


def render_generated_ui_tests(ui_cases: list[dict]) -> str:
    return f"""import pytest

from pages.login_page import LoginPage
from pages.shop_page import ShopPage


CASES = {pformat(ui_cases, width=100)}


def _login(login_page):
    login_page.open()
    login_page.login("demouser", "Password123")
    login_page.wait_for_login_success()


@pytest.mark.ui
@pytest.mark.generated
@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_ai_generated_ui_cases(driver, base_url, case):
    login_page = LoginPage(driver, base_url)
    shop_page = ShopPage(driver, base_url)

    if case["id"] == "ui_login_positive":
        login_page.open()
        login_page.login(case["input"]["username"], case["input"]["password"])
        assert case["expected_text"] in login_page.wait_for_login_success()
        return

    _login(login_page)

    if case["id"] == "ui_search_product":
        shop_page.search(case["search_term"])
        shop_page.wait_for_product_count(case["expected_count"])
        assert len(driver.find_elements(*shop_page.PRODUCT_CARDS)) == case["expected_count"]
        return

    if case["id"] == "ui_add_to_cart":
        shop_page.wait_for_products()
        shop_page.add_first_product_to_cart()
        shop_page.wait_for_cart_items()
        assert len(driver.find_elements(*shop_page.CART_ITEMS)) >= case["expected_min_cart_items"]
        return

    if case["id"] == "ui_checkout":
        shop_page.wait_for_products()
        shop_page.add_first_product_to_cart()
        shop_page.wait_for_cart_items()
        shop_page.click(shop_page.CHECKOUT_BUTTON)
        assert case["expected_text"] in shop_page.text_of(shop_page.CHECKOUT_MESSAGE)
        return

    raise AssertionError(f"Unhandled UI case: {{case['id']}}")
"""


def write_generated_tests(cases: list[dict]) -> list[str]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / "__init__.py").write_text("", encoding="utf-8")

    api_cases = [case for case in cases if case["layer"] == "api"]
    ui_cases = [case for case in cases if case["layer"] == "ui"]

    api_file = GENERATED_DIR / "test_ai_generated_api.py"
    ui_file = GENERATED_DIR / "test_ai_generated_ui.py"
    api_file.write_text(render_generated_api_tests(api_cases), encoding="utf-8")
    ui_file.write_text(render_generated_ui_tests(ui_cases), encoding="utf-8")
    return [str(api_file), str(ui_file)]


def save_cases(output_path: str = "reports/ai_generated_cases.json") -> Path:
    cases = generate_cases()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    write_generated_tests(cases)
    return path


if __name__ == "__main__":
    saved = save_cases()
    print(f"Saved AI-generated test cases to {saved} and created runnable tests in {GENERATED_DIR}")
