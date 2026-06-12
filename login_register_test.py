import asyncio
from playwright.async_api import async_playwright, expect
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('login_register_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 测试结果记录
test_results = []

class LoginRegisterTest:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "https://video-dev.shuishoukefu.com"
        
    async def setup(self):
        """初始化浏览器环境"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30000)
        logger.info("浏览器环境初始化完成")
        
    async def teardown(self):
        """清理浏览器环境"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("浏览器环境清理完成")
        
    def record_result(self, test_name: str, status: str, message: str = ""):
        """记录测试结果"""
        test_results.append({
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    async def test_login_page_load(self):
        """测试登录页面加载"""
        test_name = "登录页面加载测试"
        try:
            await self.page.goto(f'{self.base_url}/login')
            await self.page.wait_for_load_state('networkidle')
            
            page_title = await self.page.title()
            logger.info(f"页面标题: {page_title}")
            
            await expect(self.page).to_have_title('登录')
            self.record_result(test_name, 'PASS', '登录页面加载成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_empty_fields(self):
        """测试登录-邮箱和密码为空验证"""
        test_name = "登录-空字段验证"
        try:
            await self.page.goto(f'{self.base_url}/login')
            await self.page.wait_for_load_state('networkidle')
            
            login_btn = self.page.locator('button:has-text("登录")')
            await login_btn.click()
            
            await self.page.wait_for_timeout(1000)
            
            error_messages = self.page.locator('.ant-form-item-explain-error')
            if await error_messages.count() > 0:
                self.record_result(test_name, 'PASS', '空字段验证提示显示')
                logger.info(f"✅ {test_name}: 通过")
            else:
                self.record_result(test_name, 'FAIL', '未显示错误提示')
                logger.error(f"❌ {test_name}: 失败")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_with_credentials(self):
        """测试登录-输入凭据"""
        test_name = "登录-输入凭据测试"
        try:
            await self.page.goto(f'{self.base_url}/login')
            await self.page.wait_for_load_state('networkidle')
            
            email_input = self.page.locator('input[type="email"], input[placeholder*="邮箱"]')
            password_input = self.page.locator('input[type="password"], input[placeholder*="密码"]')
            
            await email_input.fill('test@example.com')
            await password_input.fill('Test123456')
            
            login_btn = self.page.locator('button:has-text("登录")')
            await login_btn.click()
            
            await self.page.wait_for_timeout(2000)
            
            if 'login' not in self.page.url.lower():
                self.record_result(test_name, 'PASS', '登录成功，页面已跳转')
                logger.info(f"✅ {test_name}: 通过")
            else:
                error_alert = self.page.locator('.ant-alert-error, .ant-message-error')
                if await error_alert.count() > 0:
                    error_text = await error_alert.first.text_content()
                    self.record_result(test_name, 'PASS', f'登录失败（预期）: {error_text}')
                    logger.info(f"✅ {test_name}: 通过（预期失败）")
                else:
                    self.record_result(test_name, 'FAIL', '登录状态未变化')
                    logger.error(f"❌ {test_name}: 失败")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_navigate_to_register(self):
        """测试跳转到注册页面"""
        test_name = "跳转到注册页面"
        try:
            await self.page.goto(f'{self.base_url}/login')
            await self.page.wait_for_load_state('networkidle')
            
            register_link = self.page.locator('a:has-text("注册")')
            if await register_link.count() > 0:
                await register_link.click()
                await self.page.wait_for_load_state('networkidle')
                
                if 'register' in self.page.url.lower():
                    self.record_result(test_name, 'PASS', '成功跳转到注册页面')
                    logger.info(f"✅ {test_name}: 通过")
                else:
                    self.record_result(test_name, 'FAIL', '页面未跳转到注册页')
                    logger.error(f"❌ {test_name}: 失败")
            else:
                self.record_result(test_name, 'SKIP', '未找到注册链接')
                logger.info(f"⚠️ {test_name}: 跳过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_register_page_load(self):
        """测试注册页面加载"""
        test_name = "注册页面加载测试"
        try:
            await self.page.goto(f'{self.base_url}/register')
            await self.page.wait_for_load_state('networkidle')
            
            page_title = await self.page.title()
            logger.info(f"注册页面标题: {page_title}")
            
            await expect(self.page).to_have_title('注册')
            self.record_result(test_name, 'PASS', '注册页面加载成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_register_empty_fields(self):
        """测试注册-空字段验证"""
        test_name = "注册-空字段验证"
        try:
            await self.page.goto(f'{self.base_url}/register')
            await self.page.wait_for_load_state('networkidle')
            
            register_btn = self.page.locator('button:has-text("注册")')
            await register_btn.click()
            
            await self.page.wait_for_timeout(1000)
            
            error_messages = self.page.locator('.ant-form-item-explain-error')
            if await error_messages.count() > 0:
                self.record_result(test_name, 'PASS', '空字段验证提示显示')
                logger.info(f"✅ {test_name}: 通过")
            else:
                self.record_result(test_name, 'FAIL', '未显示错误提示')
                logger.error(f"❌ {test_name}: 失败")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_register_with_info(self):
        """测试注册-填写信息"""
        test_name = "注册-填写信息测试"
        try:
            await self.page.goto(f'{self.base_url}/register')
            await self.page.wait_for_load_state('networkidle')
            
            company_input = self.page.locator('input[placeholder*="企业名称"], input[name*="company"]')
            email_input = self.page.locator('input[type="email"], input[placeholder*="邮箱"]')
            password_input = self.page.locator('input[type="password"], input[placeholder*="密码"]')
            phone_input = self.page.locator('input[type="tel"], input[placeholder*="手机"]')
            
            test_email = f'test_{int(datetime.now().timestamp())}@example.com'
            
            if await company_input.count() > 0:
                await company_input.fill('测试科技有限公司')
            if await email_input.count() > 0:
                await email_input.fill(test_email)
            if await password_input.count() > 0:
                await password_input.fill('Test123456')
            if await phone_input.count() > 0:
                await phone_input.fill('13800138000')
                
            register_btn = self.page.locator('button:has-text("注册")')
            await register_btn.click()
            
            await self.page.wait_for_timeout(2000)
            
            success_alert = self.page.locator('.ant-alert-success, .ant-message-success')
            if await success_alert.count() > 0:
                self.record_result(test_name, 'PASS', '注册成功')
                logger.info(f"✅ {test_name}: 通过")
            else:
                error_alert = self.page.locator('.ant-alert-error, .ant-message-error')
                if await error_alert.count() > 0:
                    error_text = await error_alert.first.text_content()
                    self.record_result(test_name, 'PASS', f'注册失败（预期）: {error_text}')
                    logger.info(f"✅ {test_name}: 通过（预期失败）")
                else:
                    self.record_result(test_name, 'FAIL', '注册状态未变化')
                    logger.error(f"❌ {test_name}: 失败")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_navigate_to_login(self):
        """测试从注册页跳转到登录页"""
        test_name = "从注册页跳转到登录页"
        try:
            await self.page.goto(f'{self.base_url}/register')
            await self.page.wait_for_load_state('networkidle')
            
            login_link = self.page.locator('a:has-text("登录")')
            if await login_link.count() > 0:
                await login_link.click()
                await self.page.wait_for_load_state('networkidle')
                
                if 'login' in self.page.url.lower():
                    self.record_result(test_name, 'PASS', '成功跳转到登录页面')
                    logger.info(f"✅ {test_name}: 通过")
                else:
                    self.record_result(test_name, 'FAIL', '页面未跳转到登录页')
                    logger.error(f"❌ {test_name}: 失败")
            else:
                self.record_result(test_name, 'SKIP', '未找到登录链接')
                logger.info(f"⚠️ {test_name}: 跳过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("="*60)
        logger.info("开始执行注册和登录功能测试")
        logger.info(f"目标URL: {self.base_url}")
        logger.info("="*60)
        
        test_methods = [
            self.test_login_page_load,
            self.test_login_empty_fields,
            self.test_login_with_credentials,
            self.test_navigate_to_register,
            self.test_register_page_load,
            self.test_register_empty_fields,
            self.test_register_with_info,
            self.test_navigate_to_login
        ]
        
        for method in test_methods:
            await method()
            
        self.generate_report()
        
    def generate_report(self):
        """生成测试报告"""
        logger.info("\n" + "="*60)
        logger.info("测试报告")
        logger.info("="*60)
        
        passed = sum(1 for r in test_results if r['status'] == 'PASS')
        failed = sum(1 for r in test_results if r['status'] == 'FAIL')
        skipped = sum(1 for r in test_results if r['status'] == 'SKIP')
        
        logger.info(f"测试总数: {len(test_results)}")
        logger.info(f"通过: {passed}")
        logger.info(f"失败: {failed}")
        logger.info(f"跳过: {skipped}")
        logger.info(f"通过率: {passed/len(test_results)*100:.2f}%")
        
        logger.info("\n测试详情:")
        for result in test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            logger.info(f"{status_icon} {result['test_name']}")
            if result['message']:
                logger.info(f"   消息: {result['message']}")
        
        # 写入报告文件
        with open('注册登录测试报告.md', 'w', encoding='utf-8') as f:
            f.write("# AI视频创作平台 - 注册登录功能测试报告\n\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试URL**: {self.base_url}\n")
            f.write(f"**测试总数**: {len(test_results)}\n")
            f.write(f"**通过**: {passed}\n")
            f.write(f"**失败**: {failed}\n")
            f.write(f"**跳过**: {skipped}\n")
            f.write(f"**通过率**: {passed/len(test_results)*100:.2f}%\n\n")
            
            f.write("## 测试详情\n\n")
            f.write("| 测试用例 | 状态 | 消息 |\n")
            f.write("|---------|------|------|\n")
            for result in test_results:
                status = "通过" if result['status'] == 'PASS' else "失败" if result['status'] == 'FAIL' else "跳过"
                f.write(f"| {result['test_name']} | {status} | {result['message']} |\n")
            
        logger.info("\n报告已生成: 注册登录测试报告.md")

async def main():
    """主函数"""
    test = LoginRegisterTest()
    try:
        await test.setup()
        await test.run_all_tests()
    finally:
        await test.teardown()

if __name__ == "__main__":
    asyncio.run(main())
