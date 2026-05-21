from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.base_url)

    def type(self, locator, value):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(value)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def text_of(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def wait_for_text(self, locator, expected_text):
        self.wait.until(EC.text_to_be_present_in_element(locator, expected_text))
        return self.text_of(locator)
