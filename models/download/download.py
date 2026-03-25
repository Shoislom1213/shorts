import yt_dlp
import os
import subprocess

from utils import prepare_folders

def download_video(url):
    prepare_folders()
    ydl_opts = {
    "format": "bv*+ba/b",
    "outtmpl": "data/videos/%(title)s.%(ext)s",
    "noplaylist": True,

    # 🔹 Header (ba’zi throttlingni kamaytiradi)
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },

    # 🔹 Tezlik va stabil
    "concurrent_fragment_downloads": 4,
    "retries": 4,
    "fragment_retries": 5,
    "socket_timeout": 10,
    "throttled_rate": 100000,
    "skip_unavailable_fragments": True,

    # 🔹 Anti-block (ENG MUHIM)
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    },

    # 🔹 Formatni majburiy mp4 qilish
    "merge_output_format": "mp4",

    # 🔹 Agar kerak bo‘lsa convert (optional)
    "postprocessors": [{
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mp4",
    }],

    # 🔹 Loglar
    "quiet": True,
    "no_warnings": False,
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return True

    except Exception as e:
        print("❌ Video xatolik:", e)
        return False


def extract_audio():
    video_folder = "data/videos"

    files = os.listdir(video_folder)

    if not files:
        print("❌ Video topilmadi")
        return False

    # 🔥 har doim bitta video bor → shuni olamiz
    video_file = os.path.join(video_folder, files[0])

    output_audio = "data/audio/audio.wav"

    command = [
        "ffmpeg",
        "-i", video_file,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_audio
    ]

    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True

    except Exception as e:
        print("❌ Audio xatolik:", e)
        return False