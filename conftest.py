import logging
from pathlib import Path

import pytest
import yaml

from common.base_request import BaseRequest
from common.driver_factory import DriverFactory
from common.logger import LoggerManager
from utils.config_reader import config_reader as global_config_reader


logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def logger():
    """Shared test logger."""
    return LoggerManager.get_logger()


@pytest.fixture(scope="session")
def config_reader():
    """Shared config reader."""
    return global_config_reader


@pytest.fixture(scope="function")
def driver():
    """Create a fresh browser for each UI test.

    Moodle demo pages occasionally close or invalidate the active Edge window
    after long modal interactions. Function scope is slower, but it prevents a
    broken WebDriver session from cascading into later tests.
    """
    drv = DriverFactory.get_driver()
    yield drv
    DriverFactory.quit_driver(drv)


@pytest.fixture(scope="session")
def api_client():
    """Shared API client."""
    client = BaseRequest()
    yield client
    client.close()


@pytest.fixture(scope="session")
def base_url(config_reader):
    """Base URL."""
    return config_reader.base_url


@pytest.fixture
def load_ui_test_data():
    """Load UI test data from data/ui."""

    def _load(filename, key=None):
        data_path = Path("data/ui") / filename
        with open(data_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data[key] if key else data

    return _load


@pytest.fixture
def load_api_test_data():
    """Load API test data from data/api."""

    def _load(filename, key=None):
        data_path = Path("data/api") / filename
        with open(data_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data[key] if key else data

    return _load


@pytest.fixture
def load_course_data(load_api_test_data):
    """Load course API test data."""
    return lambda key: load_api_test_data("course_cases.yaml", key)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to Allure when a UI test fails."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed and "driver" in item.funcargs:
        driver = item.funcargs["driver"]
        screenshot_dir = Path("report/screenshots/ui")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{item.name}.png"

        try:
            driver.save_screenshot(str(screenshot_path))
            if screenshot_path.exists():
                import allure

                allure.attach.file(
                    str(screenshot_path),
                    name="failure screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception as e:
            print(f"Warning: failed to save or attach screenshot: {e}")
