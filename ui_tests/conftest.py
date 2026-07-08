"""Playwright pytest 配置"""
import os
import pytest
from playwright.sync_api import sync_playwright


def _get_browser_options():
    """根据环境变量获取浏览器启动选项"""
    headless = os.environ.get('HEADLESS', 'false').lower() == 'true'
    slow_mo = int(os.environ.get('SLOW_MO', '300'))
    channel = os.environ.get('CHANNEL', 'chrome')
    options = {
        'headless': headless,
        'slow_mo': slow_mo,
        'channel': channel,
    }
    print(f"🔧 浏览器: {channel.upper()}, 有头模式: {not headless}")
    return options


@pytest.fixture(scope="session")
def browser():
    """启动浏览器"""
    launch_options = _get_browser_options()
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_options)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """创建新页面"""
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture(scope="session")
def api_request(browser):
    """创建 API 请求上下文"""
    context = browser.new_context()
    request = context.request
    yield request
    context.close()
