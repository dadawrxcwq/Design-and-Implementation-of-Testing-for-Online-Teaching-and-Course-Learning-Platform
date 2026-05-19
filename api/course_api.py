# api/course_api.py
# ============================================================================
# 课程管理接口模块
# ============================================================================
# 这个文件负责与在线教学平台的后端进行通信，执行课程相关的操作
# 比如：创建新课程、查询课程列表、修改课程信息、删除课程等

# 导入需要的工具包
from common.base_request import BaseRequest  # 导入网络请求的基础类（相当于打电话的基础设备）
from common.logger import LoggerManager      # 导入日志记录器（用来记录操作过程，方便查问题）
import allure                                # 导入测试报告工具（生成漂亮的测试报告）

class CourseAPI(BaseRequest):
    """
    课程管理接口类
    - 开设新课（创建课程）
    - 查看所有课程（获取列表）
    - 修改课程信息（更新课程）
    - 取消课程（删除课程）
    这个类就提供了这些功能，让测试代码可以像调用函数一样简单操作课程。
    技术说明：
    --------
    - 继承自 BaseRequest：获得了发送网络请求的能力
    - 使用 Moodle Web Service API：通过标准接口与平台通信
    """

    logger = LoggerManager.get_logger()  # 创建日志记录器，用于记录每一步操作

    # ==========================================================================
    # 课程相关的网络地址（端点）
    # ==========================================================================
    # 所有的课程操作都要访问这个统一的地址
    COURSES_ENDPOINT = '/webservice/rest/server.php'

    def __init__(self, api_client=None):
        """
        初始化方法 - 创建 CourseAPI 对象时自动执行
        
        参数说明：
        ----------
        api_client : 可选参数
            如果传入了现成的API客户端，就直接使用它的网络连接
            如果没有传入，就自己创建一个新的连接
        
        举个例子：
        ---------
        就像你要打电话：
        - 如果朋友借给你手机（api_client），你就直接用
        - 如果没有，你就用自己的手机（super().__init__()）
        """
        super().__init__()  # 调用父类的初始化方法，建立网络连接
        
        # 如果传入了现成的客户端，就用它的会话（保持登录状态）
        if api_client:
            self.session = api_client.session

    @allure.step('创建课程')  # 在测试报告中标记这一步骤的名称
    def create_course(self, course_data):
        """
        创建一门新课程
        
        这是做什么的？
        --------------
        就像在学校教务系统中开设一门新课，需要填写：
        - 课程全名（比如："软件测试实践2026年春季班"）
        - 课程简称（比如："SWTEST2026S"）
        - 所属类别（比如："计算机学院"）
        
        参数说明：
        ----------
        course_data : 字典类型
            包含课程信息的字典，例如：
            {
                'fullname': '软件测试实践',     # 课程完整名称
                'shortname': 'SWTEST2026',      # 课程简短名称（唯一标识）
                'categoryid': 1                 # 课程分类ID（默认是1）
            }
        
        返回值：
        -------
        响应对象
            服务器返回的结果，包含：
            - 成功：返回新创建课程的ID等信息
            - 失败：返回错误信息
        
        使用示例：
        ---------
        >>> api = CourseAPI()
        >>> new_course = {
        ...     'fullname': 'Python编程入门',
        ...     'shortname': 'PYTHON101',
        ...     'categoryid': 2
        ... }
        >>> result = api.create_course(new_course)
        >>> print(result.json())  # 查看创建结果
        
        工作流程：
        ---------
        1. 准备请求参数（课程信息 + 身份令牌）
        2. 发送POST请求到服务器
        3. 记录日志（方便后续查看）
        4. 返回服务器的响应
        """
        
        # 构建请求参数 - 就像填写表单一样
        params = {
            # 身份令牌 - 证明你有权限创建课程（就像门禁卡）
            'wstoken': self._get_token(),
            
            # 要调用的功能 - 告诉服务器我们要"创建课程"
            'wsfunction': 'core_course_create_courses',
            
            # 数据格式 - 要求服务器返回JSON格式（一种通用的数据格式）
            'moodlewsrestformat': 'json',
            
            # 课程的具体信息
            # courses[0] 表示第一个课程（可以同时创建多个课程）
            'courses[0][fullname]': course_data.get('fullname'),       # 课程全名
            'courses[0][shortname]': course_data.get('shortname'),     # 课程简称
            'courses[0][categoryid]': course_data.get('categoryid', 1), # 分类ID，默认是1
        }
        
        # 发送POST请求（POST用于提交数据创建新内容）
        response = self.post(self.COURSES_ENDPOINT, params=params)
        
        # 记录日志 - 把服务器的响应记录下来，方便调试和查看
        self.logger.info(f"创建课程响应: {response.json()}")
        
        # 返回服务器的响应结果
        return response

    @allure.step('获取课程列表')  # 在测试报告中标记这一步骤的名称
    def get_courses(self, criteria=None):
        """
        获取课程列表 - 查询系统中的所有课程或符合条件的课程
        
        这是做什么的？
        --------------
        就像在选课系统中浏览所有可选的课程，你可以：
        - 查看所有课程
        - 按条件筛选（比如只看某个老师的课、只看某个学院的课）
        
        参数说明：
        ----------
        criteria : 列表类型，可选参数
            筛选条件的列表，如果不传就返回所有课程
            
            每个条件是一个字典，例如：
            [
                {'key': 'search', 'value': 'Python'},    # 搜索包含"Python"的课程
                {'key': 'categoryid', 'value': 2}        # 只看分类ID为2的课程
            ]
            
            常见的筛选键（key）：
            - 'search': 搜索关键词
            - 'categoryid': 课程分类ID
            - 'shortname': 课程简称
        
        返回值：
        -------
        响应对象
            服务器返回的课程列表，例如：
            [
                {
                    'id': 123,
                    'fullname': 'Python编程入门',
                    'shortname': 'PYTHON101',
                    ...
                },
                {
                    'id': 124,
                    'fullname': 'Java高级编程',
                    'shortname': 'JAVA201',
                    ...
                }
            ]
        
        使用示例：
        ---------
        >>> api = CourseAPI()
        >>> 
        >>> # 示例1：获取所有课程
        >>> all_courses = api.get_courses()
        >>> 
        >>> # 示例2：搜索包含"测试"的课程
        >>> search_criteria = [{'key': 'search', 'value': '测试'}]
        >>> test_courses = api.get_courses(criteria=search_criteria)
        >>> 
        >>> # 示例3：查看某个分类下的课程
        >>> category_criteria = [{'key': 'categoryid', 'value': 5}]
        >>> category_courses = api.get_courses(criteria=category_criteria)
        
        工作流程：
        ---------
        1. 准备基本请求参数（身份令牌 + 功能名称）
        2. 如果有筛选条件，添加到参数中
        3. 发送GET请求到服务器（GET用于查询数据）
        4. 记录日志
        5. 返回课程列表
        """
        
        # 构建基本请求参数
        params = {
            # 身份令牌 - 证明你有权限查看课程
            'wstoken': self._get_token(),
            
            # 要调用的功能 - 告诉服务器我们要"获取课程列表"
            'wsfunction': 'core_course_get_courses',
            
            # 数据格式 - 要求返回JSON格式
            'moodlewsrestformat': 'json',
        }
        
        # 如果传入了筛选条件，就添加到请求参数中
        if criteria:
            # 遍历每个筛选条件
            for idx, criterion in enumerate(criteria):
                # 对每个条件中的每个键值对，构建参数
                # 例如：criteria[0][key] = 'search', criteria[0][value] = 'Python'
                for key, value in criterion.items():
                    params[f'criteria[{idx}][{key}]'] = value
        
        # 发送GET请求（GET用于获取/查询数据，不会修改服务器上的内容）
        response = self.get(self.COURSES_ENDPOINT, params=params)
        
        # 记录日志 - 把获取到的课程列表记录下来
        self.logger.info(f"获取课程列表响应: {response.json()}")
        
        # 返回服务器响应的课程列表
        return response

    @allure.step('更新课程')  # 在测试报告中标记这一步骤的名称
    def update_course(self, course_data):
        """
        更新课程信息 - 修改已有课程的属性
        
        这是做什么的？
        --------------
        就像修改已经开设的课程信息，比如：
        - 更改课程名称（学期更新了）
        - 修改课程描述
        - 调整可见性（暂时隐藏课程）
        - 更换授课教师
        
        重要提示：
        ---------
        必须提供课程ID，否则系统不知道要修改哪门课！
        
        参数说明：
        ----------
        course_data : 字典类型
            包含课程ID和要修改的字段，例如：
            {
                'id': 123,                        # 【必需】课程ID
                'fullname': '软件测试实践-2026春',  # 新的课程全名
                'summary': ' updated description'  # 新的课程描述
            }
            
            可以更新的常见字段：
            - 'id': 课程ID（必需）
            - 'fullname': 课程全名
            - 'shortname': 课程简称
            - 'summary': 课程简介
            - 'visible': 是否可见（1=可见，0=隐藏）
            - 'startdate': 开课日期
        
        返回值：
        -------
        响应对象
            服务器返回的更新结果：
            - 成功：通常返回空列表 [] 或成功标志
            - 失败：返回错误信息（比如课程不存在、权限不足）
        
        使用示例：
        ---------
        >>> api = CourseAPI()
        >>> 
        >>> # 示例1：修改课程名称
        >>> update_data = {
        ...     'id': 123,
        ...     'fullname': 'Python编程入门（2026修订版）'
        ... }
        >>> result = api.update_course(update_data)
        >>> 
        >>> # 示例2：隐藏课程
        >>> hide_data = {
        ...     'id': 123,
        ...     'visible': 0  # 0表示隐藏，1表示显示
        ... }
        >>> api.update_course(hide_data)
        >>> 
        >>> # 示例3：同时修改多个字段
        >>> multi_update = {
        ...     'id': 123,
        ...     'fullname': 'Java高级编程',
        ...     'summary': '本课程讲解Java高级特性...',
        ...     'visible': 1
        ... }
        >>> api.update_course(multi_update)
        
        工作流程：
        ---------
        1. 从 course_data 中提取课程ID
        2. 构建基本请求参数（令牌 + 功能名称 + 课程ID）
        3. 遍历 course_data 的其他字段，全部添加到参数中
        4. 发送POST请求到服务器
        5. 记录日志
        6. 返回更新结果
        """
        
        # 构建基本请求参数
        params = {
            # 身份令牌 - 证明你有权限修改课程
            'wstoken': self._get_token(),
            
            # 要调用的功能 - 告诉服务器我们要"更新课程"
            'wsfunction': 'core_course_update_courses',
            
            # 数据格式 - 要求返回JSON格式
            'moodlewsrestformat': 'json',
            
            # 【关键】课程ID - 告诉服务器要修改哪门课
            'courses[0][id]': course_data.get('id'),
        }
        
        # 添加其他要更新的字段
        # 遍历 course_data 中的所有字段
        for key, value in course_data.items():
            # 跳过 'id' 字段，因为上面已经添加过了
            if key != 'id':
                # 将其他字段添加到参数中
                # 例如：如果 key='fullname', value='新课程名'
                # 就会添加：params['courses[0][fullname]'] = '新课程名'
                params[f'courses[0][{key}]'] = value
        
        # 发送POST请求（POST用于提交修改）
        response = self.post(self.COURSES_ENDPOINT, params=params)
        
        # 记录日志 - 把更新结果记录下来
        self.logger.info(f"更新课程响应: {response.json()}")
        
        # 返回服务器的响应结果
        return response

    @allure.step('删除课程')  # 在测试报告中标记这一步骤的名称
    def delete_course(self, course_id):
        """
        删除课程 - 从系统中永久移除一门课程
        
        ⚠️ 警告：这是一个危险操作！
        --------------------------
        删除后课程将无法恢复，包括：
        - 课程内容（课件、视频、文档）
        - 学生作业和成绩
        - 论坛讨论记录
        - 所有相关数据
        
        这是做什么的？
        --------------
        就像取消一门不再开设的课程，比如：
        - 过时的课程（技术已经淘汰）
        - 临时试点课程（试点结束）
        - 重复创建的错误课程
        
        参数说明：
        ----------
        course_id : 整数或字符串
            要删除的课程ID，例如：123
            
            如何获取课程ID？
            - 通过 get_courses() 查询课程列表
            - 从课程URL中查看（通常包含 id=xxx）
            - 从创建课程时的返回结果中获取
        
        返回值：
        -------
        响应对象
            服务器返回的删除结果：
            - 成功：通常返回空响应或成功标志
            - 失败：返回错误信息（比如课程不存在、权限不足、课程正在使用中）
        
        使用示例：
        ---------
        >>> api = CourseAPI()
        >>> 
        >>> # 示例1：删除指定ID的课程
        >>> course_id = 123
        >>> result = api.delete_course(course_id)
        >>> 
        >>> # 示例2：先查询再删除（更安全）
        >>> courses = api.get_courses()
        >>> course_list = courses.json()
        >>> 
        >>> # 找到要删除的课程
        >>> for course in course_list:
        ...     if course['shortname'] == 'OLD_COURSE_2020':
        ...         api.delete_course(course['id'])
        ...         print(f"已删除课程: {course['fullname']}")
        >>> 
        >>> # 示例3：批量删除（谨慎使用！）
        >>> old_course_ids = [101, 102, 103]
        >>> for cid in old_course_ids:
        ...     api.delete_course(cid)
        
        安全建议：
        ---------
        1. 删除前先确认课程ID是否正确
        2. 最好先隐藏课程（visible=0），观察一段时间再删除
        3. 重要课程建议先导出备份数据
        4. 检查是否有学生正在使用该课程
        
        工作流程：
        ---------
        1. 构建请求参数（令牌 + 功能名称 + 课程ID）
        2. 发送POST请求到服务器
        3. 记录日志（只记录状态码，避免泄露敏感信息）
        4. 返回删除结果
        """
        
        # 构建请求参数
        params = {
            # 身份令牌 - 证明你有权限删除课程（通常需要管理员权限）
            'wstoken': self._get_token(),
            
            # 要调用的功能 - 告诉服务器我们要"删除课程"
            'wsfunction': 'core_course_delete_courses',
            
            # 数据格式 - 要求返回JSON格式
            'moodlewsrestformat': 'json',
            
            # 要删除的课程ID
            # courseids[0] 表示第一个要删除的课程（可以同时删除多个）
            'courseids[0]': course_id,
        }
        
        # 发送POST请求执行删除操作
        response = self.post(self.COURSES_ENDPOINT, params=params)
        
        # 记录日志 - 只记录HTTP状态码，不记录完整响应（保护数据安全）
        # 状态码说明：
        # - 200: 删除成功
        # - 403: 权限不足
        # - 404: 课程不存在
        # - 500: 服务器错误
        self.logger.info(f"删除课程响应: {response.status_code}")
        
        # 返回服务器的响应结果
        return response

    def _get_token(self):
        """
        获取 Web Service Token（身份令牌）
        
        这是什么？
        ---------
        Token 就像是一把"数字钥匙"或"门禁卡"，用来证明你的身份和权限。
        
        为什么需要Token？
        ----------------
        - 安全性：每次请求都要验证身份，防止未授权访问
        - 追踪：系统可以知道是谁在执行操作
        - 权限控制：不同角色有不同的Token，权限也不同
        
        类比理解：
        ---------
        想象你要进入学校的管理系统：
        1. 你先登录（输入用户名和密码）
        2. 系统给你一个临时通行证（Token）
        3. 之后每次操作，你都要出示这个通行证
        4. 通行证过期后，需要重新登录获取新的
        
        Token 的特点：
        -------------
        - 有时效性：通常在几小时到几天后过期
        - 有权限范围：不同Token能做的事情不同
        - 需要保密：泄露Token等于泄露账号密码
        
        返回值：
        -------
        字符串
            Web Service Token，例如："a1b2c3d4e5f6g7h8i9j0"
        
        工作流程：
        ---------
        1. 从配置文件中读取预先配置好的Token
        2. 如果配置中没有，返回一个占位符（实际使用时会报错）
        
        注意事项：
        ---------
        ⚠️ 当前实现是从配置文件读取静态Token
        ⚠️ 更好的做法是：
           - 通过登录接口动态获取Token
           - 实现Token自动刷新机制
           - 支持多用户切换
        
        配置示例（在 config/config01.yaml 中）：
        ------------------------------------
        api:
          token: "your_actual_token_here"
        
        如何获取Token？
        -------------
        1. 登录Moodle后台
        2. 进入：网站管理 > 插件 > Web服务 > 管理令牌
        3. 为用户创建新的Token
        4. 复制Token并保存到配置文件中
        
        TODO（未来改进）：
        ----------------
        - [ ] 实现自动登录获取Token
        - [ ] 添加Token过期检测和自动刷新
        - [ ] 支持从环境变量读取Token（更安全）
        - [ ] 添加Token加密存储
        """
        
        # 从配置读取器中获取Token
        from utils.config_reader import config_reader
        
        # 尝试从配置文件中读取 'api.token' 的值
        # 如果找不到，就返回 'your_token_here' 作为占位符
        # get方法的第二个参数是默认值（当配置项不存在时使用）
        return config_reader.get('api.token', 'your_token_here')
