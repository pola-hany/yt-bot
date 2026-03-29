"""
utils.py — دوال مساعدة مشتركة
"""

import os
import re
import logging
from config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

# ─── التحقق من رابط يوتيوب ───────────────────────────────────────────────────

YOUTUBE_REGEX = re.compile(
    r"(https?://)?"
    r"(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/)"
    r"[\w\-]{11}"
)

def is_youtube_url(url: str) -> bool:
    """تحقق من أن الرابط رابط يوتيوب صحيح."""
    return bool(YOUTUBE_REGEX.search(url))


# ─── إدارة مجلد التحميل ──────────────────────────────────────────────────────

def ensure_download_dir() -> None:
    """تأكد من وجود مجلد التحميل المؤقت."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def delete_file(path: str) -> None:
    """احذف الملف بعد الإرسال، مع تجاهل الأخطاء."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
            logger.info(f"🗑️ تم حذف الملف: {path}")
    except Exception as e:
        logger.warning(f"تعذّر حذف الملف {path}: {e}")


def human_readable_size(size_bytes: int) -> str:
    """تحويل حجم الملف إلى صيغة مقروءة."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.1f} GB"
