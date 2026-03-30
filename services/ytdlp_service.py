import yt_dlp
import os

def download_media(url, media_type, quality):
    try:
        cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

        # 🎯 اختيار الجودة بشكل ذكي
        if media_type == "audio":
            fmt = "bestaudio/best"
        else:
            if quality == "best":
                fmt = "bestvideo+bestaudio/best"
            else:
                fmt = f"bestvideo[height<={quality}]+bestaudio/best"

        ydl_opts = {
            'format': fmt,
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'nocheckcertificate': True,

            # 💣 أهم حاجة
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            },

            # 🔥 حل مشاكل signature
            'compat_opts': ['no-youtube-unavailable-videos'],
        }

        # 👇 الكوكيز
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return None