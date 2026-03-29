from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu, quality_menu
from downloader import Downloader
from utils import is_youtube_url, delete_file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🎬 *مرحباً بك في بوت التحميل*

📌 *الطريقة:*
1️⃣ أرسل رابط يوتيوب
2️⃣ اختر فيديو او صوت
3️⃣ اختر الجودة

⚡ البوت يعمل بسرعة وسهولة

🚀 *أرسل الرابط الآن*"""
    
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=main_menu())

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not is_youtube_url(url):
        await update.message.reply_text("❌ رابط غير صالح\nأرسل رابط يوتيوب صحيح")
        return
    
    context.user_data['url'] = url
    
    msg = await update.message.reply_text("🔄 جلب المعلومات...")
    
    try:
        info = Downloader.get_info(url)
        
        # حساب المدة بالدقائق
        duration = info.get('duration', 0)
        duration_min = duration // 60 if duration else 0
        duration_sec = duration % 60 if duration else 0
        
        text = f"✅ *{info.get('title', 'فيديو')[:50]}*\n"
        text += f"⏱️ المدة: {duration_min}:{duration_sec:02d}\n"
        text += f"👤 القناة: {info.get('uploader', 'غير معروف')[:30]}\n\n"
        text += f"اختر نوع التحميل:"
        
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=main_menu())
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            error_msg = "يوتيوب يطلب تحديث، جرب رابط فيديو آخر أو انتظر قليلاً"
        await msg.edit_text(f"❌ {error_msg[:150]}\nحاول مرة أخرى")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "video":
        context.user_data['type'] = 'video'
        await query.edit_message_text("🎥 اختر الجودة:", reply_markup=quality_menu())
    
    elif query.data == "audio":
        context.user_data['type'] = 'audio'
        await query.edit_message_text("🎧 جاري تحميل الصوت...\nقد يستغرق هذا دقيقة")
        await download(update, context)
    
    elif query.data in ['144p', '360p', '720p', 'best']:
        context.user_data['quality'] = query.data
        quality_names = {'144p': '144p', '360p': '360p', '720p': '720p', 'best': 'أفضل جودة'}
        await query.edit_message_text(f"✅ جودة {quality_names[query.data]}\n🔄 جاري التحميل...\nقد يستغرق هذا دقيقة")
        await download(update, context)
    
    elif query.data == "back":
        context.user_data.pop('type', None)
        context.user_data.pop('quality', None)
        await query.edit_message_text("اختر نوع التحميل:", reply_markup=main_menu())

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    url = context.user_data.get('url')
    download_type = context.user_data.get('type')
    quality = context.user_data.get('quality', 'best')
    
    if not url:
        await query.edit_message_text("❌ الرابط غير موجود، أرسل رابط جديد")
        return
    
    try:
        if download_type == 'video':
            file, title = Downloader.download_video(url, quality)
            
            # التحقق من وجود الملف
            import os
            if not os.path.exists(file):
                raise Exception("فشل إنشاء الملف")
            
            # إرسال الفيديو
            with open(file, 'rb') as f:
                await query.message.reply_document(
                    document=f, 
                    filename=f"{title[:50]}.mp4", 
                    caption=f"✅ تم التحميل بنجاح 🎥\n📹 {title[:40]}"
                )
        else:
            file, title = Downloader.download_audio(url)
            
            if not os.path.exists(file):
                raise Exception("فشل إنشاء ملف الصوت")
            
            with open(file, 'rb') as f:
                await query.message.reply_document(
                    document=f, 
                    filename=f"{title[:50]}.mp3", 
                    caption=f"✅ تم التحميل بنجاح 🎧\n🎵 {title[:40]}"
                )
        
        # حذف رسالة التحميل
        await query.delete()
        
        # حذف الملف بعد الإرسال
        await delete_file(file)
        
        # إظهار القائمة الرئيسية
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🎬 للتحميل مرة أخرى، أرسل رابط جديد",
            reply_markup=main_menu()
        )
        
    except Exception as e:
        error_msg = str(e)
        # تنظيف رسالة الخطأ
        if "Private video" in error_msg:
            error_msg = "هذا الفيديو خاص لا يمكن تحميله"
        elif "400" in error_msg:
            error_msg = "خطأ من يوتيوب، حاول مرة أخرى بعد دقيقة"
        elif "not found" in error_msg:
            error_msg = "الفيديو غير موجود أو تم حذفه"
        
        await query.edit_message_text(f"❌ فشل التحميل\n\nالسبب: {error_msg[:100]}\n\nحاول مرة أخرى برابط مختلف")