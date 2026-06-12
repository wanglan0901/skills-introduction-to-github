from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 记录网络请求
    responses = []
    
    def log_response(response):
        if 'login' in response.url.lower():
            responses.append({
                'url': response.url,
                'status': response.status
            })
    
    page.on('response', log_response)
    
    try:
        print("Step 1: 访问登录页面")
        page.goto('https://buffalo-dev.shuishoukefu.com')
        page.wait_for_load_state('networkidle')
        
        print("Step 2: 填写登录表单")
        page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
        page.fill('input[type="password"]', '123')
        
        print("Step 3: 点击登录按钮")
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # 等待网络请求完成
        page.wait_for_timeout(2000)
        
        print(f"\n当前URL: {page.url}")
        print(f"页面标题: {page.title()}")
        
        # 检查登录响应
        if responses:
            for resp in responses:
                print(f"\n登录响应URL: {resp['url']}")
                print(f"登录响应状态码: {resp['status']}")
                if resp['status'] == 200:
                    print("✓ 请求成功发送")
                else:
                    print(f"✗ 请求失败，状态码: {resp['status']}")
        else:
            print("✗ 未捕获到登录请求")
            
        # 检查是否有错误提示
        error_elements = page.query_selector_all('.ant-form-item-has-error, .ant-message-error')
        if error_elements:
            print("\n✗ 发现错误提示")
            for elem in error_elements:
                text = elem.text_content()
                if text:
                    print(f"  - {text.strip()}")
        else:
            print("\n✓ 未发现错误提示")
            
        # 检查是否需要验证码
        captcha = page.query_selector('img[src*="captcha"], input[placeholder*="验证码"]')
        if captcha:
            print("\n✗ 发现验证码元素，需要手动处理")
        else:
            print("\n✓ 未发现验证码")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()