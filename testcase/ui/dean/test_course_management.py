import pytest
import allure
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.auth.login_page import LoginPage
from pages.course.course_management_page import CourseManagementPage
from pages.course.participant_page import ParticipantPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


@allure.feature('课程管理')
@allure.story('Dean创建课程并拉入教师')
class TestDeanCourseManagement:

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

    @allure.title('TC-COURSE-01: Dean creates a new course')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_course(self):
        create_data = self.course_data['course_creation']

        with allure.step('1. Navigate to Manage Courses → Create new course'):
            mgmt_page = CourseManagementPage(self.driver)
            mgmt_page.navigate_to_management()
            edit_page = mgmt_page.click_create_course()

        with allure.step('2. Fill course info and save'):
            edit_page.fill_basic_info(create_data['fullname'],
                                      create_data['shortname'])
            edit_page.set_visible(create_data['visible'])
            edit_page.save_and_return()

        with allure.step('3. Verify course appears in list'):
            mgmt_page = CourseManagementPage(self.driver)
            mgmt_page.navigate_to_management()
            course_name = mgmt_page.get_first_course_name()
            allure.attach(course_name, name="Newest course", attachment_type=allure.attachment_type.TEXT)
            assert create_data['fullname'] == course_name, \
                f"Expected '{create_data['fullname']}', got '{course_name}'"

    @allure.title('TC-COURSE-02: Dean enrols teacher into course')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_enrol_teacher(self):
        enrol_data = self.course_data['teacher_enrolment']
        create_data = self.course_data['course_creation']

        with allure.step('1. Manage Courses → click first course → click Edit'):
            mgmt_page = CourseManagementPage(self.driver)
            mgmt_page.navigate_to_management()
            mgmt_page.click_course_by_name(create_data['fullname'])
            mgmt_page.click_edit_course()

        with allure.step('2. Go to Participants → Enrol users'):
            part_page = ParticipantPage(self.driver)
            part_page.go_to_participants()
            part_page.click_enrol_users()

        with allure.step(f'3. Search {enrol_data["teacher_full"]} and enrol as Teacher'):
            selected = part_page.search_and_select_user(enrol_data['teacher_name'])
            if selected:
                part_page.assign_role('教师')
                part_page.confirm()
            else:
                allure.attach(
                    f"{enrol_data['teacher_full']} may already be enrolled",
                    name="Enrolment skipped",
                    attachment_type=allure.attachment_type.TEXT
                )

        with allure.step('4. Verify teacher was enrolled'):
            # Wait for the participants table to actually render the teacher
            try:
                teacher_row = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH, f"//tr[contains(., '{enrol_data['teacher_full']}')]"
                    ))
                )
                assert teacher_row is not None, f"Teacher {enrol_data['teacher_full']} not found on participants page"
                allure.attach(
                    f"Teacher {enrol_data['teacher_full']} found in participants table",
                    name="Enrolment verification",
                    attachment_type=allure.attachment_type.TEXT
                )
            except TimeoutException:
                # If we can't find the teacher row, try checking via page source as fallback
                page_source = self.driver.page_source
                assert enrol_data['teacher_full'] in page_source, \
                    f"Teacher {enrol_data['teacher_full']} not found anywhere on page"
