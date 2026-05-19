# testcase/ui/student/test_view_course.py
from pathlib import Path

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


# Dean 创建课程时会把课程真实 URL 写入该文件。优先复用 URL，
# 可以避免 Moodle 首页搜索结果刷新慢或搜索框状态异常导致误报。
COURSE_URL_FILE = Path('data/runtime/course_url.txt')


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
        if not self.login_page.is_login_success():
            # Moodle demo 站点偶尔保留旧会话状态；清理后重登一次可降低误报。
            self.driver.delete_all_cookies()
            self.login_page.navigate()
            self.login_page.login(student.get('username', 'student'),
                                  student.get('password', 'moodle26'))
        assert self.login_page.is_login_success(), "Student login failed"
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except Exception:
            pass

    def _open_course(self):
        """进入测试课程，优先使用创建课程阶段记录的真实课程 URL。"""
        if COURSE_URL_FILE.exists():
            course_path = COURSE_URL_FILE.read_text(encoding='utf-8').strip()
            self.driver.get(self.config.base_url + course_path)
            self.login_page.wait_for_page_load()
            allure.attach(course_path, name='运行时课程地址',
                          attachment_type=allure.attachment_type.TEXT)
            return

        search_kw = self.course_data['course_access']['search_keyword']
        with allure.step(f'搜索课程：{search_kw}'):
            search_input = None
            for by, selector in [
                (By.CSS_SELECTOR, 'input[type="search"]'),
                (By.CSS_SELECTOR, 'input[name="search"]'),
            ]:
                try:
                    search_input = self.driver.find_element(by, selector)
                    if search_input and search_input.is_displayed():
                        break
                except Exception:
                    continue
            if search_input is None:
                search_input = self.driver.find_element(By.XPATH, "//input[@type='text']")

            search_input.clear()
            search_input.send_keys(search_kw)
            search_input.send_keys(Keys.ENTER)
            self.login_page.wait_for_page_load()

        with allure.step('打开搜索结果中的课程'):
            course_link = None
            for by, selector in [
                (By.XPATH, f"//a[contains(., '{search_kw}')]"),
                (By.XPATH, "//a[contains(@href, '/course/view.php')]"),
            ]:
                try:
                    links = [link for link in self.driver.find_elements(by, selector)
                             if link.is_displayed()]
                    if links:
                        course_link = links[0]
                        break
                except Exception:
                    continue

            assert course_link is not None, "Course not found in search results"
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_link)
            self.driver.execute_script("arguments[0].click();", course_link)
            self.login_page.wait_for_page_load()

    @allure.title('TC-COURSE-04: 学生查看已选课程')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_student_view_course(self):
        expected_titles = [
            self.course_data['course_access'].get('expected_title'),
            self.course_data['course_creation'].get('fullname'),
            self.course_data.get('edit_course', {}).get('new_fullname'),
        ]
        expected_titles = [title for title in expected_titles if title]

        with allure.step('进入学生已选课程'):
            self._open_course()

        with allure.step('验证课程标题显示正确'):
            course_title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            allure.attach(course_title, name='课程标题', attachment_type=allure.attachment_type.TEXT)
            assert any(title in course_title for title in expected_titles), \
                f"Expected one of {expected_titles}, got '{course_title}'"
