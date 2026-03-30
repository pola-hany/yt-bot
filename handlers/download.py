from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.youtube import download_video

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    file = download_video(url)

    if not file:
        await msg.edit_text("❌ حصل مشكلة")
        return

    # حفظ المسار عشان نستخدمه بعدين
    context.user_data["video"] = file

    # زر التحويل
    keyboard = [
        [InlineKeyboardButton("🎧 تحويل لصوت", callback_data="to_audio")]
    ]

    await update.message.reply_video(
        video=open(file, "rb"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await msg.delete()