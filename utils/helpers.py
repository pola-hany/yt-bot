import os
import re

def is_valid_url(url: str) -> bool:
    """
    يتأكد إن اللينك اللي ابعته صحيح لأي منصة
    """
    pattern = re.compile(
        r'^(https?://)?(www\.)?'
        r'(youtube\.com|youtu\.be|tiktok\.com|instagram\.com|facebook\.com|x\.com)/.+$'
    )
    return bool(pattern.match(url))


def clean_filename(filename: str) -> str:
    """
    ينضف اسم الملف من أي رموز مش مسموح بيها في النظام
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def remove_file(path: str):
    """
    يمسح ملف لو موجود
    """
    if os.path.exists(path):
        os.remove(path)