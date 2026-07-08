import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    html_path = "/Users/lanwang/Documents/trae_projects/new World/test_cases_preview.html"
    output_path = "/Users/lanwang/Documents/trae_projects/new World/测试用例_素材图片状态与视频生成按钮控制.png"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        file_url = f"file://{html_path}"
        await page.goto(file_url, wait_until="networkidle")
        
        # 获取页面完整高度
        full_height = await page.evaluate("document.body.scrollHeight")
        await page.set_viewport_size({"width": 1400, "height": full_height})
        
        # 全页截图
        await page.screenshot(path=output_path, full_page=True)
        print(f"截图已保存: {output_path}")
        
        await browser.close()

asyncio.run(main())
