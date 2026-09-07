from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DashboardPage:
    PIM_MENU = (By.XPATH, "//span[normalize-space()='PIM']")
    USER_DROPDOWN = (By.CSS_SELECTOR, "span.oxd-userdropdown-tab")
    LOGOUT = (By.XPATH, "//a[normalize-space()='Logout']")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_pim(self):
        pim = self.wait.until(EC.element_to_be_clickable(self.PIM_MENU))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pim)
        pim.click()

    def logout(self):
        self.wait.until(EC.element_to_be_clickable(self.USER_DROPDOWN)).click()
        self.wait.until(EC.element_to_be_clickable(self.LOGOUT)).click()
