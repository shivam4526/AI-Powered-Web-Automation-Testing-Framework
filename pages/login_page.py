from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "#login-form button")
    MESSAGE = (By.ID, "login-message")
    USER_STATUS = (By.ID, "user-status")

    def login(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def wait_for_login_success(self):
        return self.wait_for_text(self.USER_STATUS, "Logged in as demouser")
