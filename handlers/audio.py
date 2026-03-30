from telegram import Update
from telegram.ext import ContextTypes
from services.convert import convert_to_mp3
import os

async def convert_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    video_path = context.user_data.get("video")

    if not video_path:
        await query.message.reply_text("❌ مفيش فيديو")
        return

    msg = await query.message.reply_text("🎧 جاري التحويل...")

    audio = convert_to_mp3(video_path)

    with open(audio, "rb") as f:
        await query.message.reply_audio(f)

    await msg.delete()

    # تنظيف الملفات
    os.remove(video_path)
    os.remove(audio)