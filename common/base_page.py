# common/base_page.py
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from common.logger import LoggerManager
import time


class BasePage:
    """页面对象基类 - 封装所有常用UI操作"""

    logger = LoggerManager.get_logger()

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    @property
    def base_url(self):
        """从配置获取基础URL"""
        from utils.config_reader import config_reader
        return config_reader.base_url

    # ==================== 元素查找 ====================

    def find_element(self, locator, timeout=None):
        """
        查找单个元素（显式等待）

        Args:
            locator: 定位器元组，如 (By.ID, 'username')
            timeout: 超时时间（秒），默认使用self.timeout

        Returns:
            WebElement对象
        """
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"元素未找到（超时{timeout}秒）: {locator}")
            raise

    def find_elements(self, locator, timeout=None):
        """
        查找多个元素

        Args:
            locator: 定位器元组
            timeout: 超时时间

        Returns:
            WebElement列表
        """
        if timeout is None:
            timeout = self.timeout

        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            self.logger.error(f"元素列表未找到: {locator}")
            return []

    def find_visible_element(self, locator, timeout=None):
        """查找可见的元素"""
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"可见元素未找到: {locator}")
            raise

    def find_clickable_element(self, locator, timeout=None):
        """查找可点击的元素"""
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"可点击元素未找到: {locator}")
            raise

    # ==================== 基本操作 ====================

    def click(self, locator, timeout=None):
        """
        点击元素

        Args:
            locator: 定位器
            timeout: 超时时间
        """
        element = self.find_clickable_element(locator, timeout)
        try:
            element.click()
            self.logger.info(f"点击元素成功: {locator}")
        except ElementClickInterceptedException:
            # 如果元素被遮挡，使用JavaScript点击
            self.logger.warning(f"元素被遮挡，使用JS点击: {locator}")
            self.js_click(locator)

    def js_click(self, locator):
        """使用JavaScript点击元素"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].click();", element)
        self.logger.info(f"JS点击元素: {locator}")

    def input_text(self, locator, text, clear=True, timeout=None):
        """
        输入文本

        Args:
            locator: 定位器
            text: 要输入的文本
            clear: 是否先清空输入框
            timeout: 超时时间
        """
        element = self.find_element(locator, timeout)
        if clear:
            element.clear()
        element.send_keys(text)
        self.logger.info(f"输入文本: '{text}' 到元素 {locator}")

    def input_and_enter(self, locator, text, timeout=None):
        """输入文本并按回车键"""
        self.input_text(locator, text, timeout=timeout)
        element = self.find_element(locator, timeout)
        element.send_keys(Keys.ENTER)
        self.logger.info(f"输入文本并按回车: '{text}'")

    def get_text(self, locator, timeout=None):
        """
        获取元素文本

        Args:
            locator: 定位器
            timeout: 超时时间

        Returns:
            元素文本内容
        """
        element = self.find_visible_element(locator, timeout)
        return element.text.strip()

    def get_attribute(self, locator, attribute, timeout=None):
        """
        获取元素属性值

        Args:
            locator: 定位器
            attribute: 属性名，如 'value', 'href', 'src'
            timeout: 超时时间

        Returns:
            属性值
        """
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        self.logger.debug(f"获取属性 '{attribute}' = '{value}'")
        return value

    def get_input_value(self, locator, timeout=None):
        """获取输入框的value值"""
        return self.get_attribute(locator, 'value', timeout)

    # ==================== 下拉框操作 ====================

    def select_dropdown_by_text(self, dropdown_locator, option_text, timeout=None):
        """
        通过文本选择下拉框选项

        Args:
            dropdown_locator: 下拉框定位器
            option_text: 选项文本
            timeout: 超时时间
        """
        from selenium.webdriver.support.ui import Select

        element = self.find_element(dropdown_locator, timeout)
        select = Select(element)
        select.select_by_visible_text(option_text)
        self.logger.info(f"选择下拉框选项: '{option_text}'")

    def select_dropdown_by_value(self, dropdown_locator, value, timeout=None):
        """通过value选择下拉框选项"""
        from selenium.webdriver.support.ui import Select

        element = self.find_element(dropdown_locator, timeout)
        select = Select(element)
        select.select_by_value(value)
        self.logger.info(f"选择下拉框选项（value）: '{value}'")

    def select_dropdown_by_index(self, dropdown_locator, index, timeout=None):
        """通过索引选择下拉框选项"""
        from selenium.webdriver.support.ui import Select

        element = self.find_element(dropdown_locator, timeout)
        select = Select(element)
        select.select_by_index(index)
        self.logger.info(f"选择下拉框选项（索引）: {index}")

    def get_dropdown_options(self, dropdown_locator, timeout=None):
        """获取下拉框所有选项文本"""
        from selenium.webdriver.support.ui import Select

        element = self.find_element(dropdown_locator, timeout)
        select = Select(element)
        options = [option.text for option in select.options]
        return options

    # ==================== 复选框和单选框 ====================

    def check_checkbox(self, locator, timeout=None):
        """勾选复选框"""
        element = self.find_element(locator, timeout)
        if not element.is_selected():
            element.click()
            self.logger.info(f"勾选复选框: {locator}")

    def uncheck_checkbox(self, locator, timeout=None):
        """取消勾选复选框"""
        element = self.find_element(locator, timeout)
        if element.is_selected():
            element.click()
            self.logger.info(f"取消勾选复选框: {locator}")

    def is_checkbox_checked(self, locator, timeout=None):
        """检查复选框是否已勾选"""
        element = self.find_element(locator, timeout)
        return element.is_selected()

    def select_radio(self, locator, timeout=None):
        """选择单选框"""
        element = self.find_element(locator, timeout)
        if not element.is_selected():
            element.click()
            self.logger.info(f"选择单选框: {locator}")

    # ==================== 鼠标操作 ====================

    def double_click(self, locator, timeout=None):
        """双击元素"""
        element = self.find_clickable_element(locator, timeout)
        action = ActionChains(self.driver)
        action.double_click(element).perform()
        self.logger.info(f"双击元素: {locator}")

    def right_click(self, locator, timeout=None):
        """右键点击元素"""
        element = self.find_clickable_element(locator, timeout)
        action = ActionChains(self.driver)
        action.context_click(element).perform()
        self.logger.info(f"右键点击元素: {locator}")

    def hover(self, locator, timeout=None):
        """鼠标悬停"""
        element = self.find_visible_element(locator, timeout)
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()
        self.logger.info(f"鼠标悬停: {locator}")

    def drag_and_drop(self, source_locator, target_locator, timeout=None):
        """拖拽元素"""
        source = self.find_element(source_locator, timeout)
        target = self.find_element(target_locator, timeout)
        action = ActionChains(self.driver)
        action.drag_and_drop(source, target).perform()
        self.logger.info(f"拖拽元素: {source_locator} -> {target_locator}")

    def click_and_hold(self, locator, timeout=None):
        """按住鼠标左键"""
        element = self.find_element(locator, timeout)
        action = ActionChains(self.driver)
        action.click_and_hold(element).perform()
        self.logger.info(f"按住鼠标: {locator}")

    def release(self):
        """释放鼠标左键"""
        action = ActionChains(self.driver)
        action.release().perform()
        self.logger.info("释放鼠标")

    # ==================== 键盘操作 ====================

    def press_key(self, locator, key, timeout=None):
        """按下指定键"""
        element = self.find_element(locator, timeout)
        element.send_keys(key)
        self.logger.info(f"按键: {key}")

    def press_enter(self, locator, timeout=None):
        """按回车键"""
        self.press_key(locator, Keys.ENTER, timeout)

    def press_tab(self, locator, timeout=None):
        """按Tab键"""
        self.press_key(locator, Keys.TAB, timeout)

    def press_escape(self, locator, timeout=None):
        """按ESC键"""
        self.press_key(locator, Keys.ESCAPE, timeout)

    def select_all(self, locator, timeout=None):
        """全选（Ctrl+A）"""
        element = self.find_element(locator, timeout)
        element.send_keys(Keys.CONTROL, 'a')
        self.logger.info("全选操作")

    def copy_text(self, locator, timeout=None):
        """复制文本（Ctrl+C）"""
        element = self.find_element(locator, timeout)
        element.send_keys(Keys.CONTROL, 'c')
        self.logger.info("复制文本")

    def paste_text(self, locator, timeout=None):
        """粘贴文本（Ctrl+V）"""
        element = self.find_element(locator, timeout)
        element.send_keys(Keys.CONTROL, 'v')
        self.logger.info("粘贴文本")

    # ==================== 窗口和标签页 ====================

    def switch_to_window(self, window_index):
        """
        切换到指定窗口

        Args:
            window_index: 窗口索引，0表示第一个窗口
        """
        windows = self.driver.window_handles
        if window_index < len(windows):
            self.driver.switch_to.window(windows[window_index])
            self.logger.info(f"切换到窗口: {window_index}")
        else:
            raise IndexError(f"窗口索引 {window_index} 超出范围")

    def switch_to_new_window(self):
        """切换到最新打开的窗口"""
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        self.logger.info("切换到最新窗口")

    def close_current_window(self):
        """关闭当前窗口"""
        self.driver.close()
        self.logger.info("关闭当前窗口")

    def get_window_count(self):
        """获取窗口数量"""
        return len(self.driver.window_handles)

    def switch_to_frame(self, frame_reference):
        """
        切换到iframe

        Args:
            frame_reference: iframe的名称、ID或WebElement
        """
        self.driver.switch_to.frame(frame_reference)
        self.logger.info(f"切换到frame: {frame_reference}")

    def switch_to_default_content(self):
        """切换回主文档"""
        self.driver.switch_to.default_content()
        self.logger.info("切换到主文档")

    def switch_to_parent_frame(self):
        """切换到父frame"""
        self.driver.switch_to.parent_frame()
        self.logger.info("切换到父frame")

    # ==================== 弹窗处理 ====================

    def accept_alert(self, timeout=None):
        """接受警告框（点击确定）"""
        if timeout is None:
            timeout = self.timeout

        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()
        self.logger.info(f"接受警告框，内容: {alert_text}")
        return alert_text

    def dismiss_alert(self, timeout=None):
        """取消警告框（点击取消）"""
        if timeout is None:
            timeout = self.timeout

        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert_text = alert.text
        alert.dismiss()
        self.logger.info(f"取消警告框，内容: {alert_text}")
        return alert_text

    def get_alert_text(self, timeout=None):
        """获取警告框文本"""
        if timeout is None:
            timeout = self.timeout

        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        return alert.text

    def input_alert(self, text, timeout=None):
        """在警告框中输入文本"""
        if timeout is None:
            timeout = self.timeout

        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert.send_keys(text)
        self.logger.info(f"警告框输入: {text}")

    # ==================== 页面导航 ====================

    def navigate(self, url_path=''):
        """
        导航到指定URL

        Args:
            url_path: URL路径，会与base_url拼接
        """
        if url_path.startswith('http'):
            full_url = url_path
        else:
            full_url = f"{self.base_url}{url_path}"

        self.driver.get(full_url)
        self.logger.info(f"导航到: {full_url}")
        return self

    def refresh(self):
        """刷新页面"""
        self.driver.refresh()
        self.logger.info("刷新页面")

    def go_back(self):
        """浏览器后退"""
        self.driver.back()
        self.logger.info("浏览器后退")

    def go_forward(self):
        """浏览器前进"""
        self.driver.forward()
        self.logger.info("浏览器前进")

    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url

    def get_page_title(self):
        """获取页面标题"""
        return self.driver.title

    def wait_for_page_load(self, timeout=None):
        """等待页面加载完成"""
        if timeout is None:
            timeout = self.timeout

        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        self.logger.debug("页面加载完成")

    # ==================== 等待方法 ====================

    def wait_for_element_visible(self, locator, timeout=None):
        """等待元素可见"""
        if timeout is None:
            timeout = self.timeout

        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_element_invisible(self, locator, timeout=None):
        """等待元素不可见"""
        if timeout is None:
            timeout = self.timeout

        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_element_clickable(self, locator, timeout=None):
        """等待元素可点击"""
        if timeout is None:
            timeout = self.timeout

        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_text_present(self, text, timeout=None):
        """等待文本出现在页面中"""
        if timeout is None:
            timeout = self.timeout

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
        self.logger.info(f"文本已出现: '{text}'")

    def wait_for_url_contains(self, url_part, timeout=None):
        """等待URL包含指定字符串"""
        if timeout is None:
            timeout = self.timeout

        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(url_part)
        )
        self.logger.info(f"URL包含: '{url_part}'")

    def wait_for_url_matches(self, pattern, timeout=None):
        """等待URL匹配正则表达式"""
        if timeout is None:
            timeout = self.timeout

        WebDriverWait(self.driver, timeout).until(
            EC.url_matches(pattern)
        )

    def implicit_wait(self, seconds):
        """设置隐式等待"""
        self.driver.implicitly_wait(seconds)

    def sleep(self, seconds):
        """强制等待（不推荐频繁使用）"""
        time.sleep(seconds)
        self.logger.debug(f"强制等待 {seconds} 秒")

    # ==================== 元素状态检查 ====================

    def is_element_visible(self, locator, timeout=None):
        """检查元素是否可见"""
        try:
            element = self.wait_for_element_visible(locator, timeout or 3)
            return element.is_displayed()
        except:
            return False

    def is_element_exists(self, locator):
        """检查元素是否存在（不等待）"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_element_enabled(self, locator, timeout=None):
        """检查元素是否启用"""
        element = self.find_element(locator, timeout)
        return element.is_enabled()

    def is_element_selected(self, locator, timeout=None):
        """检查元素是否被选中（用于checkbox/radio）"""
        element = self.find_element(locator, timeout)
        return element.is_selected()

    def is_text_present(self, text):
        """检查文本是否在页面中"""
        return text in self.driver.page_source

    # ==================== JavaScript执行 ====================

    def execute_js(self, script, *args):
        """执行JavaScript代码"""
        result = self.driver.execute_script(script, *args)
        self.logger.debug(f"执行JS: {script[:50]}...")
        return result

    def scroll_to_element(self, locator):
        """滚动到指定元素"""
        element = self.find_element(locator)
        self.execute_js("arguments[0].scrollIntoView(true);", element)
        self.logger.info(f"滚动到元素: {locator}")

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.execute_js("window.scrollTo(0, document.body.scrollHeight);")
        self.logger.info("滚动到页面底部")

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.execute_js("window.scrollTo(0, 0);")
        self.logger.info("滚动到页面顶部")

    def highlight_element(self, locator):
        """高亮显示元素（调试用）"""
        element = self.find_element(locator)
        self.execute_js("""
            arguments[0].style.border = '3px solid red';
            arguments[0].style.backgroundColor = 'yellow';
        """, element)

    def remove_highlight(self, locator):
        """移除元素高亮"""
        element = self.find_element(locator)
        self.execute_js("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, element)

    # ==================== 文件上传 ====================

    def upload_file(self, file_input_locator, file_path, timeout=None):
        """
        上传文件

        Args:
            file_input_locator: 文件输入框定位器
            file_path: 文件路径
            timeout: 超时时间
        """
        element = self.find_element(file_input_locator, timeout)
        element.send_keys(file_path)
        self.logger.info(f"上传文件: {file_path}")

    # ==================== 截图方法 ====================

    def take_screenshot(self, filename=None):
        """
        截图

        Args:
            filename: 文件名（可选），默认为时间戳

        Returns:
            截图文件路径
        """
        from pathlib import Path
        import datetime

        screenshot_dir = Path('report/screenshots')
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"screenshot_{timestamp}.png"

        filepath = screenshot_dir / filename
        self.driver.save_screenshot(str(filepath))
        self.logger.info(f"截图保存: {filepath}")
        return str(filepath)

    def take_element_screenshot(self, locator, filename=None):
        """截取元素截图"""
        from pathlib import Path
        import datetime

        element = self.find_element(locator)

        screenshot_dir = Path('report/screenshots')
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"element_{timestamp}.png"

        filepath = screenshot_dir / filename
        element.screenshot(str(filepath))
        self.logger.info(f"元素截图保存: {filepath}")
        return str(filepath)

    # ==================== Cookie操作 ====================

    def get_cookies(self):
        """获取所有cookies"""
        return self.driver.get_cookies()

    def get_cookie(self, name):
        """获取指定cookie"""
        return self.driver.get_cookie(name)

    def add_cookie(self, cookie_dict):
        """添加cookie"""
        self.driver.add_cookie(cookie_dict)
        self.logger.info(f"添加cookie: {cookie_dict}")

    def delete_cookie(self, name):
        """删除指定cookie"""
        self.driver.delete_cookie(name)
        self.logger.info(f"删除cookie: {name}")

    def delete_all_cookies(self):
        """删除所有cookies"""
        self.driver.delete_all_cookies()
        self.logger.info("删除所有cookies")

    # ==================== 页面信息获取 ====================

    def get_page_source(self):
        """获取页面源码"""
        return self.driver.page_source

    def get_current_window_handle(self):
        """获取当前窗口句柄"""
        return self.driver.current_window_handle

    def get_all_window_handles(self):
        """获取所有窗口句柄"""
        return self.driver.window_handles

    # ==================== 表格操作 ====================

    def get_table_data(self, table_locator, timeout=None):
        """
        获取表格数据

        Args:
            table_locator: 表格定位器
            timeout: 超时时间

        Returns:
            二维列表，每行是一个列表
        """
        table = self.find_element(table_locator, timeout)
        rows = table.find_elements(By.TAG_NAME, 'tr')

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td') or row.find_elements(By.TAG_NAME, 'th')
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                data.append(row_data)

        self.logger.info(f"获取表格数据，共 {len(data)} 行")
        return data

    def get_table_row_count(self, table_locator, timeout=None):
        """获取表格行数"""
        data = self.get_table_data(table_locator, timeout)
        return len(data)

    def click_table_cell(self, table_locator, row_index, col_index, timeout=None):
        """点击表格单元格"""
        table = self.find_element(table_locator, timeout)
        rows = table.find_elements(By.TAG_NAME, 'tr')

        if row_index < len(rows):
            cells = rows[row_index].find_elements(By.TAG_NAME, 'td')
            if col_index < len(cells):
                cells[col_index].click()
                self.logger.info(f"点击表格单元格 [{row_index}, {col_index}]")
            else:
                raise IndexError(f"列索引 {col_index} 超出范围")
        else:
            raise IndexError(f"行索引 {row_index} 超出范围")

    # ==================== 综合工具方法 ====================

    def clear_input(self, locator, timeout=None):
        """清空输入框"""
        element = self.find_element(locator, timeout)
        element.clear()
        self.logger.info(f"清空输入框: {locator}")

    def get_element_count(self, locator, timeout=None):
        """获取匹配元素的数量"""
        elements = self.find_elements(locator, timeout)
        return len(elements)

    def is_page_loaded(self):
        """检查页面是否加载完成"""
        return self.driver.execute_script('return document.readyState') == 'complete'

    def maximize_window(self):
        """最大化窗口"""
        self.driver.maximize_window()
        self.logger.info("窗口最大化")

    def minimize_window(self):
        """最小化窗口"""
        self.driver.minimize_window()
        self.logger.info("窗口最小化")

    def set_window_size(self, width, height):
        """设置窗口大小"""
        self.driver.set_window_size(width, height)
        self.logger.info(f"设置窗口大小: {width}x{height}")

    def get_viewport_size(self):
        """获取视口大小"""
        size = self.driver.get_window_size()
        return size['width'], size['height']
# 元素查找 (4个方法)
# find_element() - 查找单个元素
# find_elements() - 查找多个元素
# find_visible_element() - 查找可见元素
# find_clickable_element() - 查找可点击元素
# 基本操作 (6个方法)
# click() - 点击（自动处理遮挡）
# js_click() - JS点击
# input_text() - 输入文本
# input_and_enter() - 输入并回车
# get_text() - 获取文本
# get_attribute() / get_input_value() - 获取属性
# 下拉框操作 (4个方法)
# select_dropdown_by_text/value/index() - 三种选择方式
# get_dropdown_options() - 获取所有选项
# 复选框/单选框 (4个方法)
# check_checkbox() / uncheck_checkbox() - 勾选/取消
# is_checkbox_checked() - 检查状态
# select_radio() - 选择单选框
# 鼠标操作 (6个方法)
# double_click() - 双击
# right_click() - 右键
# hover() - 悬停
# drag_and_drop() - 拖拽
# click_and_hold() / release() - 按住/释放
# 键盘操作 (7个方法)
# press_key() - 按指定键
# press_enter/tab/escape() - 常用键
# select_all() - 全选
# copy_text() / paste_text() - 复制粘贴
# 窗口/Frame (9个方法)
# switch_to_window() - 切换窗口
# switch_to_frame() - 切换iframe
# get_window_count() - 获取窗口数
# 等等...
# 弹窗处理 (4个方法)
# accept_alert() - 接受
# dismiss_alert() - 取消
# get_alert_text() - 获取文本
# input_alert() - 输入
# 页面导航 (7个方法)
# navigate() - 导航
# refresh() / go_back() / go_forward()
# get_current_url() / get_page_title()
# 等待方法 (7个方法)
# 等待元素可见/不可见/可点击
# 等待文本出现
# 等待URL变化
# 元素状态检查 (5个方法)
# is_element_visible() - 是否可见
# is_element_exists() - 是否存在
# is_element_enabled() - 是否启用
# is_text_present() - 文本是否存在
# JavaScript执行 (5个方法)
# execute_js() - 执行JS
# scroll_to_element() - 滚动到元素
# highlight_element() - 高亮（调试用）
# 其他实用功能
# 文件上传 (1个)
# 截图 (2个)
# Cookie操作 (5个)
# 表格操作 (4个)
# 窗口控制 (4个)