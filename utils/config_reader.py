import yaml
import os
from pathlib import Path


class ConfigReader:
    """配置读取器，支持多环境配置"""

    def __init__(self, config_file=None):
        if config_file is None:
            env = os.getenv('TEST_ENV', '01')
            config_file = f'config{env}.yaml'

        self.config_dir = Path(__file__).parent.parent / 'config'
        self._configs = {}

        # 加载主配置
        self._load_config(config_file)

        # 加载账号配置
        self._load_account()

    def _load_config(self, config_file):
        """加载主配置"""
        config_path = self.config_dir / config_file
        with open(config_path, encoding='utf-8') as f:
            self._configs['main'] = yaml.safe_load(f)

    def _load_account(self):
        """加载账号配置"""
        account_path = self.config_dir / 'account.yaml'
        if account_path.exists():
            with open(account_path, encoding='utf-8') as f:
                self._configs['account'] = yaml.safe_load(f)

    def get(self, key, default=None):
        """
        支持点号访问嵌套配置
        例如:
        - 'base_url' -> 从主配置获取
        - 'accounts.dean.username' -> 从账号配置获取
        - 'timeouts.implicit_wait' -> 从主配置获取
        """
        keys = key.split('.')

        # 判断从哪个配置段读取
        if keys[0] == 'accounts':
            # 从账号配置读取
            config_section = self._configs.get('account', {})
        else:
            # 从主配置读取
            config_section = self._configs.get('main', {})

        value = config_section
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    # ==================== 便捷属性方法 ====================

    @property
    def base_url(self):
        """获取基础URL"""
        return self._configs['main'].get('base_url', 'https://school.moodledemo.net')

    @property
    def browser(self):
        """获取浏览器配置"""
        return self._configs['main'].get('browser', 'chrome')

    @property
    def accounts(self):
        """获取所有账号配置"""
        return self._configs.get('account', {}).get('accounts', {})

    def get_account(self, role):
        """
        获取指定角色的账号

        Args:
            role: 角色名，如 'dean', 'teacher', 'student'

        Returns:
            dict: 包含username和password的字典
        """
        return self.accounts.get(role, {})

    @property
    def timeouts(self):
        """获取超时配置"""
        return self._configs['main'].get('timeouts', {})

    @property
    def window_config(self):
        """获取窗口配置"""
        return self._configs['main'].get('window', {})


# 全局实例
config_reader = ConfigReader()
