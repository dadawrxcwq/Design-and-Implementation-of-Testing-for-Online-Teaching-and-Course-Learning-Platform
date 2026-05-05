# api/course_api.py
from common.base_request import BaseRequest
from common.logger import LoggerManager
import allure


class CourseAPI(BaseRequest):
    """课程管理接口"""

    logger = LoggerManager.get_logger()

    # 课程相关端点
    COURSES_ENDPOINT = '/webservice/rest/server.php'

    def __init__(self, api_client=None):
        super().__init__()
        if api_client:
            self.session = api_client.session

    @allure.step('创建课程')
    def create_course(self, course_data):
        """
        创建课程
        
        Args:
            course_data: 课程数据字典，包含 fullname, shortname 等字段
            
        Returns:
            响应对象
        """
        params = {
            'wstoken': self._get_token(),
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses[0][fullname]': course_data.get('fullname'),
            'courses[0][shortname]': course_data.get('shortname'),
            'courses[0][categoryid]': course_data.get('categoryid', 1),
        }
        
        response = self.post(self.COURSES_ENDPOINT, params=params)
        self.logger.info(f"创建课程响应: {response.json()}")
        return response

    @allure.step('获取课程列表')
    def get_courses(self, criteria=None):
        """
        获取课程列表
        
        Args:
            criteria: 筛选条件（可选）
            
        Returns:
            响应对象
        """
        params = {
            'wstoken': self._get_token(),
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json',
        }
        
        if criteria:
            for idx, criterion in enumerate(criteria):
                for key, value in criterion.items():
                    params[f'criteria[{idx}][{key}]'] = value
        
        response = self.get(self.COURSES_ENDPOINT, params=params)
        self.logger.info(f"获取课程列表响应: {response.json()}")
        return response

    @allure.step('更新课程')
    def update_course(self, course_data):
        """
        更新课程信息
        
        Args:
            course_data: 课程数据字典，必须包含 id 字段
            
        Returns:
            响应对象
        """
        params = {
            'wstoken': self._get_token(),
            'wsfunction': 'core_course_update_courses',
            'moodlewsrestformat': 'json',
            'courses[0][id]': course_data.get('id'),
        }
        
        # 添加其他要更新的字段
        for key, value in course_data.items():
            if key != 'id':
                params[f'courses[0][{key}]'] = value
        
        response = self.post(self.COURSES_ENDPOINT, params=params)
        self.logger.info(f"更新课程响应: {response.json()}")
        return response

    @allure.step('删除课程')
    def delete_course(self, course_id):
        """
        删除课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            响应对象
        """
        params = {
            'wstoken': self._get_token(),
            'wsfunction': 'core_course_delete_courses',
            'moodlewsrestformat': 'json',
            'courseids[0]': course_id,
        }
        
        response = self.post(self.COURSES_ENDPOINT, params=params)
        self.logger.info(f"删除课程响应: {response.status_code}")
        return response

    def _get_token(self):
        """获取 Web Service Token"""
        # 这里应该从配置或认证接口获取 token
        # 暂时返回占位符，实际使用时需要从配置读取
        from utils.config_reader import config_reader
        return config_reader.get('api.token', 'your_token_here')
