"""
config.py — إعدادات البوت والمتغيرات البيئية
"""

import os

# ضع التوكن مباشرة هنا أو استخدم متغير البيئة
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7599336981:AAGy95fc8qSzsJk5DFPfK1xWHRXNN9fkoz0")

# الحد الأقصى لحجم الملف بالميجابايت قبل التحذير
MAX_FILE_SIZE_MB: int = 50

# مجلد التحميل المؤقت
DOWNLOAD_DIR: str = "downloads"

# الجودات المتاحة للفيديو
VIDEO_QUALITIES: dict = {
    "144p":  "bestvideo[height<=144]+bestaudio/best[height<=144]",
    "360p":  "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "best":  "bestvideo+bestaudio/best",
}

# جودة الصوت
AUDIO_FORMAT: str = "mp3"
AUDIO_QUALITY: str = "192"
