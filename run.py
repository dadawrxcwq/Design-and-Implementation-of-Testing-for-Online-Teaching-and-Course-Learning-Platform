import os
import sys
import subprocess
from pathlib import Path

from utils.report_notifier import send_allure_report

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def clear_report():
    """清空报告目录"""
    import shutil
    report_dirs = [
        'report/allure-results',
        'report/screenshots',
        'report/logs'
    ]
    for dir_path in report_dirs:
        path = Path(dir_path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def run_tests(test_path, markers=None, description=""):
    """
    运行测试

    Args:
        test_path: 测试路径
        markers: 标记过滤器（可选）
        description: 描述信息
    
    Returns:
        int: pytest 退出码，0表示成功，非0表示失败
    """
    print("\n" + "=" * 60)
    print(f"运行: {description}")
    print(f"测试路径: {test_path}")
    if markers:
        print(f"标记过滤: {markers}")
    print("=" * 60)
    sys.stdout.flush()

    args = [
        sys.executable,
        '-m',
        'pytest',
        test_path,
        '-v',
        '--alluredir=./report/allure-results',
    ]

    if markers:
        args.extend(['-m', markers])

    env = os.environ.copy()
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    result = subprocess.run(args, cwd=Path(__file__).parent, env=env)
    exit_code = result.returncode
    
    if exit_code == 0:
        print(f"✅ {description} - 通过")
    else:
        print(f"❌ {description} - 存在失败用例")
    
    return exit_code


def run_ui_tests(role=None):
    """运行UI测试"""
    if role:
        return run_tests(
            'testcase/ui',
            f'ui and {role}',
            f'UI测试 - {role}角色'
        )
    else:
        # 运行所有UI测试（不限制标记）
        return run_tests('testcase/ui', None, 'UI自动化测试（全部）')


def run_api_tests(module=None):
    """运行接口测试"""
    if module:
        return run_tests(
            'testcase/api',
            f'api and {module}',
            f'接口测试 - {module}模块'
        )
    else:
        return run_tests('testcase/api', 'api', '接口自动化测试（全部）')


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "=" * 60)
    print("运行性能测试")
    print("=" * 60)

    return run_tests('testcase/performance', 'performance', '性能测试')


def run_expanded_tests():
    """Run graduation-project expanded test matrix."""
    return run_tests('testcase/expanded', None, 'Graduation expanded test matrix')


def generate_allure_report():
    """生成Allure报告"""
    print("\n" + "=" * 60)
    print("生成Allure测试报告")
    print("=" * 60)

    report_dir = Path('report/allure-report')
    if report_dir.exists():
        import shutil
        shutil.rmtree(report_dir)

    os.system('allure generate report/allure-results -o report/allure-report --clean')
    print(f"\n✅ Allure报告已生成: {report_dir.absolute()}")

    send_allure_report(report_dir=report_dir)

    # 自动打开报告（使用默认浏览器）
    try:
        import webbrowser
        report_url = f'file:///{(report_dir / "index.html").absolute()}'
        webbrowser.open(report_url)
        print("🌐 已在浏览器中打开报告")
    except Exception as e:
        print(f"⚠️ 无法自动打开报告: {e}")
        print(f"请手动打开: {report_dir / 'index.html'}")


def run_full_workflow():
    """按业务逻辑顺序运行完整测试流程"""
    print("\n" + "=" * 80)
    print("🚀 开始执行完整测试工作流")
    print("=" * 80)
    print("\n说明：此工作流将按照 Moodle 平台实际业务流程顺序执行测试")
    print("      包括：登录 → 创建课程 → Enrol用户 → 作业流程 → 权限验证 → 清理数据 → 接口测试")
    
    failed_stages = []
    
    # 第一阶段：登录
    print("\n" + "─" * 80)
    print("【第一阶段】登录功能测试")
    print("─" * 80)
    exit_code = run_tests('testcase/ui/auth/test_login.py', None, '登录功能测试')
    if exit_code != 0:
        print("❌ 登录测试失败，后续测试可能无法执行")
        failed_stages.append("登录测试")
        # 不直接返回，让用户看到完整的执行情况
    else:
        print("✅ 第一阶段完成：登录测试通过")
    
    # 第二阶段：构建数据（必须同一小时内）
    print("\n" + "─" * 80)
    print("【第二阶段】构建基础数据（课程与用户Enrolment）")
    print("─" * 80)
    
    # Dean创建课程
    print("\n[2.1] Dean创建课程并拉入教师")
    exit_code = run_tests('testcase/ui/dean/test_course_management.py', None, 'Dean创建课程 + 拉入教师')
    if exit_code != 0:
        print("❌ 课程管理测试失败")
        failed_stages.append("课程管理")
    else:
        print("✅ 课程创建成功")
    
    # Teacher拉入学生
    print("\n[2.2] Teacher拉入学生")
    exit_code = run_tests('testcase/ui/teacher/test_enrol_student.py', None, 'Teacher拉入学生')
    if exit_code != 0:
        print("❌ 学生 enrolment 测试失败")
        failed_stages.append("学生Enrolment")
    else:
        print("✅ 学生Enrolment成功")
    
    # Student查看课程
    print("\n[2.3] Student查看已选课程")
    exit_code = run_tests('testcase/ui/student/test_view_course.py', None, 'Student查看课程')
    if exit_code != 0:
        print("❌ 学生查看课程测试失败")
        failed_stages.append("学生查看课程")
    else:
        print("✅ 学生可以正常查看课程")
    
    # 第三阶段：课程补充 + 作业
    print("\n" + "─" * 80)
    print("【第三阶段】课程内容完善与作业全流程")
    print("─" * 80)
    
    # Teacher编辑课程
    print("\n[3.1] Teacher编辑课程内容")
    exit_code = run_tests('testcase/ui/teacher/test_edit_course.py', None, 'Teacher编辑课程')
    if exit_code != 0:
        print("❌ 课程编辑测试失败")
        failed_stages.append("课程编辑")
    else:
        print("✅ 课程编辑成功")
    
    # Teacher创建作业 & Student提交作业 & Teacher评分 & Student查看反馈
    print("\n[3.2] 作业完整流程（创建→提交→评分→反馈）")
    exit_code = run_tests('testcase/ui/teacher/test_assignment.py', None, '作业完整流程（创建-提交-评分-反馈）')
    if exit_code != 0:
        print("❌ 作业测试失败")
        failed_stages.append("作业流程")
    else:
        print("✅ 作业流程完整执行成功")
    
    # 第四阶段：权限测试
    print("\n" + "─" * 80)
    print("【第四阶段】角色权限验证")
    print("─" * 80)
    exit_code = run_tests('testcase/ui/permission/test_permissions.py', None, '角色权限验证')
    if exit_code != 0:
        print("⚠️ 权限测试存在失败用例（部分为预期失败，用于验证权限限制）")
        failed_stages.append("权限测试")
    else:
        print("✅ 权限验证完成")
    
    # 第五阶段：删除课程（最后执行）
    print("\n" + "─" * 80)
    print("【第五阶段】清理数据 - 删除测试课程")
    print("─" * 80)
    exit_code = run_tests('testcase/ui/dean/test_delete_course.py', None, 'Dean删除课程')
    if exit_code != 0:
        print("⚠️ 课程删除测试存在失败用例")
        failed_stages.append("课程删除")
    else:
        print("✅ 测试课程已清理")
    
    # 第六阶段：接口测试
    print("\n" + "─" * 80)
    print("【第六阶段】API接口测试")
    print("─" * 80)
    exit_code = run_tests('testcase/api/test_moodle_api.py', None, 'Moodle接口测试')
    if exit_code != 0:
        print("⚠️ 接口测试存在失败用例")
        failed_stages.append("接口测试")
    else:
        print("✅ 接口测试完成")
    
    # 第七阶段：毕设扩展测试矩阵
    print("\n" + "─" * 80)
    print("【第七阶段】毕设扩展测试矩阵")
    print("─" * 80)
    exit_code = run_expanded_tests()
    if exit_code != 0:
        print("⚠️ 毕设扩展测试矩阵存在失败或浏览器环境不可用")
        failed_stages.append("毕设扩展测试")
    else:
        print("✅ 毕设扩展测试矩阵完成")

    # 第八阶段：JMeter性能测试
    print("\n" + "─" * 80)
    print("【第八阶段】JMeter性能与压力测试")
    print("─" * 80)
    exit_code = run_performance_tests()
    if exit_code != 0:
        print("⚠️ JMeter性能测试存在失败用例")
        failed_stages.append("JMeter性能测试")
    else:
        print("✅ JMeter性能测试完成，结果已写入Allure报告")

    # 总结
    print("\n" + "=" * 80)
    print("📊 测试工作流执行总结")
    print("=" * 80)
    
    if not failed_stages:
        print("✅ 所有阶段均执行成功！")
    else:
        print(f"⚠️ 以下阶段存在失败用例：")
        for stage in failed_stages:
            print(f"   - {stage}")
        print("\n💡 提示：请查看下方的 Allure 报告了解详细失败原因")
    
    print("\n📈 正在生成 Allure 测试报告...")
    return True


def main():
    """主函数"""
    clear_report()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'ui':
            role = sys.argv[2] if len(sys.argv) > 2 else None
            run_ui_tests(role)
        elif command == 'api':
            module = sys.argv[2] if len(sys.argv) > 2 else None
            run_api_tests(module)
        elif command == 'performance':
            run_performance_tests()
        elif command == 'expanded':
            run_expanded_tests()
        elif command == 'smoke':
            run_tests('testcase', 'smoke', '冒烟测试')
        elif command == 'dean':
            run_ui_tests('dean')
        elif command == 'teacher':
            run_ui_tests('teacher')
        elif command == 'student':
            run_ui_tests('student')
        elif command == 'all':
            run_ui_tests()
            run_api_tests()
            run_expanded_tests()
            run_performance_tests()
        elif command == 'workflow':
            # 新增：按业务逻辑顺序执行完整工作流
            run_full_workflow()
        elif command == 'help':
            print("""
用法: python run.py [command] [options]

命令:
  workflow    按业务逻辑顺序执行完整测试流程（推荐）
  ui          运行UI测试
    选项: dean, teacher, student
  api         运行接口测试
  expanded    运行毕设扩展测试矩阵
  performance 运行性能测试
  smoke       运行冒烟测试
  all         运行所有测试（UI + API + Expanded + Performance）
  help        显示帮助信息

示例:
  python run.py workflow              # 按顺序执行完整业务流程
  python run.py ui dean               # 仅运行Dean角色UI测试
  python run.py api                   # 运行所有接口测试
  python run.py expanded              # 运行扩展矩阵用例
            """)
            return
    else:
        # 默认运行完整工作流（按业务逻辑顺序）
        print("未指定命令，默认执行完整测试工作流...")
        run_full_workflow()

    generate_allure_report()


if __name__ == '__main__':
    main()
