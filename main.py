import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from download_util import async_download_videos


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        keyword = 'blood'
        total_count = 20
        base_url = 'https://www.youtube.com'
        url = base_url + f'/results?search_query={keyword}'

        await page.goto(url)

        await page.get_by_label("搜索过滤条件").click()
        await page.locator('//*[@id="label"]/yt-formatted-string[contains(text(), "视频")]').click()

        await page.wait_for_timeout(1000)

        await page.get_by_label("搜索过滤条件").click()
        await page.get_by_role("link", name="4 分钟以下").click()

        user_data = {}

        while True:
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight);")

            # 查询是否存在文本内容为"无更多内容"的元素
            no_more_content = await page.query_selector('//*[@id="message"][contains(text(), "无更多结果")]')

            # 如果找到了匹配的元素，说明已无更多内容，跳出循环
            if no_more_content:
                break

            user_data = await page.query_selector_all('//*[@id="thumbnail"][@href]')

            if len(user_data) >= total_count:
                break

        dt = datetime.now().strftime("%Y%m%d%H%M")

        with open(f"{keyword}_{dt}.list", 'a+') as f:
            for i in user_data:
                link = await i.get_attribute('href')
                if link is not None:
                    f.write(base_url + link + '\n')
                    # 提交线程池下载视频
                    # async_download_videos([base_url + link])

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
