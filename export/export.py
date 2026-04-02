import sqlite3
import uuid
import json
import os
from datetime import datetime

# 1. Manzillarni aniqlash
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Manbalar
JSON_SOURCE = os.path.join(ROOT_DIR, "final_shorts.json")
SOURCE_VIDEO_DIR = os.path.join(ROOT_DIR, "data", "shorts_processed")

# Maqsadli manzillar
DB_PATH = os.path.join(ROOT_DIR, "database", "shorts_info.db")
TARGET_VIDEO_DIR = os.path.join(ROOT_DIR, "database", "shorts")

def setup_database(conn):
    """Jadvalni faqat statuslar va barcha metrikalar bilan yaratadi"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(shorts)")
        columns = [column[1] for column in cursor.fetchall()]
        # Agar eski bazada raw_json yoki eski ustunlar qolgan bo'lsa, noldan quramiz
        if 'raw_json' in columns or 'published_at_yt' in columns:
            print("⚠️ Eski format aniqlandi. Baza yangilanmoqda...")
            cursor.execute("DROP TABLE IF EXISTS shorts")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shorts (
            id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            mood TEXT,
            
            start_time REAL,
            end_time REAL,
            duration REAL,
            
            pattern TEXT,
            segments INTEGER,
            hook_score REAL,
            text_emotion REAL,
            intensity REAL,
            contrast REAL,
            value REAL,
            audio_emotion REAL,
            volume REAL,
            energy REAL,
            variation REAL,
            
            hook_norm REAL,
            intensity_norm REAL,
            contrast_norm REAL,
            text_emotion_norm REAL,
            value_norm REAL,
            
            emotional_score REAL,
            value_score REAL,
            story_score REAL,
            total_score REAL,
            final_elite_score REAL,
            
            yt_hashtags TEXT,
            insta_hashtags TEXT,
            tiktok_hashtags TEXT,
            
            status_youtube TEXT DEFAULT 'READY',
            status_instagram TEXT DEFAULT 'READY',
            status_tiktok TEXT DEFAULT 'READY',
            
            file_path TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()

def export():
    if not os.path.exists(TARGET_VIDEO_DIR):
        os.makedirs(TARGET_VIDEO_DIR, exist_ok=True)

    if not os.path.exists(JSON_SOURCE):
        print(f"❌ Xato: {JSON_SOURCE} topilmadi!")
        return

    with open(JSON_SOURCE, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    setup_database(conn)
    cursor = conn.cursor()
    
    if not os.path.exists(SOURCE_VIDEO_DIR):
        print(f"❌ Xato: {SOURCE_VIDEO_DIR} topilmadi!")
        return
        
    available_files = sorted([f for f in os.listdir(SOURCE_VIDEO_DIR) if f.endswith('.mp4')])

    if not available_files:
        print("📭 Yangi videolar yo'q.")
        return

    success_count = 0
    for index, item in enumerate(json_data):
        if index < len(available_files):
            video_uuid = str(uuid.uuid4())
            old_file_name = available_files[index]
            
            new_file_name = f"{video_uuid}.mp4"
            target_path = os.path.normpath(os.path.join(TARGET_VIDEO_DIR, new_file_name))
            source_path = os.path.normpath(os.path.join(SOURCE_VIDEO_DIR, old_file_name))
            
            try:
                os.rename(source_path, target_path)
                
                tags = item.get('hashtags', {})
                yt_tags = ", ".join(tags.get('youtube', []))
                insta_tags = ", ".join(tags.get('instagram', []))
                tt_tags = ", ".join(tags.get('tiktok', []))

                # INSERT - Jami 36 ta ustun (raw_json olib tashlandi)
                # VALUES - Jami 36 ta so'roq belgisi (?)
                cursor.execute('''
                    INSERT INTO shorts (
                        id, title, category, mood, start_time, end_time, duration,
                        pattern, segments, hook_score, text_emotion, intensity, contrast, value,
                        audio_emotion, volume, energy, variation,
                        hook_norm, intensity_norm, contrast_norm, text_emotion_norm, value_norm,
                        emotional_score, value_score, story_score, total_score, final_elite_score,
                        yt_hashtags, insta_hashtags, tiktok_hashtags,
                        status_youtube, status_instagram, status_tiktok,
                        file_path, created_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    video_uuid, item.get('ai_title'), item.get('ai_category'), item.get('ai_mood'),
                    item.get('start'), item.get('end'), item.get('duration'),
                    item.get('pattern'), item.get('segments'), item.get('hook_score'),
                    item.get('text_emotion'), item.get('intensity'), item.get('contrast'), item.get('value'),
                    item.get('audio_emotion'), item.get('volume'), item.get('energy'), item.get('variation'),
                    item.get('hook_norm'), item.get('intensity_norm'), item.get('contrast_norm'),
                    item.get('text_emotion_norm'), item.get('value_norm'), item.get('emotional_score'),
                    item.get('value_score'), item.get('story_score'), item.get('total_score'),
                    item.get('final_elite_score'),
                    yt_tags, insta_tags, tt_tags,
                    'READY', 'READY', 'READY',
                    target_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                print(f"✅ Saqlandi: {item.get('ai_title')} [3x READY]")
                success_count += 1
            except Exception as e:
                print(f"❌ Xato ({old_file_name}): {e}")

    conn.commit()
    conn.close()
    print(f"\n✨ Yakunlandi. {success_count} ta video tizimga o'tkazildi.")
