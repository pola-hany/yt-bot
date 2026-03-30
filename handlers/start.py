from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بيك!\n\n"
        "ابعت لينك يوتيوب وأنا هخليك تختار:\n"
        "🎥 فيديو\n🎧 صوت\nوبعدين الجودة 😏"
    )