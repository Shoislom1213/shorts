import os
import cv2
import numpy as np
from moviepy import VideoFileClip
from moviepy.video.fx import Resize, Crop
from moviepy.audio.fx import AudioNormalize
from logger import setup_logger

logger = setup_logger("Processing")

def get_face_center(video_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    check_frames = [int(total_frames * i / 10) for i in range(1, 10)]
    face_x_positions = []
    
    for frame_no in check_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        success, frame = cap.read()
        if success:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 6)
            for (x, y, w, h) in faces:
                center_x = (x + w / 2) / frame.shape[1]
                face_x_positions.append(center_x)
                break 
    
    cap.release()
    
    if face_x_positions:
        return float(np.median(face_x_positions))
    return 0.5

def post_process_shorts(target_resolution=(1080, 1920)):
    folder = "data/row_shorts"
    output_dir = "data/shorts_processed"
    
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    video_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.mp4')]
    
    if not video_list:
        logger.warning("⚠️ Videolar topilmadi")
        return

    for input_path in video_list:
        file_name = os.path.basename(input_path)
        save_path = os.path.join(output_dir, file_name)
        logger.info(f"🚀 Processing: {file_name}")
        
        try:
            video = VideoFileClip(input_path)
            
            raw_face_x = get_face_center(input_path)
            
            w_target, h_target = target_resolution
            w_target = w_target if w_target % 2 == 0 else w_target - 1
            h_target = h_target if h_target % 2 == 0 else h_target - 1

            resized_clip = video.with_effects([Resize(height=h_target)])
            
            smooth_weight = 0.2
            face_x_percent = (raw_face_x * (1 - smooth_weight)) + (0.5 * smooth_weight)
            
            target_x_center = resized_clip.w * face_x_percent
            half_w = w_target / 2
            final_x_center = max(half_w, min(resized_clip.w - half_w, target_x_center))

            processed_video = resized_clip.with_effects([
                Crop(width=w_target, height=h_target, x_center=final_x_center, y_center=resized_clip.h / 2)
            ])

            if processed_video.audio:
                processed_video.audio = processed_video.audio.with_effects([AudioNormalize()])

            processed_video.write_videofile(
                save_path,
                codec="libx264",
                audio_codec="aac",
                fps=video.fps,
                preset="medium",
                threads=4,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "18"]
            )
            
            video.close()
            processed_video.close()
            logger.info(f"✅ Bajarildi: {save_path}")

        except Exception as e:
            logger.error(f"💥 Xato {file_name}: {str(e)}")
