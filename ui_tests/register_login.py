import asyncio
from playwright.async_api import async_playwright
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    base_url = "https://video-dev.shuishoukefu.com"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 步骤1: 打开注册页面
            logger.info("正在打开注册页面...")
            await page.goto(f"{base_url}/register")
            await page.wait_for_load_state('networkidle')
            logger.info("注册页面加载完成")
            
            # 步骤2: 填写注册信息
            logger.info("正在填写注册信息...")
            
            # 企业名称
            company_input = page.locator('input[placeholder*="企业名称"]')
            if await company_input.count() > 0:
                await company_input.fill('测试科技有限公司')
                logger.info("已填写企业名称")
            
            # 邮箱
            email_input = page.locator('input[type="email"], input[placeholder*="邮箱"]')
            test_email = f'test_{int(datetime.now().timestamp())}@example.com'
            if await email_input.count() > 0:
                await email_input.fill(test_email)
                logger.info(f"已填写邮箱: {test_email}")
            
            # 密码
            password_input = page.locator('input[type="password"], input[placeholder*="密码"]')
            if await password_input.count() > 0:
                await password_input.fill('Test123456')
                logger.info("已填写密码")
            
            # 手机号
            phone_input = page.locator('input[type="tel"], input[placeholder*="手机"]')
            if await phone_input.count() > 0:
                await phone_input.fill('13800138000')
                logger.info("已填写手机号")
            
            # 步骤3: 点击注册按钮
            logger.info("正在点击注册按钮...")
            register_btn = page.locator('button:has-text("注册")')
            if await register_btn.count() > 0:
                await register_btn.click()
                await page.wait_for_timeout(3000)
                
                success_alert = page.locator('.ant-message-success, .ant-alert-success')
                if await success_alert.count() > 0:
                    logger.info("✅ 注册成功！")
                else:
                    error_alert = page.locator('.ant-message-error, .ant-alert-error')
                    if await error_alert.count() > 0:
                        error_text = await error_alert.first.text_content()
                        logger.info(f"注册结果: {error_text}")
            
            # 步骤4: 跳转到登录页面
            logger.info("正在跳转到登录页面...")
            await page.goto(f"{base_url}/login")
            await page.wait_for_load_state('networkidle')
            logger.info("登录页面加载完成")
            
            # 步骤5: 填写登录信息
            logger.info("正在填写登录信息...")
            await email_input.fill(test_email)
            await password_input.fill('Test123456')
            
            # 步骤6: 点击登录按钮
            logger.info("正在点击登录按钮...")
            login_btn = page.locator('button:has-text("登录")')
            if await login_btn.count() > 0:
                await login_btn.click()
                await page.wait_for_timeout(3000)
                
                if 'login' not in page.url.lower():
                    logger.info("✅ 登录成功！")
                    logger.info(f"当前页面: {page.url}")
                else:
                    error_alert = page.locator('.ant-message-error, .ant-alert-error')
                    if await error_alert.count() > 0:
                        error_text = await error_alert.first.text_content()
                        logger.info(f"登录结果: {error_text}")
            
            logger.info("操作完成！")
            
        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
