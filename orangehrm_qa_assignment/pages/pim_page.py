import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException


class PIMPage:
    ADD_EMPLOYEE_MENU = (By.XPATH, "//a[normalize-space()='Add Employee']")
    EMPLOYEE_LIST_MENU = (By.XPATH, "//a[normalize-space()='Employee List']")
    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")
    PERSONAL_DETAILS_HEADER = (By.XPATH, "//h6[normalize-space()='Personal Details']")
    EMPLOYEE_NAME_INPUT = (By.XPATH, "//label[normalize-space()='Employee Name']/ancestor::div[contains(@class,'oxd-input-group')]//input")
    SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search']")
    RECORDS_FOUND = (By.CSS_SELECTOR, "div.oxd-table-card")
    # Loading spinner shown while search results are loading
    LOADING_SPINNER = (By.CSS_SELECTOR, ".oxd-loading-spinner")
    # Form loader overlay that intercepts clicks while the Add Employee form is initialising
    FORM_LOADER = (By.CSS_SELECTOR, "div.oxd-form-loader")
    # Autocomplete dropdown options in the Employee Name search field
    AUTOCOMPLETE_OPTION = (By.XPATH, "//div[contains(@class,'oxd-autocomplete-dropdown')]//span[not(contains(@class,'--disabled'))]")

    def __init__(self, driver, timeout=60):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _wait_for_form_loader(self):
        """Wait for the form-loader overlay to disappear so buttons are clickable."""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(self.FORM_LOADER)
            )
        except Exception:
            pass

    def add_employee(self, first_name, last_name):
        self.wait.until(EC.element_to_be_clickable(self.ADD_EMPLOYEE_MENU)).click()
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME)).send_keys(first_name)
        self.wait.until(EC.visibility_of_element_located(self.LAST_NAME)).send_keys(last_name)
        # Wait for the form-loading overlay to clear before clicking Save.
        self._wait_for_form_loader()
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.PERSONAL_DETAILS_HEADER))

    def open_employee_list(self):
        self.wait.until(EC.element_to_be_clickable(self.EMPLOYEE_LIST_MENU)).click()

    def _wait_for_results_to_load(self):
        """Wait for any loading spinner to disappear so the DOM has settled."""
        try:
            # Give the spinner a moment to appear, then wait for it to vanish.
            time.sleep(0.5)
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(self.LOADING_SPINNER)
            )
        except Exception:
            # Spinner may not exist on all pages — that's fine.
            pass

    def _collect_row_texts(self):
        """Re-fetch rows and collect their text, retrying on StaleElementReferenceException."""
        for attempt in range(3):
            try:
                rows = self.wait.until(
                    EC.visibility_of_all_elements_located(self.RECORDS_FOUND)
                )
                return " ".join(row.text for row in rows)
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                time.sleep(0.5)
        return ""

    def _select_autocomplete(self, full_name):
        """Type name into the autocomplete field and click the matching suggestion.

        OrangeHRM's Employee Name filter is an autocomplete widget — simply typing
        a name and pressing Search without selecting a suggestion has no effect.
        This helper waits for the dropdown to appear and clicks the best match.
        Returns True if a suggestion was selected, False otherwise.
        """
        try:
            options = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located(self.AUTOCOMPLETE_OPTION)
            )
            # Prefer an option whose text contains both first and last name parts.
            parts = full_name.lower().split()
            for option in options:
                text = option.text.lower()
                if all(part in text for part in parts):
                    option.click()
                    return True
            # Fallback: click the first available option.
            if options:
                options[0].click()
                return True
        except Exception:
            pass
        return False

    def verify_employee(self, full_name):
        first_name, last_name = full_name.split(" ", 1)

        search_box = self.wait.until(EC.visibility_of_element_located(self.EMPLOYEE_NAME_INPUT))
        search_box.clear()
        search_box.send_keys(full_name)

        # The name field is an autocomplete: we must select from the dropdown
        # before clicking Search, otherwise the filter is not applied.
        selected = self._select_autocomplete(full_name)

        if not selected:
            # Autocomplete had no suggestions (e.g. slight delay); try typing
            # just the first name so the dropdown triggers.
            search_box.clear()
            search_box.send_keys(first_name)
            self._select_autocomplete(full_name)

        self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON)).click()

        # Wait for the search results DOM to fully settle before reading text.
        self._wait_for_results_to_load()

        page_text = self._collect_row_texts()
        # The table renders first name and last name in separate columns, so
        # check that both appear somewhere in the combined row text.
        return first_name.lower() in page_text.lower() and last_name.lower() in page_text.lower()
