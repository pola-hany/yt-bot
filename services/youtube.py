import yt_dlp
import os
from config import VIDEO_FILE


def download_video(url: str):
    """
    تحميل فيديو من يوتيوب
    """
    try:
        # 🧹 لو في ملف قديم يتم مسحه
        if os.path.exists(VIDEO_FILE):
            os.remove(VIDEO_FILE)

        # ⚙️ إعدادات التحميل (مبنية على كودك)
        ydl_opts = {
            'format': 'best[ext=mp4]',  # زي ما انت كاتب
            'outtmpl': VIDEO_FILE,      # اسم ثابت من config
            'quiet': True,              # بدون spam logs
            'noplaylist': True          # يمنع تحميل playlist
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # 📌 تأكد إن فيه نتيجة
            if not info:
                return None

        # ✅ رجع اسم الملف
        return VIDEO_FILE

    except Exception as e:
        print("YOUTUBE ERROR:", e)
        return None