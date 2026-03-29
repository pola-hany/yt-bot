"""
main.py — نقطة تشغيل البوت
مسؤول عن: تهيئة البوت، تسجيل الـ handlers، بدء التشغيل
"""

import logging
import os

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN, DOWNLOAD_DIR
from handlers import start_handler, url_handler, callback_handler

# ─── إعداد الـ Logging ───────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
# تقليل الـ logs الزائدة من مكتبات خارجية
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ─── دالة إعداد البوت ────────────────────────────────────────────────────────

def create_app() -> Application:
    """أنشئ وأعدّ تطبيق البوت."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError(
            "❌ لم يتم تعيين BOT_TOKEN!\n"
            "• ضعه في config.py\n"
            "• أو عبر متغير البيئة: export BOT_TOKEN=your_token"
        )

    # إنشاء مجلد التحميل عند البدء
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    # ── تسجيل الـ Handlers ──
    app.add_handler(CommandHandler("start", start_handler))

    # استقبال الروابط النصية
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, url_handler)
    )

    # استقبال ضغطات الأزرار
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("✅ تم تسجيل جميع الـ Handlers بنجاح")
    return app


# ─── نقطة الدخول ─────────────────────────────────────────────────────────────

def main() -> None:
    """شغّل البوت."""
    logger.info("🚀 جاري تشغيل البوت...")

    app = create_app()

    # Polling — مناسب للتطوير وبيئات الـ VPS
    app.run_polling(
        poll_interval=1.0,
        drop_pending_updates=True,   # تجاهل الرسائل القديمة عند إعادة التشغيل
    )

    logger.info("🛑 تم إيقاف البوت")


if __name__ == "__main__":
    main()
