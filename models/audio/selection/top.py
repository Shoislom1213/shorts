from difflib import SequenceMatcher
import subprocess
import json
from utils import get_video_path

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

def get_top_unique_windows(windows, k=10):
    selected = []
    for w in windows:  # sorted (best → worst)
        is_duplicate = False
        for s in selected:
            if is_similar(w["text"], s["text"]):
                is_duplicate = True
                break
        if is_duplicate:
            continue
        selected.append(w)
    return selected[:k]

def combine_windows(windows, target_duration=45):
    if not windows:
        return []

    windows = sorted(windows, key=lambda x: x["start"])
    selected = []

    total = 0
    for w in windows:
        dur = w["duration"]
        if total + dur <= target_duration:
            selected.append(w)
            total += dur
        else:
            remain = target_duration - total
            if remain > 8:  # minimal duration threshold
                trimmed = {
                    **w,
                    "end": w["start"] + remain,
                    "duration": remain
                }
                selected.append(trimmed)
            break

    return selected

def build_clip_by_score(windows, score_key, top_k=10, target_duration=45):
    # 1️⃣ Top scoring windows (eng yuqori score bo‘yicha tartiblash)
    top = sorted(windows, key=lambda w: w[score_key], reverse=True)
    video_path = get_video_path()
    duratin = get_video_duration(video_path)
    top_k = calculate_top_k(duratin)
    top = get_top_unique_windows(top, k=top_k)

    combined = combine_windows(top, target_duration=target_duration)
    
    # 4️⃣ Natijani qaytarish
    return combined

def get_video_duration(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "json", video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def calculate_top_k(video_duration_seconds):
    minutes = video_duration_seconds / 60

    # har 7 minutga 1 ta short
    top_k = int(minutes / 7)

    # minimal va maksimal limit
    top_k = max(3, top_k)
    top_k = min(40, top_k)

    return top_k

def build_all_clips(scored_windows, top_k, target_duration=45):
    results = {}

    # 1️⃣ Each category
    results["emotional"] = build_clip_by_score(scored_windows, "emotional_score", top_k, target_duration)
    results["value"] = build_clip_by_score(scored_windows, "value_score", top_k, target_duration)
    results["story"] = build_clip_by_score(scored_windows, "story_score", top_k, target_duration)

    # 2️⃣ Overall total_score
    results["total_score"] = build_clip_by_score(scored_windows, "total_score", top_k, target_duration)

    return results

def get_top_segment_per_clip(clips):
    """
    clips: dict, masalan {"emotional": [...], "value": [...], ...}
    return: list of dict, har bir dict ichida original segment
    """
    top_segments = []

    for key, segs in clips.items():
        if not segs:
            continue  # bo'sh bo'lsa o'tamiz
        # har bir segmentni listga qo'shamiz
        for seg in segs:
            top_segments.append(seg)

    # optional: segmentlarni start bo'yicha tartiblash
    top_segments = sorted(top_segments, key=lambda x: x["start"])

    return top_segments