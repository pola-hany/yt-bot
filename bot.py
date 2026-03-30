import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *مرحباً بك في بوت التحميل!*\n\n"
        "أرسل رابط فيديو من:\n"
        "• يوتيوب\n"
        "• انستقرام\n"
        "• تيك توك\n\n"
        "اختر نوع التحميل المناسب لك.",
        parse_mode='Markdown'
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data['url'] = url
    
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو 🎥", callback_data='video')],
        [InlineKeyboardButton("تحميل صوت فقط 🎵", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 اختر نوع التحميل:",
        reply_markup=reply_markup
    )

async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    download_type = query.data
    context.user_data['download_type'] = download_type
    
    keyboard = [
        [InlineKeyboardButton("أفضل جودة", callback_data='best')],
        [InlineKeyboardButton("جودة متوسطة (720p)", callback_data='medium')],
        [InlineKeyboardButton("جودة منخفضة (480p)", callback_data='low')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 اختر جودة التحميل:",
        reply_markup=reply_markup
    )

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    quality = query.data
    download_type = context.user_data.get('download_type')
    url = context.user_data.get('url')
    
    if not url:
        await query.edit_message_text("❌ الرابط غير صالح")
        return
    
    await query.edit_message_text("⏳ جاري التحميل...")
    
    try:
        if download_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'download.%(ext)s',
                'quiet': True,
            }
        else:
            format_quality = {
                'best': 'best[ext=mp4]',
                'medium': 'best[height<=720][ext=mp4]',
                'low': 'best[height<=480][ext=mp4]'
            }
            
            ydl_opts = {
                'format': format_quality.get(quality, 'best[ext=mp4]'),
                'outtmpl': 'download.%(ext)s',
                'quiet': True,
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if download_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
        
        # التحقق من حجم الملف (حد 50 ميجا للتليجرام)
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        if file_size > 50:
            await query.edit_message_text(f"⚠️ الملف كبير جداً! الحجم: {file_size:.1f} ميجابايت")
            os.remove(filename)
            return
        
        with open(filename, 'rb') as media_file:
            if download_type == 'audio':
                await query.message.reply_audio(
                    audio=media_file,
                    title=info.get('title', 'Audio')
                )
            else:
                await query.message.reply_video(
                    video=media_file,
                    caption=f"🎬 {info.get('title', 'Video')}"
                )
        
        os.remove(filename)
        await query.edit_message_text("✅ تم التحميل والإرسال بنجاح!")
        
    except Exception as e:
        print(f"Error: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء التحميل. تأكد من الرابط وحاول مرة أخرى.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(handle_quality, pattern='^(video|audio)$'))
    app.add_handler(CallbackQueryHandler(download_and_send, pattern='^(best|medium|low)$'))
    
    print("🤖 البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()