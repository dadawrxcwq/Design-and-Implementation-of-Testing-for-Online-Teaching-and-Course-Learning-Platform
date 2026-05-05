# common/base_request.py
import requests
from utils.config_reader import config_reader
from common.logger import LoggerManager
import json


class BaseRequest:
    """接口请求基类"""

    logger = LoggerManager.get_logger()

    def __init__(self):
        self.base_url = config_reader.get('base_url')
        self.session = requests.Session()
        # 设置默认headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def send(self, method, endpoint, **kwargs):
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"发送{method}请求: {url}")

        if 'json' in kwargs:
            self.logger.debug(f"请求体: {json.dumps(kwargs['json'], ensure_ascii=False)}")

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            self.logger.info(f"响应状态码: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {str(e)}")
            raise

    def get(self, endpoint, **kwargs):
        return self.send('GET', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.send('POST', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.send('PUT', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.send('DELETE', endpoint, **kwargs)

    def close(self):
        """关闭session"""
        self.session.close()
