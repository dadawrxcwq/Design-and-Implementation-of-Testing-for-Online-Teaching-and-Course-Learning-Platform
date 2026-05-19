# testcase/api/test_api.py
import pytest
import allure
import re
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
from selenium.webdriver.common.by import By
import requests


def _get_session_from_selenium(driver):
    """Selenium 登录 → 提取 Cookie、sesskey、课程 ID → 注入 requests.Session"""
    login_page = LoginPage(driver)
    config = config_reader
    base_url = config.base_url

    # Selenium 登录
    login_page.navigate()
    student = config.get('accounts.student', {})
    login_page.login(student.get('username', 'student'),
                     student.get('password', 'moodle26'))
    assert login_page.is_login_success(), "Selenium login failed"

    # 提取所有 Cookie
    selenium_cookies = driver.get_cookies()

    # 从页面源码中提取 sesskey
    page_source = driver.page_source
    sesskey_match = re.search(r'"sesskey":"(\w+)"', page_source)
    sesskey = sesskey_match.group(1) if sesskey_match else None

    # 从 Selenium 当前页面提取课程 ID（比 requests 静态 HTML 更可靠）
    course_id = None
    course_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/course/view.php')]")
    for link in course_links:
        href = link.get_attribute('href')
        match = re.search(r'id=(\d+)', href)
        if match:
            course_id = match.group(1)
            break

    # 创建 requests.Session 并注入 Cookie
    session = requests.Session()
    session.get(base_url)
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'],
                            domain=cookie.get('domain', '').lstrip('.'),
                            path=cookie.get('path', '/'))

    # 把 sesskey 和 course_id 挂到 session 上供后续使用
    session._sesskey = sesskey
    session._course_id = course_id

    return session


@allure.feature('API测试')
@allure.story('用户认证接口')
class TestAuthAPI:

    @allure.title('API-01: Selenium 登录后 Cookie 可用性验证')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_cookie_transfer(self, driver):
        with allure.step('Selenium 登录并提取 Cookie'):
            session = _get_session_from_selenium(driver)

        with allure.step('用 requests 访问 Dashboard 验证登录状态'):
            dashboard_url = f"{config_reader.base_url}/my/"
            resp = session.get(dashboard_url)
            assert resp.status_code == 200
            assert "Dashboard" in resp.text or "My courses" in resp.text, \
                "Cookie transfer failed — not logged in"
            allure.attach("Cookie 传递成功，requests 处于已登录状态",
                         name="验证结果", attachment_type=allure.attachment_type.TEXT)


@allure.feature('API测试')
@allure.story('课程接口')
class TestCourseAPI:

    @allure.title('API-02: 课程详情页面通过 requests 访问')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_course_view_page_via_requests(self, driver):
        """用 Selenium 提取课程 ID，再用 requests 验证课程页可访问"""
        base_url = config_reader.base_url
        session = _get_session_from_selenium(driver)
        course_id = getattr(session, '_course_id', None)

        assert course_id is not None, \
            "无法从 Selenium 页面提取课程 ID（学生可能未加入任何课程）"
        allure.attach(course_id, name="Course ID", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f'requests 访问 /course/view.php?id={course_id}'):
            resp = session.get(f"{base_url}/course/view.php?id={course_id}")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            # 页面应包含课程标题等课程内容
            assert "course" in resp.text.lower() or "section" in resp.text.lower(), \
                "Course page does not contain expected content"
            allure.attach("课程页面可正常访问，内容正确", name="验证结果",
                         attachment_type=allure.attachment_type.TEXT)

    @allure.title('API-03: Dashboard 页面接口验证')
    @allure.severity(allure.severity_level.NORMAL)
    def test_dashboard_page(self, driver):
        """验证 requests 能正常访问 Dashboard 并返回已登录内容"""
        base_url = config_reader.base_url
        session = _get_session_from_selenium(driver)

        with allure.step('requests 访问 Dashboard (/my/)'):
            resp = session.get(f"{base_url}/my/")
            assert resp.status_code == 200

        with allure.step('验证页面内容包含已登录标识'):
            text = resp.text
            assert "Dashboard" in text or "My courses" in text or \
                   "Course overview" in text or "Timeline" in text, \
                "Dashboard page does not contain logged-in content"
            allure.attach("Dashboard 页面可正常访问", name="验证结果",
                         attachment_type=allure.attachment_type.TEXT)


@allure.feature('API测试')
@allure.story('成绩接口')
class TestGradeAPI:

    @allure.title('API-04: 成绩概览页面访问')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_grade_overview(self, driver):
        base_url = config_reader.base_url
        session = _get_session_from_selenium(driver)

        with allure.step('访问成绩概览页'):
            resp = session.get(f"{base_url}/grade/report/overview/index.php")
            assert resp.status_code == 200

        with allure.step('验证页面包含成绩内容'):
            text = resp.text.lower()
            assert "grade" in text or "overview" in text, \
                "Grade page should contain grade/overview content"
            allure.attach("成绩页面可正常访问", name="验证结果",
                         attachment_type=allure.attachment_type.TEXT)