import json
import time
from ai_moduls.generator import generate_short_metadata 

def run_pipeline():
    # 1. best.json ni o'qiymiz
    with open('best.json', 'r', encoding='utf-8') as f:
        raw_shorts = json.load(f)

    final_results = []

    print(f"🚀 Jami {len(raw_shorts)} ta segmentni qayta ishlash boshlandi...")

    for i, short in enumerate(raw_shorts):
        print(f"[{i+1}/{len(raw_shorts)}] AI tahlil qilmoqda...")
        
        # AI funksiyasiga barcha 5 ta muhim ma'lumotni beramiz
        ai_data = generate_short_metadata(
            segment_text=short['text'],
            intensity=short['intensity'],
            elite_score=short['final_elite_score'],
            emotion_score=short['emotional_score'],
            duration=short['duration']
        )

        if ai_data:
            # AI natijalarini original ma'lumotlar bilan birlashtiramiz
            short.update({
                "ai_title": ai_data['title'],
                "ai_category": ai_data['category'],
                "ai_mood": ai_data['mood'],
                "hashtags": ai_data['hashtags']
            })
            final_results.append(short)
        
        # API limitlaridan oshib ketmaslik uchun
        time.sleep(1)

    # 2. Hammasini bitta faylga saqlaymiz
    with open('final_shorts.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

    print("\n✅ Tayyor! 'final_shorts.json' yaratildi. Endi bazaga yuklashimiz mumkin.")
