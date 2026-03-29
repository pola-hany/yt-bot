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
    MAX_FILE_SIZE_MB, prepare_cookies,
)
from utils import ensure_download_dir, human_readable_size

logger = logging.getLogger(__name__)

MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ─── بناء الخيارات الأساسية ──────────────────────────────────────────────────

def _base_opts() -> dict:
    """الخيارات المشتركة لجميع عمليات التحميل."""
    opts = {
        "noplaylist":     True,
        "quiet":          True,
        "no_warnings":    True,
        "socket_timeout": 30,
        # tv_embedded + mweb يعملان بدون cookies ويتجاوزان "Sign in to confirm"
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded", "mweb"],
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) "
                "AppleWebKit/538.1 (KHTML, like Gecko) "
                "Version/6.0 TV Safari/538.1"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    # أضف cookies إن وُجدت
    cookie_path = prepare_cookies()
    if cookie_path:
        opts["cookiefile"] = cookie_path

    return opts


# ─── إيجاد الملف بعد التحميل ─────────────────────────────────────────────────

def _find_downloaded_file(output_template: str) -> Optional[str]:
    """ابحث عن الملف الذي أنشأه yt-dlp بناءً على الـ prefix."""
    base      = output_template.replace("%(ext)s", "")
    directory = os.path.dirname(base)
    prefix    = os.path.basename(base)
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
    حمّل الفيديو من يوتيوب.

    Returns:
        مسار الملف | "TOO_LARGE" | None عند الفشل
    """
    ensure_download_dir()

    file_id          = uuid.uuid4().hex
    output_template  = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    format_selector  = VIDEO_QUALITIES.get(quality_key, VIDEO_QUALITIES["best"])

    ydl_opts = {
        **_base_opts(),
        "format":               format_selector,
        "outtmpl":              output_template,
        "merge_output_format":  "mp4",
        "max_filesize":         MAX_BYTES,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_ydl, ydl_opts, url)

        file_path = _find_downloaded_file(output_template)
        if not file_path or not os.path.exists(file_path):
            logger.error("لم يُعثر على الملف بعد تحميل الفيديو")
            return None

        size = os.path.getsize(file_path)
        logger.info(f"✅ فيديو جاهز: {file_path} ({human_readable_size(size)})")

        if size > MAX_BYTES:
            logger.warning(f"الملف كبير جداً: {human_readable_size(size)}")
            return "TOO_LARGE"

        return file_path

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"خطأ yt-dlp (فيديو): {e}")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع (فيديو): {e}")
        return None


# ─── تحميل الصوت ─────────────────────────────────────────────────────────────

async def download_audio(url: str) -> Optional[str]:
    """
    حمّل الصوت بصيغة MP3.

    Returns:
        مسار الملف | "TOO_LARGE" | None عند الفشل
    """
    ensure_download_dir()

    file_id         = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        **_base_opts(),
        "format":  "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   AUDIO_FORMAT,
                "preferredquality": AUDIO_QUALITY,
            }
        ],
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_ydl, ydl_opts, url)

        # بعد FFmpeg يكون الامتداد mp3
        expected_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")
        if os.path.exists(expected_path):
            file_path = expected_path
        else:
            file_path = _find_downloaded_file(output_template)

        if not file_path or not os.path.exists(file_path):
            logger.error("لم يُعثر على ملف الصوت بعد التحميل")
            return None

        size = os.path.getsize(file_path)
        logger.info(f"✅ صوت جاهز: {file_path} ({human_readable_size(size)})")

        if size > MAX_BYTES:
            return "TOO_LARGE"

        return file_path

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"خطأ yt-dlp (صوت): {e}")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع (صوت): {e}")
        return None


# ─── تشغيل yt-dlp بشكل متزامن ────────────────────────────────────────────────

def _run_ydl(opts: dict, url: str) -> None:
    """يُستدعى من run_in_executor لتجنب تعطيل event loop."""
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
