from playwright.sync_api import sync_playwright
import time

def test_create_business():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            # 1. 访问登录页面
            print("步骤1: 访问登录页面")
            page.goto("https://buffalo-dev.shuishoukefu.com")
            page.wait_for_load_state('networkidle')
            
            # 2. 输入登录信息
            print("步骤2: 输入登录账号")
            page.fill('input[placeholder="邮箱"]', 'wanglan1@shuishoukefu.com')
            page.fill('input[type="password"]', '123')
            
            # 3. 点击登录按钮
            print("步骤3: 点击登录按钮")
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            
            # 4. 导航到商家管理页面
            print("步骤4: 导航到商家管理页面")
            page.goto("https://buffalo-dev.shuishoukefu.com/custom/business")
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            
            # 查看页面上有多少个merchantName输入框
            all_merchant_inputs = page.query_selector_all('#merchantName')
            print(f"\n页面上共有 {len(all_merchant_inputs)} 个商家名称输入框")
            
            # 5. 点击添加商家按钮
            print("\n步骤5: 点击添加商家按钮")
            add_btn = page.query_selector('button:has-text("添加商家")')
            if add_btn:
                add_btn.click()
                page.wait_for_timeout(3000)
                print("✓ 成功点击添加商家按钮")
            else:
                print("✗ 未找到添加商家按钮")
                browser.close()
                return
            
            # 获取弹窗
            modal = page.query_selector('.ant-modal')
            if modal:
                print("\n✓ 找到弹窗")
                
                # 查看弹窗内的输入框
                modal_inputs = modal.query_selector_all('input')
                print(f"弹窗内有 {len(modal_inputs)} 个输入框")
                
                # 查看弹窗内的商家名称输入框
                merchant_input = modal.query_selector('#merchantName')
                if merchant_input:
                    print("✓ 弹窗内找到商家名称输入框")
                    # 获取该输入框的完整HTML
                    html = page.evaluate('(el) => el.outerHTML', merchant_input)
                    print(f"输入框HTML: {html[:150]}...")
                    
                    # 填写
                    merchant_input.fill('测试商家_debug')
                    page.wait_for_timeout(500)
                    
                    # 验证是否填写成功
                    value = merchant_input.input_value()
                    print(f"填写后的值: '{value}'")
                    
                    # 截图
                    page.screenshot(path='/Users/lanwang/Documents/trae_projects/new World/debug_screenshot.png')
                    print("✓ 已保存调试截图")
                else:
                    print("✗ 弹窗内未找到商家名称输入框")
                    
                # 填写其他字段
                modal.query_selector('#aliasName').fill('测试商家')
                modal.query_selector('#mobile').fill('13800138000')
                modal.query_selector('#wechatNumber').fill('test_wechat')
                
                # 点击确认
                confirm_btn = modal.query_selector('button:has-text("确 认")')
                if confirm_btn:
                    confirm_btn.click()
                    page.wait_for_timeout(3000)
                    print("✓ 点击确认按钮")
                    
                    # 检查结果
                    modal_after = page.query_selector('.ant-modal')
                    if modal_after:
                        errors = modal_after.query_selector_all('.ant-form-item-explain-error')
                        if errors:
                            for err in errors:
                                print(f"错误: {err.text_content()}")
                        else:
                            print("弹窗仍在，无错误提示")
                    else:
                        print("✓✓ 创建成功！")
            else:
                print("✗ 未找到弹窗")
                
        except Exception as e:
            print(f"\n✗ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n调试完成")
            time.sleep(5)

if __name__ == "__main__":
    test_create_business()