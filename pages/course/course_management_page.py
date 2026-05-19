# pages/course/course_management_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
from pathlib import Path
from urllib.parse import parse_qs, urlparse
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
    COURSE_URL_FILE = Path('data/runtime/course_url.txt')

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

    def click_course_by_name(self, course_name):
        """Click a visible course link by its displayed name."""
        course_links = self.find_elements(
            (By.XPATH, f"//ul[contains(@class, 'course-list')]//a[contains(@class, 'coursename') and contains(., '{course_name}')]")
        )
        visible_links = [link for link in course_links if link.is_displayed()]
        if not visible_links:
            raise AssertionError(f"Course not found in management list: {course_name}")
        course_link = visible_links[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_link)
        self.driver.execute_script("arguments[0].click();", course_link)
        self.wait_for_page_load()
        return self

    def click_edit_course(self):
        """Click Edit link on course management detail page → enters course edit page"""
        edit_link = self.find_clickable_element(self.EDIT_COURSE_LINK)
        href = edit_link.get_attribute('href') or ''
        course_id = parse_qs(urlparse(href).query).get('id', [''])[0]
        if course_id:
            self.COURSE_URL_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.COURSE_URL_FILE.write_text(f'/course/view.php?id={course_id}', encoding='utf-8')
            allure.attach(f'/course/view.php?id={course_id}', name='Runtime course URL',
                          attachment_type=allure.attachment_type.TEXT)
        self.driver.execute_script("arguments[0].click();", edit_link)
        self.wait_for_page_load()
        return self

    def get_first_course_name(self):
        return self.get_text(self.FIRST_COURSE_LINK)
