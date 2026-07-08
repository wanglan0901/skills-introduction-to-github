import asyncio
from playwright.async_api import async_playwright, Page, expect
import pytest
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smoke_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 测试结果记录
test_results = []

class SmokeTest:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def setup(self):
        """初始化浏览器环境"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=500)
        self.context = await self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        self.page = await self.context.new_page()
        self.page.set_default_timeout(15000)
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
        """TC-001前置条件：验证登录页面加载"""
        test_name = "TC-001: 用户登录-页面加载验证"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/login_page.html')
            await expect(self.page.locator('.login-title')).to_have_text('用户登录')
            await expect(self.page.locator('#login-form')).to_be_visible()
            self.record_result(test_name, 'PASS', '登录页面加载成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_empty_email(self):
        """TC-002: 用户登录-邮箱为空验证"""
        test_name = "TC-002: 用户登录-邮箱为空验证"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/login_page.html')
            login_btn = self.page.locator('button:has-text("登录")')
            await login_btn.click()
            
            email_input = self.page.locator('input[type="email"]')
            await expect(email_input).to_have_class('ant-input ant-input-status-error')
            self.record_result(test_name, 'PASS', '邮箱为空验证成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_empty_password(self):
        """TC-003: 用户登录-密码为空验证"""
        test_name = "TC-003: 用户登录-密码为空验证"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/login_page.html')
            
            email_input = self.page.locator('input[type="email"]')
            await email_input.fill('test@example.com')
            
            login_btn = self.page.locator('button:has-text("登录")')
            await login_btn.click()
            
            password_input = self.page.locator('input[type="password"]')
            await expect(password_input).to_have_class('ant-input ant-input-status-error')
            self.record_result(test_name, 'PASS', '密码为空验证成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_error_clear(self):
        """TC-004: 用户登录-输入时错误清除"""
        test_name = "TC-004: 用户登录-输入时错误清除"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/login_page.html')
            
            login_btn = self.page.locator('button:has-text("登录")')
            await login_btn.click()
            
            email_input = self.page.locator('input[type="email"]')
            await expect(email_input).to_have_class('ant-input ant-input-status-error')
            
            await email_input.fill('test@example.com')
            await expect(email_input).not_to_have_class('ant-input-status-error')
            self.record_result(test_name, 'PASS', '错误样式清除成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_login_to_register_link(self):
        """TC-005: 用户登录-跳转到注册页面"""
        test_name = "TC-005: 用户登录-跳转到注册页面"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/login_page.html')
            
            register_link = self.page.locator('a:has-text("去注册")')
            if await register_link.count() > 0:
                await register_link.click()
                self.record_result(test_name, 'PASS', '跳转到注册页面成功')
                logger.info(f"✅ {test_name}: 通过")
            else:
                self.record_result(test_name, 'SKIP', '未找到注册链接')
                logger.info(f"⚠️ {test_name}: 跳过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_after_login_page(self):
        """TC-014: 视频列表-页面加载显示"""
        test_name = "TC-014: 视频列表-页面加载显示"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/after_login.html')
            
            await expect(self.page.locator('h1, h2, h3').first).to_be_visible()
            create_btn = self.page.locator('button:has-text("创建视频")')
            if await create_btn.count() > 0:
                await expect(create_btn).to_be_enabled()
            
            self.record_result(test_name, 'PASS', '视频列表页面加载成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_modal_display(self):
        """测试弹窗功能"""
        test_name = "弹窗功能测试"
        try:
            await self.page.set_content(open('/Users/lanwang/Documents/trae_projects/new World/modal_content.html').read())
            
            modal = self.page.locator('.ant-modal')
            await expect(modal).to_be_visible()
            
            close_btn = self.page.locator('.ant-modal-close')
            await close_btn.click()
            
            await expect(modal).to_be_hidden()
            self.record_result(test_name, 'PASS', '弹窗关闭功能正常')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def test_business_page(self):
        """测试业务页面"""
        test_name = "业务页面测试"
        try:
            await self.page.goto('file:///Users/lanwang/Documents/trae_projects/new World/business_page.html')
            await expect(self.page.locator('#root')).to_be_visible()
            self.record_result(test_name, 'PASS', '业务页面加载成功')
            logger.info(f"✅ {test_name}: 通过")
        except Exception as e:
            self.record_result(test_name, 'FAIL', str(e))
            logger.error(f"❌ {test_name}: 失败 - {str(e)}")
            
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("="*60)
        logger.info("开始执行冒烟测试")
        logger.info("="*60)
        
        test_methods = [
            self.test_login_page_load,
            self.test_login_empty_email,
            self.test_login_empty_password,
            self.test_login_error_clear,
            self.test_login_to_register_link,
            self.test_after_login_page,
            self.test_modal_display,
            self.test_business_page
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
        with open('测试报告.md', 'w', encoding='utf-8') as f:
            f.write("# AI视频创作平台 - 冒烟测试报告\n\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
            
        logger.info("\n报告已生成: 测试报告.md")

async def main():
    """主函数"""
    test = SmokeTest()
    try:
        await test.setup()
        await test.run_all_tests()
    finally:
        await test.teardown()

if __name__ == "__main__":
    asyncio.run(main())
