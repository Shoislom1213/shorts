import numpy as np
import json
from config import URL
from models.download.download import download_video, extract_audio
from utils import get_audio_path, get_video_path, prepare_folders
from models.detect.detect import detect_speech
from models.cutter.cutter import cut_video
from models.audio.whisper import whisper
from models.audio.windows import create_windows
from models.audio.segment import segment_cleaning
from models.audio.scoring.scoring_pipeline import scoring_pipeline
from models.audio.selection.slide_best_window import generate_context_windows
from models.audio.selection.top_windows import top_top

from logger import setup_logger

logger = setup_logger("pipeline")


def main():
    try:

        prepare_folders()

        download_video(URL)
        extract_audio()
        
        VIDEO_PATH = get_video_path()
        AUDIO_PATH = get_audio_path()

        logger.info("📊 Whisper boshlanmoqda...")
        row_segments = whisper(AUDIO_PATH)

        with open("row_segments.json", "w", encoding="utf-8") as f:
            json.dump(row_segments, f, indent=2, ensure_ascii=False)

        #🔍 SPEECH (optional — keyin yoqasiz)
        speech_segments = detect_speech(AUDIO_PATH)

        with open("row_segments.json", "r", encoding="utf-8") as f:
            row_segments = json.load(f)

        segments = segment_cleaning(row_segments)

        with open("segments.json", "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)
            
        windows = create_windows(segments)

        with open("windows.json", "w", encoding="utf-8") as f:
            json.dump(windows, f, indent=2, ensure_ascii=False)
            
        scored_windows = scoring_pipeline(windows)

        with open("scored_windows.json", "w", encoding="utf-8") as f:
            json.dump(scored_windows, f, indent=2, ensure_ascii=False)

        top_windows = top_top(scored_windows)

        with open("top_windows.json", "w", encoding="utf-8") as f:
            json.dump(top_windows, f, indent=2, ensure_ascii=False)

        all_new_windows = []

        for i in top_windows:
            new_windows = generate_context_windows(i, segments, 25, 50)
            all_new_windows.extend(new_windows)  # barcha kombinatsiyalarni qo‘shish

        with open("new_windows.json", "w", encoding="utf-8") as f:
            json.dump(all_new_windows, f, indent=2, ensure_ascii=False)

        new_scored = scoring_pipeline(all_new_windows)    

        with open("new_scored.json", "w", encoding="utf-8") as f:
            json.dump(new_scored, f, indent=2, ensure_ascii=False)

        best = top_top(new_scored)

        with open("best.json", "w", encoding="utf-8") as f:
            json.dump(best, f, indent=2, ensure_ascii=False)



        
    except Exception as e:
        logger.error(f"💥 CRASH: {e}", exc_info=True)


if __name__ == "__main__":
    main()
