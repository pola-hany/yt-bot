import yt_dlp
import os

def download_media(url, media_type, quality):
    try:
        cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

        if media_type == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'quiet': True
            }
        else:
            if quality == "best":
                fmt = "best"
            else:
                fmt = f"bestvideo[height<={quality}]+bestaudio/best"

            ydl_opts = {
                'format': fmt,
                'outtmpl': 'video.%(ext)s',
                'quiet': True
            }

        # 👇 أهم سطر
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return None
