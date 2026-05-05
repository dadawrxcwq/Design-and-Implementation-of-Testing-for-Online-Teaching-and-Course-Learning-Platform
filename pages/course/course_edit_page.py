# pages/course/course_edit_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class CourseEditPage(BasePage):
    """Moodle 课程编辑页面对象"""

    logger = LoggerManager.get_logger()

    COURSE_EDIT_URL = '/course/edit.php'

    FULLNAME_INPUT = (By.ID, 'id_fullname')
    SHORTNAME_INPUT = (By.ID, 'id_shortname')
    VISIBLE_SELECT = (By.ID, 'id_visible')
    # 保存并返回按钮：同时用 name 和你的绝对路径，确保点击成功
    SAVE_AND_RETURN_BTN = (By.NAME, 'saveandreturn')
    SAVE_AND_RETURN_FALLBACK = (By.XPATH,
        "/html/body/div[2]/div[3]/div/div[3]/div/div/div/form/div[3]/div/div/div/span/div/div[1]/span/input")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_edit(self):
        self.navigate(self.COURSE_EDIT_URL)
        self.wait_for_page_load()
        return self

    def fill_basic_info(self, fullname, shortname):
        self.input_text(self.FULLNAME_INPUT, fullname)
        self.input_text(self.SHORTNAME_INPUT, shortname)
        self.logger.info(f"填写课程信息：{fullname} / {shortname}")
        return self

    def set_visible(self, visible=True):
        value = '1' if visible else '0'
        Select(self.find_element(self.VISIBLE_SELECT)).select_by_value(value)
        return self

    def save_and_return(self):
        # 优先用 name 定位，失败则用绝对路径
        try:
            self.click(self.SAVE_AND_RETURN_BTN)
        except:
            self.logger.warning("name='saveandreturn' 定位失败，使用绝对路径")
            self.click(self.SAVE_AND_RETURN_FALLBACK)
        self.wait_for_page_load(timeout=20)
        self.logger.info("课程已保存并返回")
        return self