import yt_dlp
import os
import base64

def load_cookies():
    cookies_b64 = os.getenv("COOKIES_B64")
    
    if cookies_b64:
        try:
            with open("cookies.txt", "wb") as f:
                f.write(base64.b64decode(cookies_b64))
            return "cookies.txt"
        except Exception as e:
            print("Cookie decode error:", e)
    
    return None


def download_media(url, media_type, quality):
    try:
        cookie_file = load_cookies()

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

        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        # 💥 حل مشكلة utf-8
        ydl_opts['encoding'] = 'utf-8'
        ydl_opts['nocheckcertificate'] = True

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return None
