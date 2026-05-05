# pages/course/participant_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class ParticipantPage(BasePage):
    """Participants page and Enrol users modal"""

    logger = LoggerManager.get_logger()

    PARTICIPANTS_TAB = (By.XPATH, "//nav//a[contains(@href, 'user/index.php')]")
    ENROL_USER_BUTTON = (By.XPATH, "//input[@type='submit' and contains(@value, 'Enrol')]")
    MODAL_BODY = (By.CSS_SELECTOR, '.modal-body')
    USER_SEARCH_INPUT = (By.CSS_SELECTOR, '.modal-body .form-autocomplete-input input')
    ROLE_SELECT = (By.ID, 'id_roletoassign')
    # 确认按钮 —— 修复为你 Dean 测试成功时匹配的实际文本
    CONFIRM_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[contains(text(), 'Enrol selected users')]")

    def __init__(self, driver):
        super().__init__(driver)

    def go_to_participants(self):
        self.click(self.PARTICIPANTS_TAB)
        self.wait_for_page_load()
        return self

    def click_enrol_users(self):
        self.scroll_to_element(self.ENROL_USER_BUTTON)
        self.click(self.ENROL_USER_BUTTON)
        self.sleep(2)
        self.wait_for_element_visible(self.MODAL_BODY, timeout=10)
        return self

    def search_and_select_user(self, username):
        search_input = self.find_element(self.USER_SEARCH_INPUT)
        search_input.clear()
        search_input.send_keys(username)
        self.sleep(3)  # wait for suggestions to load
        # Simply click the first suggestion
        first_option = self.driver.find_element(
            By.CSS_SELECTOR, 'li[role="option"]:first-child')
        first_option.click()
        self.sleep(1)
        return self

    def assign_role(self, role='Student'):
        role_map = {'学生': 'Student', '教师': 'Teacher', '非编辑教师': 'Non-editing teacher'}
        english_role = role_map.get(role, role)
        Select(self.find_element(self.ROLE_SELECT)).select_by_visible_text(english_role)
        return self

    def confirm(self):
        self.click(self.CONFIRM_BUTTON)
        self.wait_for_page_load()
        return self