import os
import sys
import pytest
import subprocess
from pathlib import Path


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
    """
    print("\n" + "=" * 60)
    print(f"运行: {description}")
    print("=" * 60)

    args = [test_path, '-v']

    if markers:
        args.extend(['-m', markers])

    exit_code = pytest.main(args)
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

    # 自动打开报告（使用默认浏览器）
    try:
        import webbrowser
        report_url = f'file:///{(report_dir / "index.html").absolute()}'
        webbrowser.open(report_url)
        print("🌐 已在浏览器中打开报告")
    except Exception as e:
        print(f"⚠️ 无法自动打开报告: {e}")
        print(f"请手动打开: {report_dir / 'index.html'}")


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
            run_performance_tests()
    else:
        # 默认运行所有UI测试
        run_ui_tests()

    generate_allure_report()


if __name__ == '__main__':
    main()
