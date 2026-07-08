"""使用 Google Chrome 快速运行店铺管理测试"""
import os
import sys
import pytest

if __name__ == "__main__":
    # 设置环境变量：使用 Google Chrome 运行，非无头模式，保留截图
    os.environ['HEADLESS'] = 'false'
    os.environ['DEBUG_SCREENSHOT'] = 'true'

    # 选择要运行的测试用例
    selected_tests = [
        # 店铺列表测试
        "test_shop_management.py::TestShopList::test_店铺列表页面加载",
        "test_shop_management.py::TestShopList::test_新增店铺按钮可见",

        # 店铺创建部分测试
        "test_shop_management.py::TestShopCreation::test_新增店铺_仅填写店铺名称",

        # 编辑店铺完整流程（核心）
        "test_shop_management.py::TestShopEdit::test_编辑店铺_点击编辑按钮",
        "test_shop_management.py::TestShopEdit::test_编辑店铺_修改店铺名称",
        "test_shop_management.py::TestShopEdit::test_编辑店铺_修改下拉选项",

        # 搜索测试
        "test_shop_management.py::TestShopSearch::test_搜索店铺_输入关键词",
    ]

    print("=" * 70)
    print("🚀 使用 Google Chrome 浏览器执行店铺管理测试")
    print("=" * 70)
    print(f"共选择 {len(selected_tests)} 个测试用例")
    print()

    # 运行测试
    exit_code = pytest.main(
        selected_tests + ["-v", "-s", "--tb=long", "--headed"],
        plugins=[]
    )

    print()
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"⚠️  测试完成，退出码: {exit_code}")
    print()

    # 提示截图位置
    print("截图保存在当前目录（edit_before.png, edit_form_filled.png 等）")
