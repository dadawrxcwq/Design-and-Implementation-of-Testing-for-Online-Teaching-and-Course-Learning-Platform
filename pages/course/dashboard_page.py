# pages/course/dashboard_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class DashboardPage(BasePage):
    """
    我的课程/仪表板页面对象
    
    学生登录后默认进入的页面，显示已注册的课程列表
    """
    
    logger = LoggerManager.get_logger()
    
    # ==================== 元素定位器 ====================
    
    # 页面标题
    PAGE_TITLE = (By.CSS_SELECTOR, 'h1, .pagetitle')
    
    # 课程列表容器
    COURSE_LIST_CONTAINER = (By.CSS_SELECTOR, '.dashboard-card-deck, .course-list, [data-region="course-list"]')
    
    # 单个课程卡片（通用定位器）
    COURSE_CARD = (By.CSS_SELECTOR, '.dashboard-card, .coursebox, [data-region="course-card"]')
    
    # 课程名称链接（使用更通用的定位器）
    COURSE_LINK = (By.CSS_SELECTOR, '.coursename a, .course-title a, [data-region="course-card"] a')
    
    # 通过索引定位具体课程（第1-10个课程）
    def get_course_link_by_index(self, index):
        """
        根据索引获取课程链接的定位器
        
        Args:
            index: 课程索引（从1开始）
            
        Returns:
            定位器元组
        """
        return (By.XPATH, f"(//div[contains(@class, 'dashboard-card') or contains(@class, 'coursebox')]//a[contains(@class, 'coursename') or contains(@class, 'course-title')])[{index}]")
    
    # 课程图片
    COURSE_IMAGE = (By.CSS_SELECTOR, '.course-image img, .card-img-top')
    
    # 课程教师信息
    COURSE_TEACHER = (By.CSS_SELECTOR, '.teacher-name, .course-teacher')
    
    # 课程进度（如果有）
    COURSE_PROGRESS = (By.CSS_SELECTOR, '.progress-bar, [data-region="progress-bar"]')
    
    # 搜索框
    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[type="search"], input[name="search"]')
    
    # 筛选下拉框
    FILTER_DROPDOWN = (By.CSS_SELECTOR, 'select[name="filter"], .filter-dropdown')
    
    # 课程数量统计
    COURSE_COUNT = (By.CSS_SELECTOR, '.course-count, [data-region="course-count"]')
    
    # ==================== 核心方法 ====================
    
    def __init__(self, driver):
        super().__init__(driver)
    
    @allure.step('验证是否在仪表板页面')
    def is_on_dashboard(self):
        """检查当前是否在仪表板/我的课程页面"""
        try:
            # 检查是否有课程列表或页面标题
            return self.is_element_exists(self.COURSE_CARD) or \
                   self.is_element_exists(self.PAGE_TITLE)
        except:
            return False
    
    @allure.step('获取课程总数')
    def get_course_count(self):
        """获取页面上显示的课程数量"""
        courses = self.find_elements(self.COURSE_CARD)
        count = len(courses)
        self.logger.info(f"检测到 {count} 个课程")
        return count
    
    @allure.step('获取所有课程名称')
    def get_all_course_names(self):
        """
        获取所有课程的名称列表
        
        Returns:
            list: 课程名称列表
        """
        course_links = self.find_elements(self.COURSE_LINK)
        course_names = [link.text.strip() for link in course_links if link.text.strip()]
        self.logger.info(f"获取到 {len(course_names)} 个课程名称")
        return course_names
    
    @allure.step('点击第 {index} 个课程')
    def click_course_by_index(self, index):
        """
        点击指定索引的课程
        
        Args:
            index: 课程索引（从1开始）
            
        Returns:
            CourseDetailPage对象
        """
        from pages.course.course_detail_page import CourseDetailPage
        
        locator = self.get_course_link_by_index(index)
        
        with allure.step(f'点击第 {index} 个课程'):
            self.click(locator)
            self.wait_for_page_load(timeout=10)
        
        return CourseDetailPage(self.driver)
    
    @allure.step('点击课程: {course_name}')
    def click_course_by_name(self, course_name):
        """
        通过课程名称点击课程
        
        Args:
            course_name: 课程名称
            
        Returns:
            CourseDetailPage对象
        """
        from pages.course.course_detail_page import CourseDetailPage
        
        # 查找包含指定名称的课程链接
        locator = (By.XPATH, f"//a[contains(text(), '{course_name}')]")
        
        with allure.step(f'点击课程: {course_name}'):
            self.click(locator)
            self.wait_for_page_load(timeout=10)
        
        return CourseDetailPage(self.driver)
    
    @allure.step('搜索课程: {keyword}')
    def search_course(self, keyword):
        """
        搜索课程
        
        Args:
            keyword: 搜索关键词
        """
        if self.is_element_exists(self.SEARCH_INPUT):
            self.input_text(self.SEARCH_INPUT, keyword)
            self.press_enter(self.SEARCH_INPUT)
            self.wait_for_page_load(timeout=5)
            self.logger.info(f"搜索课程: {keyword}")
        else:
            self.logger.warning("搜索框不存在")
    
    @allure.step('验证课程列表不为空')
    def verify_course_list_not_empty(self):
        """验证课程列表不为空"""
        count = self.get_course_count()
        assert count > 0, "课程列表为空"
        return True
    
    @allure.step('验证特定课程是否存在: {course_name}')
    def verify_course_exists(self, course_name):
        """
        验证特定课程是否在列表中
        
        Args:
            course_name: 课程名称
            
        Returns:
            bool: 课程是否存在
        """
        course_names = self.get_all_course_names()
        exists = any(course_name.lower() in name.lower() for name in course_names)
        
        if exists:
            self.logger.info(f"课程存在: {course_name}")
        else:
            self.logger.warning(f"课程不存在: {course_name}")
        
        return exists