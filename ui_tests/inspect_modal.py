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
            
            # 专门查找模态框内的元素
            modal = page.query_selector('.ant-modal')
            if modal:
                print("✓ 找到模态框")
                
                # 在模态框内查找输入框
                modal_inputs = modal.query_selector_all('input')
                print(f"\n模态框内找到 {len(modal_inputs)} 个输入框:")
                for i, inp in enumerate(modal_inputs):
                    id_attr = inp.get_attribute('id')
                    placeholder = inp.get_attribute('placeholder')
                    name_attr = inp.get_attribute('name')
                    print(f"  {i+1}. id='{id_attr}', placeholder='{placeholder}', name='{name_attr}'")
                
                # 在模态框内查找选择框
                modal_selects = modal.query_selector_all('.ant-select')
                print(f"\n模态框内找到 {len(modal_selects)} 个选择框:")
                for i, sel in enumerate(modal_selects):
                    id_attr = sel.get_attribute('id')
                    print(f"  {i+1}. id='{id_attr}'")
                
                # 在模态框内查找按钮
                modal_buttons = modal.query_selector_all('button')
                print(f"\n模态框内找到 {len(modal_buttons)} 个按钮:")
                for i, btn in enumerate(modal_buttons):
                    text = btn.text_content().strip() if btn.text_content() else ""
                    print(f"  {i+1}. '{text}'")
                
                # 保存模态框HTML
                modal_html = page.evaluate('(el) => el.outerHTML', modal)
                with open('/Users/lanwang/Documents/trae_projects/new World/modal_content.html', 'w', encoding='utf-8') as f:
                    f.write(modal_html)
                print("\n模态框HTML已保存")
                
            else:
                print("✗ 未找到模态框")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        page.wait_for_timeout(5000)
        browser.close()