# testcase/ui/teacher/test_assignment.py
from datetime import datetime, timedelta
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


ASSIGNMENT_URL_FILE = Path('data/runtime/assignment_url.txt')
COURSE_URL_FILE = Path('data/runtime/course_url.txt')


@allure.feature('作业功能')
@allure.story('作业创建、提交、评分与反馈')
class TestAssignmentFlow:

    @pytest.fixture(autouse=True)
    def setup_class(self, driver):
        self.driver = driver
        self.config = config_reader
        self.login_page = LoginPage(driver)
        self.course_data = load_yaml('data/ui/course_data.yaml')
        yaml_data = load_yaml('data/ui/assignment_data.yaml')
        self.assignment_data = yaml_data.get('assignment', {})
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except Exception:
            pass

    def _login(self, role, default_username):
        """登录指定角色；Moodle demo 站点偶发旧会话残留时，清理 Cookie 后重试一次。"""
        account = self.config.get(f'accounts.{role}', {})
        username = account.get('username', default_username)
        password = account.get('password', 'moodle26')

        self.login_page.navigate()
        self.login_page.login(username, password)
        if not self.login_page.is_login_success():
            self.driver.delete_all_cookies()
            self.login_page.navigate()
            self.login_page.login(username, password)

        assert self.login_page.is_login_success(), f"{role} login failed"

    def _enter_course(self):
        """进入测试课程。优先使用 Dean 创建课程时保存的真实 URL。"""
        if COURSE_URL_FILE.exists():
            course_path = COURSE_URL_FILE.read_text(encoding='utf-8').strip()
            self.driver.get(self.config.base_url + course_path)
            self.login_page.wait_for_page_load()
            allure.attach(course_path, name='运行时课程地址',
                          attachment_type=allure.attachment_type.TEXT)
            return

        course_names = [
            self.course_data.get('edit_course', {}).get('new_fullname'),
            self.course_data['course_creation'].get('fullname'),
            self.course_data['course_creation'].get('shortname'),
        ]
        course_names = [name for name in course_names if name]
        course_link = None

        for course_name in course_names:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="search"], input[name="search"]'))
            )
            search_input.clear()
            search_input.send_keys(course_name)
            search_input.send_keys(Keys.ENTER)
            self.login_page.wait_for_page_load()
            links = self.driver.find_elements(By.XPATH, f"//a[contains(., '{course_name}')]")
            visible_links = [link for link in links if link.is_displayed()]
            if visible_links:
                course_link = visible_links[0]
                break

        if course_link is None:
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/course/view.php')]")
            visible_links = [link for link in links if link.is_displayed()]
            if visible_links:
                course_link = visible_links[0]

        assert course_link is not None, f"Course not found. Tried: {course_names}"
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_link)
        self.driver.execute_script("arguments[0].click();", course_link)
        self.login_page.wait_for_page_load()

    def _teacher_login_and_enter_course(self):
        self._login('teacher', 'teacher')
        self._enter_course()

    def _student_login_and_enter_course(self):
        self._login('student', 'student')
        self._enter_course()

    def _visible_enabled(self, locator):
        elements = self.driver.find_elements(*locator)
        return [element for element in elements if element.is_displayed() and element.is_enabled()]

    def _enable_edit_mode(self):
        """开启课程编辑模式；只要求开关处于选中状态，不强依赖 Bulk actions 文案。"""
        switch_locator = (By.CSS_SELECTOR, 'nav .editmode-switch-form input[type="checkbox"]')
        edit_switch = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(switch_locator)
        )
        if not edit_switch.is_selected():
            label = self.driver.find_element(By.CSS_SELECTOR, 'nav .editmode-switch-form label')
            self.driver.execute_script("arguments[0].click();", label)
            self.login_page.sleep(2)
            self.login_page.wait_for_page_load()

        def edit_mode_ready(driver):
            switches = driver.find_elements(*switch_locator)
            if switches and switches[0].is_selected():
                return True
            controls = driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Bulk actions')]"
                " | //button[contains(., 'Add an activity') or contains(., 'Add content')]"
                " | //button[contains(@aria-label, 'Add') or contains(@title, 'Add')]"
            )
            return any(control.is_displayed() for control in controls)

        assert WebDriverWait(self.driver, 10).until(edit_mode_ready), "Edit mode not enabled"

    def _open_activity_chooser(self):
        """打开添加活动窗口，兼容 Moodle 一步或两步菜单入口。"""
        locators = [
            (By.XPATH, "//button[contains(., 'Add an activity or resource')]"),
            (By.XPATH, "//button[contains(., 'Add an activity') or contains(., 'Add content')]"),
            (By.XPATH, "//button[contains(@aria-label, 'Add') or contains(@title, 'Add')]"),
            (By.CSS_SELECTOR, "button[data-action='open-chooser']"),
            (By.CSS_SELECTOR, ".activity-add button, .section-modchooser button"),
            (By.XPATH, "/html/body/div[4]/div[5]/div/div[3]/div/div/div/div/div/ul/li[1]/div/div[2]/div[2]/div/div/button"),
        ]
        for locator in locators:
            buttons = self._visible_enabled(locator)
            if buttons:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[0])
                self.driver.execute_script("arguments[0].click();", buttons[0])
                self.login_page.sleep(1)
                break
        else:
            raise AssertionError("Add activity menu not found")

        if self.driver.find_elements(By.ID, 'id_name'):
            return
        if self.driver.find_elements(By.XPATH, "//a[contains(., 'Assignment')] | //button[contains(., 'Assignment')]"):
            return

        second_step = [
            (By.XPATH, "//button[contains(., 'Add an activity or resource')]"),
            (By.XPATH, "/html/body/div[4]/div[5]/div/div[3]/div/div/div/div/div/ul/li[1]/div/div[2]/div[2]/div/div/div/button"),
        ]
        for locator in second_step:
            buttons = self._visible_enabled(locator)
            if buttons:
                self.driver.execute_script("arguments[0].click();", buttons[0])
                self.login_page.sleep(2)
                return

    def _fill_tinymce(self, iframe_id, text, timeout=20):
        """填写 TinyMCE；如果 iframe 未加载，则回退到隐藏 textarea。"""
        textarea_id = iframe_id.replace('_ifr', '')
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, iframe_id))
            )
            body = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tinymce'))
            )
            body.clear()
            body.send_keys(text)
            self.driver.switch_to.default_content()
            self.login_page.sleep(1)
            return True
        except TimeoutException:
            self.driver.switch_to.default_content()
            textareas = self.driver.find_elements(By.ID, textarea_id)
            if not textareas:
                return False
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                textareas[0], text
            )
            return True

    def _click_save_and_display(self):
        locators = [
            (By.ID, 'id_submitbutton2'),
            (By.ID, 'id_saveanddisplay'),
            (By.NAME, 'submitbutton2'),
            (By.XPATH, "//input[@type='submit' and contains(@value, 'Save and display')]"),
            (By.XPATH, "//button[contains(normalize-space(.), 'Save and display')]"),
            (By.ID, 'id_submitbutton'),
        ]
        for locator in locators:
            buttons = self._visible_enabled(locator)
            if buttons:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[0])
                self.driver.execute_script("arguments[0].click();", buttons[0])
                self.login_page.wait_for_page_load()
                return
        raise AssertionError("Save and display button not found")

    def _find_assignment_link(self, title, timeout=10):
        xpaths = [
            f"//a[contains(@href, '/mod/assign/view.php') and contains(normalize-space(.), '{title}')]",
            f"//a[contains(@href, 'mod/assign/view.php') and contains(normalize-space(.), '{title}')]",
            "//a[contains(@href, '/mod/assign/view.php')]",
            "//a[contains(@href, 'mod/assign/view.php')]",
        ]

        def visible_link(driver):
            for xpath in xpaths:
                links = driver.find_elements(By.XPATH, xpath)
                visible_links = [link for link in links if link.is_displayed()]
                if visible_links:
                    return visible_links[0]
            return False

        return WebDriverWait(self.driver, timeout).until(visible_link)

    def _save_assignment_url(self, title):
        current_url = self.driver.current_url
        if '/mod/assign/view.php' not in current_url:
            try:
                current_url = self._find_assignment_link(title, timeout=10).get_attribute('href')
            except TimeoutException:
                allure.attach(self.driver.current_url, name='当前页面地址',
                              attachment_type=allure.attachment_type.TEXT)
                allure.attach(self.driver.page_source[:4000], name='页面源码片段',
                              attachment_type=allure.attachment_type.TEXT)
                raise AssertionError(f"Assignment not visible after save: {title}")

        ASSIGNMENT_URL_FILE.parent.mkdir(parents=True, exist_ok=True)
        ASSIGNMENT_URL_FILE.write_text(current_url, encoding='utf-8')
        allure.attach(current_url, name='作业地址', attachment_type=allure.attachment_type.TEXT)
        return current_url

    def _open_assignment(self, title):
        if ASSIGNMENT_URL_FILE.exists():
            saved_url = ASSIGNMENT_URL_FILE.read_text(encoding='utf-8').strip()
            if saved_url:
                self.driver.get(saved_url)
                self.login_page.wait_for_page_load()
                return

        assign_link = self._find_assignment_link(title, timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assign_link)
        self.driver.execute_script("arguments[0].click();", assign_link)
        self.login_page.wait_for_page_load()

    @allure.title('TC-ASSIGN-01: 教师发布作业')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_assignment(self):
        data = self.assignment_data
        title = data.get('title', 'Assignment1')
        desc = data.get('description', '')
        due_date = datetime.now() + timedelta(days=7)

        if ASSIGNMENT_URL_FILE.exists():
            ASSIGNMENT_URL_FILE.unlink()

        self._teacher_login_and_enter_course()
        self._enable_edit_mode()

        with allure.step('打开添加活动或资源窗口'):
            self._open_activity_chooser()

        with allure.step('选择 Assignment 并进入作业表单'):
            assignment_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//a[contains(., 'Assignment')] | //button[contains(., 'Assignment')]"))
            )
            self.driver.execute_script("arguments[0].click();", assignment_option)
            self.login_page.sleep(1)
            if not self.driver.find_elements(By.ID, 'id_name'):
                add_buttons = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'modal')]//button[normalize-space(.)='Add' or contains(., 'Add')]"
                    " | //button[normalize-space(.)='Add' or contains(., 'Add')]"
                )
                visible_add_buttons = [button for button in add_buttons
                                       if button.is_displayed() and button.is_enabled()]
                if visible_add_buttons:
                    self.driver.execute_script("arguments[0].click();", visible_add_buttons[-1])
            self.login_page.wait_for_page_load()

        with allure.step('填写作业名称、描述和截止日期'):
            self.login_page.input_text((By.ID, 'id_name'), title)
            self._fill_tinymce('id_introeditor_ifr', desc)
            due = self.driver.find_element(By.ID, 'id_duedate_enabled')
            if not due.is_selected():
                due.click()
            Select(self.driver.find_element(By.ID, 'id_duedate_day')).select_by_value(str(due_date.day))
            Select(self.driver.find_element(By.ID, 'id_duedate_month')).select_by_value(str(due_date.month))
            Select(self.driver.find_element(By.ID, 'id_duedate_year')).select_by_value(str(due_date.year))

        with allure.step('保存并显示作业'):
            self._click_save_and_display()

        with allure.step('验证作业已创建并记录地址'):
            assignment_url = self._save_assignment_url(title)
            assert '/mod/assign/view.php' in assignment_url, "Assignment not visible"

    @allure.title('TC-ASSIGN-02: 学生提交作业')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_submit_assignment(self):
        data = self.assignment_data
        title = data.get('title', 'Assignment1')
        file_path = data.get('file_path', r'E:\桌面\这是一份作业.txt')

        self._student_login_and_enter_course()

        with allure.step('进入作业详情页'):
            self._open_assignment(title)

        with allure.step('打开提交页面'):
            add_buttons = self._visible_enabled((By.XPATH, "//button[contains(., 'Add submission')]"))
            if not add_buttons:
                add_buttons = self._visible_enabled(
                    (By.XPATH, "/html/body/div[2]/div[4]/div/div[2]/div/div/div[2]/div[1]/div/div/div/form/button"))
            assert add_buttons, "Add submission button not found"
            self.driver.execute_script("arguments[0].click();", add_buttons[0])
            self.login_page.sleep(2)

        with allure.step('上传作业文件'):
            add_file_btn = self.driver.find_element(By.CSS_SELECTOR, '.fp-btn-add a')
            add_file_btn.click()
            self.login_page.sleep(2)
            upload_tab = self.driver.find_element(By.XPATH, "//a[contains(., 'Upload a file')]")
            upload_tab.click()
            self.login_page.sleep(1)
            file_input = self.driver.find_element(By.NAME, 'repo_upload_file')
            file_input.send_keys(file_path)
            self.login_page.sleep(1)
            upload_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Upload this file')]")
            upload_btn.click()
            self.login_page.sleep(3)

        with allure.step('保存提交'):
            self.driver.find_element(By.ID, 'id_submitbutton').click()
            self.login_page.wait_for_page_load()

        with allure.step('验证提交成功'):
            assert self.login_page.is_text_present("Submitted for grading"), "提交失败"

    @allure.title('TC-ASSIGN-05: 教师评分')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_grade_assignment(self):
        data = self.assignment_data
        title = data.get('title', 'Assignment1')
        grade = data.get('grade', '100')
        feedback = data.get('feedback_text', 'Good job.')

        self._teacher_login_and_enter_course()

        with allure.step('进入作业详情页'):
            self._open_assignment(title)

        with allure.step('进入评分页面'):
            grade_links = self._visible_enabled((By.XPATH, "//a[contains(., 'Grade') or contains(., 'View all submissions')]"))
            if not grade_links:
                grade_links = self._visible_enabled(
                    (By.CSS_SELECTOR, "#region-main .tertiary-navigation a"))
            assert grade_links, "Grade link not found"
            self.driver.execute_script("arguments[0].click();", grade_links[0])
            self.login_page.wait_for_page_load()

        with allure.step('输入分数'):
            grade_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'id_grade'))
            )
            grade_input.clear()
            grade_input.send_keys(grade)

        with allure.step('填写反馈'):
            self._fill_tinymce('id_assignfeedbackcomments_editor_ifr', feedback)

        with allure.step('保存评分'):
            save_buttons = self._visible_enabled(
                (By.XPATH, "//button[contains(., 'Save changes')] | //input[contains(@value, 'Save changes')]"))
            if not save_buttons:
                save_buttons = self._visible_enabled(
                    (By.XPATH, "/html/body/div[4]/section/div[2]/div[5]/div/div[2]/form/button[1]"))
            assert save_buttons, "Save changes button not found"
            self.driver.execute_script("arguments[0].click();", save_buttons[0])
            self.login_page.wait_for_page_load()

        with allure.step('验证评分已保存'):
            assert self.login_page.is_text_present(grade), "评分未保存"

    @allure.title('TC-ASSIGN-06: 学生查看反馈')
    @allure.severity(allure.severity_level.NORMAL)
    def test_view_feedback(self):
        data = self.assignment_data
        title = data.get('title', 'Assignment1')
        grade = data.get('grade', '100')

        self._student_login_and_enter_course()

        with allure.step('进入作业详情页'):
            self._open_assignment(title)

        with allure.step('验证成绩可见'):
            feedback_div = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(., 'Feedback') or contains(., 'Grade')]"))
            )
            grade_text = feedback_div.text.strip()
            allure.attach(grade_text, name='反馈区域文本', attachment_type=allure.attachment_type.TEXT)
            assert grade in grade_text, f"成绩不可见。期望包含 {grade}，实际为 {grade_text}"
