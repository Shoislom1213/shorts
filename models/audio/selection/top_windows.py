import subprocess
import json
from difflib import SequenceMatcher
from utils import get_video_path

def get_video_duration(url)
    if url is None
        url = get_video_path())
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    duration = float(data["format"]["duration"])
    return duration / 60

def video_count(duration):
    amount = int(duration / 4)
    return amount 

def get_top(scored_windows):

    top_emotional = sorted(scored_windows, key=lambda w: w["emotional_score"], reverse=True)
    top_value = sorted(scored_windows, key=lambda w: w["value_score"], reverse=True)
    top_story = sorted(scored_windows, key=lambda w: w["story_score"], reverse=True)
    top_score = sorted(scored_windows, key=lambda w: w["total_score"], reverse=True)

    result = {
    "emotional": top_emotional,
    "value": top_value,
    "story": top_story,
    "total": top_score
}   
    return result 

def is_similar(a, b, threshold=0.3):
    return SequenceMatcher(None, a, b). ratio() > threshold

def get_top_windows_by_category(windows_by_category, amount):
    """
    windows_by_category: dict, har bir category: [segment1, segment2, ...]
    return: dict, har bir category: unique segments
    """
    result = {}

    for cat, windows in windows_by_category.items():
        unique = []
        for w in windows:
            duplicate = False
            for u in unique:
                if is_similar(w["text"], u["text"]):
                    duplicate = True
                    break
            if not duplicate:
                unique.append(w)

            if len(unique) >= amount:
                break    
        result[cat] = unique

    return result

def make_overall_uniqe(top_by_category, amount=None):
    selected = []
    for windows in top_by_category.values():
        selected.extend(windows[:amount])
    
    for w in selected:
        w["weighted_score"] = (
            0.4 * w.get("emotional_score", 0) +
            0.3 * w.get("value_score", 0) +
            0.3 * w.get("story_score", 0)
        )
    
    selected.sort(key=lambda w: w["weighted_score"], reverse=True)
    
    unique = []
    for w in selected:
        if not any(is_similar(w["text"], u["text"]) for u in unique):
            unique.append(w)
        if amount and len(unique) >= amount:
            break
    
    return unique

def top_top(scored_windows):
    duration = get_video_duration()
    amount = video_count(duration)
    top_catigory = get_top(scored_windows)
    result = get_top_windows_by_category(top_catigory, amount)
    overall = make_overall_uniqe(result)
    return overall




