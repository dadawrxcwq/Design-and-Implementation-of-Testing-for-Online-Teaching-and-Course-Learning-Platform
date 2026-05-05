# pages/user/user_list_page.py
from selenium.webdriver.common.by import By
from common.base_page import BasePage
from common.logger import LoggerManager
import allure


class UserListPage(BasePage):
    """用户列表页面对象"""

    logger = LoggerManager.get_logger()

    # 页面URL
    USER_LIST_URL = '/admin/user.php'

    # 元素定位器
    SEARCH_INPUT = (By.ID, 'filterform_id_sstring')
    SEARCH_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    USER_TABLE = (By.ID, 'participants')
    BULK_ACTION_SELECT = (By.NAME, 'formaction')
    BULK_ACTION_BUTTON = (By.CSS_SELECTOR, 'button[name="submitbutton"]')
    CHECKBOX_PREFIX = 'user'
    
    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('导航到用户列表页面')
    def navigate_to_user_list(self):
        """导航到用户列表页面"""
        self.navigate(self.USER_LIST_URL)
        self.logger.info("已导航到用户列表页面")
        return self

    @allure.step('搜索用户: {username}')
    def search_user(self, username):
        """
        搜索用户
        
        Args:
            username: 用户名
            
        Returns:
            self对象
        """
        self.input_text(self.SEARCH_INPUT, username)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_page_load()
        self.logger.info(f"已搜索用户: {username}")
        return self

    @allure.step('选择用户: {usernames}')
    def select_users(self, usernames):
        """
        选择多个用户
        
        Args:
            usernames: 用户名列表
            
        Returns:
            self对象
        """
        for username in usernames:
            checkbox_locator = (By.CSS_SELECTOR, f"input[value='{username}']")
            if self.is_element_exists(checkbox_locator):
                self.check_checkbox(checkbox_locator)
                self.logger.info(f"已选择用户: {username}")
        
        return self

    @allure.step('执行批量操作: {action}')
    def perform_bulk_action(self, action):
        """
        执行批量操作
        
        Args:
            action: 操作类型，如 'suspend', 'delete' 等
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 选择批量操作类型
            self.select_dropdown_by_value(self.BULK_ACTION_SELECT, action)
            
            # 点击执行按钮
            self.click(self.BULK_ACTION_BUTTON)
            
            # 等待操作完成
            self.wait_for_page_load()
            
            self.logger.info(f"批量操作 '{action}' 执行成功")
            return True
        except Exception as e:
            self.logger.error(f"批量操作失败: {str(e)}")
            return False

    @allure.step('检查用户权限: {username}')
    def check_user_permissions(self, username):
        """
        检查用户权限
        
        Args:
            username: 用户名
            
        Returns:
            list: 权限列表
        """
        # 先搜索用户
        self.search_user(username)
        
        # 这里需要根据实际页面结构调整
        # 假设权限信息显示在表格的某一列
        permissions = []
        try:
            # 查找用户行并获取权限信息
            user_row = self.find_element((By.XPATH, f"//tr[contains(td, '{username}')]"))
            # 根据实际情况解析权限
            permissions = ['Teacher', 'Course Creator']  # 示例数据
        except Exception as e:
            self.logger.warning(f"获取用户权限失败: {str(e)}")
        
        return permissions

    @allure.step('获取用户列表')
    def get_user_list(self):
        """
        获取当前页面的用户列表
        
        Returns:
            list: 用户列表
        """
        try:
            table = self.find_element(self.USER_TABLE)
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # 跳过表头
            
            users = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells:
                    users.append({
                        'username': cells[0].text.strip(),
                        'fullname': cells[1].text.strip(),
                        'email': cells[2].text.strip() if len(cells) > 2 else ''
                    })
            
            self.logger.info(f"获取到 {len(users)} 个用户")
            return users
        except Exception as e:
            self.logger.error(f"获取用户列表失败: {str(e)}")
            return []
