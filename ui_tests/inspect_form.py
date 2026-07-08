from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
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
            page.wait_for_timeout(2000)
            
            # 保存表单页面
            with open('form_details.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("表单页面已保存")
            
            # 获取所有输入框及其属性
            inputs = page.query_selector_all('input')
            print(f"\n=== 输入框详情 ({len(inputs)} 个) ===")
            for i, inp in enumerate(inputs):
                # 获取所有属性
                attr_str = page.evaluate('(el) => el.outerHTML', inp)
                print(f"\n输入框 {i+1}:")
                print(attr_str)
            
            # 获取所有选择框
            selects = page.query_selector_all('select')
            print(f"\n=== 选择框详情 ({len(selects)} 个) ===")
            for i, sel in enumerate(selects):
                attr_str = page.evaluate('(el) => el.outerHTML', sel)
                print(f"\n选择框 {i+1}:")
                print(attr_str)
            
            # 获取所有按钮
            buttons = page.query_selector_all('button')
            print(f"\n=== 按钮详情 ({len(buttons)} 个) ===")
            for i, btn in enumerate(buttons):
                text = btn.text_content().strip() if btn.text_content() else ""
                attr_str = page.evaluate('(el) => el.outerHTML', btn)
                print(f"\n按钮 {i+1}: '{text}'")
                print(attr_str)
            
            # 获取所有标签
            labels = page.query_selector_all('label, .ant-form-item-label')
            print(f"\n=== 标签详情 ({len(labels)} 个) ===")
            for i, label in enumerate(labels):
                text = label.text_content().strip() if label.text_content() else ""
                print(f"标签 {i+1}: '{text}'")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()