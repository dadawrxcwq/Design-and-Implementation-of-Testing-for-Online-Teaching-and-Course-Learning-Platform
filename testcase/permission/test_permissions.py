# testcase/ui/permission/test_permissions.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from selenium.webdriver.common.by import By


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

        with allure.step('直接访问创建课程页面'):
            driver.get(f"{config.base_url}/course/edit.php")
            login_page.wait_for_page_load()

        with allure.step('验证无法创建课程'):
            # 预期：页面提示无权限，或跳转到其他页面
            assert "edit.php" not in driver.current_url \
                or login_page.is_text_present("permission"), \
                "Teacher should not be able to create courses"

        login_page.logout()

    @allure.title('TC-PERM-02: Teacher可修改课程设置')
    @allure.severity(allure.severity_level.NORMAL)
    def test_teacher_can_edit_course_settings(self, driver):
        config = config_reader
        login_page = LoginPage(driver)

        with allure.step('Teacher登录并进入课程'):
            login_page.navigate()
            teacher = config.get('accounts.teacher', {})
            login_page.login(teacher.get('username', 'teacher'),
                             teacher.get('password', 'moodle26'))
            assert login_page.is_login_success()

            # 搜索课程
            from utils.data_loader import load_yaml
            course_data = load_yaml('data/ui/course_data.yaml')
            fullname = course_data['course_creation']['fullname']
            search_input = driver.find_element(
                By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
            search_input.clear()
            search_input.send_keys(fullname)
            search_input.send_keys('\n')
            login_page.wait_for_page_load()
            course_link = driver.find_element(
                By.XPATH, f"//a[contains(., '{fullname}')]")
            course_link.click()
            login_page.wait_for_page_load()

        with allure.step('点击Settings进入编辑页'):
            settings_link = driver.find_element(
                By.XPATH, "//nav//a[contains(text(), 'Settings')]")
            settings_link.click()
            login_page.wait_for_page_load()

        with allure.step('修改课程全称'):
            fullname_input = driver.find_element(By.ID, 'id_fullname')
            new_name = course_data.get('edit_course', {}).get('new_fullname',
                                                              "软件测试实践-修改版")
            fullname_input.clear()
            fullname_input.send_keys(new_name)

        with allure.step('保存'):
            save_btn = driver.find_element(By.ID, 'id_saveanddisplay')
            save_btn.click()
            login_page.wait_for_page_load()

        with allure.step('验证课程标题更新'):
            course_title = driver.find_element(By.CSS_SELECTOR, 'h1').text
            assert new_name in course_title, \
                f"Expected title containing '{new_name}', got '{course_title}'"

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

        with allure.step('尝试直接访问管理课程页面'):
            driver.get(f"{config.base_url}/course/management.php")
            login_page.wait_for_page_load()

        with allure.step('验证被拒绝或重定向'):
            # 预期：当前URL不包含management.php，或页面包含权限错误
            assert "management.php" not in driver.current_url \
                or login_page.is_text_present("Access denied") \
                or login_page.is_text_present("permission"), \
                "Student should not have access to course management"

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
            assert login_page.is_login_success()

            from utils.data_loader import load_yaml
            course_data = load_yaml('data/ui/course_data.yaml')
            fullname = course_data['course_creation']['fullname']
            search_input = driver.find_element(
                By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
            search_input.clear()
            search_input.send_keys(fullname)
            search_input.send_keys('\n')
            login_page.wait_for_page_load()
            course_link = driver.find_element(
                By.XPATH, f"//a[contains(., '{fullname}')]")
            course_link.click()
            login_page.wait_for_page_load()

        with allure.step('验证编辑模式开关不可见'):
            # 学生不应该看到编辑模式开关
            edit_switch = driver.find_elements(
                By.CSS_SELECTOR, '.editmode-switch-form')
            assert len(edit_switch) == 0 or not edit_switch[0].is_displayed(), \
                "Edit mode switch should not be visible to students"

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

        with allure.step('访问Data requests页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/datarequests.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面正常加载'):
            # 预期页面包含"Data requests"标题或数据请求列表
            page_source = driver.page_source
            assert "Data requests" in page_source or "datarequests" in driver.current_url, \
                "Privacy Officer should have access to Data requests"

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
            assert login_page.is_login_success()

        with allure.step('访问Data registry页面'):
            driver.get(f"{config.base_url}/admin/tool/dataprivacy/registry.php")
            login_page.wait_for_page_load()

        with allure.step('验证页面正常加载'):
            page_source = driver.page_source
            assert "Data registry" in page_source or "registry" in driver.current_url, \
                "Privacy Officer should have access to Data registry"

        login_page.logout()