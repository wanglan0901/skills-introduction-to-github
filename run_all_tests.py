"""全量自动化测试运行器
按顺序执行所有测试用例：
1. 创建商家全流程（创建+编辑+添加店铺）
2. 快速添加店铺
3. 店铺管理 pytest 测试集（18个用例）
4. UI 基础测试
5. API 测试
"""
import subprocess
import sys
import os
import time
from datetime import datetime

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

# 测试用例列表：按执行顺序排列
TEST_SUITES = [
    {
        "name": "创建商家全流程（创建→编辑→添加店铺）",
        "type": "python",
        "command": [sys.executable, os.path.join(TESTS_DIR, "test_create_business_tree_select.py")],
        "timeout": 600,
    },
    {
        "name": "快速添加店铺",
        "type": "python",
        "command": [sys.executable, os.path.join(TESTS_DIR, "test_add_shop_quick.py")],
        "timeout": 300,
    },
    {
        "name": "店铺管理模块（18个pytest用例）",
        "type": "pytest",
        "pytest_targets": [
            "test_shop_management.py",
        ],
        "timeout": 900,
    },
    {
        "name": "UI基础测试",
        "type": "pytest",
        "pytest_targets": [
            "test_ui.py",
        ],
        "timeout": 120,
    },
    {
        "name": "API基础测试",
        "type": "pytest",
        "pytest_targets": [
            "test_api.py",
        ],
        "timeout": 60,
    },
]

results = []


def run_command(cmd, timeout_seconds, env=None):
    """运行命令并返回结果"""
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=TESTS_DIR,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env or os.environ.copy(),
        )
        elapsed = time.time() - start_time
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed": elapsed,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"执行超时（>{timeout_seconds}秒）",
            "elapsed": elapsed,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "elapsed": elapsed,
        }


def parse_pytest_output(stdout, stderr):
    """解析pytest输出，提取测试统计"""
    combined = stdout + "\n" + stderr

    import re
    # 匹配 pytest 的汇总行：如 "18 passed, 1 failed in 120.34s"
    match = re.search(r'(\d+)\s+passed', combined)
    passed = int(match.group(1)) if match else 0

    match = re.search(r'(\d+)\s+failed', combined)
    failed = int(match.group(1)) if match else 0

    match = re.search(r'(\d+)\s+skipped', combined)
    skipped = int(match.group(1)) if match else 0

    match = re.search(r'(\d+)\s+error', combined)
    errors = int(match.group(1)) if match else 0

    return passed, failed, skipped, errors


def extract_standalone_result(stdout, stderr, name):
    """从独立脚本的输出中提取结果"""
    combined = stdout + stderr
    passed_indicators = ['✓✓✓', '✅✅✅', '成功！', '测试通过']
    failed_indicators = ['✗ 错误', '测试失败', 'Error:', '异常']

    passed = any(ind in combined for ind in passed_indicators)
    failed = any(ind in combined for ind in failed_indicators)

    # 对于有多个子步骤的脚本，可能有多个成功标记
    if combined.count('✓✓✓') >= 2:
        passed = True
    if combined.count('✅') >= 5:
        passed = True

    return passed, failed


def print_header(text, char="="):
    line = char * 70
    print(f"\n{line}")
    print(f"  {text}")
    print(f"{line}\n")


def main():
    print_header("🚀 全量自动化测试开始", "=")

    total_start = time.time()

    for i, suite in enumerate(TEST_SUITES, 1):
        suite_name = suite["name"]
        suite_type = suite["type"]
        timeout = suite.get("timeout", 300)

        print_header(f"[{i}/{len(TEST_SUITES)}] {suite_name}", "-")

        env = os.environ.copy()
        env.setdefault("HEADLESS", "false")
        env.setdefault("SLOW_MO", "200")
        env["PYTHONUNBUFFERED"] = "1"

        if suite_type == "python":
            print(f"▶️  执行独立脚本...")
            cmd = suite["command"]
            result = run_command(cmd, timeout, env)

            passed, has_error = extract_standalone_result(result["stdout"], result["stderr"], suite_name)

            status = "✅ PASS" if not has_error else "❌ FAIL"
            elapsed = result["elapsed"]

        elif suite_type == "pytest":
            pytest_cmd = [
                sys.executable, "-m", "pytest",
            ] + suite["pytest_targets"] + [
                "-v",
                "-s",
                "--tb=short",
            ]
            print(f"▶️  pytest {suite['pytest_targets']}")
            result = run_command(pytest_cmd, timeout, env)

            passed, failed, skipped, errors = parse_pytest_output(result["stdout"], result["stderr"])
            total = passed + failed + skipped + errors
            has_error = result["returncode"] != 0
            status = "✅ PASS" if result["returncode"] == 0 else "❌ FAIL"
            elapsed = result["elapsed"]

            suite["passed"] = passed
            suite["failed"] = failed
            suite["skipped"] = skipped

        # 记录结果
        result_record = {
            "suite": suite_name,
            "status": status,
            "elapsed": elapsed,
            "returncode": result["returncode"],
        }
        results.append(result_record)

        # 打印结果
        print(f"\n{'─' * 50}")
        print(f"📋 {suite_name}")
        print(f"{'─' * 50}")
        print(f"   状态: {status}")
        print(f"   耗时: {elapsed:.1f}秒")

        if result["returncode"] != 0:
            stderr_output = result.get("stderr", "").strip()
            if stderr_output:
                print(f"   错误详情:")
                for line in stderr_output.split('\n')[-10:]:
                    if line.strip():
                        print(f"     {line.strip()[:120]}")

            if suite_type == "pytest":
                stdout_output = result.get("stdout", "").strip()
                if stdout_output:
                    error_lines = [l for l in stdout_output.split('\n') if 'FAILED' in l or 'ERROR' in l]
                    if error_lines:
                        for line in error_lines[:5]:
                            print(f"     {line.strip()[:120]}")
        else:
            if suite_type == "pytest":
                print(f"   通过: {passed}, 失败: {failed}, 跳过: {skipped}")

        if result["returncode"] != 0 and i < len(TEST_SUITES):
            print(f"\n  ⚠️  此测试有失败，继续执行下一个...")

        # 给浏览器一些时间关闭
        time.sleep(3)

    # ============================================================
    # 汇总报告
    # ============================================================
    total_elapsed = time.time() - total_start
    print_header("🏁 全量测试完成 - 汇总报告", "=")

    passed_count = sum(1 for r in results if "PASS" in r["status"])
    failed_count = sum(1 for r in results if "FAIL" in r["status"])

    print(f"\n{'测试套件':<45} {'状态':<10} {'耗时':<10}")
    print("-" * 65)
    for r in results:
        elapsed_str = f"{r['elapsed']:.1f}s"
        print(f"{r['suite']:<45} {r['status']:<10} {elapsed_str:<10}")

    print("-" * 65)
    print(f"\n  📊 总计: {len(results)} 个测试套件")
    print(f"  ✅ 通过: {passed_count}")
    print(f"  ❌ 失败: {failed_count}")
    print(f"  ⏱️  总耗时: {total_elapsed:.1f}秒")

    # 生成报告文件
    report_path = os.path.join(TESTS_DIR, "全量测试报告.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 全量自动化测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**测试套件总数**: {len(results)}\n")
        f.write(f"**通过**: {passed_count}\n")
        f.write(f"**失败**: {failed_count}\n")
        f.write(f"**总耗时**: {total_elapsed:.1f}秒\n\n")

        f.write("## 测试套件详情\n\n")
        f.write("| 测试套件 | 状态 | 耗时 |\n")
        f.write("|---------|------|------|\n")
        for r in results:
            f.write(f"| {r['suite']} | {r['status']} | {r['elapsed']:.1f}s |\n")

    print(f"\n📄 报告已保存: {report_path}")
    print()

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
