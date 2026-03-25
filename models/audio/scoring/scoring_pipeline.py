import json
import re

from models.audio.scoring.hook_score import hook_score
from models.audio.scoring.emotion_text import emotion_text_score
from models.audio.scoring.emotion_audio import emotion_audio_score
from models.audio.scoring.intensity import intensity_score
from models.audio.scoring.contrast_score import contrast_score
from models.audio.scoring.value_scor import value_score
from models.audio.scoring.hook_score import trim_bad_ending
  

def normalize(val, max_val):
    return val / max_val if max_val > 0 else 0


def compute_total_score(w):

    # 🔥 SAFETY (text bo‘lmasa 0)
    if not w["text"] or len(w["text"].split()) < 5:
        return 0

    base = (
        w["hook_norm"] * 0.38 +
        w["contrast_norm"] * 0.25 +
        w["intensity_norm"] * 0.15 +
        w["value_norm"] * 0.15 +
        w["text_emotion_norm"] * 0.06 +
        w["audio_emotion_norm"] * 0.06
    )

    if w["hook_norm"] > 0.7:
        base *= 1.15

    if w["hook_norm"] < 0.4 and w["value_norm"] > 0.7:
        base -= 0.2

    if w["value_norm"] < 0.3:
        base -= 0.1    

    return min(base, 1.0)

def add_decision_scores(w):

    w["emotional_score"] = (
        w["intensity_norm"] * 0.4 +
        w["contrast_norm"] * 0.3 +
        w["audio_emotion_norm"] * 0.2 +
        w["text_emotion_norm"] * 0.1
    )

    w["value_score"] = (
        w["value_norm"] * 0.5 +
        w["contrast_norm"] * 0.3 +
        w["text_emotion_norm"] * 0.2
    )

    w["story_score"] = (
        w["hook_norm"] * 0.5 +
        w["contrast_norm"] * 0.3 +
        w["intensity_norm"] * 0.2
    )
    w["story_score"] = max(w["story_score"], 0.35)

    return w



def scoring_pipeline(windows):

    cleaned_windows = []

    for window in windows:

        text = window.get("text", "").strip()

        if not text or text == ".":
            continue

        cleaned_text = trim_bad_ending(text)

        if not cleaned_text or cleaned_text.strip() in [".", ","]:
            continue

        if len(cleaned_text.split()) < 5:
            continue

        window["text"] = cleaned_text

        window["hook_score"] = hook_score(window)
        window["text_emotion"] = emotion_text_score(window["text"])
        window["intensity"] = intensity_score(window["text"])
        window["contrast"] = contrast_score(window["text"])
        window["value"] = value_score(window["text"])

        txt = window["text"].lower()
        pattern_bonus = 0

        if re.search(r"you have to", txt):
            pattern_bonus += 2

        if re.search(r"the only way", txt):
            pattern_bonus += 2

        if re.search(r"no way out", txt):
            pattern_bonus += 2

        if re.search(r"this is how", txt):
            pattern_bonus += 1

        if re.search(r"let me tell you", txt):
            pattern_bonus += 1

        if re.search(r"listen", txt):
            pattern_bonus += 1

        if re.search(r"the only way", txt):
            pattern_bonus += 2

        if re.search(r"no way out", txt):
            pattern_bonus += 2

        if re.search(r"this is how", txt):
            pattern_bonus += 1

        if re.search(r"let me tell you", txt):
            pattern_bonus += 1

        if re.search(r"when things get hard", txt):
            pattern_bonus += 1     

        window["hook_score"] += min(pattern_bonus, 4)

        cleaned_windows.append(window)

    windows = cleaned_windows

    windows = emotion_audio_score(windows)

    for w in windows:
        w["hook_norm"] = normalize(w["hook_score"], 10)
        w["intensity_norm"] = normalize(w["intensity"], 15)
        w["contrast_norm"] = normalize(w["contrast"], 10)
        w["text_emotion_norm"] = min(normalize(w["text_emotion"], 10), 1.0)
        w["audio_emotion_norm"] = normalize(w["audio_emotion"], 10)
        w["value_norm"] = normalize(w["value"], 10)

    for w in windows:
        add_decision_scores(w)
       
    for w in windows:
        w["total_score"] = compute_total_score(w)

#     windows = [
#     w for w in windows
#     if (w["total_score"] > 0.28 or w["hook_norm"] > 0.7) 
#        and 30 <= w["duration"] <= 45
# ]
    windows = sorted(windows, key=lambda x: x["total_score"], reverse=True)

    filtered = []

    for w in windows:
        keep = True

        for f in filtered:
            overlap = min(w["end"], f["end"]) - max(w["start"], f["start"])

            if overlap > 0:

                ratio = overlap / min(
                    w["duration"],
                    f["duration"]
                )

                if ratio > 0.85:
                    if w["total_score"] <= f["total_score"]:
                        keep = False
                        break

        if keep:
            filtered.append(w)

    return filtered

def pick_top_by_category(windows, top_k=3):

    emotional = sorted(
        windows,
        key=lambda x: x["emotional_score"],
        reverse=True
    )

    value = sorted(
        windows,
        key=lambda x: x["value_score"],
        reverse=True
    )

    story = sorted(
        windows,
        key=lambda x: x["story_score"],
        reverse=True
    )

    return {
        "emotional": emotional[:top_k],
        "value": value[:top_k],
        "story": story[:top_k],
    }




