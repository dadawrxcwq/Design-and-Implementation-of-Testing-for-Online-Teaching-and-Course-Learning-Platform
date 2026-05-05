# pages/course/edit_mode_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class EditModePage(BasePage):
    """课程编辑模式管理页面对象"""

    logger = LoggerManager.get_logger()

    # 编辑模式开关
    EDIT_MODE_SWITCH = (By.CSS_SELECTOR, '.editmode-switch-form input[type="checkbox"]')
    EDIT_MODE_LABEL = (By.CSS_SELECTOR, '.editmode-switch-form label')

    # 开启编辑模式后出现的元素
    BULK_ACTIONS_BUTTON = (By.XPATH, "//button[contains(text(), 'Bulk actions')]")
    ADD_ACTIVITY_LINK = (By.XPATH, "//a[contains(., 'Add an activity or resource')]")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('开启编辑模式')
    def enable(self):
        """开启编辑模式"""
        switch = self.find_element(self.EDIT_MODE_SWITCH)
        if not switch.is_selected():
            label = self.find_element(self.EDIT_MODE_LABEL)
            label.click()
            self.sleep(2)
            self.wait_for_page_load()
        return self

    @allure.step('关闭编辑模式')
    def disable(self):
        """关闭编辑模式"""
        switch = self.find_element(self.EDIT_MODE_SWITCH)
        if switch.is_selected():
            label = self.find_element(self.EDIT_MODE_LABEL)
            label.click()
            self.sleep(1)
        return self

    @allure.step('验证编辑模式已开启')
    def is_edit_mode_enabled(self):
        """验证编辑模式是否已开启"""
        return self.is_element_visible(self.BULK_ACTIONS_BUTTON, timeout=5)