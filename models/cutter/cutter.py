import os
import subprocess


def cut_video(video_path, clips, output_dir="data/shorts"):
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for i, c in enumerate(clips):
        start = max(0, float(c["start"]))
        end = float(c["end"])
        duration = max(0.1, end - start)

        output_path = os.path.join(output_dir, f"short_{i}.mp4")
        
        # asosiy ishlaydigani 
        command = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(duration),

            "-map", "0:v:0",
            "-map", "0:a:0",

            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",

            "-c:a", "aac",
            "-b:a", "128k",

            output_path
        ]

        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True   # 🔥 error bo‘lsa exception
            )
            results.append(output_path)

        except subprocess.CalledProcessError:
            print(f"❌ Cut error: {start}-{end}")

    return results