import yt_dlp
import os
import re

from utils import prepare_folders, COOKIES_PATH

from logger import setup_logger

logger = setup_logger("download", "logs/app.log")

def download_video(url):
    logger.info(f"📥 Video yuklash boshlanmoqda: {url}")

    ydl_opts = {
    "format": "best",
    "outtmpl": "data/videos/%(title)s.%(ext)s",
    "noplaylist": True,
    "cookies": COOKIES_PATH,
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },
    
    "concurrent_fragment_downloads": 1,
    "retries": 4,
    "fragment_retries": 5,
    "socket_timeout": 10,
    "throttled_rate": 100000,
    "skip_unavailable_fragments": True,

  
    "merge_output_format": "mp4",
    "postprocessors": [{
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mp4",
    }],
    "quiet": True,
    "no_warnings": False,
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            logger.info(f"✅ Video yuklandi: {video_filename}")

        clean_name = sanitize_filename(os.path.basename(video_filename))
        clean_path = os.path.join(os.path.dirname(video_filename), clean_name)
        if video_filename != clean_path:
            os.rename(video_filename, clean_path)
            logger.info(f"✏️ Fayl nomi tozalandi: {clean_path}")
        else:
            logger.info("✅ Fayl nomi o‘zgartirish talab qilinmadi")

        return clean_path

    except Exception as e:
        logger.error(f"❌ Video yuklashda xato: {e}", exc_info=True)
        return False

def sanitize_filename(filename):
    ext = os.path.splitext(filename)[1] 
    name = os.path.splitext(filename)[0]

    name = name.replace("&", "and")
    name = re.sub(r'[^A-Za-z0-9 _-]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name + ext      