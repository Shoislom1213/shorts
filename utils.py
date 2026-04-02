import os
import shutil

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

COOKIES_PATH = os.path.join(BASE_DIR, "cookies.txt")


def prepare_folders():
    if os.path.exists("data"):
        shutil.rmtree("data")

    os.makedirs("data/videos", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    os.makedirs("data/row_shorts", exist_ok=True)
    os.makedirs("data/shorts_processed", exist_ok=True)

def get_video_path(folder="data/videos"):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".mp4", ".mov", ".mkv"))]
    if not files:
        raise FileNotFoundError("❌ Video topilmadi")
    return os.path.join(folder, files[0])  # faqat bitta video bo‘lsa


def get_audio_path(folder="data/audio"):
    files = os.listdir(folder)

    if not files:
        raise FileNotFoundError("❌ Audio topilmadi")

    return os.path.join(folder, files[0])
