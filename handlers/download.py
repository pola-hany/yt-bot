from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menus import main_menu

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ ابعت لينك يوتيوب صحيح")
        return

    context.user_data["url"] = url

    await update.message.reply_text(
        "اختار نوع التحميل 👇",
        reply_markup=main_menu()
    )