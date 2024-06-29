import os
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL

output_directory = 'download'
video_name = '%(title)s.%(ext)s'
output_path_template = os.path.join(output_directory, video_name)

# 创建全局线程池实例
global_executor = ThreadPoolExecutor(max_workers=os.cpu_count())


def download_by_yt_dlp(video_url, max_retries=3):
    ydl_opts = {
        'format': 'worst',
        'outtmpl': output_path_template,
        'merge_output_format': 'mp4',
        'noplaylist': True,  # 只下载单个视频，忽略播放列表
        'retries': max_retries,
        'socket_timeout': 30
    }
    retries = 0
    while retries < max_retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            print(f"Downloaded successfully: {video_url}")
            break
        except BaseException as e:
            retries += 1
            print(f"Failed to download {video_url}, attempt {retries}/{max_retries}. Error: {e}")


def async_download_videos(video_urls):
    # 提交每个视频下载任务到全局线程池
    [global_executor.submit(download_by_yt_dlp, url, 3) for url in video_urls]


if __name__ == "__main__":
    video_links = [
        "https://cn.pornhub.com/view_video.php?viewkey=665701e36604d",
        # "https://www.youtube.com/watch?v=A1m6fVnN1HI",
    ]
    async_download_videos(video_links)
