from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    try:
        page.goto('https://buffalo-dev.shuishoukefu.com')
        page.wait_for_load_state('networkidle')
        
        page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
        page.fill('input[type="password"]', '123')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        page.goto('https://buffalo-dev.shuishoukefu.com/custom/business')
        page.wait_for_load_state('networkidle')
        
        # 等待页面完全加载
        page.wait_for_timeout(2000)
        
        # 查找创建按钮
        create_btn = page.query_selector('button:has-text("创建")')
        if create_btn:
            create_btn.click()
            page.wait_for_timeout(3000)
            
            # 获取页面内容并保存
            content = page.content()
            with open('form_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("页面内容已保存到 form_page.html")
    
    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path='error.png')
    finally:
        browser.close()