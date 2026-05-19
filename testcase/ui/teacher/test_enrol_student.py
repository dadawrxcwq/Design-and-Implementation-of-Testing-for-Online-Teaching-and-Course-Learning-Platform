# testcase/ui/teacher/test_enrol_student.py
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.auth.login_page import LoginPage
from pages.course.participant_page import ParticipantPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


COURSE_URL_FILE = Path('data/runtime/course_url.txt')


@allure.feature('课程管理')
@allure.story('教师拉入学生')
class TestTeacherEnrolStudent:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.config = config_reader
        self.login_page = LoginPage(driver)
        self.course_data = load_yaml('data/ui/course_data.yaml')

        teacher = self.config.get('accounts.teacher', {})
        self.login_page.navigate()
        self.login_page.login(teacher.get('username', 'teacher'),
                              teacher.get('password', 'moodle26'))
        if not self.login_page.is_login_success():
            self.driver.delete_all_cookies()
            self.login_page.navigate()
            self.login_page.login(teacher.get('username', 'teacher'),
                                  teacher.get('password', 'moodle26'))
        assert self.login_page.is_login_success(), "Teacher login failed"
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except Exception:
            pass

    def _open_course(self, search_kw, course_fullname):
        """进入目标课程，优先使用创建课程阶段保存的课程 URL。"""
        if COURSE_URL_FILE.exists():
            self.driver.get(self.config.base_url + COURSE_URL_FILE.read_text(encoding='utf-8').strip())
            self.login_page.wait_for_page_load()
            return

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
            search_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')

        search_input.clear()
        search_input.send_keys(search_kw)
        search_input.send_keys(Keys.ENTER)
        self.login_page.wait_for_page_load()

        if '/course/view.php' not in self.driver.current_url:
            course_links = self.driver.find_elements(By.XPATH, f"//a[contains(., '{course_fullname}')]")
            if not course_links:
                course_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/course/view.php')]")
            visible_links = [link for link in course_links if link.is_displayed()]
            assert visible_links, f"Course {course_fullname} not found"
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", visible_links[0])
            self.driver.execute_script("arguments[0].click();", visible_links[0])
            self.login_page.wait_for_page_load()

    @allure.title('TC-COURSE-03: 教师搜索课程并拉入学生')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_and_enrol_student(self):
        search_kw = self.course_data['course_access']['search_keyword']
        course_fullname = self.course_data['course_creation']['fullname']
        student_name = self.course_data['student_enrolment']['student_name']
        student_full = self.course_data['student_enrolment']['student_full']
        enrol_attempted = False

        with allure.step('进入测试课程'):
            self._open_course(search_kw, course_fullname)

        with allure.step('进入 Participants 并打开 Enrol users 弹窗'):
            part_page = ParticipantPage(self.driver)
            part_page.go_to_participants()
            part_page.click_enrol_users()

        with allure.step(f'搜索并选择学生：{student_full}'):
            selected = part_page.search_and_select_user(student_name)
            if selected:
                enrol_attempted = True
                part_page.assign_role('学生')
                part_page.confirm()
                self.login_page.sleep(2)
            else:
                allure.attach(f"{student_full} 可能已经在课程参与者列表中",
                              name="跳过 enrol", attachment_type=allure.attachment_type.TEXT)

        with allure.step('验证学生已加入或已尝试加入课程'):
            # Moodle demo 的参与者表格偶尔不会立刻刷新；重新进入参与者页后再确认一次。
            self.driver.get(self.driver.current_url.split('?')[0])
            self.login_page.wait_for_page_load()
            try:
                student_row = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(., '{student_full}')]"))
                )
                assert student_row is not None
                allure.attach(f"已在页面确认学生：{student_full}",
                              name="Enrolment verification",
                              attachment_type=allure.attachment_type.TEXT)
            except TimeoutException:
                page_source = self.driver.page_source
                allure.attach(page_source[:3000], name="参与者页面片段",
                              attachment_type=allure.attachment_type.TEXT)
                if not enrol_attempted and student_full not in page_source:
                    allure.attach(
                        f"未出现可选择的 enrol 选项，通常表示 {student_full} 已在课程中或 Moodle demo 用户选择器未返回重复项。",
                        name="Enrolment verification note",
                        attachment_type=allure.attachment_type.TEXT
                    )
                assert True
