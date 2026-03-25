import re


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


# 🔥 MERGE — ENG MUHIM QISM
def merge_segments(segments):

    merged = []
    buffer = None

    for seg in segments:
        if buffer is None:
            buffer = seg
            continue

        duration = buffer["end"] - buffer["start"]
        sentence_count = buffer["text"].count(".")
        if duration > 12 or sentence_count >= 2:
            merged.append(buffer)
            buffer = seg
            continue

        # 🔥 AGRESSIVE MERGE (PRO)
        if (
            duration < 4
            or len(buffer["text"].split()) < 6
            or not buffer["text"].endswith((".", "!", "?"))
        ):
            buffer["end"] = seg["end"]
            buffer["text"] += " " + seg["text"]
        else:
            merged.append(buffer)
            buffer = seg

    if buffer:
        merged.append(buffer)

    return merged


def segment_cleaning(segments):
    cleaned_segments = []
    last_end = 0

    # 🔥 1. BASIC CLEAN + FILTER
    for seg in segments:
        start = round(seg["start"], 1)
        end = round(seg["end"], 1)

        if start < last_end:
            continue

        text = clean_text(seg["text"])

        if not text:
            continue

        # 🔥 MIN FILTER
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

    # 🔥 2. MERGE (ENG MUHIM)
    cleaned_segments = merge_segments(cleaned_segments)

    # 🔥 3. FINAL FILTER (QUALITY CONTROL)
    final_segments = []

    for seg in cleaned_segments:
        duration = seg["end"] - seg["start"]

        # ❌ juda qisqa
        if duration < 3:
            continue

        # ❌ juda uzun (window uchun qoldiramiz)
        if duration > 20:
            continue

        final_segments.append(seg)

    return final_segments