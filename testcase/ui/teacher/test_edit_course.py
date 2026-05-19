# testcase/ui/teacher/test_edit_course.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path


COURSE_URL_FILE = Path('data/runtime/course_url.txt')


@allure.feature('课程管理')
@allure.story('Teacher编辑课程')
class TestTeacherEditCourse:

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

        # 搜索并进入课程（T1/T2/T3 共用）
        self._enter_course()
        yield
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except:
            pass

    def _enter_course(self):
        """搜索课程并点击进入"""
        search_kw = self.course_data['course_access']['search_keyword']
        course_fullname = self.course_data['course_creation']['fullname']

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
            except:
                continue
        if search_input is None:
            search_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')

        search_input.clear()
        search_input.send_keys(search_kw)
        search_input.send_keys(Keys.ENTER)
        self.login_page.wait_for_page_load()

        course_links = self.driver.find_elements(
            By.XPATH, f"//a[contains(., '{course_fullname}')]")
        course_link = next((link for link in course_links if link.is_displayed()), course_links[0])
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_link)
        self.driver.execute_script("arguments[0].click();", course_link)
        self.login_page.wait_for_page_load()

    @allure.title('TC-COURSE-05: Teacher开启编辑模式')
    @allure.severity(allure.severity_level.NORMAL)
    def test_toggle_edit_mode(self):
        """T1 + T2: 开启编辑模式并断言"""
        with allure.step('1. Click Edit mode switch'):
            # T1: /html/body/div[2]/nav/div/div[2]/form/div/div/input
            edit_switch = self.driver.find_element(
                By.CSS_SELECTOR, 'nav .editmode-switch-form input[type="checkbox"]')
            # 如果未选中则点击
            if not edit_switch.is_selected():
                # 点击其label来切换
                label = self.driver.find_element(By.CSS_SELECTOR, 'nav .editmode-switch-form label')
                label.click()
                self.login_page.sleep(1)

        with allure.step('2. Verify Bulk actions button appears'):
            # T1 断言: /html/body/div[4]/div[5]/div/header/div/div[2]/div[2]/div/button
            bulk_btn = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Bulk actions')]")
            assert bulk_btn.is_displayed(), "Bulk actions button not visible"

    @allure.title('TC-COURSE-06: Teacher修改课程名并保存')
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_course_name(self):
        """T3: 修改Course full name并验证"""
        new_fullname = self.course_data['edit_course']['new_fullname']

        with allure.step('1. Click Settings in left navigation'):
            # T3 Settings: /html/body/div[4]/div[5]/div/div[2]/nav/ul/li[2]/a
            settings_link = self.driver.find_element(
                By.XPATH, "//nav//a[contains(text(), 'Settings')]")
            settings_link.click()
            self.login_page.wait_for_page_load()

        with allure.step('2. Clear and input new Course full name'):
            # T3 form: id_fullname
            fullname_input = self.driver.find_element(By.ID, 'id_fullname')
            fullname_input.clear()
            fullname_input.send_keys(new_fullname)

        with allure.step('3. Click Save and display'):
            # T3: id_saveanddisplay
            save_btn = self.driver.find_element(By.ID, 'id_saveanddisplay')
            save_btn.click()
            self.login_page.wait_for_page_load()

        with allure.step('4. Verify course title updated'):
            # T3 assertion: h1 element
            course_title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            allure.attach(course_title, name="Course title", attachment_type=allure.attachment_type.TEXT)
            assert new_fullname in course_title, \
                f"Expected title containing '{new_fullname}', got '{course_title}'"
