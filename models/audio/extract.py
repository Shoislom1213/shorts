import os
os.environ["TQDM_DISABLE"] = "1"

import whisper
from logger import setup_logger
import re

logger = setup_logger("whisper")

# 🔥 MODEL
model = whisper.load_model("small")


# 🔥 TEXT CLEANING
def clean_text(text):
    text = (
        text.replace("  ", " ")
            .replace("..", ".")
            .replace(" ,", ",")
            .replace(" .", ".")
            .strip()
    )

    if text in [".", ",", ""]:
        return ""

    return text

def split_long_segment(seg):
    text = seg["text"]
    start = seg["start"]
    end = seg["end"]

    parts = text.split(".")
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) <= 1:
        return [seg]

    duration = end - start
    step = duration / len(parts)

    new_segments = []

    for i, part in enumerate(parts):
        s = round(start + i * step, 2)
        e = round(s + step, 2)

        new_segments.append({
            "start": s,
            "end": e,
            "text": part + "."
        })

    return new_segments

def extract_segments(audio_path):
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

    segments = result["segments"]
    cleaned_segments = []

    last_end = 0

    for seg in segments:
        start = round(seg["start"], 1)
        end = round(seg["end"], 1)

        if start < last_end:
            continue

        text = clean_text(seg["text"])

        if not text:
            continue

        # 🔥 LONG → SPLIT
        if (end - start) > 12:
            split_segs = split_long_segment({
                "start": start,
                "end": end,
                "text": text
            })

            for s in split_segs:
                if len(s["text"].split()) >= 4 and len(s["text"]) >= 20:
                    cleaned_segments.append({
                        "start": s["start"],
                        "end": s["end"],
                        "text": s["text"]
                    })

            last_end = end
            continue  # 🔥 faqat shu yerda

        # 🔥 NORMAL FILTER
        if len(text.split()) < 4:
            continue

        if len(text) < 20:
            continue

        cleaned_segments.append({
            "start": start,
            "end": end,
            "text": text
        })

        last_end = end
    return cleaned_segments