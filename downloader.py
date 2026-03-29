"""
downloader.py — منطق التحميل باستخدام yt-dlp
مسؤول عن: تحميل الفيديو والصوت، إدارة الملفات المؤقتة
"""

import os
import uuid
import logging
import asyncio
from typing import Optional

import yt_dlp

from config import (
    DOWNLOAD_DIR, VIDEO_QUALITIES, AUDIO_FORMAT, AUDIO_QUALITY,
    MAX_FILE_SIZE_MB, COOKIES_FILE, COOKIES_FROM_BROWSER,
)
from utils import ensure_download_dir, human_readable_size

logger = logging.getLogger(__name__)

# الحد الأقصى للحجم بالبايت
MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ─── بناء خيارات الـ Cookies ─────────────────────────────────────────────────

def _cookies_opts() -> dict:
    """
    أرجع خيارات الـ cookies المناسبة حسب الإعداد في config.py.

    الأولوية:
    1. cookies_from_browser  (جهاز محلي)
    2. cookiefile            (ملف يدوي — مناسب للسيرفر)
    3. لا شيء                (بدون cookies)
    """
    if COOKIES_FROM_BROWSER:
        logger.info(f"🍪 استخدام cookies من المتصفح: {COOKIES_FROM_BROWSER}")
        return {"cookiesfrombrowser": (COOKIES_FROM_BROWSER,)}

    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        logger.info(f"🍪 استخدام ملف cookies: {COOKIES_FILE}")
        return {"cookiefile": COOKIES_FILE}

    logger.warning("⚠️ لا توجد cookies — قد يفشل التحميل لبعض الفيديوهات")
    return {}


# ─── إعدادات yt-dlp المشتركة ─────────────────────────────────────────────────

def _base_opts() -> dict:
    """الخيارات الأساسية المشتركة بين تحميل الفيديو والصوت."""
    opts = {
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        # إعدادات لتقليل احتمال الحظر
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }
    opts.update(_cookies_opts())
    return opts


# ─── دالة مساعدة: إيجاد الملف المحمّل ──────────────────────────────────────

def _find_downloaded_file(output_template: str) -> Optional[str]:
    """
    ابحث عن الملف الذي حمّله yt-dlp بناءً على قالب الاسم.
    yt-dlp قد يضيف امتداداً مختلفاً، لذا نبحث بالـ prefix.
    """
    base = output_template.replace("%(ext)s", "")
    directory = os.path.dirname(base)
    prefix = os.path.basename(base)

    try:
        for fname in os.listdir(directory):
            if fname.startswith(prefix):
                return os.path.join(directory, fname)
    except Exception as e:
        logger.error(f"خطأ في البحث عن الملف: {e}")
    return None


# ─── تحميل الفيديو ───────────────────────────────────────────────────────────

async def download_video(url: str, quality_key: str) -> Optional[str]:
    """
    حمّل الفيديو من يوتيوب بالجودة المطلوبة.

    Args:
        url: رابط الفيديو
        quality_key: مفتاح الجودة من VIDEO_QUALITIES (144p, 360p, 720p, best)

    Returns:
        مسار الملف المحمّل، أو None عند الفشل، أو "TOO_LARGE" إذا تجاوز الحد
    """
    ensure_download_dir()

    file_id = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    format_selector = VIDEO_QUALITIES.get(quality_key, VIDEO_QUALITIES["best"])

    ydl_opts = {
        **_base_opts(),
        "format": format_selector,
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "max_filesize": MAX_BYTES,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_ydl, ydl_opts, url)

        file_path = _find_downloaded_file(output_template)

        if not file_path or not os.path.exists(file_path):
            logger.error("لم يُعثر على الملف بعد التحميل")
            return None

        size = os.path.getsize(file_path)
        logger.info(f"✅ تم تحميل الفيديو: {file_path} ({human_readable_size(size)})")

        if size > MAX_BYTES:
            logger.warning(f"الملف كبير جداً: {human_readable_size(size)}")
            return "TOO_LARGE"

        return file_path

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"خطأ yt-dlp أثناء التحميل: {e}")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء تحميل الفيديو: {e}")
        return None


# ─── تحميل الصوت ─────────────────────────────────────────────────────────────

async def download_audio(url: str) -> Optional[str]:
    """
    حمّل الصوت فقط من يوتيوب بصيغة MP3.

    Args:
        url: رابط الفيديو

    Returns:
        مسار ملف الصوت المحمّل، أو None عند الفشل
    """
    ensure_download_dir()

    file_id = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        **_base_opts(),
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_FORMAT,
                "preferredquality": AUDIO_QUALITY,
            }
        ],
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_ydl, ydl_opts, url)

        expected_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

        if os.path.exists(expected_path):
            file_path = expected_path
        else:
            file_path = _find_downloaded_file(output_template)

        if not file_path or not os.path.exists(file_path):
            logger.error("لم يُعثر على ملف الصوت بعد التحميل")
            return None

        size = os.path.getsize(file_path)
        logger.info(f"✅ تم تحميل الصوت: {file_path} ({human_readable_size(size)})")

        if size > MAX_BYTES:
            return "TOO_LARGE"

        return file_path

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"خطأ yt-dlp أثناء تحميل الصوت: {e}")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء تحميل الصوت: {e}")
        return None


# ─── دالة مساعدة للتشغيل المتزامن ───────────────────────────────────────────

def _run_ydl(opts: dict, url: str) -> None:
    """شغّل yt-dlp بشكل متزامن (يُستدعى من executor)."""
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
