from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from common.logger import LoggerManager
from utils.config_reader import config_reader


class DriverFactory:
    """Browser driver factory."""

    @staticmethod
    def _apply_common_options(options):
        """Apply options that keep UI tests responsive without changing behavior."""
        options.page_load_strategy = "eager"
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        return options

    @staticmethod
    def get_driver(browser=None):
        browser = (browser or __import__("os").getenv("TEST_BROWSER") or config_reader.get("browser", "chrome")).lower()
        logger = LoggerManager.get_logger()

        if browser == "chrome":
            options = DriverFactory._apply_common_options(ChromeOptions())
            logger.info("Starting Chrome browser")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        elif browser == "edge":
            options = DriverFactory._apply_common_options(EdgeOptions())
            logger.info("Starting Edge browser with webdriver-manager")
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.page_load_strategy = "eager"
            logger.info("Starting Firefox browser")
            driver = webdriver.Firefox(options=options)

        else:
            raise ValueError(f"Unsupported browser: {browser}")

        driver.maximize_window()
        driver.implicitly_wait(config_reader.get("timeouts.implicit_wait", 2))
        return driver

    @staticmethod
    def quit_driver(driver):
        """Safely close browser."""
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
