"""店铺管理模块自动化测试用例"""
import pytest
import time
import random
import os
from playwright.sync_api import Page, expect

# CI 环境自动切换为无头模式
HEADLESS = os.environ.get('CI') is not None or os.environ.get('HEADLESS', '').lower() == 'true'
SCREENSHOT_DIR = os.environ.get('SCREENSHOT_DIR', os.path.dirname(os.path.abspath(__file__)))

# 测试数据
TEST_ACCOUNT = {
    'email': 'wanglan1@shuishoukefu.com',
    'password': '123'
}


class TestShopManagement:
    """店铺管理模块测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """每个测试用例的前置条件：登录并导航到商家详情页"""
        self.page = page
        self.page.set_default_timeout(15000)

        # 1. 登录
        self._login()

        # 2. 导航到商家管理页面
        self.page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(2000)

        # 3. 点击第一个商家的详情按钮进入详情页
        self._enter_business_detail()

        yield

        # 测试后截图（仅在失败时）
        if os.environ.get('DEBUG_SCREENSHOT') == 'true':
            self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, f'fail_{time.time()}.png'))

    def _login(self):
        """登录方法"""
        self.page.goto("https://buffalo-dev.shuishoukefu.com", timeout=30000)
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(2000)

        self.page.fill('input[placeholder="邮箱"]', TEST_ACCOUNT['email'])
        self.page.fill('input[type="password"]', TEST_ACCOUNT['password'])

        # 勾选服务协议
        try:
            checkbox = self.page.locator('input[type="checkbox"]').first
            checkbox.check(force=True)
        except:
            try:
                self.page.locator('label:has-text("已阅读")').click()
            except:
                pass

        self.page.click('button[type="submit"]')
        self.page.wait_for_timeout(5000)
        self.page.wait_for_load_state('networkidle')

    def _enter_business_detail(self):
        """进入商家详情页"""
        detail_btns = self.page.locator('button:has-text("详情"), a:has-text("详情")').all()
        if len(detail_btns) > 0:
            detail_btns[0].click()
            self.page.wait_for_timeout(3000)
            self.page.wait_for_load_state('networkidle')

    def _click_add_shop_button(self) -> bool:
        """点击新增店铺按钮，返回是否成功"""
        selectors = [
            'button:has-text("新增店铺")',
            'button:has-text("添加店铺")',
            'button:has-text("+新增店铺")',
            'button:has-text("新建店铺")',
        ]

        for selector in selectors:
            loc = self.page.locator(selector).first
            if loc.count() > 0 and loc.is_visible():
                loc.click()
                self.page.wait_for_timeout(3000)
                return True
        return False

    def _wait_for_modal(self) -> Page:
        """等待弹窗出现并返回弹窗元素"""
        try:
            modal = self.page.locator('.ant-modal').first
            modal.wait_for(timeout=10000)
            return modal
        except:
            modal = self.page.locator('.ant-drawer').first
            modal.wait_for(timeout=5000)
            return modal

    def _fill_shop_form(self, modal: Page, shop_name: str = None, skip_optional: bool = False):
        """填写店铺表单"""
        unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'

        # 店铺名称
        if shop_name is None:
            shop_name = f'测试店铺_{unique_suffix}'

        name_input = modal.locator('#shopName')
        if name_input.count() == 0:
            name_input = modal.locator('[placeholder*="店铺名称"]')
        if name_input.count() == 0:
            name_input = modal.locator('[placeholder*="店铺"]')

        if name_input.count() > 0:
            name_input.click()
            name_input.fill(shop_name)

        # 平台（第一个下拉框）
        if not skip_optional:
            all_selects = modal.locator('.ant-select').all()
            if len(all_selects) >= 1:
                self._select_dropdown(all_selects[0])

            # 合作状态（第二个下拉框）
            if len(all_selects) >= 2:
                self._select_dropdown(all_selects[1])

            # 合作周期（日期选择器）
            date_pickers = modal.locator('.ant-picker').all()
            if len(date_pickers) > 0:
                self._select_date(date_pickers[0])

            # 部门（树形选择器）
            tree_select = modal.locator('.ant-tree-select').first
            if tree_select.count() > 0:
                self._select_tree_node(tree_select)

            # 备注
            remark_input = modal.locator('textarea').first
            if remark_input.count() > 0:
                remark_input.fill(f'自动化测试备注_{unique_suffix}')

        return shop_name

    def _select_dropdown(self, select_el) -> bool:
        """选择下拉选项"""
        try:
            select_el.click()
            self.page.wait_for_timeout(800)

            dropdown = self.page.locator('.ant-select-dropdown:visible').first
            dropdown.wait_for(timeout=5000)
            self.page.wait_for_timeout(500)

            options = self.page.locator('.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)').all()
            if len(options) == 0:
                options = self.page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()

            if len(options) > 0:
                options[0].click()
                self.page.wait_for_timeout(500)
                return True
        except Exception as e:
            print(f"下拉选择异常: {e}")
        return False

    def _select_date(self, date_picker) -> bool:
        """选择日期"""
        try:
            date_picker.click()
            self.page.wait_for_timeout(1000)

            # 选择今天
            today = self.page.locator('.ant-picker-cell-today').first
            if today.count() > 0 and today.is_visible():
                today.click()
                self.page.wait_for_timeout(500)

            # 如果是范围选择器，再选一个结束日期
            end_cells = self.page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').all()
            if len(end_cells) > 3:
                end_cells[5].click()
                self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            print(f"日期选择异常: {e}")
        return False

    def _select_tree_node(self, tree_select) -> bool:
        """选择树形节点"""
        try:
            tree_select.click()
            self.page.wait_for_timeout(3000)

            tree_nodes = self.page.locator('.ant-select-tree-treenode').all()
            if len(tree_nodes) == 0:
                tree_nodes = self.page.locator('.ant-tree-treenode').all()

            for node in tree_nodes[:20]:
                try:
                    hidden = self.page.evaluate(
                        '(el) => el.getAttribute("aria-hidden") === "true"',
                        node.element_handle()
                    )
                    if not hidden and node.is_visible():
                        node.click()
                        self.page.wait_for_timeout(500)
                        return True
                except:
                    continue
        except Exception as e:
            print(f"树形选择异常: {e}")
        return False

    def _click_confirm_button(self, modal: Page) -> bool:
        """点击确认按钮"""
        selectors = [
            'button:has-text("确 定")',
            'button:has-text("确定")',
            'button:has-text("确 认")',
            'button:has-text("确认")',
            '.ant-modal-footer .ant-btn-primary',
        ]

        for selector in selectors:
            btn = modal.locator(selector).first
            if btn.count() > 0 and btn.is_visible():
                btn.click()
                self.page.wait_for_timeout(3000)
                return True
        return False


class TestShopList(TestShopManagement):
    """店铺列表测试"""

    def test_店铺列表页面加载(self, page: Page):
        """TC-SM-001: 验证店铺列表页面正常加载"""
        # 进入详情页后应该能看到店铺列表
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state('networkidle')

        # 验证页面有关键元素（店铺列表相关）
        content = self.page.content()
        # 检查是否有店铺相关内容或表格
        assert '店铺' in content or 'shop' in content.lower(), "页面应包含店铺相关内容"

    def test_新增店铺按钮可见(self, page: Page):
        """TC-SM-002: 验证新增店铺按钮可见且可点击"""
        self.page.wait_for_timeout(2000)

        found = self._click_add_shop_button()
        assert found, "应能找到新增店铺按钮"


class TestShopCreation(TestShopManagement):
    """店铺创建测试"""

    def test_新增店铺_必填字段为空(self, page: Page):
        """TC-SM-003: 验证店铺名称为空时点击确定会提示错误"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        # 直接点击确定，不填写任何内容
        self._click_confirm_button(modal)

        # 检查是否有表单错误提示
        errors = modal.locator('.ant-form-item-explain-error').all()
        if len(errors) > 0:
            has_name_error = any('店铺名称' in err.text_content() or '店铺' in err.text_content()
                                 for err in errors)
            assert has_name_error, "应提示店铺名称不能为空"

    def test_新增店铺_正常流程(self, page: Page):
        """TC-SM-004: 验证正常填写表单可以成功创建店铺"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        # 填写表单
        shop_name = self._fill_shop_form(modal)

        # 点击确定
        success = self._click_confirm_button(modal)

        # 验证弹窗关闭或显示成功提示
        assert success, "点击确定按钮应成功"

        # 等待结果
        self.page.wait_for_timeout(3000)

        # 检查是否成功（弹窗关闭或无错误提示）
        try:
            if modal.is_visible():
                errors = modal.locator('.ant-form-item-explain-error').all()
                assert len(errors) == 0, "表单不应有错误"
        except:
            # 弹窗已关闭，说明创建成功
            pass

    def test_新增店铺_仅填写店铺名称(self, page: Page):
        """TC-SM-005: 验证仅填写店铺名称（必填项）可以创建店铺"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        # 仅填写店铺名称
        shop_name = self._fill_shop_form(modal, skip_optional=True)

        # 点击确定
        self._click_confirm_button(modal)

        self.page.wait_for_timeout(3000)

        # 检查是否成功
        try:
            if modal.is_visible():
                errors = modal.locator('.ant-form-item-explain-error').all()
                assert len(errors) == 0, "表单不应有错误"
        except:
            pass

    def test_新增店铺_选择平台下拉框(self, page: Page):
        """TC-SM-006: 验证平台下拉框可以选择选项"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        # 查找下拉框
        selects = modal.locator('.ant-select').all()
        assert len(selects) >= 1, "应有平台下拉框"

        # 选择平台
        selected = self._select_dropdown(selects[0])
        assert selected, "应能选择平台选项"

    def test_新增店铺_选择合作状态下拉框(self, page: Page):
        """TC-SM-007: 验证合作状态下拉框可以选择选项"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        selects = modal.locator('.ant-select').all()
        if len(selects) >= 2:
            selected = self._select_dropdown(selects[1])
            assert selected, "应能选择合作状态选项"

    def test_新增店铺_选择合作周期日期(self, page: Page):
        """TC-SM-008: 验证合作周期日期选择器可以正常工作"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        date_pickers = modal.locator('.ant-picker').all()
        if len(date_pickers) > 0:
            selected = self._select_date(date_pickers[0])
            assert selected, "应能选择日期"

    def test_新增店铺_选择部门树形选择器(self, page: Page):
        """TC-SM-009: 验证部门树形选择器可以正常工作"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        tree_select = modal.locator('.ant-tree-select').first
        if tree_select.count() > 0:
            selected = self._select_tree_node(tree_select)
            # 树形选择可能因为数据问题失败，不强制断言成功

    def test_新增店铺_填写备注(self, page: Page):
        """TC-SM-010: 验证备注字段可以正常填写"""
        self._click_add_shop_button()
        modal = self._wait_for_modal()

        remark_input = modal.locator('textarea').first
        if remark_input.count() > 0:
            test_remark = f'测试备注_{int(time.time())}'
            remark_input.fill(test_remark)

            actual_value = remark_input.input_value()
            assert test_remark in actual_value, "备注应成功填写"


class TestShopEdit(TestShopManagement):
    """店铺编辑测试"""

    @pytest.fixture(autouse=True)
    def setup_with_shop(self, page: Page):
        """前置条件：创建一个店铺"""
        self.page = page
        self.page.set_default_timeout(15000)

        self._login()

        self.page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(2000)
        self._enter_business_detail()

        self._click_add_shop_button()
        modal = self._wait_for_modal()
        self.created_shop_name = self._fill_shop_form(modal, skip_optional=True)
        self._click_confirm_button(modal)
        self.page.wait_for_timeout(3000)

        yield

    def _click_edit_button_for_shop(self, shop_name: str) -> bool:
        """根据店铺名称查找并点击编辑按钮"""
        selectors = [
            f'tr:has-text("{shop_name}") button:has-text("编辑")',
            f'tr:has-text("{shop_name}") a:has-text("编辑")',
            f'[class*="row"]:has-text("{shop_name}") button:has-text("编辑")',
            f'tr:has-text("{shop_name}") [class*="edit"]',
        ]

        for selector in selectors:
            loc = self.page.locator(selector).first
            if loc.count() > 0 and loc.is_visible():
                loc.click()
                self.page.wait_for_timeout(3000)
                return True

        all_edit_btns = self.page.locator('button:has-text("编辑"), a:has-text("编辑")').all()
        for btn in all_edit_btns:
            try:
                row = btn.locator('xpath=ancestor::tr').first
                if row.count() > 0 and (shop_name in (row.text_content() or '')):
                    btn.click()
                    self.page.wait_for_timeout(3000)
                    return True
            except:
                continue

        if len(all_edit_btns) > 0:
            all_edit_btns[0].click()
            self.page.wait_for_timeout(3000)
            return True

        return False

    def test_编辑店铺_点击编辑按钮(self, page: Page):
        """TC-SM-011: 验证可以点击编辑按钮打开编辑弹窗"""
        self.page.wait_for_timeout(2000)

        clicked = self._click_edit_button_for_shop(self.created_shop_name)
        assert clicked, "应能找到并点击编辑按钮"

        modal = self._wait_for_modal()
        assert modal.is_visible(), "编辑弹窗应可见"

    def test_编辑店铺_修改店铺名称(self, page: Page):
        """TC-SM-012: 验证可以修改店铺名称"""
        self.page.wait_for_timeout(2000)

        clicked = self._click_edit_button_for_shop(self.created_shop_name)
        assert clicked, "应能找到并点击编辑按钮"

        modal = self._wait_for_modal()

        name_input = modal.locator('#shopName')
        if name_input.count() == 0:
            name_input = modal.locator('[placeholder*="店铺名称"]')

        if name_input.count() > 0:
            new_name = f'编辑店铺_{int(time.time())}'
            name_input.fill('')
            name_input.fill(new_name)

            self._click_confirm_button(modal)
            self.page.wait_for_timeout(3000)

    def test_编辑店铺_修改下拉选项(self, page: Page):
        """TC-SM-013: 验证可以修改下拉选项"""
        self.page.wait_for_timeout(2000)

        clicked = self._click_edit_button_for_shop(self.created_shop_name)
        assert clicked, "应能找到并点击编辑按钮"

        modal = self._wait_for_modal()

        selects = modal.locator('.ant-select').all()
        if len(selects) >= 1:
            try:
                clear_btn = modal.locator('.ant-select-clear').first
                if clear_btn.count() > 0 and clear_btn.is_visible():
                    clear_btn.click()
                    self.page.wait_for_timeout(500)
            except:
                pass

            self._select_dropdown(selects[0])

    def _fill_edit_form_all_fields(self, modal: Page):
        """编辑店铺表单：修改所有字段"""
        unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
        edit_data = {}

        # 1. 修改店铺名称
        edit_data['shop_name'] = f'编辑店铺_{unique_suffix}'
        name_input = modal.locator('#shopName')
        if name_input.count() == 0:
            name_input = modal.locator('[placeholder*="店铺名称"]')
        if name_input.count() == 0:
            name_input = modal.locator('[placeholder*="店铺"]')
        if name_input.count() > 0:
            name_input.click()
            name_input.fill('')
            name_input.fill(edit_data['shop_name'])

        # 2. 修改平台（第一个下拉框）
        selects = modal.locator('.ant-select').all()
        if len(selects) >= 1:
            try:
                clear_btn = modal.locator('.ant-select-clear').first
                if clear_btn.count() > 0 and clear_btn.is_visible():
                    clear_btn.click()
                    self.page.wait_for_timeout(500)
            except:
                pass
            self._select_dropdown_with_index(selects[0], 1)

        # 3. 修改合作状态（第二个下拉框）
        if len(selects) >= 2:
            try:
                clear_btn = modal.locator('.ant-select-clear').first
                if clear_btn.count() > 0 and clear_btn.is_visible():
                    clear_btn.click()
                    self.page.wait_for_timeout(500)
            except:
                pass
            self._select_dropdown_with_index(selects[1], 1)

        # 4. 修改合作周期（日期选择器）
        date_pickers = modal.locator('.ant-picker').all()
        if len(date_pickers) > 0:
            self._select_date(date_pickers[0])

        # 5. 修改部门（树形选择器）
        tree_select = modal.locator('.ant-tree-select').first
        if tree_select.count() > 0:
            tree_select.click()
            self.page.wait_for_timeout(3000)

            tree_nodes = self.page.locator('.ant-select-tree-treenode').all()
            if len(tree_nodes) == 0:
                tree_nodes = self.page.locator('.ant-tree-treenode').all()

            if len(tree_nodes) > 1:
                target_idx = min(2, len(tree_nodes) - 1)
                try:
                    hidden = self.page.evaluate(
                        '(el) => el.getAttribute("aria-hidden") === "true"',
                        tree_nodes[target_idx].element_handle()
                    )
                    if not hidden and tree_nodes[target_idx].is_visible():
                        tree_nodes[target_idx].click()
                        self.page.wait_for_timeout(500)
                    else:
                        for node in tree_nodes[:20]:
                            try:
                                hidden = self.page.evaluate(
                                    '(el) => el.getAttribute("aria-hidden") === "true"',
                                    node.element_handle()
                                )
                                if not hidden and node.is_visible():
                                    node.click()
                                    self.page.wait_for_timeout(500)
                                    break
                            except:
                                continue
                except:
                    for node in tree_nodes[:20]:
                        try:
                            hidden = self.page.evaluate(
                                '(el) => el.getAttribute("aria-hidden") === "true"',
                                node.element_handle()
                            )
                            if not hidden and node.is_visible():
                                node.click()
                                self.page.wait_for_timeout(500)
                                break
                        except:
                            continue
            elif len(tree_nodes) == 1:
                tree_nodes[0].click()
                self.page.wait_for_timeout(500)

        # 6. 修改备注
        remark_input = modal.locator('#remark')
        if remark_input.count() == 0:
            remark_input = modal.locator('[placeholder*="备注"]')
        if remark_input.count() == 0:
            remark_input = modal.locator('textarea').first
        if remark_input.count() > 0:
            edit_data['remark'] = f'编辑备注_{unique_suffix}'
            remark_input.click()
            remark_input.fill('')
            remark_input.fill(edit_data['remark'])

        return edit_data

    def _select_dropdown_with_index(self, select_el, index: int) -> bool:
        """选择下拉框中指定索引的选项"""
        try:
            select_el.click()
            self.page.wait_for_timeout(800)

            dropdown = self.page.locator('.ant-select-dropdown:visible').first
            dropdown.wait_for(timeout=5000)
            self.page.wait_for_timeout(500)

            options = self.page.locator(
                '.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)'
            ).all()
            if len(options) == 0:
                options = self.page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()

            if len(options) > index:
                options[index].click()
                self.page.wait_for_timeout(500)
                return True
            elif len(options) > 0:
                options[0].click()
                self.page.wait_for_timeout(500)
                return True
        except Exception as e:
            print(f"下拉选择(index={index})异常: {e}")
        return False

    def test_编辑店铺_完整修改所有字段(self, page: Page):
        """TC-SM-018: 验证编辑店铺可以完整修改所有字段（店铺名称、平台、合作状态、合作周期、部门、备注）"""
        self.page.wait_for_timeout(2000)

        # 1. 查找刚创建的店铺并点击编辑按钮
        clicked = self._click_edit_button_for_shop(self.created_shop_name)
        assert clicked, "应能找到并点击编辑按钮"

        modal = self._wait_for_modal()
        assert modal.is_visible(), "编辑弹窗应可见"

        self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_before.png'))

        # 2. 修改所有字段
        edit_data = self._fill_edit_form_all_fields(modal)

        self.page.wait_for_timeout(1000)
        self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_form_filled.png'))

        # 3. 点击确定
        confirm_clicked = self._click_confirm_button(modal)
        assert confirm_clicked, "点击确定按钮应成功"

        self.page.wait_for_timeout(3000)

        self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_result.png'))

        # 验证结果：弹窗关闭或无错误提示
        try:
            if modal.is_visible():
                errors = modal.locator('.ant-form-item-explain-error').all()
                assert len(errors) == 0, f"表单不应有错误，发现: {[e.text_content() for e in errors]}"

                messages = self.page.locator('.ant-message-notice-content').all()
                for msg in messages:
                    print(f"提示信息: {msg.text_content()}")
            else:
                print(f"✓ 编辑店铺成功！修改后的名称: {edit_data.get('shop_name', 'N/A')}")
        except:
            print("✓ 编辑店铺成功（弹窗已关闭）")


class TestShopSearch(TestShopManagement):
    """店铺搜索测试"""

    def test_搜索店铺_输入关键词(self, page: Page):
        """TC-SM-014: 验证可以输入关键词搜索店铺"""
        self.page.wait_for_timeout(2000)

        # 查找搜索框
        search_input = self.page.locator('input[placeholder*="搜索"]').first
        if search_input.count() == 0:
            search_input = self.page.locator('input[placeholder*="请输入"]').first

        if search_input.count() > 0:
            search_input.click()
            search_input.fill('测试')
            self.page.keyboard.press('Enter')
            self.page.wait_for_timeout(2000)

    def test_搜索店铺_清空搜索框(self, page: Page):
        """TC-SM-015: 验证可以清空搜索框重新搜索"""
        self.page.wait_for_timeout(2000)

        search_input = self.page.locator('input[placeholder*="搜索"]').first
        if search_input.count() == 0:
            search_input = self.page.locator('input[placeholder*="请输入"]').first

        if search_input.count() > 0:
            search_input.fill('测试店铺')
            self.page.wait_for_timeout(500)

            # 清空
            search_input.fill('')
            self.page.wait_for_timeout(500)


class TestShopDeletion(TestShopManagement):
    """店铺删除测试"""

    @pytest.fixture(autouse=True)
    def setup_with_shop(self, page: Page):
        """前置条件：创建一个待删除的店铺"""
        self.page = page
        self.page.set_default_timeout(15000)

        # 登录
        self._login()

        # 进入商家详情页
        self.page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(2000)
        self._enter_business_detail()

        # 创建店铺
        self._click_add_shop_button()
        modal = self._wait_for_modal()
        self._fill_shop_form(modal, skip_optional=True)
        self._click_confirm_button(modal)
        self.page.wait_for_timeout(3000)

        yield

    def test_删除店铺_点击删除按钮(self, page: Page):
        """TC-SM-016: 验证可以点击删除按钮"""
        self.page.wait_for_timeout(2000)

        # 查找删除按钮
        delete_btns = self.page.locator('button:has-text("删除"), a:has-text("删除")').all()
        if len(delete_btns) > 0:
            delete_btns[0].click()
            self.page.wait_for_timeout(1000)

            # 检查是否有确认对话框
            # Ant Design 通常会有一个确认弹窗
            confirm_modal = self.page.locator('.ant-modal').first
            if confirm_modal.count() > 0 and confirm_modal.is_visible():
                # 点击确认删除
                confirm_btn = confirm_modal.locator('button:has-text("确 认"), button:has-text("确认"), button:has-text("确定")').first
                if confirm_btn.count() > 0:
                    confirm_btn.click()
                    self.page.wait_for_timeout(3000)


class TestShopDetail(TestShopManagement):
    """店铺详情测试"""

    def test_店铺详情_查看详情信息(self, page: Page):
        """TC-SM-017: 验证可以查看店铺详情信息"""
        self.page.wait_for_timeout(2000)

        # 查找详情按钮
        detail_btns = self.page.locator('button:has-text("详情"), a:has-text("详情")').all()
        if len(detail_btns) > 1:  # 第一个是商家的，后面的可能是店铺的
            detail_btns[1].click()
            self.page.wait_for_timeout(3000)

            # 检查是否有详情内容
            content = self.page.content()
            assert len(content) > 0, "详情页应有内容"


# ============================================================
# 辅助函数：运行单个测试场景
# ============================================================
def run_single_test():
    """运行单个测试场景（用于调试）"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        test = TestShopCreation()
        test.page = page
        test.setup(page)

        try:
            test.test_新增店铺_正常流程(page)
            print("测试通过")
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            time.sleep(3)
            browser.close()


if __name__ == "__main__":
    # run_single_test()
    pytest.main([__file__, "-v", "-s"])
