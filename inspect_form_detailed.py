from playwright.sync_api import sync_playwright
import re

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
            
            # 保存截图
            page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/form_before_submit.png')
            print("表单截图已保存")
            
            # 获取页面内容分析表单结构
            content = page.content()
            
            # 查找所有 input 标签
            input_pattern = r'<input[^>]*>'
            inputs = re.findall(input_pattern, content)
            print(f"\n找到 {len(inputs)} 个输入框:")
            for i, inp in enumerate(inputs):
                print(f"\n{i+1}. {inp}")
            
            # 查找所有 button 标签
            button_pattern = r'<button[^>]*>.*?</button>'
            buttons = re.findall(button_pattern, content)
            print(f"\n找到 {len(buttons)} 个按钮:")
            for i, btn in enumerate(buttons):
                print(f"\n{i+1}. {btn}")
            
            # 查找 label 标签
            label_pattern = r'<label[^>]*>.*?</label>'
            labels = re.findall(label_pattern, content)
            print(f"\n找到 {len(labels)} 个标签:")
            for i, label in enumerate(labels):
                print(f"\n{i+1}. {label}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        page.wait_for_timeout(5000)
        browser.close()