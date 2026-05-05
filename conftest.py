import pytest
from common.driver_factory import DriverFactory
from common.logger import LoggerManager
from common.base_request import BaseRequest
from utils.config_reader import config_reader
from pathlib import Path
import yaml
import logging

# 抑制 Selenium 和 urllib3 的 DEBUG 日志
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


# ========== 全局Fixtures ==========

@pytest.fixture(scope='session')
def logger():
    """日志记录器"""
    return LoggerManager.get_logger()


@pytest.fixture(scope='session')
def config_reader():
    """配置读取器"""
    return config_reader


@pytest.fixture(scope='function')
def driver():
    """UI测试浏览器驱动"""
    drv = DriverFactory.get_driver()
    yield drv
    DriverFactory.quit_driver(drv)


@pytest.fixture(scope='session')
def api_client():
    """API客户端"""
    client = BaseRequest()
    yield client
    client.close()


@pytest.fixture(scope='session')
def base_url(config_reader):
    """基础URL"""
    return config_reader.base_url


# ========== 数据加载Fixtures ==========

@pytest.fixture
def load_ui_test_data():
    """加载UI测试数据"""

    def _load(filename, key=None):
        data_path = Path('data/ui') / filename
        with open(data_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data[key] if key else data

    return _load


@pytest.fixture
def load_api_test_data():
    """加载API测试数据"""

    def _load(filename, key=None):
        data_path = Path('data/api') / filename
        with open(data_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data[key] if key else data

    return _load


@pytest.fixture
def load_course_data(load_api_test_data):
    """加载课程测试数据"""
    return lambda key: load_api_test_data('course_cases.yaml', key)


# ========== Hooks ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """捕获测试结果，用于失败截图"""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == 'call' and rep.failed:
        # 测试失败时截图
        if 'driver' in item.funcargs:
            driver = item.funcargs['driver']
            screenshot_dir = Path('report/screenshots/ui')
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"{item.name}.png"
            
            try:
                driver.save_screenshot(str(screenshot_path))
                
                # 确认文件存在后再附加到Allure报告
                if screenshot_path.exists():
                    import allure
                    allure.attach.file(
                        str(screenshot_path),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
            except Exception as e:
                print(f"警告: 截图保存或附加失败: {e}")
