# import subprocess
# import os
# from pathlib import Path
# import pytest
# import allure
#
#
# class JMeterRunner:
#     """JMeter性能测试执行器"""
#
#     def __init__(self):
#         self.jmx_dir = Path('performance/jmx')
#         self.report_dir = Path('report/performance')
#         self.report_dir.mkdir(parents=True, exist_ok=True)
#
#     def run_test(self, jmx_file, thread_count=10, duration=60):
#         """
#         运行单个JMeter测试
#
#         Args:
#             jmx_file: JMX文件名（不含路径）
#             thread_count: 并发线程数
#             duration: 测试持续时间（秒）
#         """
#         jmx_path = self.jmx_dir / jmx_file
#         result_file = self.report_dir / f"{jmx_file.stem}.jtl"
#         html_report = self.report_dir / f"{jmx_file.stem}_report"
#
#         cmd = [
#             'jmeter',
#             '-n',
#             '-t', str(jmx_path),
#             '-l', str(result_file),
#             '-Jthreads', str(thread_count),
#             '-Jduration', str(duration),
#             '-e',
#             '-o', str(html_report)
#         ]
#
#         result = subprocess.run(cmd, capture_output=True, text=True)
#
#         if result.returncode != 0:
#             raise Exception(f"JMeter测试失败: {result.stderr}")
#
#         return {
#             'result_file': result_file,
#             'html_report': html_report
#         }
#
#
# @pytest.mark.performance
# class TestPerformance:
#     """性能测试用例"""
#
#     @pytest.fixture
#     def jmeter(self):
#         return JMeterRunner()
#
#     @allure.title('PERF001-登录性能测试')
#     @allure.description('测试登录接口的性能表现')
#     @pytest.mark.smoke
#     def test_login_performance(self, jmeter):
#         """登录性能测试"""
#         result = jmeter.run_test('login.jmx', thread_count=50, duration=120)
#
#         assert result['result_file'].exists(), "性能测试结果文件未生成"
#         assert result['html_report'].exists(), "性能测试报告未生成"
#
#         allure.attach.file(
#             result['html_report'] / 'index.html',
#             name="登录性能报告",
#             attachment_type=allure.attachment_type.HTML
#         )
#
#     @allure.title('PERF002-课程访问性能测试')
#     @allure.description('测试课程访问的性能表现')
#     def test_course_access_performance(self, jmeter):
#         """课程访问性能测试"""
#         result = jmeter.run_test('course_access.jmx', thread_count=100, duration=180)
#
#         assert result['result_file'].exists()
#
#     @allure.title('PERF003-测验提交性能测试')
#     @allure.description('测试测验提交的性能表现')
#     def test_quiz_submit_performance(self, jmeter):
#         """测验提交性能测试"""
#         result = jmeter.run_test('quiz_submit.jmx', thread_count=30, duration=300)
#
#         assert result['result_file'].exists()
