import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from download_util import async_download_videos


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        await context.add_cookies([
            {
                "name": "auth_token",
                "value": "05280b9c94cab756ae4038e302e260131a038db8",
                "domain": ".x.com",
                "path": "/"
            }
        ])
        page = await context.new_page()

        keyword = '博彩'
        total_count = 20
        base_url = 'https://x.com'
        url = base_url + f'/search?q={keyword}&src=typed_query'



        # 用于存储视频 URL
        video_urls = []

        # 拦截网络请求的响应
        def handle_response(response):
            try:
                if (
                        response.request.resource_type == "media"
                        and "video" in response.headers.get("content-type", "")
                        and "video.twimg.com" in response.url
                ):
                    print(f"Found video URL: {response.url}")
                    video_urls.append(response.url)
            except Exception as e:
                print(f"Error handling response: {e}")

        # 设置监听器
        context.on("response", handle_response)

        await page.goto(url)

        page.wait_for_timeout(5000)  # 等待 5 秒以确保视频请求已发送

        print(video_urls)
        user_data = ()

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
