"""
config.py — إعدادات البوت والمتغيرات البيئية
"""

import os
import base64
import logging

logger = logging.getLogger(__name__)

# ─── توكن البوت ──────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7599336981:AAGy95fc8qSzsJk5DFPfK1xWHRXNN9fkoz0")

# ─── إعدادات الملفات ─────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB: int = 50
DOWNLOAD_DIR: str    = "downloads"

# ─── جودات الفيديو ───────────────────────────────────────────────────────────
# نستخدم fallback تلقائي بـ / لو الجودة المطلوبة مش متاحة
VIDEO_QUALITIES: dict = {
    "144p": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=144]+bestaudio/best[height<=144]/best",
    "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
}

# ─── إعدادات الصوت ───────────────────────────────────────────────────────────
AUDIO_FORMAT:  str = "mp3"
AUDIO_QUALITY: str = "192"

# ─── إعدادات Cookies لـ Railway ──────────────────────────────────────────────
#
# على Railway لا يمكن رفع ملفات مباشرة ولا استخدام متصفح.
# الحل: حوّل cookies.txt إلى Base64 وأضفه كـ Environment Variable.
#
# خطوات الإعداد:
#   1. استخرج cookies.txt من متصفحك (وأنت مسجّل دخول على يوتيوب)
#   2. حوّله لـ Base64:
#        Linux/Mac:  base64 -w 0 cookies.txt
#        Windows PowerShell: [Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt"))
#   3. على Railway → Variables → أضف:
#        COOKIES_B64 = <النص الناتج>
#
# البوت سيفك التشفير تلقائياً ويكتب الملف عند التشغيل.
# ─────────────────────────────────────────────────────────────────────────────

COOKIES_B64:  str = os.getenv("COOKIES_B64", "")          # Base64 (Railway)
COOKIES_FILE: str = os.getenv("COOKIES_FILE", "cookies.txt")  # مسار الملف المحلي


def prepare_cookies() -> str | None:
    """
    جهّز ملف الـ cookies وأرجع مساره، أو None إن لم يكن متاحاً.
    الأولوية: COOKIES_B64 (Railway) ← COOKIES_FILE (محلي)
    """
    # ── الأولوية 1: فك Base64 من متغير البيئة ──
    if COOKIES_B64:
        cookie_path = os.path.join(DOWNLOAD_DIR, "yt_cookies.txt")
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            decoded = base64.b64decode(COOKIES_B64)
            with open(cookie_path, "wb") as f:
                f.write(decoded)
            logger.info(f"🍪 تم استعادة cookies من COOKIES_B64 → {cookie_path}")
            return cookie_path
        except Exception as e:
            logger.error(f"فشل فك تشفير COOKIES_B64: {e}")

    # ── الأولوية 2: ملف محلي ──
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        logger.info(f"🍪 استخدام ملف cookies: {COOKIES_FILE}")
        return COOKIES_FILE

    logger.warning("⚠️ لا توجد cookies — التحميل قد يفشل لبعض الفيديوهات")
    return None
