"""UI 测试示例 - 使用 Playwright"""
import pytest
from playwright.sync_api import Page, expect


class TestUIBasics:
    """基础 UI 测试"""

    def test_打开网页(self, page: Page):
        """测试打开网页"""
        page.goto("https://example.com")
        expect(page).to_have_title("Example Domain")

    def test_click按钮(self, page: Page):
        """测试点击按钮"""
        page.goto("https://example.com")
        button = page.locator("h1")
        expect(button).to_be_visible()

    def test填写表单(self, page: Page):
        """测试填写表单"""
        page.goto("https://www.w3schools.com/html/tryit.asp?filename=tryhtml_form_submit")
        page.frame_locator("iframe[name='iframeResult']").locator("input[name='fname']").fill("Test User")
        page.frame_locator("iframe[name='iframeResult']").locator("input[name='fname']").fill("")


class TestUIActions:
    """UI 交互测试"""

    def test等待元素(self, page: Page):
        """测试等待元素加载"""
        page.goto("https://example.com")
        page.wait_for_selector("h1", state="visible")

    def test获取文本(self, page: Page):
        """测试获取元素文本"""
        page.goto("https://example.com")
        title = page.locator("h1").inner_text()
        assert title == "Example Domain"

    def test截图(self, page: Page, tmp_path):
        """测试截图功能"""
        page.goto("https://example.com")
        screenshot_path = tmp_path / "screenshot.png"
        page.screenshot(path=str(screenshot_path))
        assert screenshot_path.exists()
