from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menus import quality_menu

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["type"] = query.data

    await query.message.reply_text(
        "اختار الجودة 👇",
        reply_markup=quality_menu()
    )