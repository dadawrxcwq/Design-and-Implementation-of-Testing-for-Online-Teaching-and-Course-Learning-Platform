# testcase/ui/teacher/test_assignment.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from pages.course.edit_mode_page import EditModePage
from pages.course.assignment_page import (
    AssignmentPage, SubmissionPage
)
from utils.config_reader import config_reader
from utils.data_loader import load_yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@allure.feature('作业功能')
@allure.story('作业全流程测试')
class TestAssignment:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.config = config_reader
        self.login_page = LoginPage(driver)
        self.course_data = load_yaml('data/ui/course_data.yaml')

        # Teacher登录并进入课程
        teacher = self.config.get('accounts.teacher', {})
        self.login_page.navigate()
        self.login_page.login(teacher.get('username', 'teacher'),
                              teacher.get('password', 'moodle26'))
        assert self.login_page.is_login_success(), "Teacher login failed"

        # 搜索并进入课程
        self._enter_course()

        # 开启编辑模式
        edit_mode = EditModePage(driver)
        edit_mode.enable()
        assert edit_mode.is_edit_mode_enabled(), "Edit mode not enabled"

        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    def _enter_course(self):
        """搜索课程并点击进入"""
        fullname = self.course_data['course_creation']['fullname']
        search_input = self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
        search_input.clear()
        search_input.send_keys(fullname)
        search_input.send_keys(Keys.ENTER)
        self.login_page.wait_for_page_load()

        course_link = self.driver.find_element(
            By.XPATH, f"//a[contains(., '{fullname}')]")
        course_link.click()
        self.login_page.wait_for_page_load()

    @allure.title('TC-ASSIGN-01: 教师发布作业')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_assignment(self):
        assign_page = AssignmentPage(self.driver)

        with allure.step('点击添加活动或资源'):
            assign_page.add_activity()

        with allure.step('选择Assignment'):
            assign_page.select_assignment()

        with allure.step('填写作业信息'):
            assign_page.set_title("单元测试设计")
            assign_page.set_description("请提交测试用例设计文档，包含等价类划分、边界值分析等内容。")
            assign_page.set_due_date("2026-05-06 23:30")

        with allure.step('保存作业'):
            assign_page.save_and_display()

        with allure.step('验证作业在课程页可见'):
            assert assign_page.is_assignment_visible("单元测试设计"), \
                "Assignment not visible on course page"


@allure.feature('作业功能')
@allure.story('学生提交与查看反馈')
class TestStudentAssignment:

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

        self._enter_course()
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    def _enter_course(self):
        """搜索课程并进入"""
        fullname = self.course_data['course_creation']['fullname']
        search_input = self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
        search_input.clear()
        search_input.send_keys(fullname)
        search_input.send_keys(Keys.ENTER)
        self.login_page.wait_for_page_load()
        course_link = self.driver.find_element(
            By.XPATH, f"//a[contains(., '{fullname}')]")
        course_link.click()
        self.login_page.wait_for_page_load()

    @allure.title('TC-ASSIGN-02: 学生提交作业')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_student_submit_assignment(self):
        assign_page = AssignmentPage(self.driver)

        with allure.step('进入作业活动'):
            assign_page.open_assignment("单元测试设计")

        sub_page = SubmissionPage(self.driver)

        with allure.step('点击添加提交并上传文件'):
            sub_page.add_submission()
            # 上传文件路径（需根据实际路径调整）
            sub_page.upload_file("D:/test_files/test_design.docx")

        with allure.step('提交作业'):
            sub_page.submit_assignment()

        with allure.step('验证提交成功'):
            assert sub_page.is_submitted(), "Submission failed"

    @allure.title('TC-ASSIGN-06: 学生查看成绩和反馈')
    @allure.severity(allure.severity_level.NORMAL)
    def test_student_view_grade_feedback(self):
        assign_page = AssignmentPage(self.driver)

        with allure.step('进入作业活动'):
            assign_page.open_assignment("单元测试设计")

        sub_page = SubmissionPage(self.driver)

        with allure.step('查看成绩和评语'):
            grade = sub_page.get_grade()
            feedback = sub_page.get_feedback()
            allure.attach(f"成绩: {grade}\n评语: {feedback}",
                         name="成绩与反馈",
                         attachment_type=allure.attachment_type.TEXT)

        with allure.step('验证成绩存在'):
            assert grade is not None, "No grade found"