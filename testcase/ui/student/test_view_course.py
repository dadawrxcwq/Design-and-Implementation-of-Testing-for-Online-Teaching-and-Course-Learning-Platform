# testcase/ui/student/test_view_course.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@allure.feature('学生功能')
@allure.story('学生查看已选课程')
class TestStudentViewCourse:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.config = config_reader
        self.login_page = LoginPage(driver)
        self.course_data = load_yaml('data/ui/course_data.yaml')

        student = self.config.get('accounts.student', {})
        self.login_page.navigate()
        self.login_page.login(student.get('username', 'student'),
                              student.get('password', 'moodle26'))
        assert self.login_page.is_login_success(), "Student login failed"
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    @allure.title('TC-COURSE-04: 学生搜索并查看新课程')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_student_view_course(self):
        search_kw = self.course_data['course_access']['search_keyword']
        expected_title = self.course_data['course_access']['expected_title']

        with allure.step(f'1. Search for "{search_kw}"'):
            search_input = None
            for by, selector in [
                (By.CSS_SELECTOR, 'input[type="search"]'),
                (By.CSS_SELECTOR, 'input[name="search"]'),
            ]:
                try:
                    search_input = self.driver.find_element(by, selector)
                    if search_input and search_input.is_displayed():
                        break
                except:
                    continue
            if search_input is None:
                search_input = self.driver.find_element(By.XPATH, "//input[@type='text']")

            search_input.clear()
            search_input.send_keys(search_kw)
            search_input.send_keys(Keys.ENTER)
            self.login_page.wait_for_page_load()

        with allure.step('2. Click first search result'):
            course_link = None
            for by, selector in [
                (By.XPATH, "//a[contains(., '软件测试实践')]"),
                (By.XPATH, "//a[contains(@href, '/course/view.php')]"),
            ]:
                try:
                    links = self.driver.find_elements(by, selector)
                    if links:
                        course_link = links[0]
                        break
                except:
                    continue

            assert course_link is not None, "Course not found in search results"
            course_link.click()
            self.login_page.wait_for_page_load()

        with allure.step('3. Verify course title'):
            course_title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            allure.attach(course_title, name="Course title", attachment_type=allure.attachment_type.TEXT)
            assert expected_title in course_title, \
                f"Expected title containing '{expected_title}', got '{course_title}'"