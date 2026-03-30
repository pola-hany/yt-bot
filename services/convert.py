import subprocess

def convert_to_mp3(video_path):
    audio_path = "audio.mp3"

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-ab", "192k",
        "-ar", "44100",
        "-y",
        audio_path
    ]

    subprocess.run(command)

    return audio_path