"""使用 Google Chrome 浏览器执行店铺编辑全流程测试"""
from playwright.sync_api import sync_playwright
import time
import random
import os

SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_ACCOUNT = {
    'email': 'wanglan1@shuishoukefu.com',
    'password': '123'
}


def run_chrome_test():
    with sync_playwright() as p:
        # 使用系统安装的 Google Chrome
        browser = p.chromium.launch(
            channel='chrome',      # 使用 Google Chrome
            headless=False,        # 有界面模式
            slow_mo=500            # 减慢操作速度，便于观察
        )
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        page.set_default_timeout(20000)

        try:
            # ============================================================
            # 1. 登录系统
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤1: 登录系统")
            print("=" * 70)
            page.goto("https://buffalo-dev.shuishoukefu.com", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            print(f"   已访问登录页: {page.url}")

            page.fill('input[placeholder="邮箱"]', TEST_ACCOUNT['email'])
            page.fill('input[type="password"]', TEST_ACCOUNT['password'])

            try:
                checkbox = page.locator('input[type="checkbox"]').first
                checkbox.check(force=True)
                print("   ✓ 已勾选服务协议")
            except:
                try:
                    page.locator('label:has-text("已阅读")').click()
                    print("   ✓ 已勾选服务协议(通过label)")
                except:
                    print("   ⚠️ 无需勾选协议")

            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            page.wait_for_load_state('networkidle')
            print(f"   ✓ 登录成功: {page.url}")

            # ============================================================
            # 2. 导航到商家管理页面
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤2: 导航到商家管理页面")
            print("=" * 70)
            page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_business_page.png'))
            print("   ✓ 已到达商家管理页面")

            # ============================================================
            # 3. 进入第一个商家的详情页
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤3: 进入商家详情页（查看已有店铺）")
            print("=" * 70)

            detail_btns = page.locator('button:has-text("详情"), a:has-text("详情")').all()
            if len(detail_btns) == 0:
                print("   ✗ 未找到详情按钮，请检查页面")
                return

            detail_btns[0].click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle')
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_shop_list.png'))
            print(f"   ✓ 已进入商家详情页，找到 {len(detail_btns)} 个详情按钮")

            # ============================================================
            # 4. 查找并点击编辑按钮
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤4: 查找店铺并点击编辑按钮")
            print("=" * 70)

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle')

            # 延长时间等待店铺列表完全加载
            page.wait_for_timeout(3000)

            # 调试截图
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_debug_page.png'))
            print("   已保存调试截图: chrome_debug_page.png")

            # 获取当前页面标题和URL
            print(f"   当前URL: {page.url}")
            print(f"   页面标题: {page.title()}")

            # 调试：打印页面中所有可见按钮
            all_btns = page.locator('button:visible').all()
            print(f"   页面可见按钮数: {len(all_btns)}")
            for i, btn in enumerate(all_btns[:30]):
                try:
                    txt = btn.text_content()
                    enabled = btn.is_enabled()
                    print(f"   按钮[{i}]: '{txt}' enabled={enabled}")
                except:
                    pass

            # 查找包含"编辑"的按钮（更宽松的匹配）
            edit_btn = None

            # 方式1: 精确匹配
            edit_btns = page.locator('button:text("编辑")').all()
            print(f"   精确匹配'编辑'按钮: {len(edit_btns)} 个")
            edit_btns = page.locator('button:text-is("编辑")').all()
            print(f"   完全匹配'编辑'按钮: {len(edit_btns)} 个")

            # 方式2: 使用正则或包含匹配
            edit_btns = page.locator('button:has-text("编辑")').all()
            print(f"   包含'编辑'按钮: {len(edit_btns)} 个")
            for i, btn in enumerate(edit_btns):
                try:
                    txt = btn.text_content()
                    print(f"   编辑按钮[{i}]: '{txt}'")
                    try:
                        if btn.is_enabled():
                            print(f"     -> 可用，尝试点击")
                            edit_btn = btn
                            break
                    except:
                        # 如果检查状态失败，尝试直接点击
                        print(f"     -> 状态检查失败，尝试点击")
                        edit_btn = btn
                        break
                except:
                    pass

            # 方式3: 查找表格中操作列的button
            if edit_btn is None:
                rows = page.locator('table tbody tr').all()
                print(f"   表格行数: {len(rows)}")
                for ri, row in enumerate(rows[:10]):
                    row_text = row.text_content()
                    if row_text and '编辑' in row_text:
                        print(f"   行[{ri}] 包含'编辑': {row_text[:80]}")
                        btns_in_row = row.locator('button').all()
                        for bi, b in enumerate(btns_in_row):
                            bt = b.text_content()
                            print(f"     按钮[{bi}]: '{bt}'")
                            if bt and '编辑' in bt:
                                edit_btn = b

            # 方式4: 在页面中搜索包含编辑的链接或span
            if edit_btn is None:
                edit_links = page.locator('a:has-text("编辑"), span:has-text("编辑")').all()
                print(f"   编辑链接/span: {len(edit_links)} 个")
                for el in edit_links:
                    try:
                        txt = el.text_content()
                        print(f"     '{txt}'")
                        el.click()
                        page.wait_for_timeout(3000)
                        # 检查是否出现了弹窗
                        modal_check = page.locator('.ant-modal').first
                        if modal_check.count() > 0 and modal_check.is_visible():
                            edit_btn = el
                            break
                        drawer_check = page.locator('.ant-drawer').first
                        if drawer_check.count() > 0 and drawer_check.is_visible():
                            edit_btn = el
                            break
                        print(f"     点击后未出现弹窗")
                    except:
                        pass

            if edit_btn is None:
                print("   ✗ 未找到可用的编辑按钮")
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_no_edit_btn.png'))
                return

            # 如果还没点击，尝试点击
            try:
                edit_btn.click()
            except:
                pass
            page.wait_for_timeout(3000)
            print("   ✓ 已点击编辑按钮")

            # ============================================================
            # 5. 等待编辑弹窗出现
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤5: 等待编辑弹窗出现")
            print("=" * 70)

            try:
                edit_modal = page.locator('.ant-modal').first
                edit_modal.wait_for(timeout=10000)
                print("   ✓ 编辑弹窗（Modal）已出现")
            except:
                edit_modal = page.locator('.ant-drawer').first
                edit_modal.wait_for(timeout=5000)
                print("   ✓ 编辑弹窗（Drawer）已出现")

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_edit_before.png'))
            print("   ✓ 已保存编辑前截图: chrome_edit_before.png")

            # 查看弹窗中的表单元素
            all_inputs = edit_modal.locator('input:visible').all()
            all_selects = edit_modal.locator('.ant-select').all()
            all_textareas = edit_modal.locator('textarea').all()
            date_pickers = edit_modal.locator('.ant-picker').all()
            tree_select = edit_modal.locator('.ant-tree-select').first

            print(f"\n   弹窗内表单元素:")
            print(f"     input 输入框: {len(all_inputs)} 个")
            print(f"     下拉选择器: {len(all_selects)} 个")
            for i, s in enumerate(all_selects):
                try:
                    text = s.text_content()
                    print(f"       下拉{i}: {text[:40] if text else ''}")
                except:
                    pass
            print(f"     textarea: {len(all_textareas)} 个")
            print(f"     日期选择器: {len(date_pickers)} 个")
            print(f"     树形选择器: {'✅ 存在' if tree_select.count() > 0 else '❌ 不存在'}")

            # ============================================================
            # 6. 修改店铺名称
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤6: 修改店铺名称")
            print("=" * 70)

            unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
            new_shop_name = f'Chrome编辑店铺_{unique_suffix}'

            name_input = edit_modal.locator('#shopName')
            if name_input.count() == 0:
                name_input = edit_modal.locator('[placeholder*="店铺名称"]')
            if name_input.count() == 0:
                name_input = edit_modal.locator('[placeholder*="店铺"]')

            if name_input.count() > 0:
                old_name = name_input.input_value()
                name_input.click()
                name_input.fill('')
                name_input.fill(new_shop_name)
                print(f"   ✓ 名称: {old_name or '(空)'} → {new_shop_name}")
            else:
                print("   ✗ 未找到店铺名称输入框")

            # ============================================================
            # 7. 修改平台（下拉选择）
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤7: 修改平台（下拉选择）")
            print("=" * 70)

            def select_dropdown(select_el, label, index=0):
                try:
                    # 尝试清除当前选择
                    try:
                        clear_btn = select_el.locator('.ant-select-clear').first
                        if clear_btn.count() > 0 and clear_btn.is_visible():
                            clear_btn.click()
                            page.wait_for_timeout(500)
                            print(f"    已清除{label}当前选择")
                    except:
                        pass

                    select_el.click()
                    page.wait_for_timeout(800)

                    dropdown = page.locator('.ant-select-dropdown:visible').first
                    dropdown.wait_for(timeout=5000)
                    page.wait_for_timeout(500)

                    options = page.locator(
                        '.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)'
                    ).all()
                    if len(options) == 0:
                        options = page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()

                    if len(options) > 0:
                        idx = min(index, len(options) - 1)
                        option_text = options[idx].text_content()
                        options[idx].click()
                        page.wait_for_timeout(500)
                        print(f"   ✓ {label}: {option_text}")
                        return True
                    else:
                        print(f"   ⚠️ {label}: 无可用选项")
                        return False
                except Exception as e:
                    print(f"   ✗ {label}选择异常: {e}")
                    return False

            if len(all_selects) >= 1:
                select_dropdown(all_selects[0], "平台", index=1)

            # ============================================================
            # 8. 修改合作状态（下拉选择）
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤8: 修改合作状态（下拉选择）")
            print("=" * 70)

            if len(all_selects) >= 2:
                select_dropdown(all_selects[1], "合作状态", index=1)

            # ============================================================
            # 9. 修改合作周期（日期选择）
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤9: 修改合作周期（日期选择）")
            print("=" * 70)

            if len(date_pickers) > 0:
                try:
                    date_pickers[0].click()
                    page.wait_for_timeout(1000)

                    today = page.locator('.ant-picker-cell-today').first
                    if today.count() > 0 and today.is_visible():
                        today_text = today.get_attribute('title') or '今天'
                        today.click()
                        page.wait_for_timeout(500)

                        end_cells = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').all()
                        if len(end_cells) > 3:
                            end_idx = min(5, len(end_cells) - 1)
                            end_text = end_cells[end_idx].get_attribute('title') or ''
                            end_cells[end_idx].click()
                            page.wait_for_timeout(500)
                            print(f"   ✓ 合作周期: {today_text} → {end_text}")
                        else:
                            print(f"   ✓ 开始日期: {today_text}")
                    else:
                        print("   ⚠️ 未找到今日日期，尝试选择第一个可用日期")
                        first_cell = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').first
                        if first_cell.count() > 0:
                            first_cell.click()
                            page.wait_for_timeout(500)
                            print("   ✓ 已选择日期")
                except Exception as e:
                    print(f"   ✗ 日期选择异常: {e}")
            else:
                print("   ⚠️ 未找到日期选择器")

            # ============================================================
            # 10. 修改部门（树形选择）
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤10: 修改部门（树形选择）")
            print("=" * 70)

            if tree_select.count() > 0:
                try:
                    tree_select.click()
                    page.wait_for_timeout(3000)

                    tree_nodes = page.locator('.ant-select-tree-treenode').all()
                    if len(tree_nodes) == 0:
                        tree_nodes = page.locator('.ant-tree-treenode').all()

                    print(f"   树形节点数: {len(tree_nodes)}")

                    if len(tree_nodes) > 1:
                        target_idx = min(2, len(tree_nodes) - 1)
                        node_text = tree_nodes[target_idx].text_content()
                        tree_nodes[target_idx].click()
                        page.wait_for_timeout(500)
                        print(f"   ✓ 部门: {node_text}")
                    elif len(tree_nodes) == 1:
                        node_text = tree_nodes[0].text_content()
                        tree_nodes[0].click()
                        page.wait_for_timeout(500)
                        print(f"   ✓ 部门: {node_text}")
                    else:
                        print("   ⚠️ 无树形节点可选")
                except Exception as e:
                    print(f"   ✗ 树形选择异常: {e}")
            else:
                print("   ⚠️ 未找到部门树形选择器")

            # ============================================================
            # 11. 修改备注
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤11: 修改备注")
            print("=" * 70)

            remark_input = edit_modal.locator('#remark')
            if remark_input.count() == 0:
                remark_input = edit_modal.locator('[placeholder*="备注"]')
            if remark_input.count() == 0:
                remark_input = edit_modal.locator('textarea').first

            if remark_input.count() > 0:
                new_remark = f'Chrome自动化编辑备注_{unique_suffix}'
                remark_input.click()
                remark_input.fill('')
                remark_input.fill(new_remark)
                print(f"   ✓ 备注: {new_remark}")
            else:
                print("   ⚠️ 未找到备注输入框")

            # 填写完成截图
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_edit_filled.png'))
            print("\n   ✓ 已保存填写后截图: chrome_edit_filled.png")

            # ============================================================
            # 12. 点击确定按钮
            # ============================================================
            print("\n" + "=" * 70)
            print("📌 步骤12: 点击确定按钮")
            print("=" * 70)

            confirm_selectors = [
                'button:has-text("确 定")',
                'button:has-text("确定")',
                'button:has-text("确 认")',
                'button:has-text("确认")',
                '.ant-modal-footer .ant-btn-primary',
            ]

            confirm_btn = None
            for selector in confirm_selectors:
                btn = edit_modal.locator(selector).first
                if btn.count() > 0 and btn.is_visible():
                    confirm_btn = btn
                    print(f"   使用选择器: {selector}")
                    break

            if confirm_btn:
                confirm_btn.click()
                print("   ✓ 已点击确定按钮，等待结果...")
                page.wait_for_timeout(3000)

                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_edit_result.png'))
                print("   ✓ 已保存结果截图: chrome_edit_result.png")

                # 验证结果
                try:
                    if edit_modal.is_visible():
                        errors = edit_modal.locator('.ant-form-item-explain-error').all()
                        if len(errors) > 0:
                            print("\n   ⚠️ 表单验证错误:")
                            for err in errors:
                                print(f"     ✗ {err.text_content()}")
                        else:
                            print("\n   ⚠️ 弹窗仍在，查看提示信息:")
                            messages = page.locator('.ant-message-notice-content').all()
                            for msg in messages:
                                print(f"     📢 {msg.text_content()}")
                    else:
                        print("\n   🎉 ✅✅✅ 编辑店铺成功！弹窗已关闭 ✅✅✅")
                except:
                    print("\n   🎉 ✅✅✅ 编辑店铺成功！弹窗已关闭 ✅✅✅")
            else:
                print("   ✗ 未找到确定按钮")

            # ============================================================
            # 完成
            # ============================================================
            print("\n" + "=" * 70)
            print(f"🏁 测试完成！已保存以下截图:")
            print("=" * 70)
            screenshots = [
                'chrome_business_page.png',
                'chrome_shop_list.png',
                'chrome_edit_before.png',
                'chrome_edit_filled.png',
                'chrome_edit_result.png',
            ]
            for s in screenshots:
                path = os.path.join(SCREENSHOT_DIR, s)
                if os.path.exists(path):
                    print(f"   ✅ {s}")
                else:
                    print(f"   ❌ {s} (未生成)")

            print(f"\n修改后的店铺名称: {new_shop_name}")

        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'chrome_error.png'))
                print("   错误截图已保存: chrome_error.png")
            except:
                pass

        finally:
            print("\n浏览器将在5秒后自动关闭...")
            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 使用 Google Chrome 浏览器执行店铺编辑全流程测试")
    print("=" * 70)
    run_chrome_test()
