from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN

from handlers.start import start
from handlers.download import handle_link
from handlers.options import choose_type
from handlers.quality import choose_quality

app = ApplicationBuilder().token(TOKEN).build()

# handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(choose_type, pattern="video|audio"))
app.add_handler(CallbackQueryHandler(choose_quality, pattern="144|360|720|best"))

# 💥 error handler
async def error_handler(update, context):
    print("ERROR:", context.error)

app.add_error_handler(error_handler)

app.run_polling()
