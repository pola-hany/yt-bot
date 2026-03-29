import re
import os
import asyncio

def is_youtube_url(url: str) -> bool:
    pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    return re.match(pattern, url) is not None

async def delete_file(path: str, delay: int = 30):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)