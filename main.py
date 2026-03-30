import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from handlers.start import start
from handlers.download import handle_download
from handlers.audio import convert_audio

TOKEN = os.getenv("TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
app.add_handler(CallbackQueryHandler(convert_audio, pattern="to_audio"))

app.run_polling()