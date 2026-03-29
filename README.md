# 🎬 YouTube Downloader Bot

بوت تيليجرام لتحميل الفيديوهات والصوت من يوتيوب

---

## 📁 هيكل المشروع

```
youtube_bot/
├── main.py          # نقطة التشغيل الرئيسية
├── config.py        # الإعدادات والمتغيرات
├── handlers.py      # معالجات أحداث البوت
├── downloader.py    # منطق التحميل (yt-dlp)
├── keyboards.py     # لوحات المفاتيح Inline
├── messages.py      # نصوص الرسائل
├── utils.py         # دوال مساعدة
├── requirements.txt # المكتبات المطلوبة
└── .env.example     # مثال متغيرات البيئة
```

---

## ⚙️ التثبيت والتشغيل

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

> ملاحظة: يحتاج تحميل الفيديو إلى `ffmpeg` مثبت على النظام:
> - **Ubuntu/Debian:** `sudo apt install ffmpeg`
> - **Windows:** حمّله من [ffmpeg.org](https://ffmpeg.org)
> - **macOS:** `brew install ffmpeg`

### 2. إعداد التوكن

**الطريقة الأولى** — عبر `config.py`:
```python
BOT_TOKEN = "your_token_here"
```

**الطريقة الثانية** — عبر متغير البيئة:
```bash
export BOT_TOKEN="your_token_here"
python main.py
```

### 3. تشغيل البوت
```bash
python main.py
```

---

## 🚀 الميزات

- ✅ تحميل فيديو بجودات: 144p / 360p / 720p / أفضل جودة
- ✅ تحميل صوت بصيغة MP3 (192 kbps)
- ✅ أزرار Inline تفاعلية
- ✅ التحقق من صحة روابط يوتيوب
- ✅ معالجة شاملة للأخطاء
- ✅ حذف الملفات المؤقتة تلقائياً
- ✅ رسائل حالة (جاري التحميل / الإرسال)

---

## 📦 رفع على Railway / Render

1. ارفع المشروع على GitHub
2. أنشئ مشروعاً جديداً على Railway أو Render
3. أضف متغير البيئة `BOT_TOKEN`
4. حدد أمر البدء: `python main.py`
