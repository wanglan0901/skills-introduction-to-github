from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()
    
    try:
        # 登录
        page.goto('https://buffalo-dev.shuishoukefu.com')
        page.wait_for_load_state('networkidle')
        page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
        page.fill('input[type="password"]', '123')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # 导航到商家管理页面
        page.goto('https://buffalo-dev.shuishoukefu.com/custom/business')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        
        # 点击添加商家按钮
        add_btn = page.query_selector('button:has-text("添加商家")')
        if add_btn:
            add_btn.click()
            page.wait_for_timeout(3000)
            
            # 获取模态框
            modal = page.query_selector('.ant-modal')
            if modal:
                # 检查部门选择框
                dept_select = modal.query_selector('.ant-select')
                if dept_select:
                    print("找到部门选择框")
                    
                    # 点击选择部门
                    dept_select.click()
                    page.wait_for_timeout(2000)  # 增加等待时间
                    
                    # 查找下拉选项
                    dropdown = page.query_selector('.ant-select-dropdown:not([style*="none"])')
                    if dropdown:
                        options = dropdown.query_selector_all('.ant-select-item-option')
                        print(f"找到 {len(options)} 个选项")
                        
                        if options:
                            # 选择第一个选项
                            options[0].click()
                            page.wait_for_timeout(500)
                            print("已选择第一个部门")
                        else:
                            print("没有可用的部门选项")
                    
                    # 截图查看状态
                    page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/form_debug.png')
                    
                    # 填写其他字段
                    page.fill('#merchantName', '测试商家_v10')
                    page.fill('#aliasName', '测试商家')
                    page.fill('#mobile', '13800138000')
                    page.fill('#wechatNumber', 'test_wechat')
                    
                    # 验证填写
                    name_value = page.input_value('#merchantName')
                    print(f"商家名称填写值: {name_value}")
                    
                    # 截图
                    page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/form_filled.png')
                    
                    # 点击确认
                    confirm_btn = modal.query_selector('button:has-text("确 认")')
                    if confirm_btn:
                        confirm_btn.click()
                        page.wait_for_timeout(3000)
                        
                        # 检查结果
                        modal_after = page.query_selector('.ant-modal')
                        if modal_after:
                            error = modal_after.query_selector('.ant-form-item-explain-error')
                            if error:
                                print(f"错误: {error.text_content()}")
                            page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/error_state.png')
                        else:
                            print("✓ 创建成功！")
                            page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/success_state.png')
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        page.wait_for_timeout(5000)
        browser.close()