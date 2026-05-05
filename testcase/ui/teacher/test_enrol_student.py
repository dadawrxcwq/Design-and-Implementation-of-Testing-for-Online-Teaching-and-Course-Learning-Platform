# testcase/ui/teacher/test_enrol_student.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from pages.course.participant_page import ParticipantPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# 新增导入
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@allure.feature('课程管理')
@allure.story('Teacher拉入学生')
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
        assert self.login_page.is_login_success(), "Teacher login failed"
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    @allure.title('TC-COURSE-03: Teacher搜索课程并加入学生')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_and_enrol_student(self):
        search_kw = self.course_data['course_access']['search_keyword']
        course_fullname = self.course_data['course_creation']['fullname']
        student_name = self.course_data['student_enrolment']['student_name']
        student_full = self.course_data['student_enrolment']['student_full']

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
                search_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')

            search_input.clear()
            search_input.send_keys(search_kw)
            search_input.send_keys(Keys.ENTER)
            self.login_page.wait_for_page_load()

        with allure.step(f'2. Click course "{course_fullname}" in results'):
            course_link = self.driver.find_element(
                By.XPATH, f"//a[contains(., '{course_fullname}')]")
            course_link.click()
            self.login_page.wait_for_page_load()

        with allure.step('3. Go to Participants and enrol student'):
            part_page = ParticipantPage(self.driver)
            part_page.go_to_participants()
            part_page.click_enrol_users()

        with allure.step(f'4. Search student {student_full} and enrol as Student'):
            part_page.search_and_select_user(student_name)
            part_page.assign_role('学生')
            part_page.confirm()

        with allure.step('5. Verify student appears in participants list'):
            try:
                student_row = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        f"//tr[contains(., '{student_full}')]"
                    ))
                )
                assert student_row is not None, \
                    f"Student {student_full} not found on participants page"
                allure.attach(
                    f"Student {student_full} confirmed in participants table",
                    name="Enrolment verification",
                    attachment_type=allure.attachment_type.TEXT
                )
            except TimeoutException:
                page_source = self.driver.page_source
                assert student_full in page_source, \
                    f"Student {student_full} not found anywhere on page"