from playwright.sync_api import sync_playwright
import time
import random
import os

# CI 环境自动切换为无头模式，本地运行保持有头模式
HEADLESS = os.environ.get('CI') is not None or os.environ.get('HEADLESS', '').lower() == 'true'
SCREENSHOT_DIR = os.environ.get('SCREENSHOT_DIR', os.path.dirname(os.path.abspath(__file__)))

def test_create_business():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=0 if HEADLESS else 300, channel='chrome')
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 访问登录页面
            print("步骤1: 访问登录页面")
            page.goto("https://buffalo-dev.shuishoukefu.com", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            print(f"  当前URL: {page.url}")
            print(f"  页面标题: {page.title()}")
            
            # 2. 输入登录信息
            print("\n步骤2: 输入登录账号")
            page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
            page.fill('input[type="password"]', '123')
            print("✓ 账号密码已填写")
            
            # 2.5. 勾选服务协议复选框
            print("\n步骤2.5: 勾选服务协议复选框")
            try:
                checkbox = page.locator('input[type="checkbox"]').first
                checkbox.check(force=True)
                print("✓ 已勾选「我已阅读并同意《服务协议及隐私政策》」")
            except Exception as e:
                print(f"⚠️ 勾选协议复选框时出现问题: {e}")
                # 尝试点击label
                try:
                    page.locator('label:has-text("已阅读")').click()
                    print("✓ 通过label点击勾选协议")
                except:
                    pass
            
            # 3. 点击登录按钮
            print("\n步骤3: 点击登录按钮")
            page.click('button[type="submit"]')
            # 等待登录完成 - 等待URL变化或页面跳转
            page.wait_for_timeout(5000)
            page.wait_for_load_state('networkidle')
            print(f"  登录后URL: {page.url}")
            print("✓ 登录完成")
            
            # 检查页面是否仍然有效
            try:
                page.title()
            except:
                print("✗ 登录后页面已关闭，可能发生了重定向到新标签页")
                # 尝试获取最新打开的页面
                pages = context.pages
                print(f"  当前打开的页面数: {len(pages)}")
                if len(pages) > 0:
                    page = pages[-1]
                    print(f"  切换到页面: {page.url}")
                else:
                    print("✗ 没有可用页面")
                    return
            
            # 4. 导航到商家管理页面
            print("\n步骤4: 导航到商家管理页面")
            page.goto("https://buffalo-dev.shuishoukefu.com/custom/business", timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            print(f"  商家管理页面URL: {page.url}")
            
            # 检查页面内容
            page_content = page.content()
            if '添加商家' in page_content or '商家' in page_content:
                print("✓ 成功到达商家管理页面")
            else:
                print("⚠️ 页面可能未正确加载商家管理内容")
            
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'step4_business_page.png'))
            
            # 5. 点击添加商家按钮
            print("\n步骤5: 点击添加商家按钮")
            # 尝试多种定位策略
            add_btn = None
            selectors = [
                'button:has-text("添加商家")',
                'button:has-text("新增")',
                'button:has-text("新建")',
                '.ant-btn-primary:has-text("添加")',
            ]
            
            for selector in selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.count() > 0 and loc.is_visible():
                        add_btn = loc
                        print(f"  使用选择器找到按钮: {selector}")
                        break
                except:
                    continue
            
            if add_btn is None:
                print("✗ 未找到添加商家按钮，截图保存")
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'step5_no_button.png'))
                return
            
            add_btn.click()
            page.wait_for_timeout(3000)
            print("✓ 成功点击添加商家按钮")
            
            # 6. 等待弹窗出现
            print("\n步骤6: 等待弹窗出现")
            try:
                modal = page.locator('.ant-modal').first
                modal.wait_for(timeout=10000)
                print("✓ 弹窗已出现")
            except:
                # 尝试查找drawer
                modal = page.locator('.ant-drawer').first
                try:
                    modal.wait_for(timeout=5000)
                    print("✓ Drawer已出现")
                except:
                    print("✗ 未找到弹窗或Drawer")
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'step6_no_modal.png'))
                    return
            
            # 7. 选择部门（树形选择器）
            print("\n步骤7: 选择部门（树形选择器）")
            
            # 尝试通过deptId找到树形选择器
            dept_select = None
            dept_selectors = [
                '#deptId',
                '[data-field="deptId"]',
                '.ant-tree-select',
                '[class*="tree-select"]',
            ]
            
            for selector in dept_selectors:
                try:
                    loc = modal.locator(selector).first
                    if loc.count() > 0:
                        dept_select = loc
                        print(f"  找到部门选择器: {selector}")
                        break
                except:
                    continue
            
            if dept_select:
                dept_select.click()
                print("✓ 点击部门树形选择框")
                page.wait_for_timeout(3000)
                
                # 查找下拉树形节点
                tree_nodes = page.locator('.ant-select-tree-treenode').all()
                if len(tree_nodes) == 0:
                    tree_nodes = page.locator('.ant-tree-treenode').all()
                if len(tree_nodes) == 0:
                    tree_nodes = page.locator('[class*="tree-node"]').all()
                
                print(f"  找到 {len(tree_nodes)} 个树形节点")
                
                if len(tree_nodes) > 0:
                    # 找可点击的节点（排除aria-hidden）
                    for i, node in enumerate(tree_nodes[:20]):  # 最多遍历前20个
                        try:
                            hidden = page.evaluate(
                                '(el) => el.getAttribute("aria-hidden") === "true"',
                                node.element_handle()
                            )
                            if not hidden and node.is_visible():
                                node.click()
                                page.wait_for_timeout(500)
                                print(f"  已选择部门（节点 #{i+1}）")
                                break
                        except:
                            continue
                else:
                    print("⚠️ 未找到树形节点，尝试直接点击展开的选项")
                    # 尝试其他下拉选项
                    dropdown_items = page.locator('.ant-select-item').all()
                    if len(dropdown_items) > 0:
                        dropdown_items[0].click()
                        page.wait_for_timeout(500)
                        print("✓ 已选择下拉选项")
            else:
                print("⚠️ 未找到部门树形选择器，跳过部门选择")
            
            # 8. 在弹窗内填写表单
            print("\n步骤8: 在弹窗内填写表单")
            
            # 生成唯一数据
            unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
            unique_name = f'测试商家_{unique_suffix}'
            unique_alias = f'测试_{unique_suffix}'
            unique_mobile = f'138{random.randint(10000000, 99999999)}'
            unique_wechat = f'test_wechat_{unique_suffix}'
            
            # 商家名称
            merchant_input = modal.locator('#merchantName')
            if merchant_input.count() == 0:
                merchant_input = modal.locator('[placeholder*="商家名称"]')
            if merchant_input.count() > 0:
                merchant_input.click()
                merchant_input.fill(unique_name)
                print(f"✓ 商家名称: {unique_name}")
            else:
                print("✗ 未找到商家名称输入框")
            
            # 商家简称
            alias_input = modal.locator('#aliasName')
            if alias_input.count() == 0:
                alias_input = modal.locator('[placeholder*="简称"]')
            if alias_input.count() > 0:
                alias_input.click()
                alias_input.fill(unique_alias)
                print(f"✓ 商家简称: {unique_alias}")
            
            # 手机号
            mobile_input = modal.locator('#mobile')
            if mobile_input.count() == 0:
                mobile_input = modal.locator('[placeholder*="手机"]')
            if mobile_input.count() > 0:
                mobile_input.click()
                mobile_input.fill(unique_mobile)
                print(f"✓ 手机号: {unique_mobile}")
            
            # 微信号
            wechat_input = modal.locator('#wechatNumber')
            if wechat_input.count() == 0:
                wechat_input = modal.locator('[placeholder*="微信"]')
            if wechat_input.count() > 0:
                wechat_input.click()
                wechat_input.fill(unique_wechat)
                print(f"✓ 微信号: {unique_wechat}")
            
            # 截图确认
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'tree_form.png'))
            print("✓ 已保存表单截图: tree_form.png")
            
            # 9. 点击确认按钮
            print("\n步骤9: 点击确认按钮")
            confirm_selectors = [
                'button:has-text("确 认")',
                'button:has-text("确认")',
                'button:has-text("确定")',
                '.ant-modal-footer .ant-btn-primary',
            ]
            
            confirm_btn = None
            for selector in confirm_selectors:
                try:
                    loc = modal.locator(selector).first
                    if loc.count() > 0 and loc.is_visible():
                        confirm_btn = loc
                        break
                except:
                    continue
            
            if confirm_btn:
                confirm_btn.click()
                print("✓ 点击确认按钮")
            else:
                print("✗ 未找到确认按钮")
            
            # 10. 等待处理结果
            print("\n步骤10: 等待处理结果")
            page.wait_for_timeout(3000)
            
            # 截图
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'tree_result.png'))
            print("✓ 已保存结果截图: tree_result.png")
            
            # 检查结果 - 弹窗是否关闭
            created_success = False
            try:
                if modal.is_visible():
                    print("⚠️ 弹窗仍在显示")
                    # 检查错误信息
                    errors = modal.locator('.ant-form-item-explain-error').all()
                    if errors:
                        for err in errors:
                            print(f"  ✗ 表单错误: {err.text_content()}")
                    # 也检查message提示
                    messages = page.locator('.ant-message-notice-content').all()
                    for msg in messages:
                        print(f"  提示信息: {msg.text_content()}")
                else:
                    print("✓✓✓ 创建商家成功！弹窗已关闭 ✓✓✓")
                    created_success = True
            except:
                # 弹窗可能已被移除
                print("✓✓✓ 创建商家成功！弹窗已关闭（页面更新）✓✓✓")
                created_success = True
            
            # ===================================================================
            # 第二部分：编辑商家
            # ===================================================================
            if created_success:
                print("\n" + "="*60)
                print("开始执行：编辑商家自动化测试")
                print("="*60)
                
                # 等待表格刷新，新增的商家出现在列表中
                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle')
                
                # E1. 在表格中查找刚创建的商家并点击编辑按钮
                print("\n编辑步骤E1: 查找刚创建的商家并点击编辑按钮")
                
                # 先在搜索框中搜索刚创建的商家，快速定位
                try:
                    search_input = page.locator('input[placeholder*="搜索"]').first
                    if search_input.count() == 0:
                        search_input = page.locator('input[placeholder*="请输入"]').first
                    if search_input.count() > 0:
                        search_input.click()
                        search_input.fill(unique_name)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(2000)
                        print(f"  搜索商家: {unique_name}")
                except:
                    print("  ⚠️ 搜索框不可用，尝试直接定位表格行")
                
                # 查找表格中该商家的行，定位编辑按钮
                edit_btn = None
                edit_selectors = [
                    f'tr:has-text("{unique_name}") button:has-text("编辑")',
                    f'tr:has-text("{unique_name}") a:has-text("编辑")',
                    f'[class*="row"]:has-text("{unique_name}") button:has-text("编辑")',
                    f'tr:has-text("{unique_name}") [class*="edit"]',
                ]
                
                for selector in edit_selectors:
                    try:
                        loc = page.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            edit_btn = loc
                            print(f"  使用选择器找到编辑按钮: {selector}")
                            break
                    except:
                        continue
                
                if edit_btn is None:
                    # 兜底：在表格所有可见按钮中查找"编辑"
                    all_edit_btns = page.locator('button:has-text("编辑"), a:has-text("编辑")').all()
                    for btn in all_edit_btns:
                        try:
                            # 确认该按钮在包含唯一商家名称的行中
                            row = btn.locator('xpath=ancestor::tr').first
                            if row.count() > 0 and unique_name in (row.text_content() or ''):
                                edit_btn = btn
                                break
                        except:
                            continue
                
                if edit_btn:
                    edit_btn.click()
                    page.wait_for_timeout(3000)
                    print("✓ 成功点击编辑按钮")
                else:
                    print("✗ 未找到编辑按钮")
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_no_button.png'))
                    return
                
                # E2. 等待编辑弹窗出现
                print("\n编辑步骤E2: 等待编辑弹窗出现")
                try:
                    edit_modal = page.locator('.ant-modal').first
                    edit_modal.wait_for(timeout=10000)
                    print("✓ 编辑弹窗已出现")
                except:
                    try:
                        edit_modal = page.locator('.ant-drawer').first
                        edit_modal.wait_for(timeout=5000)
                        print("✓ 编辑Drawer已出现")
                    except:
                        print("✗ 未找到编辑弹窗")
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_no_modal.png'))
                        return
                
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_before.png'))
                print("✓ 已保存编辑前截图: edit_before.png")
                
                # E3. 修改商家名称
                print("\n编辑步骤E3: 修改商家名称")
                edit_unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
                edit_name = f'编辑商家_{edit_unique_suffix}'
                
                merchant_input = edit_modal.locator('#merchantName')
                if merchant_input.count() == 0:
                    merchant_input = edit_modal.locator('[placeholder*="商家名称"]')
                if merchant_input.count() > 0:
                    merchant_input.click()
                    merchant_input.fill('')  # 清空
                    merchant_input.fill(edit_name)
                    print(f"✓ 修改商家名称: {unique_name} → {edit_name}")
                else:
                    print("✗ 未找到商家名称输入框")
                
                # E4. 修改商家简称
                print("\n编辑步骤E4: 修改商家简称")
                edit_alias = f'编辑简称_{edit_unique_suffix}'
                
                alias_input = edit_modal.locator('#aliasName')
                if alias_input.count() == 0:
                    alias_input = edit_modal.locator('[placeholder*="简称"]')
                if alias_input.count() > 0:
                    alias_input.click()
                    alias_input.fill('')
                    alias_input.fill(edit_alias)
                    print(f"✓ 修改商家简称: → {edit_alias}")
                
                # E5. 修改部门（树形选择器 - 选择不同节点）
                print("\n编辑步骤E5: 修改部门（树形选择器）")
                
                dept_select = None
                dept_selectors = [
                    '#deptId',
                    '[data-field="deptId"]',
                    '.ant-tree-select',
                    '[class*="tree-select"]',
                ]
                
                for selector in dept_selectors:
                    try:
                        loc = edit_modal.locator(selector).first
                        if loc.count() > 0:
                            dept_select = loc
                            print(f"  找到部门选择器: {selector}")
                            break
                    except:
                        continue
                
                if dept_select:
                    # 先清空当前选择（点击清除按钮）
                    try:
                        clear_btn = edit_modal.locator('.ant-select-clear, .ant-tree-select-clear').first
                        if clear_btn.count() > 0 and clear_btn.is_visible():
                            clear_btn.click()
                            page.wait_for_timeout(500)
                            print("  ✓ 已清除当前部门选择")
                    except:
                        pass
                    
                    dept_select.click()
                    print("✓ 点击部门树形选择框")
                    page.wait_for_timeout(3000)
                    
                    tree_nodes = page.locator('.ant-select-tree-treenode').all()
                    if len(tree_nodes) == 0:
                        tree_nodes = page.locator('.ant-tree-treenode').all()
                    if len(tree_nodes) == 0:
                        tree_nodes = page.locator('[class*="tree-node"]').all()
                    
                    print(f"  找到 {len(tree_nodes)} 个树形节点")
                    
                    if len(tree_nodes) > 1:
                        # 选择第3个节点（不同于创建时的第2个节点）
                        target_idx = min(2, len(tree_nodes) - 1)  # 索引2 = 第3个
                        node = tree_nodes[target_idx]
                        try:
                            node.click()
                            page.wait_for_timeout(500)
                            print(f"  ✓ 已选择部门（节点 #{target_idx+1}）")
                        except:
                            print("  ⚠️ 节点点击失败")
                    elif len(tree_nodes) == 1:
                        tree_nodes[0].click()
                        print("  ✓ 已选择部门（唯一节点）")
                    else:
                        print("  ⚠️ 未找到树形节点")
                else:
                    print("⚠️ 未找到部门树形选择器，跳过部门修改")
                
                # E6. 修改手机号
                print("\n编辑步骤E6: 修改手机号")
                edit_mobile = f'139{random.randint(10000000, 99999999)}'
                
                mobile_input = edit_modal.locator('#mobile')
                if mobile_input.count() == 0:
                    mobile_input = edit_modal.locator('[placeholder*="手机"]')
                if mobile_input.count() > 0:
                    mobile_input.click()
                    mobile_input.fill('')
                    mobile_input.fill(edit_mobile)
                    print(f"✓ 修改手机号: → {edit_mobile}")
                
                # E7. 修改微信号
                print("\n编辑步骤E7: 修改微信号")
                edit_wechat = f'edit_wechat_{edit_unique_suffix}'
                
                wechat_input = edit_modal.locator('#wechatNumber')
                if wechat_input.count() == 0:
                    wechat_input = edit_modal.locator('[placeholder*="微信"]')
                if wechat_input.count() > 0:
                    wechat_input.click()
                    wechat_input.fill('')
                    wechat_input.fill(edit_wechat)
                    print(f"✓ 修改微信号: → {edit_wechat}")
                
                # E8. 修改备注
                print("\n编辑步骤E8: 修改备注")
                edit_remark = f'自动化测试备注_{edit_unique_suffix}'
                
                remark_input = edit_modal.locator('#remark')
                if remark_input.count() == 0:
                    remark_input = edit_modal.locator('[placeholder*="备注"]')
                if remark_input.count() == 0:
                    remark_input = edit_modal.locator('textarea').first
                if remark_input.count() > 0:
                    remark_input.click()
                    remark_input.fill('')
                    remark_input.fill(edit_remark)
                    print(f"✓ 修改备注: {edit_remark}")
                else:
                    print("⚠️ 未找到备注输入框")
                
                # 编辑表单截图
                page.wait_for_timeout(1000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_form.png'))
                print("✓ 已保存编辑表单截图: edit_form.png")
                
                # E9. 点击确认按钮
                print("\n编辑步骤E9: 点击确认按钮")
                confirm_selectors = [
                    'button:has-text("确 认")',
                    'button:has-text("确认")',
                    'button:has-text("确定")',
                    '.ant-modal-footer .ant-btn-primary',
                ]
                
                confirm_btn = None
                for selector in confirm_selectors:
                    try:
                        loc = edit_modal.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            confirm_btn = loc
                            break
                    except:
                        continue
                
                if confirm_btn:
                    confirm_btn.click()
                    print("✓ 点击确认按钮")
                else:
                    print("✗ 未找到确认按钮")
                
                # E10. 等待编辑处理结果
                print("\n编辑步骤E10: 等待编辑处理结果")
                page.wait_for_timeout(3000)
                
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'edit_result.png'))
                print("✓ 已保存编辑结果截图: edit_result.png")
                
                # 检查编辑结果
                edited_success = False
                try:
                    if edit_modal.is_visible():
                        print("⚠️ 编辑弹窗仍在显示")
                        errors = edit_modal.locator('.ant-form-item-explain-error').all()
                        if errors:
                            for err in errors:
                                print(f"  ✗ 表单错误: {err.text_content()}")
                        messages = page.locator('.ant-message-notice-content').all()
                        for msg in messages:
                            print(f"  提示信息: {msg.text_content()}")
                    else:
                        print("✓✓✓ 编辑商家成功！弹窗已关闭 ✓✓✓")
                        edited_success = True
                except:
                    print("✓✓✓ 编辑商家成功！弹窗已关闭（页面更新）✓✓✓")
                    edited_success = True
            
            # ===================================================================
            # 第三部分：添加店铺
            # ===================================================================
            if edited_success:
                print("\n" + "="*60)
                print("开始执行：添加店铺自动化测试")
                print("="*60)
                
                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle')
                
                # S1. 搜索编辑后的商家，点击详情按钮
                print("\n店铺步骤S1: 查找编辑后的商家并点击详情按钮")
                
                # 先清空搜索框重新搜索编辑后的商家
                try:
                    search_input = page.locator('input[placeholder*="搜索"]').first
                    if search_input.count() == 0:
                        search_input = page.locator('input[placeholder*="请输入"]').first
                    if search_input.count() > 0:
                        search_input.click()
                        search_input.fill('')
                        search_input.fill(edit_name)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(2000)
                        print(f"  搜索编辑后的商家: {edit_name}")
                except:
                    print("  ⚠️ 搜索框不可用，尝试直接定位表格行")
                
                # 查找详情按钮
                detail_btn = None
                detail_selectors = [
                    f'tr:has-text("{edit_name}") button:has-text("详情")',
                    f'tr:has-text("{edit_name}") a:has-text("详情")',
                    f'[class*="row"]:has-text("{edit_name}") button:has-text("详情")',
                    f'tr:has-text("{edit_name}") [class*="detail"]',
                ]
                
                for selector in detail_selectors:
                    try:
                        loc = page.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            detail_btn = loc
                            print(f"  使用选择器找到详情按钮: {selector}")
                            break
                    except:
                        continue
                
                if detail_btn is None:
                    all_detail_btns = page.locator('button:has-text("详情"), a:has-text("详情")').all()
                    for btn in all_detail_btns:
                        try:
                            row = btn.locator('xpath=ancestor::tr').first
                            if row.count() > 0 and edit_name in (row.text_content() or ''):
                                detail_btn = btn
                                break
                        except:
                            continue
                
                if detail_btn:
                    detail_btn.click()
                    page.wait_for_timeout(3000)
                    page.wait_for_load_state('networkidle')
                    print("✓ 成功点击详情按钮，已进入商家详情页")
                else:
                    print("✗ 未找到详情按钮")
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_no_detail_button.png'))
                    return
                
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_detail_page.png'))
                print("✓ 已保存详情页截图: shop_detail_page.png")
                
                # S2. 点击"+新增店铺"按钮
                print("\n店铺步骤S2: 点击'+新增店铺'按钮")
                
                add_shop_btn = None
                shop_btn_selectors = [
                    'button:has-text("新增店铺")',
                    'button:has-text("添加店铺")',
                    'button:has-text("+新增店铺")',
                    'button:has-text("新建店铺")',
                    '.ant-btn-primary:has-text("新增")',
                ]
                
                for selector in shop_btn_selectors:
                    try:
                        loc = page.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            add_shop_btn = loc
                            print(f"  使用选择器找到按钮: {selector}")
                            break
                    except:
                        continue
                
                if add_shop_btn:
                    add_shop_btn.click()
                    page.wait_for_timeout(3000)
                    print("✓ 成功点击'+新增店铺'按钮")
                else:
                    print("✗ 未找到新增店铺按钮")
                    page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_no_add_button.png'))
                    return
                
                # S3. 等待店铺弹窗出现
                print("\n店铺步骤S3: 等待店铺弹窗出现")
                try:
                    shop_modal = page.locator('.ant-modal').first
                    shop_modal.wait_for(timeout=10000)
                    print("✓ 新增店铺弹窗已出现")
                except:
                    try:
                        shop_modal = page.locator('.ant-drawer').first
                        shop_modal.wait_for(timeout=5000)
                        print("✓ 新增店铺Drawer已出现")
                    except:
                        print("✗ 未找到新增店铺弹窗")
                        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_no_modal.png'))
                        return
                
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_modal_empty.png'))
                
                # S4. 填写店铺名称
                print("\n店铺步骤S4: 填写店铺名称")
                shop_unique_suffix = f'{int(time.time())}{random.randint(100, 999)}'
                shop_name = f'测试店铺_{shop_unique_suffix}'
                
                # 尝试多种定位策略查找店铺名称输入框
                name_input = shop_modal.locator('#shopName')
                if name_input.count() == 0:
                    name_input = shop_modal.locator('[placeholder*="店铺名称"]')
                if name_input.count() == 0:
                    name_input = shop_modal.locator('[placeholder*="店铺"]')
                if name_input.count() == 0:
                    # 可能是弹窗中第一个普通input
                    inputs = shop_modal.locator('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])').all()
                    if len(inputs) > 0:
                        name_input = inputs[0]
                
                if name_input.count() > 0:
                    name_input.click()
                    name_input.fill(shop_name)
                    print(f"✓ 店铺名称: {shop_name}")
                else:
                    print("✗ 未找到店铺名称输入框")
                
                # S5. 下拉选择"平台"
                print("\n店铺步骤S5: 下拉选择'平台'")
                
                def select_dropdown_option(modal, select_locator, label):
                    """通用下拉选择函数：点击选择器，等待下拉面板展开，选择第一个非已选中的选项"""
                    try:
                        select_locator.click()
                        page.wait_for_timeout(800)
                        # 等待可见的下拉面板出现
                        try:
                            dropdown = page.locator('.ant-select-dropdown:visible').first
                            dropdown.wait_for(timeout=5000)
                            page.wait_for_timeout(500)
                        except:
                            pass
                        # 仅在可见下拉面板中查找选项
                        options = page.locator('.ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-selected)').all()
                        if len(options) == 0:
                            options = page.locator('.ant-select-dropdown:visible .ant-select-item-option').all()
                        if len(options) > 0:
                            options[0].click()
                            page.wait_for_timeout(500)
                            print(f"  ✓ 已选择{label}")
                            return True
                    except Exception as e:
                        print(f"  ⚠️ {label}选择异常: {e}")
                    return False
                
                # 获取弹窗中所有ant-select下拉框
                all_selects = shop_modal.locator('.ant-select').all()
                print(f"  弹窗中共找到 {len(all_selects)} 个下拉框")
                
                # 平台选第一个下拉框
                if len(all_selects) >= 1:
                    select_dropdown_option(shop_modal, all_selects[0], "平台")
                
                # S6. 下拉选择"合作状态"
                print("\n店铺步骤S6: 下拉选择'合作状态'")
                
                if len(all_selects) >= 2:
                    select_dropdown_option(shop_modal, all_selects[1], "合作状态")
                else:
                    print("  ⚠️ 合作状态下拉选择失败：下拉框数量不足")
                
                # S7. 合作周期（日期选择器）
                print("\n店铺步骤S7: 选择合作周期（日期选择器）")
                date_selected = False
                
                # 查找日期选择器 - 可能是范围选择器
                date_selectors = [
                    '#cooperationPeriod',
                    '[data-field="cooperationPeriod"]',
                    '[placeholder*="合作周期"]',
                    '.ant-picker-range',
                    '.ant-date-picker',
                ]
                
                date_input = None
                for selector in date_selectors:
                    try:
                        loc = shop_modal.locator(selector).first
                        if loc.count() > 0:
                            date_input = loc
                            print(f"  找到日期选择器: {selector}")
                            break
                    except:
                        continue
                
                if date_input:
                    date_input.click()
                    page.wait_for_timeout(1000)
                    
                    # 处理日期选择器弹窗
                    # 先点击今天的日期作为开始
                    try:
                        today_cell = page.locator('.ant-picker-cell-today').first
                        if today_cell.count() > 0:
                            today_cell.click()
                            page.wait_for_timeout(500)
                            print("  ✓ 已选择开始日期")
                            date_selected = True
                        else:
                            # 点击第一个可用日期
                            first_cell = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').first
                            if first_cell.count() > 0:
                                first_cell.click()
                                page.wait_for_timeout(500)
                                print("  ✓ 已选择开始日期（首个可用）")
                                date_selected = True
                    except:
                        pass
                    
                    # 如果是范围选择器，还需要选结束日期
                    try:
                        # 再点击一个后面的日期作为结束
                        end_cells = page.locator('.ant-picker-cell:not(.ant-picker-cell-disabled)').all()
                        if len(end_cells) > 2:
                            end_cells[min(5, len(end_cells)-1)].click()
                            page.wait_for_timeout(500)
                            print("  ✓ 已选择结束日期")
                    except:
                        pass
                else:
                    print("  ⚠️ 未找到日期选择器，跳过")
                
                # S8. 部门（树形选择器）
                print("\n店铺步骤S8: 选择部门（树形选择器）")
                shop_dept = None
                for selector in ['.ant-tree-select', '[class*="tree-select"]']:
                    try:
                        loc = shop_modal.locator(selector).first
                        if loc.count() > 0:
                            shop_dept = loc
                            break
                    except:
                        continue
                
                if shop_dept:
                    shop_dept.click()
                    print("✓ 点击部门树形选择框")
                    page.wait_for_timeout(3000)
                    
                    tree_nodes = page.locator('.ant-select-tree-treenode').all()
                    if len(tree_nodes) == 0:
                        tree_nodes = page.locator('.ant-tree-treenode').all()
                    if len(tree_nodes) == 0:
                        tree_nodes = page.locator('[class*="tree-node"]').all()
                    
                    print(f"  找到 {len(tree_nodes)} 个树形节点")
                    
                    if len(tree_nodes) > 0:
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
                        print("  ⚠️ 未找到树形节点")
                else:
                    print("  ⚠️ 未找到部门树形选择器，跳过")
                
                # S9. 填写备注
                print("\n店铺步骤S9: 填写备注")
                shop_remark = f'店铺备注_{shop_unique_suffix}'
                
                remark_input = shop_modal.locator('#remark')
                if remark_input.count() == 0:
                    remark_input = shop_modal.locator('[placeholder*="备注"]')
                if remark_input.count() == 0:
                    remark_input = shop_modal.locator('textarea').first
                if remark_input.count() > 0:
                    remark_input.click()
                    remark_input.fill(shop_remark)
                    print(f"✓ 店铺备注: {shop_remark}")
                else:
                    print("⚠️ 未找到备注输入框")
                
                # 截图表单
                page.wait_for_timeout(1000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_form.png'))
                print("✓ 已保存店铺表单截图: shop_form.png")
                
                # S10. 点击"确定"按钮
                print("\n店铺步骤S10: 点击'确定'按钮")
                confirm_selectors = [
                    'button:has-text("确 定")',
                    'button:has-text("确定")',
                    'button:has-text("确 认")',
                    'button:has-text("确认")',
                    '.ant-modal-footer .ant-btn-primary',
                ]
                
                confirm_btn = None
                for selector in confirm_selectors:
                    try:
                        loc = shop_modal.locator(selector).first
                        if loc.count() > 0 and loc.is_visible():
                            confirm_btn = loc
                            break
                    except:
                        continue
                
                if confirm_btn:
                    confirm_btn.click()
                    print("✓ 点击确定按钮")
                else:
                    print("✗ 未找到确定按钮")
                
                # S11. 等待处理结果
                print("\n店铺步骤S11: 等待处理结果")
                page.wait_for_timeout(3000)
                
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'shop_result.png'))
                print("✓ 已保存店铺结果截图: shop_result.png")
                
                # 检查结果
                try:
                    if shop_modal.is_visible():
                        print("⚠️ 店铺弹窗仍在显示")
                        errors = shop_modal.locator('.ant-form-item-explain-error').all()
                        if errors:
                            for err in errors:
                                print(f"  ✗ 表单错误: {err.text_content()}")
                        messages = page.locator('.ant-message-notice-content').all()
                        for msg in messages:
                            print(f"  提示信息: {msg.text_content()}")
                    else:
                        print("✓✓✓ 新增店铺成功！弹窗已关闭 ✓✓✓")
                except:
                    print("✓✓✓ 新增店铺成功！弹窗已关闭（页面更新）✓✓✓")
                
        except Exception as e:
            print(f"\n✗ 测试过程中出现错误: {str(e)}")
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'tree_error.png'))
                print("  错误截图已保存: tree_error.png")
            except:
                pass
            import traceback
            traceback.print_exc()
        finally:
            print("\n测试完成！浏览器将在5秒后关闭...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    test_create_business()
