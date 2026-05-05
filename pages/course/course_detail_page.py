# pages/course/course_detail_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class CourseDetailPage(BasePage):
    """
    课程详情/课程内容页面对象
    
    显示单个课程的详细内容、资源、活动等
    """
    
    logger = LoggerManager.get_logger()
    
    # ==================== 元素定位器 ====================
    
    # 课程标题
    COURSE_TITLE = (By.CSS_SELECTOR, 'h1, .pagetitle, .course-header h2')
    
    # 课程描述/简介
    COURSE_DESCRIPTION = (By.CSS_SELECTOR, '.course-description, .summary, [data-region="course-summary"]')
    
    # 课程教师信息
    COURSE_TEACHERS = (By.CSS_SELECTOR, '.teacher-name, .course-contacts, [data-region="teachers"]')
    
    # 课程内容区域
    COURSE_CONTENT = (By.CSS_SELECTOR, '.course-content, #region-main, [data-region="course-content"]')
    
    # 课程章节/主题
    COURSE_SECTIONS = (By.CSS_SELECTOR, '.section, .topic, [data-region="section"]')
    
    # 课程活动/资源列表
    ACTIVITY_LIST = (By.CSS_SELECTOR, '.activity, .mod-indent-outer, [data-region="activity"]')
    
    # 特定活动类型
    ASSIGNMENT_LINK = (By.CSS_SELECTOR, '.modtype_assign a, [data-mod-type="assign"]')
    QUIZ_LINK = (By.CSS_SELECTOR, '.modtype_quiz a, [data-mod-type="quiz"]')
    RESOURCE_LINK = (By.CSS_SELECTOR, '.modtype_resource a, [data-mod-type="resource"]')
    FORUM_LINK = (By.CSS_SELECTOR, '.modtype_forum a, [data-mod-type="forum"]')
    
    # 导航面包屑
    BREADCRUMB = (By.CSS_SELECTOR, '.breadcrumb, .breadcrumbs, [data-region="breadcrumb"]')
    
    # 返回按钮
    BACK_BUTTON = (By.CSS_SELECTOR, '.back-button, a[href*="mycourses"], a[href*="dashboard"]')
    
    # 课程进度（如果有）
    PROGRESS_BAR = (By.CSS_SELECTOR, '.progress-bar, [data-region="completion-progress"]')
    
    # 参与人数/学生数
    PARTICIPANT_COUNT = (By.CSS_SELECTOR, '.participant-count, [data-region="participants"]')
    
    # ==================== 核心方法 ====================
    
    def __init__(self, driver):
        super().__init__(driver)
    
    @allure.step('验证是否在课程详情页面')
    def is_on_course_detail(self):
        """检查当前是否在课程详情页面"""
        try:
            return self.is_element_exists(self.COURSE_TITLE) and \
                   self.is_element_exists(self.COURSE_CONTENT)
        except:
            return False
    
    @allure.step('获取课程标题')
    def get_course_title(self):
        """获取课程标题"""
        title = self.get_text(self.COURSE_TITLE)
        self.logger.info(f"课程标题: {title}")
        return title
    
    @allure.step('获取课程描述')
    def get_course_description(self):
        """获取课程描述文本"""
        if self.is_element_exists(self.COURSE_DESCRIPTION):
            description = self.get_text(self.COURSE_DESCRIPTION)
            self.logger.info(f"课程描述长度: {len(description)} 字符")
            return description
        return None
    
    @allure.step('获取课程教师信息')
    def get_course_teachers(self):
        """获取课程教师列表"""
        if self.is_element_exists(self.COURSE_TEACHERS):
            teachers = self.get_text(self.COURSE_TEACHERS)
            self.logger.info(f"课程教师: {teachers}")
            return teachers
        return None
    
    @allure.step('获取课程章节数量')
    def get_section_count(self):
        """获取课程章节/主题数量"""
        sections = self.find_elements(self.COURSE_SECTIONS)
        count = len(sections)
        self.logger.info(f"课程章节数: {count}")
        return count
    
    @allure.step('获取课程活动数量')
    def get_activity_count(self):
        """获取课程活动/资源数量"""
        activities = self.find_elements(self.ACTIVITY_LIST)
        count = len(activities)
        self.logger.info(f"课程活动数: {count}")
        return count
    
    @allure.step('获取所有活动名称')
    def get_all_activity_names(self):
        """
        获取所有活动的名称列表
        
        Returns:
            list: 活动名称列表
        """
        activities = self.find_elements(self.ACTIVITY_LIST)
        activity_names = [act.text.strip() for act in activities if act.text.strip()]
        self.logger.info(f"获取到 {len(activity_names)} 个活动")
        return activity_names
    
    @allure.step('点击活动: {activity_name}')
    def click_activity_by_name(self, activity_name):
        """
        通过活动名称点击活动
        
        Args:
            activity_name: 活动名称
        """
        locator = (By.XPATH, f"//a[contains(text(), '{activity_name}')]")
        self.click(locator)
        self.wait_for_page_load(timeout=10)
        self.logger.info(f"点击活动: {activity_name}")
    
    @allure.step('返回到我的课程')
    def go_back_to_dashboard(self):
        """返回到仪表板/我的课程页面"""
        from pages.course.dashboard_page import DashboardPage
        
        if self.is_element_exists(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
        else:
            # 如果没有返回按钮，使用浏览器后退
            self.go_back()
        
        self.wait_for_page_load(timeout=10)
        return DashboardPage(self.driver)
    
    @allure.step('验证课程基本信息完整性')
    def verify_course_basic_info(self):
        """
        验证课程基本信息是否完整
        
        Returns:
            dict: 验证结果
        """
        result = {
            'has_title': self.is_element_exists(self.COURSE_TITLE),
            'has_content': self.is_element_exists(self.COURSE_CONTENT),
            'has_sections': self.get_section_count() > 0,
            'has_activities': self.get_activity_count() > 0,
        }
        
        all_valid = all(result.values())
        
        if all_valid:
            self.logger.info("课程基本信息验证通过")
        else:
            missing = [k for k, v in result.items() if not v]
            self.logger.warning(f"课程缺少信息: {missing}")
        
        return result