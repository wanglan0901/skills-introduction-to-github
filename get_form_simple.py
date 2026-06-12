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
            page.wait_for_timeout(3000)
            
            # 使用 page.content() 获取完整页面
            content = page.content()
            
            # 查找所有 input 和 button 标签
            import re
            inputs = re.findall(r'<input[^>]*>', content)
            buttons = re.findall(r'<button[^>]*>.*?</button>', content)
            labels = re.findall(r'<label[^>]*>.*?</label>', content)
            
            print("=== 输入框 ===")
            for i, inp in enumerate(inputs[:20]):
                print(f"{i+1}. {inp}")
            
            print("\n=== 按钮 ===")
            for i, btn in enumerate(buttons[:20]):
                print(f"{i+1}. {btn}")
            
            print("\n=== 标签 ===")
            for i, label in enumerate(labels[:20]):
                print(f"{i+1}. {label}")
            
            # 保存到文件
            with open('form_raw.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("\n表单页面已保存到 form_raw.html")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()