# pages/auth/login_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class LoginPage(BasePage):
    """
    登录页面对象

    负责Moodle平台的登录、登出及相关操作
    URL: /login/index.php
    """

    logger = LoggerManager.get_logger()

    # ==================== 页面URL ====================
    LOGIN_URL = '/login/index.php'

    # ==================== 元素定位器 ====================

    # 首页登录链接（未登录状态）
    LOGIN_LINK = (By.XPATH, "//nav//div[contains(@class, 'usermenu')]//a[contains(text(), 'Log in')]")
    
    # 登录表单元素
    USERNAME_INPUT = (By.XPATH, "//form//input[@type='text' and @name='username']")
    PASSWORD_INPUT = (By.XPATH, "//form//input[@type='password' and @name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")  # 简化定位器
    REMEMBER_USERNAME_CHECKBOX = (By.ID, 'rememberusername')

    # 错误和提示信息
    ERROR_MESSAGE = (By.CLASS_NAME, 'alert-danger')
    SUCCESS_MESSAGE = (By.CLASS_NAME, 'alert-success')
    LOGIN_FAILED_ALERT = (By.CSS_SELECTOR, '.alert.alert-error')

    # 登录成功后的用户菜单和头像
    USER_MENU = (By.CSS_SELECTOR, '.usermenu')
    USER_MENU_TOGGLE = (By.CSS_SELECTOR, '.usermenu .dropdown-toggle')
    USER_AVATAR = (By.XPATH, "//nav//div[contains(@class, 'usermenu')]//img[contains(@class, 'userpicture')]")
    LOGOUT_LINK = (By.XPATH, "//a[contains(text(), 'Log out')]")
    PROFILE_LINK = (By.XPATH, "//a[contains(text(), 'Profile')]")
    DASHBOARD_LINK = (By.XPATH, "//a[contains(text(), 'Dashboard')]")

    # 其他登录选项
    GUEST_LOGIN_BUTTON = (By.XPATH, "//input[@value='Login as a guest']")

    # Cookie同意按钮（首次访问可能出现）
    COOKIE_CONSENT_BUTTON = (By.ID, 'cookie-consent-accept')

    # ==================== 核心方法 ====================

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('导航到登录页面')
    def navigate(self):
        """导航到登录页面"""
        super().navigate(self.LOGIN_URL)
        self.logger.info("已导航到登录页面")
        return self
    
    @allure.step('点击首页登录链接')
    def click_login_link_from_homepage(self):
        """从首页点击登录链接跳转到登录页面"""
        try:
            # 先导航到首页
            from common.base_page import BasePage
            base_page = BasePage(self.driver)
            base_page.navigate('/')
            self.wait_for_page_load(timeout=8)
            
            # 尝试多种方式找到登录链接
            login_locators = [
                (By.XPATH, "//nav//div[contains(@class, 'usermenu')]//a[contains(text(), 'Log in')]"),
                (By.XPATH, "//a[contains(text(), 'Log in')]"),
                (By.CSS_SELECTOR, "a[href*='login']"),
            ]
            
            clicked = False
            for locator in login_locators:
                if self.is_element_exists(locator):
                    self.click(locator)
                    self.wait_for_page_load(timeout=5)
                    self.logger.info("已从首页点击登录链接")
                    clicked = True
                    break
            
            if not clicked:
                # 如果找不到登录链接，直接跳转到登录页面
                self.logger.warning("未找到登录链接，直接跳转到登录页面")
                super().navigate(self.LOGIN_URL)
                
        except Exception as e:
            self.logger.error(f"点击登录链接失败: {str(e)}")
            # 降级方案：直接导航到登录页面
            super().navigate(self.LOGIN_URL)
        
        return self

    @allure.step('执行登录操作 - 用户名: {username}')
    def login(self, username, password, remember_username=False, save_session=True, role=None):
        """
        执行完整的登录流程

        Args:
            username: 用户名
            password: 密码
            remember_username: 是否记住用户名
            save_session: 是否保存会话（默认保存）
            role: 角色名称（用于保存会话，如果不指定则使用username）

        Returns:
            self对象，支持链式调用
        """
        self.logger.info(f"开始登录流程，用户: {username}")

        # 处理可能出现的Cookie同意弹窗
        if self.is_element_exists(self.COOKIE_CONSENT_BUTTON):
            self.click(self.COOKIE_CONSENT_BUTTON)
            self.logger.info("已关闭Cookie同意弹窗")

        # 输入用户名
        self.input_text(self.USERNAME_INPUT, username)

        # 输入密码
        self.input_text(self.PASSWORD_INPUT, password)

        # 选择是否记住用户名
        if remember_username:
            self.check_checkbox(self.REMEMBER_USERNAME_CHECKBOX)

        # 点击登录按钮
        self.click(self.LOGIN_BUTTON)

        # 等待页面加载完成（增加超时时间，Moodle响应可能较慢）
        self.wait_for_page_load(timeout=15)

        self.logger.info(f"登录操作完成，用户: {username}")
        
        # 如果登录成功且需要保存会话
        if save_session and self.is_login_success():
            self.save_current_session(role or username)
        
        return self

    @allure.step('快速登录（不等待）')
    def quick_login(self, username, password):
        """
        快速登录，不进行额外检查

        Args:
            username: 用户名
            password: 密码
        """
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    # ==================== 验证方法 ====================

    @allure.step('验证登录是否成功')
    def is_login_success(self):
        """
        检查是否登录成功
        
        Returns:
            bool: True表示登录成功，False表示失败
        """
        try:
            # 等待页面完全加载
            self.wait_for_page_load(timeout=8)
            
            # 方法1：检查用户头像是否可见（登录成功的标志）
            avatar_visible = self.is_element_visible(self.USER_AVATAR, timeout=5)
            
            # 方法2：检查用户菜单是否可见
            user_menu_visible = self.is_element_visible(self.USER_MENU, timeout=5)
            
            # 方法3：检查是否有错误消息（登录失败的标志）
            has_error = self.is_element_visible(self.ERROR_MESSAGE, timeout=2)
            
            if avatar_visible or user_menu_visible:
                return True
            elif has_error:
                return False
            else:
                # 截图调试
                self.take_screenshot("login_status_debug")
                return False
        except Exception as e:
            self.logger.error(f"检查登录状态时出错: {str(e)}")
            return False

    @allure.step('验证登录是否失败')
    def is_login_failed(self):
        """
        检查是否登录失败

        Returns:
            bool: True表示登录失败
        """
        return self.is_element_exists(self.ERROR_MESSAGE) or \
            self.is_element_exists(self.LOGIN_FAILED_ALERT)

    @allure.step('获取错误消息')
    def get_error_message(self):
        """
        获取登录失败的错误消息

        Returns:
            str: 错误消息文本，如果没有错误则返回None
        """
        try:
            if self.is_element_visible(self.ERROR_MESSAGE, timeout=3):
                error_msg = self.get_text(self.ERROR_MESSAGE)
                self.logger.info(f"获取到错误消息: {error_msg}")
                return error_msg
            elif self.is_element_visible(self.LOGIN_FAILED_ALERT, timeout=3):
                error_msg = self.get_text(self.LOGIN_FAILED_ALERT)
                self.logger.info(f"获取到错误消息: {error_msg}")
                return error_msg
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取错误消息时出错: {str(e)}")
            return None

    @allure.step('获取成功消息')
    def get_success_message(self):
        """获取成功消息"""
        try:
            if self.is_element_visible(self.SUCCESS_MESSAGE, timeout=3):
                return self.get_text(self.SUCCESS_MESSAGE)
            return None
        except:
            return None

    @allure.step('验证当前用户是否为: {expected_username}')
    def verify_current_user(self, expected_username):
        """
        验证当前登录的用户名是否正确

        Args:
            expected_username: 期望的用户名

        Returns:
            bool: 验证结果
        """
        try:
            # 点击用户菜单
            self.click(self.USER_MENU_TOGGLE)

            # 尝试获取用户头像的 alt 属性或 title 属性（通常包含用户名）
            try:
                avatar_element = self.find_element(self.USER_AVATAR)
                username_in_alt = avatar_element.get_attribute('alt')
                username_in_title = avatar_element.get_attribute('title')
                
                # 优先使用 alt 属性
                displayed_name = username_in_alt or username_in_title or ''
            except:
                # 如果无法从头像获取，则使用菜单文本的第一行
                menu_text = self.get_text(self.USER_MENU)
                displayed_name = menu_text.split('\n')[0] if menu_text else ''

            # 关闭菜单（再次点击）
            self.click(self.USER_MENU_TOGGLE)

            # 验证用户名
            is_match = expected_username.lower() in displayed_name.lower()

            if is_match:
                self.logger.info(f"用户验证成功: {displayed_name}")
            else:
                self.logger.warning(f"用户验证失败: 期望={expected_username}, 实际={displayed_name}")

            return is_match
        except Exception as e:
            self.logger.error(f"验证用户时出错: {str(e)}")
            return False

    # ==================== 登出方法 ====================

    @allure.step('执行登出操作')
    def logout(self):
        """
        执行登出操作

        Returns:
            LoginPage对象，方便继续操作
        """
        if not self.is_login_success():
            self.logger.warning("用户未登录，无需登出")
            return self

        try:
            # 点击用户菜单
            self.click(self.USER_MENU_TOGGLE)

            # 等待登出链接出现
            self.wait_for_element_visible(self.LOGOUT_LINK, timeout=5)

            # 点击登出
            self.click(self.LOGOUT_LINK)

            # 等待页面加载
            self.wait_for_page_load()

            self.logger.info("登出成功")
            return self
        except Exception as e:
            self.logger.error(f"登出失败: {str(e)}")
            raise

    # ==================== 访客登录 ====================

    @allure.step('以访客身份登录')
    def login_as_guest(self):
        """以访客身份登录"""
        if self.is_element_exists(self.GUEST_LOGIN_BUTTON):
            self.click(self.GUEST_LOGIN_BUTTON)
            self.wait_for_page_load()
            self.logger.info("已以访客身份登录")
            return True
        else:
            self.logger.warning("访客登录按钮不存在")
            return False

    # ==================== 辅助方法 ====================

    @allure.step('清除登录表单')
    def clear_form(self):
        """清除登录表单中的所有输入"""
        self.clear_input(self.USERNAME_INPUT)
        self.clear_input(self.PASSWORD_INPUT)
        self.logger.info("已清除登录表单")
        return self

    @allure.step('检查是否在登录页面')
    def is_on_login_page(self):
        """检查当前是否在登录页面"""
        try:
            return self.is_element_exists(self.USERNAME_INPUT) and \
                self.is_element_exists(self.PASSWORD_INPUT) and \
                self.is_element_exists(self.LOGIN_BUTTON)
        except:
            return False

    @allure.step('获取页面标题')
    def get_page_title_text(self):
        """获取登录页面的标题"""
        title_locator = (By.CSS_SELECTOR, 'h1, h2, .logintitle')
        try:
            return self.get_text(title_locator)
        except:
            return self.get_page_title()

    @allure.step('检查是否记住用户名复选框')
    def is_remember_username_checked(self):
        """检查记住用户名复选框是否已勾选"""
        return self.is_checkbox_checked(self.REMEMBER_USERNAME_CHECKBOX)

    # ==================== 高级验证方法 ====================

    @allure.step('验证登录页面的完整性')
    def verify_login_page_elements(self):
        """
        验证登录页面的所有关键元素是否存在

        Returns:
            dict: 元素存在性检查结果
        """
        elements_check = {
            'username_input': self.is_element_exists(self.USERNAME_INPUT),
            'password_input': self.is_element_exists(self.PASSWORD_INPUT),
            'login_button': self.is_element_exists(self.LOGIN_BUTTON),
        }

        all_exist = all(elements_check.values())

        if all_exist:
            self.logger.info("登录页面元素验证通过")
        else:
            missing = [k for k, v in elements_check.items() if not v]
            self.logger.warning(f"登录页面缺少元素: {missing}")

        return elements_check

    @allure.step('截图保存登录页面')
    def capture_login_page(self, filename='login_page.png'):
        """截取登录页面"""
        return self.take_screenshot(filename)

    @allure.step('保存当前会话')
    def save_current_session(self, role=None):
        """
        保存当前登录状态的cookies
        
        Args:
            role: 角色名称（如 'student', 'teacher'），如果不指定则从配置推断
        """
        from utils.session_manager import session_manager
        
        try:
            # 获取所有cookies
            cookies = self.driver.get_cookies()
            
            # 如果没有指定role，尝试从username推断
            if not role:
                # 这里可以根据实际情况调整映射关系
                current_url = self.get_current_url()
                if 'manager' in current_url:
                    role = 'dean'
                else:
                    # 默认使用第一个角色
                    role = 'unknown'
            
            # 保存会话
            session_manager.save_session(role, cookies)
            self.logger.info(f"已保存 {role} 角色的会话")
            
        except Exception as e:
            self.logger.error(f"保存会话失败: {str(e)}")
    
    @allure.step('使用保存的会话登录 - 角色: {role}')
    def login_with_saved_session(self, role):
        """
        使用保存的会话快速登录（无需输入用户名密码）
        
        Args:
            role: 角色名称
            
        Returns:
            bool: 是否成功加载会话
        """
        from utils.session_manager import session_manager
        
        self.logger.info(f"尝试使用保存的 {role} 会话登录")
        
        # 先导航到网站
        self.navigate('/')
        self.wait_for_page_load(timeout=5)
        
        # 添加cookies
        success = session_manager.add_cookies_to_driver(self.driver, role)
        
        if success:
            self.wait_for_page_load(timeout=5)
            
            # 验证是否登录成功
            if self.is_login_success():
                self.logger.info(f"使用保存的 {role} 会话登录成功")
                return True
            else:
                self.logger.warning(f"{role} 会话已失效，需要重新登录")
                return False
        else:
            self.logger.warning(f"无法加载 {role} 的会话")
            return False

    # ==================== 针对不同角色的登录方法 ====================

    @allure.step('Dean角色登录')
    def login_as_dean(self, password='moodle26', save_session=True):
        """Dean（教育院长）登录"""
        return self.login('manager', password, save_session=save_session, role='dean')

    @allure.step('Teacher角色登录')
    def login_as_teacher(self, password='moodle26', save_session=True):
        """Teacher（讲师）登录"""
        return self.login('teacher', password, save_session=save_session, role='teacher')

    @allure.step('Student角色登录')
    def login_as_student(self, password='moodle26', save_session=True):
        """Student（学生）登录"""
        return self.login('student', password, save_session=save_session, role='student')

    @allure.step('Mentor角色登录')
    def login_as_mentor(self, password='moodle26', save_session=True):
        """Mentor（学习支持导师）登录"""
        return self.login('parent', password, save_session=save_session, role='mentor')

    @allure.step('Privacy Officer角色登录')
    def login_as_privacy_officer(self, password='moodle26', save_session=True):
        """Privacy Officer（隐私官员）登录"""
        return self.login('privacyofficer', password, save_session=save_session, role='privacy_officer')
