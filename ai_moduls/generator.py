import json
from openai import OpenAI
from config import API

client = OpenAI(api_key=API)

ALLOWED_CATEGORIES = [
    "Health & Medicine", "Business & Finance", "Psychology & Mind",
    "Technology & AI", "Education & Facts", "Philosophy & Deep Talk"
]

ALLOWED_MOODS = [
    "Motivational", "Sad & Emotional", "Funny & Humorous",
    "Serious & Informative", "Calm & Peaceful", "Energetic & Hype"
]

def generate_short_metadata(segment_text, intensity, elite_score, emotion_score, duration):
    """
    Analyzes video segment parameters and returns standardized metadata in English.
    """
    
    categories_str = ", ".join(ALLOWED_CATEGORIES)
    moods_str = ", ".join(ALLOWED_MOODS)

    prompt = f"""
    You are a professional SMM expert specializing in viral English-speaking content. 
    Prepare metadata for the following video segment.

    [VIDEO PARAMETERS]
    - TRANSCRIPT: "{segment_text}"
    - INTENSITY: {intensity}/20 (Higher intensity requires more "hooky" and "shocking" titles)
    - EMOTIONAL SCORE: {emotion_score}/1.0 (Emotional depth of the text)
    - QUALITY SCORE: {elite_score}/1.0 (General viral potential)
    - DURATION: {duration} seconds
    
    [TASK]
    Return ONLY a JSON object in English with the following structure:
    {{
        "title": "catchy English title (max 50 characters)",
        "category": "[Select from: {categories_str}]",
        "mood": "[Select from: {moods_str}]",
        "hashtags": {{
            "instagram": ["5 niche English hashtags"],
            "youtube": ["3 niche English hashtags"],
            "tiktok": ["5 niche English hashtags"]
        }}
    }}
    
    [STRICT RULES]
    1. Everything (title, hashtags) must be in ENGLISH only.
    2. The title must match the duration (short clips need punchy, short titles).
    3. 'category' and 'mood' MUST be strictly from the provided lists.
    4. Do not use Uzbek or any other language.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are a professional video analyst who only outputs JSON in English."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        if result['category'] not in ALLOWED_CATEGORIES: result['category'] = "Education & Facts"
        if result['mood'] not in ALLOWED_MOODS: result['mood'] = "Serious & Informative"
            
        return result
    
    except Exception as e:
        return None