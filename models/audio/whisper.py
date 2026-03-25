import os
os.environ["TQDM_DISABLE"] = "1"

import whisper
from logger import setup_logger

logger = setup_logger("whisper")

model = whisper.load_model("small")


def whisper(audio_path):
    logger.info("🎧 Whisper boshlandi...")

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

    return result["segments"]