import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN
from handlers import start, handle_url, button

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """تشغيل البوت"""
    if not TOKEN:
        logger.error("❌ لم يتم تعيين BOT_TOKEN في متغيرات البيئة")
        return
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(button))
    
    # مسح أي webhooks قديمة قبل البدء
    logger.info("🔄 جاري مسح الـ webhooks القديمة...")
    await app.bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("✅ البوت يعمل...")
    
    # بدء البوت مع polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # البقاء قيد التشغيل
    try:
        await asyncio.get_event_loop().create_future()
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
