import requests

def download_video(url: str):
    try:
        api_url = "https://api.cobalt.tools/api/json"

        payload = {
            "url": url,
            "vCodec": "h264",
            "vQuality": "720",
            "aFormat": "mp3",
            "isAudioOnly": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        res = requests.post(api_url, json=payload, headers=headers)
        data = res.json()

        # لو مفيش فيديو
        if "url" not in data:
            print("API ERROR:", data)
            return None

        video_url = data["url"]

        # تحميل الفيديو
        file_name = "video.mp4"
        video = requests.get(video_url).content

        with open(file_name, "wb") as f:
            f.write(video)

        return file_name

    except Exception as e:
        print("YOUTUBE API ERROR:", e)
        return None
