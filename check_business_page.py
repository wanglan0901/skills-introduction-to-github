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
        
        # 获取页面标题
        print(f"页面标题: {page.title()}")
        print(f"当前URL: {page.url}")
        
        # 获取所有按钮
        buttons = page.query_selector_all('button')
        print(f"\n=== 页面上的按钮 ===")
        print(f"共找到 {len(buttons)} 个按钮")
        for i, btn in enumerate(buttons):
            text = btn.text_content().strip() if btn.text_content() else ""
            print(f"{i+1}. 文本: '{text}'")
        
        # 获取所有链接
        links = page.query_selector_all('a')
        print(f"\n=== 页面上的链接 ===")
        print(f"共找到 {len(links)} 个链接")
        for i, link in enumerate(links[:10]):  # 只显示前10个
            text = link.text_content().strip() if link.text_content() else ""
            href = link.get_attribute('href')
            print(f"{i+1}. 文本: '{text}', 链接: {href}")
        
        # 保存页面内容
        with open('business_page.html', 'w', encoding='utf-8') as f:
            f.write(page.content())
        print("\n页面内容已保存到 business_page.html")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()