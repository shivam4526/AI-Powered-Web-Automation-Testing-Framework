from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class ShopPage(BasePage):
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.ID, "search-btn")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".product-item")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".add-to-cart-btn")
    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item")
    CHECKOUT_BUTTON = (By.ID, "checkout-btn")
    CHECKOUT_MESSAGE = (By.ID, "checkout-message")

    def search(self, query: str):
        self.type(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)

    def wait_for_products(self):
        self.wait.until(EC.presence_of_all_elements_located(self.PRODUCT_CARDS))

    def add_first_product_to_cart(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BUTTONS)).click()

    def wait_for_cart_items(self):
        self.wait.until(EC.presence_of_all_elements_located(self.CART_ITEMS))

    def wait_for_product_count(self, count: int):
        self.wait.until(lambda driver: len(driver.find_elements(*self.PRODUCT_CARDS)) == count)
