# testcase/api/test_moodle_api.py
import pytest
import allure
import re
from pages.auth.login_page import LoginPage
from utils.config_reader import config_reader
import requests


def _get_credentials_from_selenium(driver):
    """Selenium 登录 → 提取 MoodleSession Cookie 和 sesskey → 注入 requests.Session"""
    login_page = LoginPage(driver)
    config = config_reader
    base_url = config.base_url

    # 1. Selenium 登录
    login_page.navigate()
    student = config.get('accounts.student', {})
    login_page.login(student.get('username', 'student'),
                     student.get('password', 'moodle26'))
    assert login_page.is_login_success(), "Selenium login failed"

    # 2. 提取 MoodleSession Cookie
    selenium_cookies = driver.get_cookies()
    moodle_session = None
    for c in selenium_cookies:
        if c['name'] == 'MoodleSession':
            moodle_session = c['value']
            break
    assert moodle_session is not None, "MoodleSession cookie not found after Selenium login"

    # 3. 提取 sesskey
    page_source = driver.page_source
    match = re.search(r'"sesskey":"(\w+)"', page_source)
    assert match, "sesskey not found in page source"
    sesskey = match.group(1)

    # 4. 创建 requests.Session 并注入 Cookie
    session = requests.Session()
    session.get(base_url)  # 建立域
    session.cookies.set('MoodleSession', moodle_session,
                        domain='school.moodledemo.net', path='/')
    session._sesskey = sesskey

    allure.attach(moodle_session, name="MoodleSession", attachment_type=allure.attachment_type.TEXT)
    allure.attach(sesskey, name="sesskey", attachment_type=allure.attachment_type.TEXT)
    return session


@allure.feature('API测试')
@allure.story('Moodle 接口验证 (Selenium 登录 + Requests 调用)')
class TestMoodleAPI:

    @allure.title('API-01: 验证 Selenium 登录后凭证提取')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_credential_extraction(self, driver):
        """验证能正常提取 MoodleSession 和 sesskey"""
        session = _get_credentials_from_selenium(driver)
        assert session.cookies.get('MoodleSession') is not None
        assert getattr(session, '_sesskey', None) is not None
        allure.attach("凭证提取成功", name="Status", attachment_type=allure.attachment_type.TEXT)

    @allure.title('API-02: 课程列表 Ajax 接口 (JSON 校验)')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_course_list(self, driver):
        """携带 MoodleSession 和 sesskey 调用课程列表接口，校验 JSON 结构"""
        base_url = config_reader.base_url
        session = _get_credentials_from_selenium(driver)
        sesskey = session._sesskey

        with allure.step('调用 core_course_get_enrolled_courses 接口'):
            url = f"{base_url}/lib/ajax/service.php?sesskey={sesskey}"
            body = [{
                "index": 0,
                "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
                "args": {
                    "offset": 0,
                    "limit": 10,
                    "classification": "all",
                    "sort": "fullname"
                }
            }]
            resp = session.post(url, json=body)
            assert resp.status_code == 200, f"HTTP {resp.status_code}"
            data = resp.json()

        with allure.step('校验 JSON 结构'):
            allure.attach(str(data)[:600], name="JSON Response (truncated)",
                         attachment_type=allure.attachment_type.JSON)
            assert isinstance(data, list), "应为数组"
            item = data[0] if data else {}
            # error 为 False 才是成功
            assert item.get('error', False) is False, f"接口返回错误: {item}"

            # 课程列表藏在 item.data.courses 中
            courses = item.get('data', {}).get('courses', [])
            assert len(courses) > 0, "课程列表为空"
            first_course = courses[0]
            assert 'id' in first_course, "缺少 id 字段"
            assert 'fullname' in first_course, "缺少 fullname 字段"
            allure.attach(first_course['fullname'], name="第一门课程名",
                         attachment_type=allure.attachment_type.TEXT)

    @allure.title('API-03: 成绩概览页面')
    @allure.severity(allure.severity_level.NORMAL)
    def test_grade_page(self, driver):
        """携带凭证访问成绩页面，验证内容"""
        base_url = config_reader.base_url
        session = _get_credentials_from_selenium(driver)

        resp = session.get(f"{base_url}/grade/report/overview/index.php")
        assert resp.status_code == 200
        text = resp.text.lower()
        assert "grade" in text or "overview" in text, "页面缺少成绩相关内容"
        allure.attach("成绩页面访问成功", name="Status", attachment_type=allure.attachment_type.TEXT)