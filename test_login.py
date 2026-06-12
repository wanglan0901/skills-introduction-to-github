from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    try:
        print("Step 1: 访问登录页面")
        page.goto('https://buffalo-dev.shuishoukefu.com')
        page.wait_for_load_state('networkidle')
        print(f"页面标题: {page.title()}")
        
        # 检查登录表单是否存在
        email_input = page.query_selector('input[placeholder="邮箱"]')
        pass_input = page.query_selector('input[type="password"]')
        
        if email_input and pass_input:
            print("Step 2: 填写登录表单")
            page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
            page.fill('input[type="password"]', '123')
            
            print("Step 3: 点击登录按钮")
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            
            print(f"登录后页面标题: {page.title()}")
            print(f"当前URL: {page.url}")
            
            # 检查是否登录成功（URL是否改变）
            if page.url != 'https://buffalo-dev.shuishoukefu.com/':
                print("✓ 登录成功")
                
                # 保存当前页面
                with open('after_login.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("页面内容已保存")
            else:
                print("✗ 登录失败，URL未改变")
        else:
            print("✗ 未找到登录表单")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()