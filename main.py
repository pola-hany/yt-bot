"""
main.py — نقطة تشغيل البوت
مسؤول عن: تهيئة البوت، تسجيل الـ handlers، بدء التشغيل
"""

import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, DOWNLOAD_DIR
from handlers import start_handler, url_handler, callback_handler

# ─── إعداد الـ Logging ───────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ─── معالج الأخطاء العام ─────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج مركزي لجميع الأخطاء غير المتوقعة.
    يمنع تعطّل البوت ويسجّل الخطأ في الـ logs.
    """
    logger.error("حدث خطأ أثناء معالجة تحديث:", exc_info=context.error)

    # إذا كان الخطأ Conflict — يعني في نسختان شغّالتان في نفس الوقت
    from telegram.error import Conflict
    if isinstance(context.error, Conflict):
        logger.critical(
            "⚠️ Conflict Error: تأكد من إيقاف جميع نسخ البوت الأخرى!\n"
            "على Railway: تأكد من وجود deployment واحد فقط نشط."
        )
        return

    # أرسل رسالة خطأ للمستخدم إن أمكن
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ حدث خطأ غير متوقع، يرجى المحاولة مجدداً."
            )
        except Exception:
            pass


# ─── دالة إعداد البوت ────────────────────────────────────────────────────────

def create_app() -> Application:
    """أنشئ وأعدّ تطبيق البوت."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError(
            "❌ لم يتم تعيين BOT_TOKEN!\n"
            "• على Railway: أضفه في Variables\n"
            "• محلياً: export BOT_TOKEN=your_token"
        )

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    # ── تسجيل الـ Handlers ──
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, url_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # ── معالج الأخطاء المركزي (يحل مشكلة "No error handlers are registered") ──
    app.add_error_handler(error_handler)

    logger.info("✅ تم تسجيل جميع الـ Handlers بنجاح")
    return app


# ─── نقطة الدخول ─────────────────────────────────────────────────────────────

def main() -> None:
    """شغّل البوت."""
    logger.info("🚀 جاري تشغيل البوت...")

    app = create_app()

    app.run_polling(
        poll_interval=2.0,
        # تجاهل الرسائل المتراكمة عند إعادة التشغيل
        drop_pending_updates=True,
        # تحديد أنواع التحديثات المطلوبة فقط (يقلل الضغط)
        allowed_updates=[
            Update.MESSAGE,
            Update.CALLBACK_QUERY,
        ],
    )

    logger.info("🛑 تم إيقاف البوت")


if __name__ == "__main__":
    main()
