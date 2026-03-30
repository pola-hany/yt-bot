from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 أهلاً بيك في بوت التحميل 🔥\n\n"
        "📥 ابعت لينك فيديو من يوتيوب\n"
        "🎧 وبعد ما الفيديو يتحمل تقدر تحوله لصوت بسهولة\n\n"
        "🚀 البوت سريع وبسيط وجاهز يخدمك"
    )

    await update.message.reply_text(text)