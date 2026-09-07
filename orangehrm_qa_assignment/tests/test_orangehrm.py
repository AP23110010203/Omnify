import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.pim_page import PIMPage


EMPLOYEES = [
    ("Akhil", "QAOne"),
    ("Ravi", "QATwo"),
    ("Sita", "QAThree"),
    ("Anu", "QAFour"),
]


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    # Disable unnecessary features that slow down page loads on the demo site
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    # Give Chrome up to 90 s to finish loading each page before raising a
    # TimeoutException (avoids urllib3 ReadTimeoutError on slow demo sites).
    driver.set_page_load_timeout(90)
    # Fallback implicit wait so quick element lookups don't need an explicit Wait.
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_orangehrm_end_to_end(driver):
    # Use environment variables so credentials are not committed to GitHub.
    username = os.getenv("ORANGEHRM_USERNAME", "Admin")
    password = os.getenv("ORANGEHRM_PASSWORD", "admin123")

    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)
    pim_page = PIMPage(driver)

    # 1. Login
    login_page.open()
    login_page.login(username, password)
    assert login_page.is_dashboard_visible(), "Login failed"

    # 2. Navigate to PIM
    dashboard_page.open_pim()

    # 3. Add employees
    created_employees = []
    for first_name, last_name in EMPLOYEES:
        pim_page.add_employee(first_name, last_name)
        created_employees.append(f"{first_name} {last_name}")

        # Return to PIM before adding the next employee.
        dashboard_page.open_pim()

    # 4. Verify employees
    for full_name in created_employees:
        pim_page.open_employee_list()
        verified = pim_page.verify_employee(full_name)
        assert verified, f"Employee not found: {full_name}"
        print(f"{full_name} - Name Verified")
        dashboard_page.open_pim()

    # 5. Logout
    dashboard_page.logout()
