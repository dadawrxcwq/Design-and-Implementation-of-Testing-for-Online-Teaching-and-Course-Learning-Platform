# pages/course/assignment_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class AssignmentPage(BasePage):
    """
    作业管理页面对象
    包含作业创建、编辑、查看提交列表等
    """

    logger = LoggerManager.get_logger()

    # ==================== 元素定位器 ====================

    # 添加活动/资源按钮
    ADD_ACTIVITY_LINK = (By.XPATH, "//a[contains(., 'Add an activity or resource')]")

    # 活动选择器中选"Assignment"
    ASSIGNMENT_RADIO = (By.XPATH, "//label[contains(., 'Assignment')]")
    ADD_BUTTON = (By.XPATH, "//input[@value='Add']")

    # 作业设置表单
    ASSIGNMENT_NAME_INPUT = (By.ID, 'id_name')
    ASSIGNMENT_DESC_EDITOR = (By.ID, 'id_introeditor')
    ASSIGNMENT_DESC_IFRAME = (By.CSS_SELECTOR, '#id_introeditor_ifr')
    DUE_DATE_ENABLE_CHECKBOX = (By.ID, 'id_duedate_enabled')
    DUE_DATE_DAY_SELECT = (By.ID, 'id_duedate_day')
    DUE_DATE_MONTH_SELECT = (By.ID, 'id_duedate_month')
    DUE_DATE_YEAR_SELECT = (By.ID, 'id_duedate_year')
    DUE_DATE_HOUR_SELECT = (By.ID, 'id_duedate_hour')
    DUE_DATE_MINUTE_SELECT = (By.ID, 'id_duedate_minute')

    # 保存按钮
    SAVE_AND_DISPLAY_BTN = (By.ID, 'id_saveanddisplay')
    SAVE_AND_RETURN_BTN = (By.ID, 'id_saveandreturn')

    # 查看所有提交
    VIEW_ALL_SUBMISSIONS_LINK = (By.XPATH, "//a[contains(., 'View all submissions')]")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('点击添加活动或资源')
    def add_activity(self):
        """点击'Add an activity or resource'链接"""
        self.click(self.ADD_ACTIVITY_LINK)
        self.wait_for_page_load()
        return self

    @allure.step('选择Assignment活动并点击Add')
    def select_assignment(self):
        """在活动选择器中选择Assignment"""
        self.click(self.ASSIGNMENT_RADIO)
        self.click(self.ADD_BUTTON)
        self.wait_for_page_load()
        return self

    @allure.step('设置作业标题：{title}')
    def set_title(self, title):
        """设置作业名称"""
        self.input_text(self.ASSIGNMENT_NAME_INPUT, title)
        return self

    @allure.step('设置作业描述：{description}')
    def set_description(self, description):
        """在TinyMCE编辑器中输入描述"""
        self.driver.switch_to.frame(self.find_element(self.ASSIGNMENT_DESC_IFRAME))
        editor_body = self.driver.find_element(By.CSS_SELECTOR, '#tinymce')
        editor_body.clear()
        editor_body.send_keys(description)
        self.driver.switch_to.default_content()
        return self

    @allure.step('设置截止日期：{due_date}')
    def set_due_date(self, due_date_str):
        """设置截止日期，格式 '2026-05-06 23:30'"""
        parts = due_date_str.split(' ')
        date_part = parts[0].split('-')
        time_part = parts[1].split(':')

        # 启用截止日期
        self.check_checkbox(self.DUE_DATE_ENABLE_CHECKBOX)

        # 设置日期
        from selenium.webdriver.support.ui import Select
        Select(self.find_element(self.DUE_DATE_DAY_SELECT)).select_by_value(date_part[2])
        Select(self.find_element(self.DUE_DATE_MONTH_SELECT)).select_by_value(str(int(date_part[1])))
        Select(self.find_element(self.DUE_DATE_YEAR_SELECT)).select_by_value(date_part[0])

        # 设置时间
        Select(self.find_element(self.DUE_DATE_HOUR_SELECT)).select_by_value(time_part[0])
        Select(self.find_element(self.DUE_DATE_MINUTE_SELECT)).select_by_value(time_part[1])
        return self

    @allure.step('保存并显示')
    def save_and_display(self):
        """点击保存并显示按钮"""
        self.click(self.SAVE_AND_DISPLAY_BTN)
        self.wait_for_page_load()
        return self

    @allure.step('保存并返回课程')
    def save_and_return(self):
        """点击保存并返回课程按钮"""
        self.click(self.SAVE_AND_RETURN_BTN)
        self.wait_for_page_load()
        return self

    @allure.step('验证作业在课程页面可见')
    def is_assignment_visible(self, assignment_name):
        """验证作业名称在课程页面可见"""
        locator = (By.XPATH, f"//a[contains(., '{assignment_name}')]")
        return self.is_element_visible(locator, timeout=5)

    @allure.step('点击作业进入详情')
    def open_assignment(self, assignment_name):
        """点击作业名称进入作业详情页"""
        locator = (By.XPATH, f"//a[contains(., '{assignment_name}')]")
        self.click(locator)
        self.wait_for_page_load()
        return self

    @allure.step('点击View all submissions')
    def view_all_submissions(self):
        """点击View all submissions链接"""
        self.click(self.VIEW_ALL_SUBMISSIONS_LINK)
        self.wait_for_page_load()
        return SubmissionListPage(self.driver)


class SubmissionListPage(BasePage):
    """提交列表页面对象"""

    logger = LoggerManager.get_logger()

    # 提交列表
    SUBMISSION_TABLE = (By.CSS_SELECTOR, 'table.submissions')
    GRADE_LINK = (By.XPATH, "//a[contains(., 'Grade')]")

    # 评分表单
    GRADE_INPUT = (By.ID, 'id_grade')
    FEEDBACK_EDITOR = (By.ID, 'id_assignfeedbackcomments_editor')
    FEEDBACK_IFRAME = (By.CSS_SELECTOR, '#id_assignfeedbackcomments_editor_ifr')
    SAVE_GRADE_BTN = (By.ID, 'id_submitbutton')

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('点击第一个学生的评分链接')
    def grade_first_submission(self):
        """点击第一个提交的评分链接"""
        grade_links = self.find_elements(self.GRADE_LINK)
        if grade_links:
            grade_links[0].click()
            self.wait_for_page_load()
        return GradingPage(self.driver)

    @allure.step('获取提交数量')
    def get_submission_count(self):
        """获取提交数量"""
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table.submissions tbody tr')
        return len(rows)


class GradingPage(BasePage):
    """评分页面对象"""

    logger = LoggerManager.get_logger()

    GRADE_INPUT = (By.ID, 'id_grade')
    FEEDBACK_IFRAME = (By.CSS_SELECTOR, '#id_assignfeedbackcomments_editor_ifr')
    SAVE_CHANGES_BTN = (By.ID, 'id_submitbutton')
    SAVE_AND_SHOW_NEXT_BTN = (By.XPATH, "//input[@value='Save and show next']")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('输入分数：{score} / 评语：{feedback}')
    def set_grade_and_feedback(self, score, feedback):
        """输入分数和评语"""
        self.input_text(self.GRADE_INPUT, str(score))

        if feedback:
            self.driver.switch_to.frame(self.find_element(self.FEEDBACK_IFRAME))
            editor_body = self.driver.find_element(By.CSS_SELECTOR, '#tinymce')
            editor_body.clear()
            editor_body.send_keys(feedback)
            self.driver.switch_to.default_content()
        return self

    @allure.step('保存评分')
    def save_grade(self):
        """保存评分"""
        self.click(self.SAVE_CHANGES_BTN)
        self.wait_for_page_load()
        return self


class SubmissionPage(BasePage):
    """学生提交作业页面对象"""

    logger = LoggerManager.get_logger()

    # 提交按钮
    ADD_SUBMISSION_BTN = (By.XPATH, "//input[@value='Add submission']")
    EDIT_SUBMISSION_BTN = (By.XPATH, "//input[@value='Edit submission']")
    SUBMIT_ASSIGNMENT_BTN = (By.ID, 'id_submitbutton')

    # 文件上传
    FILE_INPUT = (By.NAME, 'files_file')

    # 提交状态
    SUBMISSION_STATUS = (By.CSS_SELECTOR, '.submissionstatussingle')
    SUBMISSION_SUCCESS_MSG = (By.XPATH, "//div[contains(@class, 'alert-success')]")

    # 反馈和成绩
    GRADE_DISPLAY = (By.CSS_SELECTOR, '.grade')
    FEEDBACK_TEXT = (By.CSS_SELECTOR, '.feedback .comment')

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('点击添加提交')
    def add_submission(self):
        """点击Add submission按钮"""
        if self.is_element_exists(self.ADD_SUBMISSION_BTN):
            self.click(self.ADD_SUBMISSION_BTN)
            self.wait_for_page_load()
        return self

    @allure.step('上传文件：{file_path}')
    def upload_file(self, file_path):
        """上传文件"""
        self.upload_file(self.FILE_INPUT, file_path)
        return self

    @allure.step('提交作业')
    def submit_assignment(self):
        """点击提交作业按钮"""
        self.click(self.SUBMIT_ASSIGNMENT_BTN)
        self.wait_for_page_load()
        return self

    @allure.step('验证提交成功')
    def is_submitted(self):
        """验证作业已提交"""
        return self.is_element_visible(self.SUBMISSION_STATUS, timeout=5) and \
            "submitted" in self.driver.page_source.lower()

    @allure.step('获取成绩')
    def get_grade(self):
        """获取成绩"""
        if self.is_element_exists(self.GRADE_DISPLAY):
            return self.get_text(self.GRADE_DISPLAY)
        return None

    @allure.step('获取评语')
    def get_feedback(self):
        """获取评语"""
        if self.is_element_exists(self.FEEDBACK_TEXT):
            return self.get_text(self.FEEDBACK_TEXT)
        return None