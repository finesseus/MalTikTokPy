from src.tiktokapipy import TikTokAPIWarning
# from src.tiktokapipy.api import TikTokAPI
from src.tiktokapipy.async_api import AsyncTikTokAPI

import asyncio
import aiohttp
import os

async def save_video(video):
    async with aiohttp.ClientSession() as session:
        async with session.get(video.video.download_addr) as resp:
            video_content = await resp.read()
            # Extract file extension from the video URL
            _, file_extension = os.path.splitext(video.video.download_addr)
            file_name = f"downloaded_video{file_extension}"
            # Save the video to a file
            with open(file_name, "wb") as file:
                file.write(video_content)
            return file_name

async def download_video(link):
    async with AsyncTikTokAPI() as api:
        video = await api.video(link)
        # if video.image_post:
        #     # downloaded_file = await save_slideshow(video)  # Assumes save_slideshow is defined elsewhere
        #     print('burrr')
        # else:
        downloaded_file = await save_video(video)
        return downloaded_file
    
if __name__ == "__main__":
    asyncio.run(download_video('https://www.tiktok.com/@officialmattebaes/video/7306011078352276769?_r=1&_t=8hjuNza2lbS'))
