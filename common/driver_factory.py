# common/driver_factory.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils.config_reader import config_reader
from common.logger import LoggerManager
import time
import subprocess
import platform


class DriverFactory:
    """浏览器驱动工厂"""
    
    @staticmethod
    def _kill_edge_processes():
        """清理残留的Edge进程"""
        try:
            system = platform.system()
            if system == 'Windows':
                # Windows系统
                subprocess.run(['taskkill', '/F', '/IM', 'msedge.exe'], 
                             capture_output=True, timeout=5)
                subprocess.run(['taskkill', '/F', '/IM', 'msedgedriver.exe'], 
                             capture_output=True, timeout=5)
            elif system == 'Darwin':  # macOS
                subprocess.run(['pkill', '-f', 'Microsoft Edge'], 
                             capture_output=True, timeout=5)
                subprocess.run(['pkill', '-f', 'msedgedriver'], 
                             capture_output=True, timeout=5)
            else:  # Linux
                subprocess.run(['pkill', '-f', 'edge'], 
                             capture_output=True, timeout=5)
            
            time.sleep(1)  # 等待进程完全关闭
            LoggerManager.get_logger().debug("已清理Edge相关进程")
        except Exception as e:
            LoggerManager.get_logger().debug(f"清理进程时出错（可忽略）: {str(e)}")

    @staticmethod
    def get_driver():
        browser = config_reader.get('browser', 'chrome').lower()

        if browser == 'chrome':
            options = Options()
            # options.add_argument('--headless')  # 无头模式
            
            LoggerManager.get_logger().info("启动 Chrome 浏览器")
            driver = webdriver.Chrome(options=options)
                
        elif browser == 'edge':
            options = EdgeOptions()
            
            # 尝试清理残留进程
            DriverFactory._kill_edge_processes()
            
            # 直接使用系统 PATH 中的 EdgeDriver（已手动下载）
            LoggerManager.get_logger().info("启动 Edge 浏览器（使用本地驱动）")
            
            try:
                driver = webdriver.Edge(options=options)
            except Exception as e:
                LoggerManager.get_logger().warning(f"首次启动Edge失败，尝试清理后重启: {str(e)}")
                # 再次清理进程
                DriverFactory._kill_edge_processes()
                time.sleep(2)
                # 重试
                driver = webdriver.Edge(options=options)
                
        elif browser == 'firefox':
            options = FirefoxOptions()
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"不支持的浏览器: {browser}")

        driver.maximize_window()
        driver.implicitly_wait(10)
        return driver

    @staticmethod
    def quit_driver(driver):
        """安全关闭浏览器"""
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
