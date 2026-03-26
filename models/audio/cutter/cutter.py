from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import lum_contrast, colorx, fadein, fadeout
from moviepy.audio.fx.all import audio_normalize

def create_shorts(video_path, segments, target_resolution=(1080, 1920), fade_duration=0.5):

    video = VideoFileClip(video_path)
    short_paths = []

    for i, seg in enumerate(segments, 1):
        start = seg["start"]
        end = seg["end"]

        short_clip = video.subclip(start, end)

        w, h = target_resolution
        short_clip = short_clip.resize(height=h)
        short_clip = short_clip.crop(
            x_center=short_clip.w/2,
            width=w,
            y_center=short_clip.h/2,
            height=h
        )

        short_clip = lum_contrast(short_clip, lum=10, contrast=15)  # yorqinlik + kontrast
        short_clip = colorx(short_clip, 1.2)  # ranglar biroz jonlanadi

        if short_clip.audio:
            short_clip = short_clip.audio_normalize()

        short_clip = fadein(short_clip, fade_duration)
        short_clip = fadeout(short_clip, fade_duration)

        output_path = f"data/shorts/short_{i}.mp4"
        short_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            threads=4
        )

        short_paths.append(output_path)

    return short_paths