from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    try:
        # 启用请求拦截来查看响应
        all_responses = []
        
        def log_all_responses(response):
            all_responses.append({
                'url': response.url,
                'status': response.status,
                'headers': dict(response.headers)
            })
        
        page.on('response', log_all_responses)
        
        # 登录
        page.goto('https://buffalo-dev.shuishoukefu.com')
        page.wait_for_load_state('networkidle')
        
        page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
        page.fill('input[type="password"]', '123')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        
        print(f"登录后URL: {page.url}")
        print(f"页面标题: {page.title()}")
        
        # 检查所有响应
        print("\n=== 所有HTTP响应 ===")
        for resp in all_responses:
            print(f"\nURL: {resp['url']}")
            print(f"状态码: {resp['status']}")
            # 检查是否有Set-Cookie
            if 'set-cookie' in resp['headers']:
                print(f"Set-Cookie: {resp['headers']['set-cookie']}")
        
        # 检查当前页面的Cookie
        cookies = browser.contexts[0].cookies()
        print("\n=== 当前Cookie ===")
        for cookie in cookies:
            print(f"{cookie['name']}: {cookie['value'][:50]}...")
        
        # 尝试直接访问商家页面
        print("\n=== 尝试直接访问商家管理页面 ===")
        page.goto('https://buffalo-dev.shuishoukefu.com/custom/business')
        page.wait_for_load_state('networkidle')
        print(f"访问后URL: {page.url}")
        print(f"页面标题: {page.title()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()