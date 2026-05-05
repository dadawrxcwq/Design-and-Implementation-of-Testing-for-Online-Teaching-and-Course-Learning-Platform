# common/logger.py
import logging
from pathlib import Path


class LoggerManager:
    """日志管理器，单例模式"""

    _logger = None

    @classmethod
    def get_logger(cls, name="AutoTest"):
        if cls._logger is None:
            cls._logger = cls._setup_logger(name)
        return cls._logger

    @staticmethod
    def _setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # 最低级别，handler再过滤

        # 避免重复添加handler
        if logger.handlers:
            return logger

        # 控制台handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 文件handler
        log_dir = Path(__file__).parent.parent / 'report' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / 'test.log', encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

        return logger
