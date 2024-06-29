import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from download_util import async_download_videos


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        keyword = 'Chinese'
        total_count = 100
        base_url = 'https://cn.pornhub.com'
        url = base_url + f'/video/search?search={keyword}'

        await page.goto(url)

        await page.locator('//*[@id="modalWrapMTubes"]/div/div/button').click()

        dt = datetime.now().strftime("%Y%m%d%H%M")

        while True:
            # 在这里提取当前页面的数据
            current_page_data = await page.query_selector_all("//*[@class='title']//*[@href and not(@target)]")

            with open(f"{keyword}_{dt}.list", 'a+') as f:
                for i in current_page_data:
                    total_count -= 1
                    link = await i.get_attribute('href')
                    f.write(base_url + link + '\n')
                    # async_download_videos([base_url + link])

            if total_count <= 0:
                break

            # 检查是否存在“下一页”的按钮
            next_button = await page.query_selector("//*[@class='page_next omega']")  # 替换成你页面的“下一页”按钮的选择器

            if next_button:
                await next_button.click()
                # 等待页面加载完毕，可以根据页面具体情况调整等待方式
                await page.wait_for_load_state('domcontentloaded')
            else:
                break

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
