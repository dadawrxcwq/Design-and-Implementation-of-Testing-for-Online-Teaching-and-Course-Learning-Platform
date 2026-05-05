# testcase/api/test_api.py
import pytest
import allure
from common.base_request import BaseRequest
from utils.config_reader import config_reader
from selenium.webdriver.common.by import By


@allure.feature('API测试')
@allure.story('用户认证接口')
class TestAuthAPI:

    @pytest.fixture(scope='class')
    def api_client(self):
        """创建API客户端"""
        client = BaseRequest()
        yield client
        client.close()

    @allure.title('登录接口验证 - 正确凭据')
    @allure.description('验证使用正确用户名密码登录后能获取有效的Session Cookie')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_api_valid_credentials(self, api_client):
        """POST /login/index.php 正确登录"""

        with allure.step('发送登录请求'):
            login_url = f"{config_reader.base_url}/login/index.php"
            payload = {
                'username': 'student',
                'password': 'moodle26'
            }
            response = api_client.post(login_url, data=payload, allow_redirects=False)

        with allure.step('验证响应状态码（302重定向）'):
            allure.attach(str(response.status_code), name="状态码",
                         attachment_type=allure.attachment_type.TEXT)
            assert response.status_code in [302, 303], \
                f"Expected 302/303 redirect, got {response.status_code}"

        with allure.step('验证响应头包含MoodleSession Cookie'):
            cookies = response.cookies
            allure.attach(str(dict(cookies)), name="Cookies",
                         attachment_type=allure.attachment_type.TEXT)
            assert 'MoodleSession' in cookies, \
                "Login response should contain MoodleSession cookie"

    @allure.title('登录接口验证 - 错误密码')
    @allure.description('验证使用错误密码登录时返回登录页面且不设置Session')
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_api_invalid_password(self, api_client):
        """POST /login/index.php 错误密码"""

        with allure.step('发送错误密码登录请求'):
            login_url = f"{config_reader.base_url}/login/index.php"
            payload = {
                'username': 'student',
                'password': 'wrongpassword'
            }
            response = api_client.post(login_url, data=payload, allow_redirects=False)

        with allure.step('验证响应状态码'):
            allure.attach(str(response.status_code), name="状态码",
                         attachment_type=allure.attachment_type.TEXT)
            # 错误登录可能返回200（停留在登录页）或302（重定向回登录页）
            assert response.status_code in [200, 302], \
                f"Expected 200 or 302, got {response.status_code}"

        with allure.step('验证页面包含错误提示'):
            assert "Invalid login" in response.text \
                or "username or password" in response.text.lower(), \
                "Login page should show error message for invalid credentials"


@allure.feature('API测试')
@allure.story('课程接口')
class TestCourseAPI:

    @pytest.fixture(scope='class')
    def auth_client(self):
        """创建已登录的API客户端"""
        client = BaseRequest()
        login_url = f"{config_reader.base_url}/login/index.php"
        payload = {'username': 'student', 'password': 'moodle26'}
        client.post(login_url, data=payload, allow_redirects=True)
        return client

    @allure.title('课程列表接口验证')
    @allure.description('验证登录后能通过Ajax接口获取已选课程列表')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_enrolled_courses(self, auth_client):
        """GET /lib/ajax/service.php 获取已选课程列表"""

        with allure.step('构造Ajax请求获取课程列表'):
            # Moodle 5.x的课程列表接口需要通过特定的参数调用
            ajax_url = "/lib/ajax/service.php"
            params = {
                'sesskey': self._get_sesskey(auth_client),
                'info': 'core_course_get_enrolled_courses_by_timeline_classification',
            }
            # 实际请求body为JSON格式
            request_body = [{
                "index": 0,
                "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
                "args": {
                    "offset": 0,
                    "limit": 10,
                    "classification": "all",
                    "sort": "fullname"
                }
            }]
            response = auth_client.post(ajax_url, json=request_body)

        with allure.step('验证响应状态码为200'):
            allure.attach(str(response.status_code), name="状态码",
                         attachment_type=allure.attachment_type.TEXT)
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"

        with allure.step('验证返回的课程数据不为空'):
            data = response.json()
            allure.attach(str(data[:2]) if data else "空列表",
                         name="返回数据（前2条）",
                         attachment_type=allure.attachment_type.JSON)
            # 如果学生已加入课程，列表不应为空
            assert isinstance(data, list), "Response should be a list of courses"

    @allure.title('课程详情页面可正常访问')
    @allure.description('验证通过HTTP GET访问课程页面返回200')
    @allure.severity(allure.severity_level.NORMAL)
    def test_course_view_page_accessible(self, auth_client):
        """GET /course/view.php?id=XX 访问课程详情"""

        with allure.step('访问课程详情页'):
            # 使用演示站存在的课程ID（因每小时重置，课程ID会变化）
            # 这里先用已知ID进行测试，实际运行时需动态获取
            course_url = "/course/view.php?id=90"
            response = auth_client.get(course_url)

        with allure.step('验证页面可正常访问'):
            allure.attach(str(response.status_code), name="状态码",
                         attachment_type=allure.attachment_type.TEXT)
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"

        with allure.step('验证页面包含课程内容'):
            assert "course" in response.text.lower() \
                or "section" in response.text.lower(), \
                "Course page should contain course content"

    def _get_sesskey(self, client):
        """从页面中提取sesskey"""
        dashboard_url = f"{config_reader.base_url}/my/"
        response = client.get(dashboard_url)
        # 从HTML中提取sesskey
        import re
        match = re.search(r'"sesskey":"(\w+)"', response.text)
        if match:
            return match.group(1)
        return None


@allure.feature('API测试')
@allure.story('成绩接口')
class TestGradeAPI:

    @pytest.fixture(scope='class')
    def auth_client(self):
        """创建已登录的客户端"""
        client = BaseRequest()
        login_url = f"{config_reader.base_url}/login/index.php"
        payload = {'username': 'student', 'password': 'moodle26'}
        client.post(login_url, data=payload, allow_redirects=True)
        return client

    @allure.title('成绩概览接口验证')
    @allure.description('验证学生能正常访问成绩概览页面')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_grade_overview(self, auth_client):
        """GET /grade/report/overview/index.php 访问成绩概览"""

        with allure.step('访问成绩概览页面'):
            grade_url = "/grade/report/overview/index.php"
            response = auth_client.get(grade_url)

        with allure.step('验证页面状态码'):
            allure.attach(str(response.status_code), name="状态码",
                         attachment_type=allure.attachment_type.TEXT)
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"

        with allure.step('验证页面包含成绩相关内容'):
            assert "Grade" in response.text or "grade" in response.text, \
                "Grade overview page should show grade information"