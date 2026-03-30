import os
import requests
from config import FASTSAVER_KEY

def get_video(url):
    """
    تحميل الفيديو من أي منصة مدعومة بدون علامة مائية
    """
    try:
        api = f"https://api.fastsaverapi.com/v1/download?key={FASTSAVER_KEY}&url={url}"
        res = requests.get(api).json()

        if res.get("status") != "success":
            print("API ERROR:", res)
            return None

        return res["result"]["url"]

    except Exception as e:
        print("ERROR:", e)
        return None