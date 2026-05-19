# testcase/ui/permission/test_permissions.py
from pathlib import Path

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


# 课程创建阶段会记录真实课程地址。权限测试优先使用该地址，避免搜索页偶发无结果。
COURSE_URL_FILE = Path('data/runtime/course_url.txt')


def _login_with_retry(driver, login_page, account, default_username, role_name):
    """登录 Moodle；若站点保留旧会话导致判定失败，则清 Cookie 后重试一次。"""
    username = account.get('username', default_username)
    password = account.get('password', 'moodle26')

    login_page.navigate()
    login_page.login(username, password)
    if not login_page.is_login_success():
        driver.delete_all_cookies()
        login_page.navigate()
        login_page.login(username, password)

    assert login_page.is_login_success(), f"{role_name} login failed"


def _open_course(driver, login_page, config):
    """进入测试课程；优先使用运行时课程 URL，缺失时再退回到课程搜索。"""
    if COURSE_URL_FILE.exists():
        course_path = COURSE_URL_FILE.read_text(encoding='utf-8').strip()
        driver.get(config.base_url + course_path)
        login_page.wait_for_page_load()
        allure.attach(course_path, name='运行时课程地址',
                      attachment_type=allure.attachment_type.TEXT)
        return

    course_data = load_yaml('data/ui/course_data.yaml')
    shortname = course_data['course_creation']['shortname']
    search_input = driver.find_element(
        By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
    search_input.clear()
    search_input.send_keys(shortname)
    search_input.send_keys(Keys.ENTER)
    login_page.wait_for_page_load()

    course_link = driver.find_element(By.XPATH, "//a[contains(@href, 'course/view.php')]")
    course_link.click()
    login_page.wait_for_page_load()


@allure.feature('角色权限')
@allure.story('教师权限边界')
class TestTeacherPermissions:

    @allure.title('TC-PERM-01: 教师不能直接创建新课程')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_teacher_cannot_create_course(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('教师登录'):
            teacher = config.get('accounts.teacher', {})
            _login_with_retry(driver, login_page, teacher, 'teacher', 'Teacher')

        with allure.step('直接访问课程创建页面'):
            driver.get(f"{config.base_url}/course/edit.php")
            login_page.wait_for_page_load()

        with allure.step('验证系统拒绝教师创建课程'):
            page_text = driver.page_source
            assert "does not exist" in page_text or "Error" in driver.title, \
                "Teacher should not have permission to create courses"

        login_page.logout()

    @allure.title('TC-PERM-02: 教师可以修改课程全称')
    @allure.severity(allure.severity_level.NORMAL)
    def test_teacher_can_edit_course_name(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('教师登录'):
            teacher = config.get('accounts.teacher', {})
            _login_with_retry(driver, login_page, teacher, 'teacher', 'Teacher')

        with allure.step('进入测试课程'):
            _open_course(driver, login_page, config)

        with allure.step('进入课程设置页面'):
            settings_link = driver.find_element(By.XPATH, "//nav//a[contains(text(), 'Settings')]")
            settings_link.click()
            login_page.wait_for_page_load()

        with allure.step('修改课程全称并保存'):
            new_name = "软件测试实践-权限测试"
            fullname_input = driver.find_element(By.ID, 'id_fullname')
            fullname_input.clear()
            fullname_input.send_keys(new_name)
            save_btn = driver.find_element(By.ID, 'id_saveanddisplay')
            save_btn.click()
            login_page.wait_for_page_load()

        with allure.step('验证课程标题已更新'):
            course_title = driver.find_element(By.CSS_SELECTOR, 'h1').text
            assert new_name in course_title, \
                f"Expected '{new_name}' in title, got '{course_title}'"

        login_page.logout()


@allure.feature('角色权限')
@allure.story('学生权限边界')
class TestStudentPermissions:

    @allure.title('TC-PERM-03: 学生禁止访问课程管理页面')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_student_blocked_from_management(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('学生登录'):
            student = config.get('accounts.student', {})
            _login_with_retry(driver, login_page, student, 'student', 'Student')

        with allure.step('直接访问课程管理页面'):
            driver.get(f"{config.base_url}/course/management.php")
            login_page.wait_for_page_load()

        with allure.step('验证系统重定向或拒绝访问'):
            current_url = driver.current_url
            assert "management.php" not in current_url, \
                f"Student should be redirected away from management.php, but URL is {current_url}"

        login_page.logout()

    @allure.title('TC-PERM-04: 学生无编辑模式开关')
    @allure.severity(allure.severity_level.NORMAL)
    def test_student_no_edit_mode(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('学生登录并进入课程'):
            student = config.get('accounts.student', {})
            _login_with_retry(driver, login_page, student, 'student', 'Student')
            _open_course(driver, login_page, config)

        with allure.step('验证编辑模式开关不可见'):
            edit_forms = driver.find_elements(By.CSS_SELECTOR, '.editmode-switch-form')
            all_hidden = True
            for form in edit_forms:
                parent_class = form.find_element(By.XPATH, '..').get_attribute('class') or ''
                if 'hidden' not in parent_class:
                    all_hidden = False
                    break
            assert all_hidden or len(edit_forms) == 0, \
                "Edit mode switch should not be accessible to Student"

        login_page.logout()


@allure.feature('角色权限')
@allure.story('隐私官权限验证')
class TestPrivacyOfficerPermissions:

    @allure.title('TC-PERM-05: 隐私官可以访问数据请求页面')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_privacy_officer_data_requests(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('隐私官登录'):
            po = config.get('accounts.privacy_officer', {})
            _login_with_retry(driver, login_page, po, 'privacyofficer', 'Privacy Officer')

        with allure.step('访问 Data requests 页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/datarequests.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面标题包含 Data requests'):
            page_title = driver.title
            allure.attach(page_title, name="页面标题",
                          attachment_type=allure.attachment_type.TEXT)
            assert "Data requests" in page_title, \
                f"Expected 'Data requests' in title, got '{page_title}'"

        login_page.logout()

    @allure.title('TC-PERM-06: 隐私官可以访问数据注册表页面')
    @allure.severity(allure.severity_level.NORMAL)
    def test_privacy_officer_data_registry(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('隐私官登录'):
            po = config.get('accounts.privacy_officer', {})
            _login_with_retry(driver, login_page, po, 'privacyofficer', 'Privacy Officer')

        with allure.step('访问 Data registry 页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/registry.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面可正常访问'):
            page_title = driver.title
            body_text = driver.find_element(By.TAG_NAME, 'body').text[:200]
            allure.attach(f"Title: {page_title}\nBody: {body_text}",
                          name="页面内容", attachment_type=allure.attachment_type.TEXT)
            assert "registry" in page_title.lower() or "data" in body_text.lower(), \
                f"Data registry page not accessible. Title: '{page_title}'"

        login_page.logout()
