import subprocess
import json
from difflib import SequenceMatcher
from utils import get_video_path
from logger import setup_logger
import math
logger = setup_logger("Top windows")

def get_video_duration(url=None):
    if url is None:
        url = get_video_path()
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

def calculate_final_score(w):
    content_score = (
        0.4 * w.get("emotional_score", 0) + 
        0.3 * w.get("value_score", 0) + 
        0.3 * w.get("story_score", 0)
    )
    audio_score = (
        0.4 * w.get("energy", 0) + 
        0.3 * w.get("volume", 0) + 
        0.3 * w.get("variation", 0)
    )
    return (0.7 * content_score) + (0.3 * audio_score)

def video_count(duration_min):
    if duration_min < 10: return 1
    elif 10 <= duration_min < 20: return 3 
    elif 20 <= duration_min < 30: return 5 
    elif 30 <= duration_min < 40: return 6 
    elif 40 <= duration_min < 50: return 8  
    elif 50 <= duration_min < 60: return 9 
    elif 60 <= duration_min < 80: return 12    
    else: return 14

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

def is_similar(w1, w2, text_threshold=0.25, time_threshold=0.5):
    """
    Matn va Vaqt bo'yicha dublikatlarni aniqlash.
    """
    # 1. Matn o'xshashligi
    text_ratio = SequenceMatcher(None, w1["text"], w2["text"]).ratio()
    if text_ratio > text_threshold:
        return True
    
    # 2. Vaqt bo'yicha ustma-ust tushish (Overlap)
    overlap_start = max(w1['start'], w2['start'])
    overlap_end = min(w1['end'], w2['end'])
    
    if overlap_end > overlap_start:
        overlap_duration = overlap_end - overlap_start
        min_duration = min(w1['end'] - w1['start'], w2['end'] - w2['start'])
        if (overlap_duration / min_duration) > time_threshold:
            return True
            
    return False

def get_top_windows_by_category(windows_by_category, amount):
    result = {}
    for cat, windows in windows_by_category.items():
        # Avval hamma segmentlarga ball beramiz
        for w in windows:
            w["final_elite_score"] = calculate_final_score(w)
            
        # Ball bo'yicha saralaymiz
        sorted_windows = sorted(windows, key=lambda x: x["final_elite_score"], reverse=True)
        
        unique = []
        for w in sorted_windows:
            if not any(is_similar(w, u) for u in unique):
                unique.append(w)
            if len(unique) >= amount:
                break
        result[cat] = unique
    return result

def make_overall_uniqe(top_by_category, amount):
    """Barcha kategoriyalardan eng zo'rlarini yagona ro'yxatga yig'ish."""
    all_selected = []
    for windows in top_by_category.values():
        all_selected.extend(windows)
    
    # Umumiy ro'yxatni yana bir bor ball bo'yicha saralaymiz
    all_selected.sort(key=lambda w: w["final_elite_score"], reverse=True)
    
    overall_unique = []
    for w in all_selected:
        # Dublikatlarni (matn va vaqt bo'yicha) tekshirib yig'amiz
        if not any(is_similar(w, u) for u in overall_unique):
            overall_unique.append(w)
        
        if len(overall_unique) >= amount:
            break
            
    return overall_unique

def top_top(scored_windows):
    logger.info("Elite segmentlar aniqlanmoqda...")
    duration = get_video_duration()
    amount = video_count(duration)
    
    # 1. Kategoriyalar bo'yicha topish
    # (scored_windows dict emas, list bo'lsa, uni quyidagicha ajratamiz)
    # Agar scored_windows allaqachon get_top(scored_windows) dan o'tgan bo'lsa:
    from copy import deepcopy
    
    # Kategoriyalar uchun obyekt (agar get_top ishlatilsa)
    top_categories = {
        "emotional": sorted(scored_windows, key=lambda w: w["emotional_score"], reverse=True),
        "value": sorted(scored_windows, key=lambda w: w["value_score"], reverse=True),
        "story": sorted(scored_windows, key=lambda w: w["story_score"], reverse=True),
        "total": sorted(scored_windows, key=lambda w: w["total_score"], reverse=True)
    }
    
    result_by_cat = get_top_windows_by_category(top_categories, amount)
    
    # 2. Yakuniy yagona ro'yxat
    overall = make_overall_uniqe(result_by_cat, amount)
    
    logger.info(f"Top {len(overall)} ta segment aniqlandi!")
    return overall




