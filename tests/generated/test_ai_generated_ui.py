import pytest

from pages.login_page import LoginPage
from pages.shop_page import ShopPage


CASES = [{'expected_text': 'Logged in as demouser',
  'feature': 'login',
  'id': 'ui_login_positive',
  'input': {'password': 'Password123', 'username': 'demouser'},
  'layer': 'ui',
  'title': 'AI generated UI test: valid login updates the session banner',
  'type': 'positive'},
 {'expected_count': 1,
  'feature': 'search',
  'id': 'ui_search_product',
  'layer': 'ui',
  'search_term': 'Laptop',
  'title': 'AI generated UI test: searching for Laptop narrows products to one card',
  'type': 'positive'},
 {'expected_min_cart_items': 1,
  'feature': 'cart',
  'id': 'ui_add_to_cart',
  'layer': 'ui',
  'title': 'AI generated UI test: adding a product creates a cart item',
  'type': 'positive'},
 {'expected_text': 'Checkout complete',
  'feature': 'checkout',
  'id': 'ui_checkout',
  'layer': 'ui',
  'title': 'AI generated UI test: checkout displays the completion message',
  'type': 'positive'}]


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

    raise AssertionError(f"Unhandled UI case: {case['id']}")
