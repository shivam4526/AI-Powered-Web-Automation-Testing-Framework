import pytest

from pages.login_page import LoginPage
from pages.shop_page import ShopPage


@pytest.mark.ui
def test_valid_login(driver, base_url):
    page = LoginPage(driver, base_url)
    page.open()
    page.login("demouser", "Password123")
    assert "Logged in as demouser" in page.wait_for_login_success()


@pytest.mark.ui
def test_invalid_login(driver, base_url):
    page = LoginPage(driver, base_url)
    page.open()
    page.login("demouser", "WrongPassword")
    assert "Invalid username or password" in page.text_of(page.MESSAGE)


@pytest.mark.ui
def test_search_product(driver, base_url):
    login_page = LoginPage(driver, base_url)
    shop_page = ShopPage(driver, base_url)
    login_page.open()
    login_page.login("demouser", "Password123")
    login_page.wait_for_login_success()
    shop_page.search("Laptop")
    shop_page.wait_for_product_count(1)
    assert len(driver.find_elements(*shop_page.PRODUCT_CARDS)) == 1


@pytest.mark.ui
def test_add_to_cart(driver, base_url):
    login_page = LoginPage(driver, base_url)
    shop_page = ShopPage(driver, base_url)
    login_page.open()
    login_page.login("demouser", "Password123")
    login_page.wait_for_login_success()
    shop_page.wait_for_products()
    shop_page.add_first_product_to_cart()
    shop_page.wait_for_cart_items()
    assert len(driver.find_elements(*shop_page.CART_ITEMS)) >= 1


@pytest.mark.ui
def test_checkout(driver, base_url):
    login_page = LoginPage(driver, base_url)
    shop_page = ShopPage(driver, base_url)
    login_page.open()
    login_page.login("demouser", "Password123")
    login_page.wait_for_login_success()
    shop_page.wait_for_products()
    shop_page.add_first_product_to_cart()
    shop_page.wait_for_cart_items()
    shop_page.click(shop_page.CHECKOUT_BUTTON)
    assert "Checkout complete" in shop_page.text_of(shop_page.CHECKOUT_MESSAGE)
