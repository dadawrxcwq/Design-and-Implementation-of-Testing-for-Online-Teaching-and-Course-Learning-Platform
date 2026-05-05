# import pytest
# import allure
# from pages.auth.login_page import LoginPage
# from pages.user.user_list_page import UserListPage
#
#
# @allure.feature('Dean角色测试')
# @allure.story('用户管理')
# class TestUserManagement:
#     """Dean角色的用户管理功能测试"""
#
#     @pytest.fixture(autouse=True)
#     def setup(self, driver, config_reader):
#         """测试前置准备"""
#         self.driver = driver
#         self.config = config_reader
#
#         # 以Dean身份登录
#         dean_account = self.config.get('accounts.dean')
#         login_page = LoginPage(driver)
#         login_page.navigate()
#         login_page.login(dean_account['username'], dean_account['password'])
#
#         assert login_page.is_login_success(), "Dean登录失败"
#
#         yield
#
#         # 测试后清理：登出
#         login_page.logout()
#
#     @allure.title('TC001-Dean可以批量操作用户')
#     @allure.description('验证Dean可以执行批量用户操作')
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.smoke
#     @pytest.mark.ui
#     @pytest.mark.dean
#     def test_bulk_user_operations(self):
#         """测试批量用户操作"""
#         user_list_page = UserListPage(self.driver)
#         user_list_page.navigate_to_user_list()
#
#         # 选择多个用户
#         user_list_page.select_users(['student1', 'student2'])
#
#         # 执行批量操作
#         result = user_list_page.perform_bulk_action('suspend')
#
#         assert result, "批量操作失败"
#
#     @allure.title('TC002-Dean可以创建Cohorts')
#     @allure.description('验证Dean可以创建和管理Cohorts')
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.ui
#     @pytest.mark.dean
#     def test_create_cohort(self):
#         """测试创建Cohort"""
#         from pages.user.cohort_page import CohortPage
#
#         cohort_page = CohortPage(self.driver)
#         cohort_page.navigate()
#
#         cohort_name = f"Test_Cohort_{pytest.random_id()}"
#         cohort_page.create_cohort(cohort_name, "测试Cohort")
#
#         assert cohort_page.is_cohort_exists(cohort_name), "Cohort创建失败"
#
#     @allure.title('TC003-Dean可以检查用户权限')
#     @allure.description('验证Dean可以检查单个用户的权限')
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.ui
#     @pytest.mark.dean
#     def test_check_user_permissions(self):
#         """测试检查用户权限"""
#         user_list_page = UserListPage(self.driver)
#         user_list_page.navigate_to_user_list()
#
#         permissions = user_list_page.check_user_permissions('teacher')
#
#         assert 'Teacher' in permissions, "权限检查失败"
