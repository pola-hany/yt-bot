from telegram.ext import ApplicationBuilder
from handlers.start import start
from handlers.download import handle_download
from config import TOKEN
from telegram.ext import CommandHandler, MessageHandler, filters

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))

    app.run_polling()

if __name__ == "__main__":
    main()
