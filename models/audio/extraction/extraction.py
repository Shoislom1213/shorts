import os
import subprocess

from utils import get_video_path
from logger import setup_logger

logger = setup_logger("extraction")  

def extract_audio(video_file=None, output_audio="data/audio/audio.wav"):
    """
    Video fayldan audio WAV chiqaradi (16kHz, mono, PCM16).
    video_file : str : video fayl pathi (None bo‘lsa get_video_path ishlatiladi)
    output_audio : str : chiqadigan audio fayl pathi
    """

    if video_file is None:
        video_file = get_video_path() 
    logger.info(f"📹 Video path: {video_file}")  

    
    if not video_file or not os.path.exists(video_file):
        logger.error("❌ Video fayl topilmadi yoki noto‘g‘ri path")
        return False  

    output_folder = os.path.dirname(output_audio)
    os.makedirs(output_folder, exist_ok=True)
    logger.info(f"📁 Audio chiqishi papkasi tayyorlandi: {output_folder}")


    FFMPEG_PATH = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
    if not os.path.exists(FFMPEG_PATH):
        logger.error("❌ FFmpeg topilmadi")
        return False
    
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", video_file,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_audio
    ]
    logger.info(f"🎵 Audio chiqarish boshlanmoqda: {output_audio}")

    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"✅ Audio muvaffaqiyatli chiqarildi: {output_audio}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Audio chiqarishda xato: {e}", exc_info=True)
        return False

