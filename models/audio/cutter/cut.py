from moviepy.video.io.VideoFileClip import VideoFileClip
from logger import setup_logger
import os

logger = setup_logger("Cuting")

def create_shorts(video_path, segments):
    logger.info(f"Video yuklanmoqda: {video_path}")
    
    video = VideoFileClip(video_path)
    short_paths = []

    for i, seg in enumerate(segments, 1):
        start = seg["start"]
        end = seg["end"]

        # ✅ Yangi MoviePy-da subclip o‘rniga: .subclip emas, .cutout(start, end) yoki video[start:end] ishlatiladi
        short_clip = video.subclip(start, end) if hasattr(video, "subclip") else video[start:end]

        output_path = f"data/row_shorts/short_{i}.mp4"
        short_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=video.fps
        )

        short_clip.close()
        short_paths.append(output_path)
        logger.info(f"Short {i} tayyor: {output_path}")

    video.close()
    logger.info("Barcha shorts kesildi")
    return short_paths