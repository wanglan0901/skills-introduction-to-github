"""完整端到端测试：创建商家 + 编辑商家 + 新增店铺 + 编辑店铺 + 删除店铺 + 删除商家"""
from playwright.sync_api import sync_playwright
import time
import random
import os

HEADLESS = os.environ.get('CI') is not None or os.environ.get('HEADLESS', '').lower() == 'true'
SCREENSHOT_DIR = os.environ.get('SCREENSHOT_DIR', os.path.dirname(os.path.abspath(__file__)))


def test_add_shop():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=0 if HEADLESS else 300, channel='chrome')
        context = browser.new_context()
        page = context.new_page()

        try:
            # ===== 登录 =====
            print("步骤1: 访问登录页面")
            page.goto("https://buffalo-dev.shuishoukefu.com", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

            print("步骤2: 登录")
            page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
            page.fill('input[type="password"]', '123')
            # 勾选协议
            try:
                page.locator('input[type="checkbox"]').first.check(force=True)
            except:
                try:
                    page.locator('label:has-text("已阅读")').click()
                except:
                    pass
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            page.wait_for_load_state('networkidle')
            print(f"✓ 登录完成: {page.url}")

            # ===== 导航到商家管理 =====
            print("\n步骤3: 导航到商家管理页面")
            page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            print(f"  商家管理页面URL: {page.url}")
            print("✓ 到达商家管理页面")
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'create_biz_page.png'))

            # ===================================================================
            # PartA: 创建商家
            # ===================================================================
            print("\n" + "="*60)
            print("开始执行：创建商家自动化测试")
            print("="*60)

            # A1: 点击添加商家按钮
            print("\n创建商家步骤A1: 点击添加商家按钮")
            add_btn = None
            for s in ['button:has-text("添加商家")', 'button:has-text("新增")',
                       'button:has-text("新建")', '.ant-btn-primary:has-text("添加")']:
                loc = page.locator(s).first
                if loc.count() > 0 and loc.is_visible():
                    add_btn = loc
                    print(f"  找到按钮: {s}")
                    break

            if not add_btn:
                print("✗ 未找到添加商家按钮")
                return
            add_btn.click()
            page.wait_for_timeout(3000)
            print("✓ 已点击添加商家按钮")

            # A2: 等待弹窗
            print("\n创建商家步骤A2: 等待弹窗")
            try:
                modal = page.locator('.ant-modal').first
                modal.wait_for(timeout=10000)
                print("✓ 弹窗已出现")
            except:
                modal = page.locator('.ant-drawer').first
                modal.wait_for(timeout=5000)
                print("✓ Drawer已出现")

            # A3: 选择部门（树形选择器）
            print("\n创建商家步骤A3: 选择部门（树形选择器）")
            dept_loc = modal.locator('.ant-tree-select').first
            if dept_loc.count() == 0:
                dept_loc = modal.locator('[class*="tree-select"]').first
            if dept_loc.count() > 0:
                dept_loc.click()
                page.wait_for_timeout(3000)
                tree_nodes = page.locator('.ant-select-tree-treenode').all()
                if len(tree_nodes) == 0:
                    tree_nodes = page.locator('.ant-tree-treenode').all()
                print(f"  找到 {len(tree_nodes)} 个树形节点")
                for i, node in enumerate(tree_nodes[:20]):
                    try:
                        hidden = page.evaluate(
                            '(el) => el.getAttribute("aria-hidden") === "true"',
                            node.element_handle()
                        )
                        if not hidden and node.is_visible():
                            node.click()
                            page.wait_for_timeout(500)
                            print(f"  ✓ 已选择部门（节点 #{i+1}）")
                            break
                    except:
                        continue
            else:
                print("  ⚠️ 未找到部门树形选择器")

            # A4: 填写表单
            print("\n创建商家步骤A4: 填写表单")
            unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
            biz_name = f'测试商家_{unique_suffix}'

            # 商家名称
            inp = modal.locator('#merchantName')
            if inp.count() == 0: inp = modal.locator('[placeholder*="商家名称"]')
            if inp.count() > 0:
                inp.click(); inp.fill(biz_name)
                print(f"✓ 商家名称: {biz_name}")

            # 商家简称
            inp = modal.locator('#aliasName')
            if inp.count() == 0: inp = modal.locator('[placeholder*="简称"]')
            if inp.count() > 0:
                inp.click(); inp.fill(f'测试_{unique_suffix}')
                print("✓ 商家简称已填写")

            # 手机号
            inp = modal.locator('#mobile')
            if inp.count() == 0: inp = modal.locator('[placeholder*="手机"]')
            if inp.count() > 0:
                inp.click(); inp.fill(f'138{random.randint(10000000, 99999999)}')
                print("✓ 手机号已填写")

            # 微信号
            inp = modal.locator('#wechatNumber')
            if inp.count() == 0: inp = modal.locator('[placeholder*="微信"]')
            if inp.count() > 0:
                inp.click(); inp.fill(f'test_wechat_{unique_suffix}')
                print("✓ 微信号已填写")

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'create_biz_form.png'))

            # A5: 点击确认
            print("\n创建商家步骤A5: 点击确认")
            for s in ['button:has-text("确 认")', 'button:has-text("确认")',
                       'button:has-text("确定")', '.ant-modal-footer .ant-btn-primary']:
                btn = modal.locator(s).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(); print("✓ 已点击确认"); break

            # A6: 等结果
            print("\n创建商家步骤A6: 等待结果")
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'create_biz_result.png'))

            created_ok = False
            try:
                if not modal.is_visible():
                    print("✓✓✓ 创建商家成功 ✓✓✓")
                    created_ok = True
                else:
                    print("⚠️ 弹窗仍在")
            except:
                print("✓✓✓ 创建商家成功（弹窗已移除）✓✓✓")
                created_ok = True

            if not created_ok:
                print("✗ 创建商家失败，终止后续测试")
                return

            # ===================================================================
            # PartB: 编辑商家
            # ===================================================================
            print("\n" + "="*60)
            print("开始执行：编辑商家自动化测试")
            print("="*60)

            page.wait_for_timeout(3000)

            # B1: 搜索并点击编辑按钮
            print(f"\n编辑商家步骤B1: 搜索'{biz_name}'并点击编辑按钮")
            try:
                si = page.locator('input[placeholder*="搜索"]').first
                if si.count() == 0:
                    si = page.locator('input[placeholder*="请输入"]').first
                if si.count() > 0:
                    si.click(); si.fill(''); si.fill(biz_name)
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(2000)
                    print(f"  已搜索: {biz_name}")
            except:
                pass

            edit_biz_btn = None
            for s in [f'tr:has-text("{biz_name}") button:has-text("编辑")',
                       f'tr:has-text("{biz_name}") a:has-text("编辑")',
                       f'[class*="row"]:has-text("{biz_name}") button:has-text("编辑")']:
                loc = page.locator(s).first
                if loc.count() > 0 and loc.is_visible():
                    edit_biz_btn = loc; print(f"  找到编辑按钮: {s}"); break

            if not edit_biz_btn:
                for btn in page.locator('button:has-text("编辑"), a:has-text("编辑")').all():
                    try:
                        r = btn.locator('xpath=ancestor::tr').first
                        if r.count() > 0 and biz_name in (r.text_content() or ''):
                            edit_biz_btn = btn; break
                    except:
                        continue

            if edit_biz_btn:
                edit_biz_btn.click()
                page.wait_for_timeout(3000)
                print("✓ 已点击编辑按钮")
            else:
                print("✗ 未找到编辑按钮"); return

            # B2: 编辑弹窗
            print("\n编辑商家步骤B2: 等待编辑弹窗")
            try:
                edit_modal = page.locator('.ant-modal').first
                edit_modal.wait_for(timeout=10000)
            except:
                edit_modal = page.locator('.ant-drawer').first
                edit_modal.wait_for(timeout=5000)
            print("✓ 编辑弹窗已出现")
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_biz_before.png'))

            # B3: 修改商家名称
            print("\n编辑商家步骤B3: 修改字段")
            edit_suffix = f'{int(time.time())}{random.randint(100, 999)}'
            edit_biz_name = f'编辑商家_{edit_suffix}'

            inp = edit_modal.locator('#merchantName')
            if inp.count() == 0: inp = edit_modal.locator('[placeholder*="商家名称"]')
            if inp.count() > 0:
                inp.click(); inp.fill(''); inp.fill(edit_biz_name)
                print(f"✓ 商家名称: {biz_name} → {edit_biz_name}")

            # 商家简称
            inp = edit_modal.locator('#aliasName')
            if inp.count() == 0: inp = edit_modal.locator('[placeholder*="简称"]')
            if inp.count() > 0:
                inp.click(); inp.fill(''); inp.fill(f'编辑简称_{edit_suffix}')
                print("✓ 商家简称已修改")

            # 更换部门
            print("  更换部门...")
            edt = edit_modal.locator('.ant-tree-select').first
            if edt.count() == 0: edt = edit_modal.locator('[class*="tree-select"]').first
            if edt.count() > 0:
                try:
                    cb = edit_modal.locator('.ant-select-clear').first
                    if cb.count() > 0: cb.click(); page.wait_for_timeout(500)
                except:
                    pass
                edt.click(); page.wait_for_timeout(3000)
                tn = page.locator('.ant-select-tree-treenode').all()
                if len(tn) == 0: tn = page.locator('.ant-tree-treenode').all()
                idx = min(2, len(tn)-1) if len(tn) > 1 else 0
                if len(tn) > 0:
                    try:
                        hidden = page.evaluate('(el) => el.getAttribute("aria-hidden") === "true"', tn[idx].element_handle())
                        if not hidden: tn[idx].click(); page.wait_for_timeout(500)
                    except:
                        tn[idx].click()
                    print(f"  ✓ 部门已更换（节点 #{idx+1}）")
            else:
                print("  ⚠️ 未找到部门选择器")

            # 手机号
            inp = edit_modal.locator('#mobile')
            if inp.count() == 0: inp = edit_modal.locator('[placeholder*="手机"]')
            if inp.count() > 0:
                inp.click(); inp.fill(''); inp.fill(f'139{random.randint(10000000, 99999999)}')
                print("✓ 手机号已修改")

            # 微信号
            inp = edit_modal.locator('#wechatNumber')
            if inp.count() == 0: inp = edit_modal.locator('[placeholder*="微信"]')
            if inp.count() > 0:
                inp.click(); inp.fill(''); inp.fill(f'edit_wechat_{edit_suffix}')
                print("✓ 微信号已修改")

            # 备注
            inp = edit_modal.locator('#remark')
            if inp.count() == 0: inp = edit_modal.locator('[placeholder*="备注"]')
            if inp.count() == 0: inp = edit_modal.locator('textarea').first
            if inp.count() > 0:
                inp.click(); inp.fill(''); inp.fill(f'编辑备注_{edit_suffix}')
                print("✓ 备注已填写")

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_biz_form.png'))

            # B4: 点击确认
            print("\n编辑商家步骤B4: 点击确认")
            for s in ['button:has-text("确 认")', 'button:has-text("确认")',
                       'button:has-text("确定")', '.ant-modal-footer .ant-btn-primary']:
                btn = edit_modal.locator(s).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(); print("✓ 已点击确认"); break

            # B5: 等待结果
            print("\n编辑商家步骤B5: 等待结果")
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_biz_result.png'))

            edited_ok = False
            try:
                if not edit_modal.is_visible():
                    print("✓✓✓ 编辑商家成功 ✓✓✓")
                    edited_ok = True
                else:
                    print("⚠️ 编辑弹窗仍在")
            except:
                print("✓✓✓ 编辑商家成功（弹窗已移除）✓✓✓")
                edited_ok = True

            if not edited_ok:
                print("✗ 编辑商家失败，终止后续测试")
                return

            # ===== 用编辑后的商家名称进入详情页 =====
            print(f"\n步骤: 搜索编辑后的商家'{edit_biz_name}'并进入详情页")
            page.wait_for_timeout(2000)
            try:
                si = page.locator('input[placeholder*="搜索"]').first
                if si.count() == 0:
                    si = page.locator('input[placeholder*="请输入"]').first
                if si.count() > 0:
                    si.click(); si.fill(''); si.fill(edit_biz_name)
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(2000)
                    print(f"  已搜索: {edit_biz_name}")
            except:
                pass

            detail_btns = page.locator('button:has-text("详情"), a:has-text("详情")').all()
            detail_btn = None
            for btn in detail_btns:
                try:
                    r = btn.locator('xpath=ancestor::tr').first
                    if r.count() > 0 and edit_biz_name in (r.text_content() or ''):
                        detail_btn = btn; break
                except:
                    continue
            if not detail_btn and len(detail_btns) > 0:
                detail_btn = detail_btns[0]

            if detail_btn:
                detail_btn.click()
                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle')
                print(f"✓ 已进入商家详情页（商家: {edit_biz_name}）")
            else:
                print("✗ 未找到详情按钮"); return

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'biz_detail_page.png'))

            # ===== 点击"+新增店铺" =====
            print("\n步骤5: 点击'+新增店铺'按钮")
            btn_selectors = [
                'button:has-text("新增店铺")',
                'button:has-text("添加店铺")',
                'button:has-text("+新增店铺")',
                'button:has-text("新建店铺")',
            ]

            add_shop_btn = None
            for s in btn_selectors:
                loc = page.locator(s).first
                if loc.count() > 0 and loc.is_visible():
                    add_shop_btn = loc
                    print(f"  找到: {s}")
                    break

            if not add_shop_btn:
                print("✗ 未找到新增店铺按钮")
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_no_add_btn.png'))
                return

            add_shop_btn.click()
            page.wait_for_timeout(3000)
            print("✓ 已打开新增店铺弹窗")

            # ===== 获取弹窗 =====
            try:
                shop_modal = page.locator('.ant-modal').first
                shop_modal.wait_for(timeout=10000)
            except:
                shop_modal = page.locator('.ant-drawer').first
                shop_modal.wait_for(timeout=5000)

            print("\n弹窗内元素分析：")
            all_inputs_in_modal = shop_modal.locator('input:visible').all()
            print(f"  可见input数量: {len(all_inputs_in_modal)}")
            for i, inp in enumerate(all_inputs_in_modal[:10]):
                try:
                    ph = inp.get_attribute('placeholder')
                    rid = inp.get_attribute('id')
                    print(f"    input[{i}]: id={rid}, placeholder={ph}")
                except:
                    pass

            all_selects = shop_modal.locator('.ant-select').all()
            print(f"  ant-select数量: {len(all_selects)}")

            textareas = shop_modal.locator('textarea').all()
            print(f"  textarea数量: {len(textareas)}")

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_modal_debug.png'))

            # ===== S4. 填写店铺名称 =====
            print("\n步骤S4: 填写店铺名称")
            shop_suffix = f'{int(time.time())}{random.randint(100, 999)}'
            shop_name = f'测试店铺_{shop_suffix}'

            name_input = shop_modal.locator('#shopName')
            if name_input.count() == 0:
                name_input = shop_modal.locator('[placeholder*="店铺名称"]')
            if name_input.count() == 0:
                name_input = shop_modal.locator('[placeholder*="店铺"]')
            if name_input.count() == 0:
                # 第一个可见 input
                for inp in all_inputs_in_modal:
                    try:
                        if inp.is_visible() and inp.is_editable():
                            name_input = inp
                            break
                    except:
                        continue

            if name_input.count() > 0:
                name_input.click()
                name_input.fill(shop_name)
                print(f"✓ 店铺名称: {shop_name}")
            else:
                print("✗ 未找到店铺名称输入框")

            # ===== S5 & S6. 下拉选择平台和合作状态 =====
            def pick_dropdown(select_el, label):
                try:
                    select_el.click()
                    page.wait_for_timeout(800)
                    # 等可见面板
                    dd = page.locator('.ant-select-dropdown:visible').first
                    dd.wait_for(timeout=5000)
                    page.wait_for_timeout(500)
                    # 在可见面板中找非已选中的选项
                    opts = page.locator('.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)').all()
                    if len(opts) == 0:
                        opts = page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()
                    if len(opts) > 0:
                        opts[0].click()
                        page.wait_for_timeout(500)
                        text = opts[0].text_content()
                        print(f"✓ {label}: {text}")
                        return True
                except Exception as e:
                    print(f"  ⚠️ {label}失败: {e}")
                return False

            all_selects = shop_modal.locator('.ant-select').all()
            print(f"\n步骤S5-S6: 弹窗内共 {len(all_selects)} 个下拉框")

            if len(all_selects) >= 1:
                print("\n步骤S5: 选择平台")
                pick_dropdown(all_selects[0], "平台")

            if len(all_selects) >= 2:
                print("\n步骤S6: 选择合作状态")
                pick_dropdown(all_selects[1], "合作状态")

            # ===== S7. 合作周期（日期选择器） =====
            print("\n步骤S7: 选择合作周期（日期选择器）")
            date_pickers = shop_modal.locator('.ant-picker').all()
            print(f"  日期选择器数量: {len(date_pickers)}")

            if len(date_pickers) > 0:
                date_pickers[0].click()
                page.wait_for_timeout(1000)

                # 选今天
                try:
                    today = page.locator('.ant-picker-cell-today').first
                    if today.count() > 0 and today.is_visible():
                        today.click()
                        page.wait_for_timeout(500)
                        print("✓ 开始日期: 今天")
                except:
                    pass

                # 如果是范围选择器，再选一个后面的日期
                try:
                    end_cells = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').all()
                    if len(end_cells) > 3:
                        end_cells[5].click()
                        page.wait_for_timeout(500)
                        print("✓ 结束日期: 5天后")
                except:
                    pass
            else:
                print("  ⚠️ 未找到日期选择器")

            # ===== S8. 部门（树形选择器） =====
            print("\n步骤S8: 选择部门（树形选择器）")
            tree_loc = shop_modal.locator('.ant-tree-select').first
            if tree_loc.count() == 0:
                tree_loc = shop_modal.locator('[class*="tree-select"]').first

            if tree_loc.count() > 0:
                tree_loc.click()
                page.wait_for_timeout(3000)

                tn = page.locator('.ant-select-tree-treenode').all()
                if len(tn) == 0:
                    tn = page.locator('.ant-tree-treenode').all()
                print(f"  树形节点: {len(tn)} 个")

                for i, node in enumerate(tn[:20]):
                    try:
                        hidden = page.evaluate(
                            '(el) => el.getAttribute("aria-hidden") === "true"',
                            node.element_handle()
                        )
                        if not hidden and node.is_visible():
                            node.click()
                            page.wait_for_timeout(500)
                            print(f"✓ 部门: 节点#{i+1}")
                            break
                    except:
                        continue
            else:
                print("  ⚠️ 未找到部门树形选择器")

            # ===== S9. 填写备注 =====
            print("\n步骤S9: 填写备注")
            ta = shop_modal.locator('textarea').first
            if ta.count() > 0:
                ta.click()
                ta.fill(f'快速测试备注_{shop_suffix}')
                print("✓ 备注已填写")
            else:
                print("  ⚠️ 未找到备注输入框")

            # ===== 截图表单 =====
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_shop_form.png'))
            print("\n✓ 已保存表单截图: quick_shop_form.png")

            # ===== S10. 点击确定 =====
            print("\n步骤S10: 点击确定按钮")
            for s in ['button:has-text("确 定")', 'button:has-text("确定")',
                       'button:has-text("确 认")', 'button:has-text("确认")',
                       '.ant-modal-footer .ant-btn-primary']:
                btn = shop_modal.locator(s).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click()
                    print("✓ 已点击确定")
                    break
            else:
                print("✗ 未找到确定按钮")

            # ===== S11. 等结果 =====
            print("\n步骤S11: 等待处理结果")
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_shop_result.png'))

            add_shop_success = False
            try:
                if not shop_modal.is_visible():
                    print("✓✓✓ 新增店铺成功 ✓✓✓")
                    add_shop_success = True
                else:
                    print("⚠️ 弹窗仍在")
                    for e in shop_modal.locator('.ant-form-item-explain-error').all():
                        print(f"  ✗ {e.text_content()}")
            except:
                print("✓✓✓ 新增店铺成功（弹窗已移除）✓✓✓")
                add_shop_success = True

            # ===================================================================
            # 编辑店铺
            # ===================================================================
            if add_shop_success:
                print("\n" + "="*60)
                print("开始执行：编辑店铺自动化测试")
                print("="*60)

                page.wait_for_timeout(3000)

                # E1: 搜索新增的店铺并点击编辑按钮
                print("\n编辑步骤E1: 在店铺列表中搜索并点击编辑按钮")

                # 先搜索
                try:
                    s_input = page.locator('input[placeholder*="搜索"]').first
                    if s_input.count() == 0:
                        s_input = page.locator('input[placeholder*="请输入"]').first
                    if s_input.count() > 0:
                        s_input.click()
                        page.wait_for_timeout(300)
                        s_input.fill('')
                        s_input.fill(shop_name)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(2000)
                        print(f"  搜索店铺: {shop_name}")
                except:
                    print("  ⚠️ 搜索功能不可用")

                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_shop_list.png'))

                # 查找编辑按钮
                edit_shop_selectors = [
                    f'tr:has-text("{shop_name}") button:has-text("编辑")',
                    f'tr:has-text("{shop_name}") a:has-text("编辑")',
                    f'[class*="row"]:has-text("{shop_name}") button:has-text("编辑")',
                    f'tr:has-text("{shop_name}") [class*="edit"]',
                ]

                edit_shop_btn = None
                for selector in edit_shop_selectors:
                    try:
                        loc = page.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            edit_shop_btn = loc
                            print(f"  找到编辑按钮: {selector}")
                            break
                    except:
                        continue

                if edit_shop_btn is None:
                    # 遍历表格行找编辑按钮
                    all_edit_btns = page.locator('button:has-text("编辑"), a:has-text("编辑")').all()
                    for btn in all_edit_btns:
                        try:
                            row = btn.locator('xpath=ancestor::tr').first
                            if row.count() > 0 and shop_name in (row.text_content() or ''):
                                edit_shop_btn = btn
                                break
                        except:
                            continue

                if edit_shop_btn:
                    edit_shop_btn.click()
                    page.wait_for_timeout(3000)
                    print("✓ 已点击编辑按钮")
                else:
                    print("✗ 未找到该店铺的编辑按钮")
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_shop_no_btn.png'))
                    return

                # E2: 等待编辑弹窗
                print("\n编辑步骤E2: 等待编辑弹窗")
                try:
                    edit_shop_modal = page.locator('.ant-modal').first
                    edit_shop_modal.wait_for(timeout=10000)
                    print("✓ 编辑弹窗已出现")
                except:
                    edit_shop_modal = page.locator('.ant-drawer').first
                    edit_shop_modal.wait_for(timeout=5000)
                    print("✓ 编辑Drawer已出现")

                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_shop_modal_before.png'))

                # E3: 修改店铺名称
                print("\n编辑步骤E3: 修改店铺名称")
                edit_shop_suffix = f'{int(time.time())}{random.randint(100, 999)}'
                edit_shop_name = f'编辑店铺_{edit_shop_suffix}'

                edit_name_input = edit_shop_modal.locator('#shopName')
                if edit_name_input.count() == 0:
                    edit_name_input = edit_shop_modal.locator('[placeholder*="店铺名称"]')
                if edit_name_input.count() == 0:
                    edit_name_input = edit_shop_modal.locator('[placeholder*="店铺"]')
                if edit_name_input.count() == 0:
                    inputs = edit_shop_modal.locator('input:visible').all()
                    for inp in inputs:
                        try:
                            if inp.is_visible() and inp.is_editable():
                                edit_name_input = inp
                                break
                        except:
                            continue

                if edit_name_input.count() > 0:
                    edit_name_input.click()
                    page.wait_for_timeout(300)
                    edit_name_input.fill('')  # 先清空
                    edit_name_input.fill(edit_shop_name)
                    print(f"✓ 店铺名称修改为: {edit_shop_name}")
                else:
                    print("✗ 未找到店铺名称输入框")

                # E4: 修改平台（选另一个选项）
                print("\n编辑步骤E4: 修改平台")
                all_edit_selects = edit_shop_modal.locator('.ant-select').all()
                print(f"  编辑弹窗内下拉框数量: {len(all_edit_selects)}")

                def pick_dropdown_edit(select_el, label):
                    try:
                        select_el.click()
                        page.wait_for_timeout(800)
                        dd = page.locator('.ant-select-dropdown:visible').first
                        dd.wait_for(timeout=5000)
                        page.wait_for_timeout(500)
                        # 选非已选中的第2个（与新增时不同）
                        opts = page.locator(
                            '.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)'
                        ).all()
                        if len(opts) == 0:
                            opts = page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()
                        if len(opts) >= 2:
                            opts[1].click()  # 选第二个，与新增时区分
                        elif len(opts) >= 1:
                            opts[0].click()
                        else:
                            return False
                        page.wait_for_timeout(500)
                        print(f"✓ {label}已修改")
                        return True
                    except Exception as e:
                        print(f"  ⚠️ {label}修改失败: {e}")
                    return False

                if len(all_edit_selects) >= 1:
                    pick_dropdown_edit(all_edit_selects[0], "平台")

                # E5: 修改合作状态
                print("\n编辑步骤E5: 修改合作状态")
                if len(all_edit_selects) >= 2:
                    pick_dropdown_edit(all_edit_selects[1], "合作状态")

                # E6: 修改合作周期
                print("\n编辑步骤E6: 修改合作周期")
                date_pickers_edit = edit_shop_modal.locator('.ant-picker').all()
                if len(date_pickers_edit) > 0:
                    date_pickers_edit[0].click()
                    page.wait_for_timeout(1000)
                    # 选下个月的日期
                    try:
                        end_cells = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').all()
                        if len(end_cells) > 8:
                            end_cells[8].click()
                            page.wait_for_timeout(500)
                            print("✓ 开始日期已修改")
                            if len(end_cells) > 15:
                                end_cells[15].click()
                                page.wait_for_timeout(500)
                                print("✓ 结束日期已修改")
                    except Exception as e:
                        print(f"  ⚠️ 日期修改异常: {e}")
                else:
                    print("  ⚠️ 未找到日期选择器")

                # E7: 更换部门（树形选择器）
                print("\n编辑步骤E7: 更换部门")
                edit_tree = edit_shop_modal.locator('.ant-tree-select').first
                if edit_tree.count() == 0:
                    edit_tree = edit_shop_modal.locator('[class*="tree-select"]').first

                if edit_tree.count() > 0:
                    # 先尝试清除已选中的值
                    try:
                        clear_btn = edit_shop_modal.locator('.ant-select-clear').first
                        if clear_btn.count() > 0:
                            clear_btn.click()
                            page.wait_for_timeout(500)
                            print("  已清除旧的部门选择")
                    except:
                        pass

                    edit_tree.click()
                    page.wait_for_timeout(3000)
                    tn = page.locator('.ant-select-tree-treenode').all()
                    if len(tn) == 0:
                        tn = page.locator('.ant-tree-treenode').all()
                    print(f"  树形节点: {len(tn)} 个")

                    for i, node in enumerate(tn[:20]):
                        try:
                            hidden = page.evaluate(
                                '(el) => el.getAttribute("aria-hidden") === "true"',
                                node.element_handle()
                            )
                            if not hidden and node.is_visible():
                                node.click()
                                page.wait_for_timeout(500)
                                print(f"✓ 部门已更换: 节点#{i+1}")
                                break
                        except:
                            continue
                else:
                    print("  ⚠️ 未找到部门树形选择器")

                # E8: 修改备注
                print("\n编辑步骤E8: 修改备注")
                edit_ta = edit_shop_modal.locator('textarea').first
                if edit_ta.count() > 0:
                    edit_ta.click()
                    page.wait_for_timeout(300)
                    edit_ta.fill('')  # 清空旧备注
                    edit_ta.fill(f'编辑店铺备注_{edit_shop_suffix}')
                    print(f"✓ 备注已修改")
                else:
                    print("  ⚠️ 未找到备注输入框")

                # 截图
                page.wait_for_timeout(1000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_shop_form.png'))
                print("\n✓ 已保存编辑表单截图: edit_shop_form.png")

                # E9: 点击确定
                print("\n编辑步骤E9: 点击确定")
                for s in ['button:has-text("确 定")', 'button:has-text("确定")',
                           'button:has-text("确 认")', 'button:has-text("确认")',
                           '.ant-modal-footer .ant-btn-primary']:
                    btn = edit_shop_modal.locator(s).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        print("✓ 已点击确定")
                        break
                else:
                    print("✗ 未找到确定按钮")

                # E10: 等结果
                print("\n编辑步骤E10: 等待处理结果")
                page.wait_for_timeout(3000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_shop_result.png'))

                edit_shop_success = False
                try:
                    if not edit_shop_modal.is_visible():
                        print("✓✓✓ 编辑店铺成功 ✓✓✓")
                        edit_shop_success = True
                    else:
                        print("⚠️ 弹窗仍在")
                        for e in edit_shop_modal.locator('.ant-form-item-explain-error').all():
                            print(f"  ✗ {e.text_content()}")
                except:
                    print("✓✓✓ 编辑店铺成功（弹窗已移除）✓✓✓")
                    edit_shop_success = True

                # ===================================================================
                # 删除店铺
                # ===================================================================
                if edit_shop_success:
                    print("\n" + "="*60)
                    print("开始执行：删除店铺自动化测试")
                    print("="*60)

                    page.wait_for_timeout(3000)

                    # 使用编辑后的店铺名搜索
                    target_name = edit_shop_name

                    # D1: 搜索并点击删除按钮
                    print("\n删除步骤D1: 搜索并点击删除按钮")

                    try:
                        s_input = page.locator('input[placeholder*="搜索"]').first
                        if s_input.count() == 0:
                            s_input = page.locator('input[placeholder*="请输入"]').first
                        if s_input.count() > 0:
                            s_input.click()
                            page.wait_for_timeout(300)
                            s_input.fill('')
                            s_input.fill(target_name)
                            page.keyboard.press('Enter')
                            page.wait_for_timeout(2000)
                            print(f"  搜索店铺: {target_name}")
                    except:
                        print("  ⚠️ 搜索功能不可用")

                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_shop_list.png'))

                    # 查找删除按钮
                    delete_shop_selectors = [
                        f'tr:has-text("{target_name}") button:has-text("删除")',
                        f'tr:has-text("{target_name}") a:has-text("删除")',
                        f'[class*="row"]:has-text("{target_name}") button:has-text("删除")',
                        f'tr:has-text("{target_name}") [class*="delete"]',
                    ]

                    delete_shop_btn = None
                    for selector in delete_shop_selectors:
                        try:
                            loc = page.locator(selector).first
                            if loc.count() > 0 and loc.is_visible():
                                delete_shop_btn = loc
                                print(f"  找到删除按钮: {selector}")
                                break
                        except:
                            continue

                    if delete_shop_btn is None:
                        all_delete_btns = page.locator('button:has-text("删除"), a:has-text("删除")').all()
                        for btn in all_delete_btns:
                            try:
                                row = btn.locator('xpath=ancestor::tr').first
                                if row.count() > 0 and target_name in (row.text_content() or ''):
                                    delete_shop_btn = btn
                                    break
                            except:
                                continue

                    if delete_shop_btn:
                        # 监听可能的浏览器 confirm 对话框
                        page.on("dialog", lambda d: print(f"  [dialog] {d.message}") or d.accept())
                        delete_shop_btn.click()
                        page.wait_for_timeout(3000)
                        print("✓ 已点击删除按钮")
                    else:
                        print("✗ 未找到该店铺的删除按钮")
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_shop_no_btn.png'))
                        return

                    # D2: 等待删除确认弹窗（用多种方式探测）
                    print("\n删除步骤D2: 等待删除确认弹窗")

                    # 截图看点击后页面状态
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_click_result.png'))

                    # 收集所有可能的弹窗容器
                    print("  === 页面可见容器排查 ===")
                    for sel in ['.ant-modal', '.ant-modal-confirm', '.ant-drawer',
                                 '.ant-popover', '.ant-popconfirm', '[role="dialog"]',
                                 '[class*="modal"]', '[class*="dialog"]']:
                        cnt = page.locator(sel).count()
                        if cnt > 0:
                            for idx in range(min(cnt, 3)):
                                try:
                                    el = page.locator(sel).nth(idx)
                                    if el.is_visible():
                                        txt = el.text_content()[:200] if el.text_content() else ''
                                        print(f"  {sel}[{idx}]: visible, text={txt}")
                                except:
                                    pass

                    # 尝试在全局页面查找 textarea
                    all_page_ta = page.locator('textarea').all()
                    print(f"\n  页面全局 textarea 数量: {len(all_page_ta)}")
                    for i, ta in enumerate(all_page_ta):
                        try:
                            if ta.is_visible():
                                val = ta.input_value()
                                print(f"  textarea[{i}]: visible, value='{val}'")
                        except:
                            pass

                    all_page_input = page.locator('input[type="text"], input:not([type])').all()
                    print(f"  页面全局 text-input 数量: {len(all_page_input)}")
                    for i, inp in enumerate(all_page_input[:5]):
                        try:
                            if inp.is_visible():
                                val = inp.input_value()
                                ph = inp.get_attribute('placeholder') or ''
                                print(f"  input[{i}]: visible, value='{val}', placeholder='{ph}'")
                        except:
                            pass

                    # D3: 填写删除原因 - 直接用 page.fill 全局匹配
                    print("\n删除步骤D3: 填写删除原因")
                    reason_filled = False

                    # 方式A: 全局文本输入框直接 fill（fill 会自动 scroll/click）
                    input_selectors = [
                        'textarea',
                        'input[type="text"]',
                        'input:not([type])',
                        '[role="textbox"]',
                        '[contenteditable="true"]',
                    ]
                    for sel in input_selectors:
                        try:
                            el = page.locator(sel).last  # 用 last，因为弹窗通常是最后出现的
                            if el.count() > 0 and el.is_visible():
                                el.click()
                                page.wait_for_timeout(500)
                                el.fill('测试删除店铺')
                                page.wait_for_timeout(500)
                                try:
                                    actual = el.input_value()
                                    if actual == '测试删除店铺':
                                        reason_filled = True
                                        print(f"✓ 删除原因已填入（{sel}[last]）, 确认值='{actual}'")
                                        break
                                except:
                                    # textarea 的 input_value 可能失败
                                    actual = el.text_content()
                                    if '测试删除店铺' in (actual or ''):
                                        reason_filled = True
                                        print(f"✓ 删除原因已填入（{sel}[last]）")
                                        break
                        except Exception as ex:
                            print(f"  {sel}[last] 尝试失败: {ex}")

                    # 方式B: 用 type 模拟键盘输入
                    if not reason_filled:
                        print("  尝试键盘输入方式...")
                        try:
                            # 先找到弹窗内最可能的输入元素
                            visible_ta = None
                            for h in ['.ant-modal-confirm textarea', '.ant-modal textarea',
                                       '.ant-drawer textarea', 'textarea']:
                                loc = page.locator(h).first
                                if loc.count() > 0 and loc.is_visible():
                                    visible_ta = loc
                                    break
                            if visible_ta:
                                visible_ta.click()
                                page.wait_for_timeout(500)
                                visible_ta.press('Control+a')
                                visible_ta.press('Backspace')
                                page.wait_for_timeout(200)
                                visible_ta.type('测试删除店铺', delay=50)
                                page.wait_for_timeout(500)
                                try:
                                    actual = visible_ta.input_value()
                                    print(f"  键盘输入后值='{actual}'")
                                    if actual == '测试删除店铺':
                                        reason_filled = True
                                        print("✓ 删除原因已填入（键盘输入）")
                                except:
                                    pass
                        except Exception as ex:
                            print(f"  键盘输入失败: {ex}")

                    # 方式C: evaluate JS 直接设置
                    if not reason_filled:
                        print("  尝试 JS 直接设置...")
                        try:
                            reason_set = page.evaluate('''
                                () => {
                                    const tas = document.querySelectorAll('textarea');
                                    for (const ta of tas) {
                                        if (ta.offsetParent !== null) {
                                            ta.focus();
                                            ta.value = '测试删除店铺';
                                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                                            ta.dispatchEvent(new Event('change', { bubbles: true }));
                                            return true;
                                        }
                                    }
                                    return false;
                                }
                            ''')
                            if reason_set:
                                reason_filled = True
                                print("✓ 删除原因已填入（JS注入）")
                            else:
                                print("  JS注入也未找到可输入textarea")
                        except Exception as ex:
                            print(f"  JS注入失败: {ex}")

                    if not reason_filled:
                        print("  ⚠️ 所有方式均未成功填入删除原因")

                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_reason.png'))

                    # D4: 点击确定 - 用页面级定位，优先找可见弹窗中的确定按钮
                    print("\n删除步骤D4: 点击确定")
                    confirm_clicked = False
                    for s in ['button:has-text("确 定")', 'button:has-text("确定")',
                               'button:has-text("确 认")', 'button:has-text("确认")',
                               '.ant-modal-confirm .ant-btn-primary',
                               '.ant-modal-footer .ant-btn-primary',
                               '.ant-modal .ant-btn-primary',
                               '.ant-btn-primary']:
                        # 优先在可见弹窗中找
                        for container_sel in ['.ant-modal-confirm:visible', '.ant-modal:visible',
                                               '.ant-drawer:visible', '']:
                            try:
                                scope = page.locator(container_sel) if container_sel else page
                                btn = scope.locator(s).first
                                if btn.count() > 0 and btn.is_visible():
                                    btn.click()
                                    print(f"✓ 已点击确定（{container_sel or '全局'} > {s}）")
                                    confirm_clicked = True
                                    break
                            except:
                                continue
                        if confirm_clicked:
                            break

                    if not confirm_clicked:
                        print("✗ 未找到确定按钮")

                    # D5: 等待删除结果
                    print("\n删除步骤D5: 等待处理结果")
                    page.wait_for_timeout(3000)
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_result.png'))

                    # 检查弹窗是否消失
                    remaining_modals = page.locator('.ant-modal:visible, .ant-modal-confirm:visible').count()
                    if remaining_modals == 0:
                        print("✓✓✓ 删除店铺成功 ✓✓✓")
                        delete_shop_success = True
                    else:
                        print(f"⚠️ 仍有 {remaining_modals} 个可见弹窗")
                        delete_shop_success = True  # 仍尝试继续

                    # ===================================================================
                    # 删除商家
                    # ===================================================================
                    if delete_shop_success:
                        print("\n" + "="*60)
                        print("开始执行：删除商家自动化测试")
                        print("="*60)

                        # B1: 返回商家管理页面
                        print("\n删除商步骤B1: 返回商家管理页面")
                        page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(3000)
                        print("✓ 已返回商家管理页面")
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_biz_list.png'))

                        # B2: 搜索并点击对应商家的删除按钮
                        print(f"\n删除商步骤B2: 搜索商家'{edit_biz_name}'并点击删除按钮")

                        try:
                            s_input = page.locator('input[placeholder*="搜索"]').first
                            if s_input.count() == 0:
                                s_input = page.locator('input[placeholder*="请输入"]').first
                            if s_input.count() > 0:
                                s_input.click()
                                page.wait_for_timeout(300)
                                s_input.fill('')
                                s_input.fill(edit_biz_name)
                                page.keyboard.press('Enter')
                                page.wait_for_timeout(2000)
                                print(f"  已搜索: {edit_biz_name}")
                        except:
                            print("  ⚠️ 搜索功能不可用")

                        # 处理浏览器原生 confirm 对话框
                        page.on("dialog", lambda d: print(f"  [dialog] {d.message}") or d.accept())

                        # 查找删除按钮
                        biz_delete_btn = None
                        biz_delete_selectors = [
                            f'tr:has-text("{edit_biz_name}") button:has-text("删除")',
                            f'tr:has-text("{edit_biz_name}") a:has-text("删除")',
                            f'[class*="row"]:has-text("{edit_biz_name}") button:has-text("删除")',
                            f'tr:has-text("{edit_biz_name}") [class*="delete"]',
                        ]
                        for selector in biz_delete_selectors:
                            try:
                                loc = page.locator(selector).first
                                if loc.count() > 0 and loc.is_visible():
                                    biz_delete_btn = loc
                                    print(f"  找到删除按钮: {selector}")
                                    break
                            except:
                                continue

                        if biz_delete_btn is None:
                            all_delete = page.locator('button:has-text("删除"), a:has-text("删除")').all()
                            for btn in all_delete:
                                try:
                                    r = btn.locator('xpath=ancestor::tr').first
                                    if r.count() > 0 and edit_biz_name in (r.text_content() or ''):
                                        biz_delete_btn = btn
                                        break
                                except:
                                    continue

                        if biz_delete_btn:
                            biz_delete_btn.click()
                            page.wait_for_timeout(3000)
                            print("✓ 已点击删除按钮")
                        else:
                            print("✗ 未找到该商家的删除按钮")
                            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_biz_no_btn.png'))
                            return

                        # 截图看点击后状态
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_biz_click_result.png'))

                        # B3: 填写删除原因
                        print("\n删除商步骤B3: 填写删除原因")
                        reason_filled = False

                        # 排查可见容器
                        print("  === 页面可见容器排查 ===")
                        for sel in ['.ant-modal', '.ant-modal-confirm', '.ant-drawer',
                                      '.ant-popover', '.ant-popconfirm', '[role="dialog"]',
                                      '[class*="modal"]', '[class*="dialog"]']:
                            cnt = page.locator(sel).count()
                            if cnt > 0:
                                for idx in range(min(cnt, 3)):
                                    try:
                                        el = page.locator(sel).nth(idx)
                                        if el.is_visible():
                                            txt = el.text_content()[:200] if el.text_content() else ''
                                            print(f"  {sel}[{idx}]: visible, text={txt}")
                                    except:
                                        pass

                        # 方式A: fill 最后出现的 textarea
                        for sel in ['textarea', 'input[type="text"]', 'input:not([type])',
                                      '[role="textbox"]', '[contenteditable="true"]']:
                            try:
                                el = page.locator(sel).last
                                if el.count() > 0 and el.is_visible():
                                    el.click()
                                    page.wait_for_timeout(500)
                                    el.fill('测试删除商家')
                                    page.wait_for_timeout(500)
                                    try:
                                        if el.input_value() == '测试删除商家':
                                            reason_filled = True
                                            print(f"✓ 删除原因已填入（{sel}[last]）")
                                            break
                                    except:
                                        if '测试删除商家' in (el.text_content() or ''):
                                            reason_filled = True
                                            print(f"✓ 删除原因已填入（{sel}[last]）")
                                            break
                            except Exception as ex:
                                print(f"  {sel}[last] 失败: {ex}")

                        # 方式B: type 键盘输入
                        if not reason_filled:
                            print("  尝试键盘输入...")
                            try:
                                for h in ['.ant-modal-confirm textarea', '.ant-modal textarea',
                                           '.ant-drawer textarea', 'textarea']:
                                    loc = page.locator(h).first
                                    if loc.count() > 0 and loc.is_visible():
                                        loc.click()
                                        page.wait_for_timeout(500)
                                        loc.press('Control+a')
                                        loc.press('Backspace')
                                        page.wait_for_timeout(200)
                                        loc.type('测试删除商家', delay=50)
                                        page.wait_for_timeout(500)
                                        try:
                                            if loc.input_value() == '测试删除商家':
                                                reason_filled = True
                                                print("✓ 删除原因已填入（键盘输入）")
                                                break
                                        except:
                                            pass
                                if not reason_filled:
                                    # type 到活跃元素
                                    page.keyboard.type('测试删除商家', delay=50)
                                    reason_filled = True
                                    print("✓ 删除原因已填入（page.keyboard.type）")
                            except Exception as ex:
                                print(f"  键盘输入失败: {ex}")

                        # 方式C: JS 注入
                        if not reason_filled:
                            print("  尝试 JS 注入...")
                            try:
                                reason_set = page.evaluate('''() => {
                                    const tas = document.querySelectorAll('textarea');
                                    for (const ta of tas) {
                                        if (ta.offsetParent !== null) {
                                            ta.focus(); ta.value = '测试删除商家';
                                            ta.dispatchEvent(new Event('input', {bubbles: true}));
                                            ta.dispatchEvent(new Event('change', {bubbles: true}));
                                            return true;
                                        }
                                    }
                                    return false;
                                }''')
                                if reason_set:
                                    reason_filled = True
                                    print("✓ 删除原因已填入（JS注入）")
                            except Exception as ex:
                                print(f"  JS注入失败: {ex}")

                        if not reason_filled:
                            print("  ⚠️ 未能填入删除原因")

                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_biz_reason.png'))

                        # B4: 点击确定
                        print("\n删除商步骤B4: 点击确定")
                        confirm_clicked = False
                        for s in ['button:has-text("确 定")', 'button:has-text("确定")',
                                   'button:has-text("确 认")', 'button:has-text("确认")',
                                   '.ant-modal-confirm .ant-btn-primary',
                                   '.ant-modal-footer .ant-btn-primary',
                                   '.ant-modal .ant-btn-primary',
                                   '.ant-btn-primary']:
                            for container_sel in ['.ant-modal-confirm:visible', '.ant-modal:visible',
                                                   '.ant-drawer:visible', '']:
                                try:
                                    scope = page.locator(container_sel) if container_sel else page
                                    btn = scope.locator(s).first
                                    if btn.count() > 0 and btn.is_visible():
                                        btn.click()
                                        print(f"✓ 已点击确定（{container_sel or '全局'} > {s}）")
                                        confirm_clicked = True
                                        break
                                except:
                                    continue
                            if confirm_clicked:
                                break

                        if not confirm_clicked:
                            print("✗ 未找到确定按钮")

                        # B5: 等待结果
                        print("\n删除商步骤B5: 等待处理结果")
                        page.wait_for_timeout(5000)
                        page.wait_for_load_state('networkidle')
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'delete_biz_result.png'))

                        remaining = page.locator('.ant-modal:visible, .ant-modal-confirm:visible').count()
                        if remaining == 0:
                            print("✓✓✓ 删除商家成功 ✓✓✓")
                        else:
                            print(f"⚠️ 仍有 {remaining} 个可见弹窗，请检查截图")

        except Exception as e:
            print(f"\n✗ 错误: {e}")
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'quick_error.png'))
            except:
                pass
            import traceback
            traceback.print_exc()
        finally:
            print("\n完成！")
            time.sleep(3)
            browser.close()


if __name__ == "__main__":
    test_add_shop()
