# pages/course/course_management_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class CourseManagementPage(BasePage):
    """Moodle Manage Courses page (/course/management.php)"""

    logger = LoggerManager.get_logger()

    MANAGEMENT_URL = '/course/management.php'
    # Create new course link
    CREATE_COURSE_LINK = (By.XPATH, "//a[contains(@href, 'course/edit.php')]")
    # Course list and first course
    COURSE_LIST = (By.CSS_SELECTOR, 'ul.course-list')
    FIRST_COURSE_LINK = (By.CSS_SELECTOR, 'ul.course-list li:first-child a.coursename')
    # Edit button on course management detail page
    EDIT_COURSE_LINK = (By.XPATH, "//a[contains(@href, 'course/edit.php') and contains(@class, 'action-edit')]")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_management(self):
        self.navigate(self.MANAGEMENT_URL)
        self.wait_for_page_load()
        return self

    def click_create_course(self):
        self.click(self.CREATE_COURSE_LINK)
        self.wait_for_page_load()
        from pages.course.course_edit_page import CourseEditPage
        return CourseEditPage(self.driver)

    def click_first_course(self):
        """Click first course name → enters course management detail page"""
        self.click(self.FIRST_COURSE_LINK)
        self.wait_for_page_load()
        return self

    def click_edit_course(self):
        """Click Edit link on course management detail page → enters course edit page"""
        self.click(self.EDIT_COURSE_LINK)
        self.wait_for_page_load()
        return self

    def get_first_course_name(self):
        return self.get_text(self.FIRST_COURSE_LINK)