import yt_dlp
import os

class Downloader:
    
    # الإعدادات الأساسية المشتركة
    BASE_OPTS = {
        'quiet': True,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'prefer_insecure': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    @staticmethod
    def get_info(url):
        """جلب معلومات الفيديو"""
        opts = Downloader.BASE_OPTS.copy()
        opts['quiet'] = True
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            raise Exception(f"فشل جلب المعلومات: {str(e)}")
    
    @staticmethod
    def download_video(url, quality):
        """تحميل فيديو بجودة محددة"""
        
        # خريطة الجودة
        quality_map = {
            '144p': 'worst[height<=144]',
            '360p': 'best[height<=360]',
            '720p': 'best[height<=720]',
            'best': 'best[height<=1080]'
        }
        
        format_spec = quality_map.get(quality, 'best')
        
        opts = Downloader.BASE_OPTS.copy()
        opts.update({
            'outtmpl': '/tmp/video_%(id)s.%(ext)s',
            'format': format_spec,
            'merge_output_format': 'mp4',
        })
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # البحث عن الملف المحمل
                video_id = info.get('id', '')
                extensions = ['.mp4', '.webm', '.mkv']
                file_path = None
                
                for ext in extensions:
                    test_path = f'/tmp/video_{video_id}{ext}'
                    if os.path.exists(test_path):
                        file_path = test_path
                        break
                
                if not file_path:
                    # محاولة طريقة أخرى للحصول على المسار
                    file_path = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.mkv', '.mp4')
                
                return file_path, info.get('title', 'video')
                
        except Exception as e:
            raise Exception(f"فشل تحميل الفيديو: {str(e)}")
    
    @staticmethod
    def download_audio(url):
        """تحميل الصوت بصيغة mp3"""
        
        opts = Downloader.BASE_OPTS.copy()
        opts.update({
            'outtmpl': '/tmp/audio_%(id)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # البحث عن ملف mp3
                audio_id = info.get('id', '')
                file_path = f'/tmp/audio_{audio_id}.mp3'
                
                if not os.path.exists(file_path):
                    # محاولة طريقة أخرى
                    base_path = ydl.prepare_filename(info)
                    file_path = base_path.replace('.webm', '.mp3').replace('.m4a', '.mp3')
                
                return file_path, info.get('title', 'audio')
                
        except Exception as e:
            raise Exception(f"فشل تحميل الصوت: {str(e)}")