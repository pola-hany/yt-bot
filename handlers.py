"""
handlers.py — معالجات أحداث البوت
يحتوي على: /start، استقبال الروابط، الأزرار الـ Inline
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import main_menu_keyboard, video_quality_keyboard, back_keyboard
from messages import (
    WELCOME, CHOOSE_TYPE, CHOOSE_VIDEO_QUALITY, AUDIO_CONFIRM,
    DOWNLOADING, SENDING, INVALID_URL, DOWNLOAD_FAILED,
    FILE_TOO_LARGE, NO_URL_SAVED, GENERAL_ERROR
)
from downloader import download_video, download_audio
from utils import is_youtube_url, delete_file

logger = logging.getLogger(__name__)


# ─── /start ──────────────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start: رسالة الترحيب."""
    await update.message.reply_text(
        text=WELCOME,
        parse_mode=ParseMode.MARKDOWN,
    )


# ─── استقبال الرابط ──────────────────────────────────────────────────────────

async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج الرسائل النصية:
    - يتحقق من صحة الرابط
    - يحفظه في user_data
    - يعرض قائمة الاختيار
    """
    url = update.message.text.strip()

    if not is_youtube_url(url):
        await update.message.reply_text(
            text=INVALID_URL,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # حفظ الرابط مؤقتاً في بيانات المستخدم
    context.user_data["youtube_url"] = url

    await update.message.reply_text(
        text=CHOOSE_TYPE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(),
    )


# ─── معالج الأزرار الـ Inline ────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج ضغطات الأزرار:
    - type_video    → عرض قائمة الجودة
    - type_audio    → بدء تحميل الصوت
    - quality_*     → بدء تحميل الفيديو بالجودة المختارة
    - back_to_menu  → العودة للقائمة الرئيسية
    """
    query  = update.callback_query
    await query.answer()  # إيقاف مؤشر التحميل على الزر

    data = query.data
    url  = context.user_data.get("youtube_url")

    # ── رجوع للقائمة الرئيسية ──
    if data == "back_to_menu":
        if not url:
            await query.edit_message_text(
                text=NO_URL_SAVED,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        await query.edit_message_text(
            text=CHOOSE_TYPE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(),
        )
        return

    # ── اختيار نوع التحميل ──
    if data == "type_video":
        await query.edit_message_text(
            text=CHOOSE_VIDEO_QUALITY,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=video_quality_keyboard(),
        )
        return

    if data == "type_audio":
        if not url:
            await query.edit_message_text(text=NO_URL_SAVED, parse_mode=ParseMode.MARKDOWN)
            return
        await _handle_audio_download(query, url)
        return

    # ── اختيار جودة الفيديو ──
    if data.startswith("quality_"):
        quality_key = data.replace("quality_", "")   # e.g. "144p", "720p", "best"
        if not url:
            await query.edit_message_text(text=NO_URL_SAVED, parse_mode=ParseMode.MARKDOWN)
            return
        await _handle_video_download(query, url, quality_key)
        return


# ─── تحميل الفيديو ───────────────────────────────────────────────────────────

async def _handle_video_download(query, url: str, quality_key: str) -> None:
    """نفّذ تحميل الفيديو وأرسله للمستخدم."""
    # رسالة "جاري التحميل"
    await query.edit_message_text(
        text=DOWNLOADING,
        parse_mode=ParseMode.MARKDOWN,
    )

    file_path = await download_video(url, quality_key)

    if file_path == "TOO_LARGE":
        await query.edit_message_text(
            text=FILE_TOO_LARGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_keyboard(),
        )
        return

    if not file_path:
        await query.edit_message_text(
            text=DOWNLOAD_FAILED,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_keyboard(),
        )
        return

    # رسالة "جاري الإرسال"
    await query.edit_message_text(
        text=SENDING,
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        with open(file_path, "rb") as video_file:
            await query.message.reply_video(
                video=video_file,
                caption=(
                    f"🎥 *تم التحميل بنجاح!*\n"
                    f"📊 الجودة: `{quality_key}`\n\n"
                    "استمتع بالمشاهدة 🎬"
                ),
                parse_mode=ParseMode.MARKDOWN,
                supports_streaming=True,
            )
        # حذف رسالة "جاري الإرسال" بعد الإرسال
        await query.delete_message()

    except Exception as e:
        logger.error(f"خطأ أثناء إرسال الفيديو: {e}")
        await query.edit_message_text(
            text=GENERAL_ERROR,
            parse_mode=ParseMode.MARKDOWN,
        )
    finally:
        delete_file(file_path)


# ─── تحميل الصوت ─────────────────────────────────────────────────────────────

async def _handle_audio_download(query, url: str) -> None:
    """نفّذ تحميل الصوت وأرسله للمستخدم."""
    await query.edit_message_text(
        text=AUDIO_CONFIRM,
        parse_mode=ParseMode.MARKDOWN,
    )

    file_path = await download_audio(url)

    if file_path == "TOO_LARGE":
        await query.edit_message_text(
            text=FILE_TOO_LARGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_keyboard(),
        )
        return

    if not file_path:
        await query.edit_message_text(
            text=DOWNLOAD_FAILED,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_keyboard(),
        )
        return

    await query.edit_message_text(
        text=SENDING,
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        with open(file_path, "rb") as audio_file:
            await query.message.reply_audio(
                audio=audio_file,
                caption=(
                    "🎧 *تم تحميل الصوت بنجاح!*\n"
                    "📀 الصيغة: `MP3` | الجودة: `192 kbps`\n\n"
                    "استمتع بالاستماع 🎵"
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        await query.delete_message()

    except Exception as e:
        logger.error(f"خطأ أثناء إرسال الصوت: {e}")
        await query.edit_message_text(
            text=GENERAL_ERROR,
            parse_mode=ParseMode.MARKDOWN,
        )
    finally:
        delete_file(file_path)
