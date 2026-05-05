# testcase/ui/dean/test_delete_course.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from pages.course.course_management_page import CourseManagementPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml
from selenium.webdriver.common.by import By


@allure.feature('课程管理')
@allure.story('Dean删除课程')
class TestDeanDeleteCourse:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.config = config_reader
        self.login_page = LoginPage(driver)
        self.course_data = load_yaml('data/ui/course_data.yaml')

        dean = self.config.get('accounts.dean', {})
        self.login_page.navigate()
        self.login_page.login(dean.get('username', 'manager'),
                              dean.get('password', 'moodle26'))
        assert self.login_page.is_login_success(), "Dean login failed"
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    @allure.title('TC-COURSE-09: Dean删除课程')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_course(self):
        course_fullname = self.course_data['course_creation']['fullname']

        with allure.step('1. Navigate to Manage Courses'):
            mgmt_page = CourseManagementPage(self.driver)
            mgmt_page.navigate_to_management()

        with allure.step('2. Click delete icon on first course'):
            # D1: /html/body/div[4]/div[3]/div/div[3]/div/div/div/form/div[2]/div[2]/div/div/ul/li[1]/div/div[3]/span/a[3]/i
            delete_icon = self.driver.find_element(
                By.CSS_SELECTOR, 'ul.course-list li:first-child a.action-delete i')
            delete_icon.click()
            self.login_page.wait_for_page_load()

        with allure.step('3. Click Delete button on confirmation page'):
            # D1: /html/body/div[2]/div[3]/div/div[3]/div/div/div/div/div/div[3]/div/div[2]/form/button
            delete_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Delete')]")
            delete_button.click()
            self.login_page.wait_for_page_load()

        with allure.step('4. Verify deletion success message'):
            course_shortname = self.course_data['course_creation']['shortname']
            heading = self.driver.find_element(By.CSS_SELECTOR, 'h2').text
            allure.attach(heading, name="Deletion result",
                          attachment_type=allure.attachment_type.TEXT)
            assert course_shortname in heading or "Deleting" in heading, \
                f"Expected heading containing '{course_shortname}', got '{heading}'"