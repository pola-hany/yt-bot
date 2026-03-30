import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعت لينك فيديو من يوتيوب 🎥")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    await update.message.reply_text("جاري التحميل... ⏳")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': 'video.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video)

        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("حصل مشكلة 😢")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == "__main__":
    main()