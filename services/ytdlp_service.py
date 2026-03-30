from telegram import Update
from telegram.ext import ContextTypes
from services.ytdlp_service import download_media

async def choose_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data
    url = context.user_data.get("url")
    media_type = context.user_data.get("type")

    msg = await query.message.reply_text("⏳ جاري التحميل...")

    file_path = download_media(url, media_type, quality)

    if not file_path:
        await msg.edit_text("❌ حصل خطأ")
        return

    if media_type == "video":
        with open(file_path, "rb") as f:
            await query.message.reply_video(f)
    else:
        with open(file_path, "rb") as f:
            await query.message.reply_audio(f)

    await msg.delete()