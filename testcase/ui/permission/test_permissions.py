# testcase/ui/permission/test_permissions.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@allure.feature('角色权限')
@allure.story('Teacher权限边界')
class TestTeacherPermissions:

    @allure.title('TC-PERM-01: Teacher无法创建新课程')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_teacher_cannot_create_course(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Teacher登录'):
            login_page.navigate()
            teacher = config.get('accounts.teacher', {})
            login_page.login(teacher.get('username', 'teacher'),
                             teacher.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Teacher login failed"

        with allure.step('直接访问创建课程页面 /course/edit.php'):
            driver.get(f"{config.base_url}/course/edit.php")
            login_page.wait_for_page_load()

        with allure.step('验证系统拒绝访问'):
            # 实测：页面显示 "An unusual error occurred trying to view a page that does not exist"
            page_text = driver.page_source
            assert "does not exist" in page_text or "Error" in driver.title, \
                "Teacher should not have permission to create courses"

        login_page.logout()

    @allure.title('TC-PERM-02: Teacher可修改课程全称')
    @allure.severity(allure.severity_level.NORMAL)
    def test_teacher_can_edit_course_name(self, driver):
        """已在 TC-COURSE-06 中验证通过，此处复用验证"""
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Teacher登录'):
            login_page.navigate()
            teacher = config.get('accounts.teacher', {})
            login_page.login(teacher.get('username', 'teacher'),
                             teacher.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Teacher login failed"

        with allure.step('搜索并进入课程（使用简称SWTEST2026）'):
            from utils.data_loader import load_yaml
            course_data = load_yaml('data/ui/course_data.yaml')
            shortname = course_data['course_creation']['shortname']
            search_input = driver.find_element(
                By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
            search_input.clear()
            search_input.send_keys(shortname)
            search_input.send_keys(Keys.ENTER)
            login_page.wait_for_page_load()
            course_link = driver.find_element(
                By.XPATH, f"//a[contains(@href, 'course/view.php')]")
            course_link.click()
            login_page.wait_for_page_load()

        with allure.step('点击Settings进入编辑页'):
            settings_link = driver.find_element(
                By.XPATH, "//nav//a[contains(text(), 'Settings')]")
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
@allure.story('Student权限边界')
class TestStudentPermissions:

    @allure.title('TC-PERM-03: Student禁止访问管理课程页面')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_student_blocked_from_management(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Student登录'):
            login_page.navigate()
            student = config.get('accounts.student', {})
            login_page.login(student.get('username', 'student'),
                             student.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Student login failed"

        with allure.step('直接访问管理课程页面 /course/management.php'):
            driver.get(f"{config.base_url}/course/management.php")
            login_page.wait_for_page_load()

        with allure.step('验证系统拒绝访问'):
            # 实测：学生看到的是课程分类页面（All courses），不是404
            # 验证当前URL不包含 management.php
            current_url = driver.current_url
            assert "management.php" not in current_url, \
                f"Student should be redirected away from management.php, but URL is {current_url}"

        login_page.logout()

    @allure.title('TC-PERM-04: Student无编辑模式开关')
    @allure.severity(allure.severity_level.NORMAL)
    def test_student_no_edit_mode(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Student登录并进入课程'):
            login_page.navigate()
            student = config.get('accounts.student', {})
            login_page.login(student.get('username', 'student'),
                             student.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Student login failed"

            from utils.data_loader import load_yaml
            course_data = load_yaml('data/ui/course_data.yaml')
            shortname = course_data['course_creation']['shortname']
            search_input = driver.find_element(
                By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
            search_input.clear()
            search_input.send_keys(shortname)
            search_input.send_keys(Keys.ENTER)
            login_page.wait_for_page_load()
            course_link = driver.find_element(
                By.XPATH, f"//a[contains(@href, 'course/view.php')]")
            course_link.click()
            login_page.wait_for_page_load()

        with allure.step('验证编辑模式开关不存在或隐藏'):
            edit_forms = driver.find_elements(
                By.CSS_SELECTOR, '.editmode-switch-form')
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
@allure.story('Privacy Officer权限验证')
class TestPrivacyOfficerPermissions:

    @allure.title('TC-PERM-05: Privacy Officer可访问Data requests')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_privacy_officer_data_requests(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Privacy Officer登录'):
            login_page.navigate()
            po = config.get('accounts.privacy_officer', {})
            login_page.login(po.get('username', 'privacyofficer'),
                             po.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Privacy Officer login failed"

        with allure.step('访问 Data requests 页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/datarequests.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面标题包含 Data requests'):
            page_title = driver.title
            allure.attach(page_title, name="Page Title",
                         attachment_type=allure.attachment_type.TEXT)
            assert "Data requests" in page_title, \
                f"Expected 'Data requests' in title, got '{page_title}'"

        login_page.logout()

    @allure.title('TC-PERM-06: Privacy Officer可查看Data registry')
    @allure.severity(allure.severity_level.NORMAL)
    def test_privacy_officer_data_registry(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Privacy Officer登录'):
            login_page.navigate()
            po = config.get('accounts.privacy_officer', {})
            login_page.login(po.get('username', 'privacyofficer'),
                             po.get('password', 'moodle26'))
            assert login_page.is_login_success(), "Privacy Officer login failed"

        with allure.step('访问 Data registry 页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/registry.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面可正常访问'):
            # 用页面标题和可见文本综合判断
            page_title = driver.title
            body_text = driver.find_element(By.TAG_NAME, 'body').text[:200]
            allure.attach(f"Title: {page_title}\nBody: {body_text}",
                         name="Page Content", attachment_type=allure.attachment_type.TEXT)
            # 页面标题或可见文本中应包含 registry 或 data 相关字样
            assert "registry" in page_title.lower() or "data" in body_text.lower(), \
                f"Data registry page not accessible. Title: '{page_title}'"

        login_page.logout()