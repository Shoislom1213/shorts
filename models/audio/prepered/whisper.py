import os
os.environ["TQDM_DISABLE"] = "1"

import whisper
from logger import setup_logger

logger = setup_logger("whisper")

logger.info("🟢 Whisper model yuklanmoqda...")
model = whisper.load_model("small")
logger.info("✅ Whisper model tayyor")

def whisper(audio_path):
    
    logger.info(f"🎧 Whisper boshlandi: {audio_path}")

    try:
        result = model.transcribe(
            audio_path,
            language="en",
            fp16=False,
            verbose=False,
            word_timestamps=True,
            temperature=0,
            beam_size=5,
            best_of=5,
            condition_on_previous_text=False,
        )
        segments = result["segments"]
        logger.info(f"✅ Whisper tugadi: {len(segments)} segment topildi")
        return segments

    except Exception as e:
        logger.error(f"❌ Whisper jarayonida xato: {e}", exc_info=True)
        return []