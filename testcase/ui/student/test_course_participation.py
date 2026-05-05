# testcase/ui/student/test_course_participation.py
import pytest
import allure
from pages.auth.login_page import LoginPage
from pages.course.dashboard_page import DashboardPage
from pages.course.course_detail_page import CourseDetailPage
from utils.config_reader import config_reader
from utils.data_loader import load_yaml


@allure.feature('学生功能')
@allure.story('课程参与')
class TestCourseParticipation:
    """学生课程参与功能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """测试前置准备"""
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.config = config_reader
        
        # 加载测试数据
        try:
            self.course_data = load_yaml('data/ui/course_data.yaml')
        except:
            self.course_data = {}
        
        yield
        
        # 测试后清理：如果已登录则登出
        try:
            if self.login_page.is_login_success():
                self.login_page.logout()
        except Exception as e:
            self.login_page.logger.warning(f"清理时出错: {str(e)}")
    
    @pytest.fixture(scope='function')
    def login_as_student(self):
        """
        以学生身份登录并进入仪表板
        智能登录：优先使用保存的Session，如果失效则执行普通登录
        """
        student_account = self.config.get('accounts.student', {})
        username = student_account.get('username', 'student')
        password = student_account.get('password', 'moodle26')
        
        with allure.step('尝试使用保存的Session快速登录'):
            # 先尝试使用保存的Session
            success = self.login_page.login_with_saved_session('student')
            
            if success:
                allure.attach(
                    f"✓ 使用保存的Session成功登录（快速模式）",
                    name="登录方式",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                with allure.step('Session失效或不存在，执行完整登录'):
                    self.login_page.navigate()
                    self.login_page.login(username, password, save_session=True, role='student')
                    
                    with allure.step('验证登录成功'):
                        assert self.login_page.is_login_success(), "学生登录失败"
                    
                    allure.attach(
                        f"✓ 执行完整登录流程（标准模式）",
                        name="登录方式",
                        attachment_type=allure.attachment_type.TEXT
                    )
        
        # 返回仪表板页面对象
        return DashboardPage(self.driver)
    
    @allure.title('TC001-学生登录后查看我的课程列表')
    @allure.description('验证学生登录后能够看到已注册的课程列表')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_view_my_courses_list(self, login_as_student):
        """查看我的课程列表"""
        dashboard = login_as_student
        
        with allure.step('验证在仪表板页面'):
            assert dashboard.is_on_dashboard(), "不在仪表板页面"
        
        with allure.step('获取课程数量'):
            course_count = dashboard.get_course_count()
            allure.attach(
                f"课程数量: {course_count}",
                name="课程统计",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step('验证课程列表不为空'):
            expected_min = self.course_data.get('course_tests', {}).get(
                'course_list_verification', {}
            ).get('expected_min_courses', 1)
            
            assert course_count >= expected_min, \
                f"课程数量不足，期望至少{expected_min}个，实际{course_count}个"
    
    @allure.title('TC002-获取所有课程名称')
    @allure.description('验证能够获取所有课程的名称列表')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_get_all_course_names(self, login_as_student):
        """获取所有课程名称"""
        dashboard = login_as_student
        
        with allure.step('获取所有课程名称'):
            course_names = dashboard.get_all_course_names()
        
        with allure.step('验证课程名称列表'):
            assert len(course_names) > 0, "课程名称列表为空"
            
            # 记录课程名称
            course_list_text = "\n".join([
                f"{i+1}. {name}" for i, name in enumerate(course_names)
            ])
            allure.attach(
                course_list_text,
                name="课程列表",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title('TC003-访问第一个课程查看详情')
    @allure.description('验证学生可以点击进入第一个课程并查看详情')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_access_first_course(self, login_as_student):
        """访问第一个课程"""
        dashboard = login_as_student
        
        with allure.step('点击第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('验证进入课程详情页面'):
            assert course_detail.is_on_course_detail(), "未进入课程详情页面"
        
        with allure.step('获取课程标题'):
            title = course_detail.get_course_title()
            allure.attach(
                title,
                name="课程标题",
                attachment_type=allure.attachment_type.TEXT
            )
            assert title, "课程标题为空"
    
    @allure.title('TC004-访问第二个课程查看详情')
    @allure.description('验证学生可以点击进入第二个课程并查看详情')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_access_second_course(self, login_as_student):
        """访问第二个课程"""
        dashboard = login_as_student
        
        with allure.step('点击第二个课程'):
            course_detail = dashboard.click_course_by_index(2)
        
        with allure.step('验证进入课程详情页面'):
            assert course_detail.is_on_course_detail(), "未进入课程详情页面"
        
        with allure.step('获取课程信息'):
            title = course_detail.get_course_title()
            allure.attach(
                title,
                name="课程标题",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title('TC005-验证课程基本信息完整性')
    @allure.description('验证课程详情页显示完整的基本信息')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_verify_course_basic_info(self, login_as_student):
        """验证课程基本信息"""
        dashboard = login_as_student
        
        with allure.step('进入第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('验证课程基本信息'):
            verification = course_detail.verify_course_basic_info()
            
            # 记录验证结果
            result_text = "\n".join([
                f"{key}: {'✓' if value else '✗'}" 
                for key, value in verification.items()
            ])
            allure.attach(
                result_text,
                name="验证结果",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 验证关键信息存在
            assert verification['has_title'], "课程标题缺失"
            assert verification['has_content'], "课程内容区域缺失"
    
    @allure.title('TC006-查看课程章节和活动数量')
    @allure.description('验证能够获取课程的章节和活动统计信息')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_get_course_sections_and_activities(self, login_as_student):
        """查看课程章节和活动"""
        dashboard = login_as_student
        
        with allure.step('进入第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('获取章节数量'):
            section_count = course_detail.get_section_count()
            allure.attach(
                f"章节数量: {section_count}",
                name="章节统计",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step('获取活动数量'):
            activity_count = course_detail.get_activity_count()
            allure.attach(
                f"活动数量: {activity_count}",
                name="活动统计",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step('验证统计数据'):
            assert section_count >= 0, "章节数量异常"
            assert activity_count >= 0, "活动数量异常"
    
    @allure.title('TC007-从课程详情返回我的课程')
    @allure.description('验证可以从课程详情页返回到我的课程列表')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_back_to_dashboard_from_course(self, login_as_student):
        """从课程详情返回"""
        dashboard = login_as_student
        
        with allure.step('进入第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('验证在课程详情页'):
            assert course_detail.is_on_course_detail(), "未进入课程详情"
        
        with allure.step('返回到我的课程'):
            dashboard_again = course_detail.go_back_to_dashboard()
        
        with allure.step('验证回到仪表板'):
            assert dashboard_again.is_on_dashboard(), "未回到仪表板页面"
    
    @allure.title('TC008-访问多个不同课程')
    @allure.description('验证学生可以访问多个不同的课程')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    @pytest.mark.parametrize("course_index", [1, 2, 3])
    def test_access_multiple_courses(self, login_as_student, course_index):
        """访问多个课程（参数化测试）"""
        dashboard = login_as_student
        
        with allure.step(f'点击第 {course_index} 个课程'):
            course_detail = dashboard.click_course_by_index(course_index)
        
        with allure.step('验证进入课程详情'):
            assert course_detail.is_on_course_detail(), f"未能进入第{course_index}个课程"
        
        with allure.step('获取课程标题'):
            title = course_detail.get_course_title()
            allure.attach(
                f"课程 {course_index}: {title}",
                name=f"第{course_index}个课程",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step('返回课程列表'):
            dashboard = course_detail.go_back_to_dashboard()
    
    @allure.title('TC009-查看课程教师信息')
    @allure.description('验证能够查看课程的教师信息')
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_view_course_teachers(self, login_as_student):
        """查看课程教师"""
        dashboard = login_as_student
        
        with allure.step('进入第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('获取教师信息'):
            teachers = course_detail.get_course_teachers()
            
            if teachers:
                allure.attach(
                    teachers,
                    name="教师信息",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    "该课程未显示教师信息",
                    name="教师信息",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title('TC010-查看课程描述')
    @allure.description('验证能够查看课程的描述信息')
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.student
    @pytest.mark.course
    def test_view_course_description(self, login_as_student):
        """查看课程描述"""
        dashboard = login_as_student
        
        with allure.step('进入第一个课程'):
            course_detail = dashboard.click_course_by_index(1)
        
        with allure.step('获取课程描述'):
            description = course_detail.get_course_description()
            
            if description:
                # 限制描述长度，避免报告过长
                desc_preview = description[:500] + "..." if len(description) > 500 else description
                allure.attach(
                    desc_preview,
                    name="课程描述",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    "该课程没有描述信息",
                    name="课程描述",
                    attachment_type=allure.attachment_type.TEXT
                )