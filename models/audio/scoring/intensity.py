import re
from logger import setup_logger
logger = setup_logger("Intensity")
STRONG_WORDS = {
    # 🚨 urgency / command (eng kuchli signal)
    "urgency": {
        "words": [
            "must", "have to", "need to", "never", "stop", "start",
            "now", "today", "immediately", "right now", "don't", "do not"
        ],
        "phrases": [
            "you must", "you need to", "stop doing this",
            "start doing this", "don't do this"
        ],
        "weight": 2.5
    },

    # 💥 transformation (viral kontent asosi)
    "change": {
        "words": [
            "change", "transform", "improve", "upgrade", "shift",
            "become", "turn into", "grow", "level up"
        ],
        "phrases": [
            "change your life", "transform your life",
            "become better", "level up your life"
        ],
        "weight": 2.2
    },

    # 🧠 knowledge / insight
    "knowledge": {
        "words": [
            "secret", "truth", "lesson", "reality",
            "fact", "reason", "understand", "realize"
        ],
        "phrases": [
            "no one tells you", "this is the truth",
            "here is why", "this is why"
        ],
        "weight": 2.4
    },

    # 🎯 success
    "success": {
        "words": [
            "success", "win", "achieve", "result",
            "progress", "growth", "improvement"
        ],
        "phrases": [
            "achieve success", "be successful"
        ],
        "weight": 1.6
    },

    # ❌ failure / pain
    "failure": {
        "words": [
            "failure", "fail", "mistake", "error",
            "wrong", "problem", "issue", "bad"
        ],
        "phrases": [
            "biggest mistake", "common mistake",
            "this is wrong"
        ],
        "weight": 2.0
    },

    # ❤️ emotion (hissiy trigger)
    "emotion": {
        "words": [
            "fear", "pain", "dream", "confidence",
            "stress", "anxiety", "happy", "sad",
            "motivation", "inspiration"
        ],
        "phrases": [
            "feel better", "change your mindset",
            "believe in yourself"
        ],
        "weight": 1.8
    },

    # ⚡ power / impact
    "power": {
        "words": [
            "powerful", "unstoppable", "dangerous",
            "strong", "crazy", "insane", "massive",
            "incredible", "unbelievable"
        ],
        "phrases": [
            "this is powerful", "very dangerous",
            "this will shock you"
        ],
        "weight": 2.0
    },

    # ❓ curiosity / hook (YANGI – juda muhim)
    "curiosity": {
        "words": [
            "why", "how", "what", "imagine", "think"
        ],
        "phrases": [
            "do you know", "have you ever",
            "what if", "imagine this"
        ],
        "weight": 2.2
    }
}

def intensity_score(text: str) -> float:
    raw_text = text
    text = text.lower()
    words = text.split()
    score = 0

    def contains_word(text, word):
        return re.search(rf"\b{re.escape(word)}\b", text)

    # =========================
    # 🔥 1. STRONG WORD GROUPS (count-based, capped)
    # =========================
    for group in STRONG_WORDS.values():
        count = 0

        for w in group.get("words", []):
            if contains_word(text, w):
                count += 1

        for p in group.get("phrases", []):
            if re.search(rf"\b{re.escape(p)}\b", text):
                count += 2  # phrase stronger

        if count > 0:
            score += min(count * group["weight"], group["weight"] * 2)

    # =========================
    # 🎯 2. YOU / DIRECT ADDRESS (balanced)
    # =========================
    has_if_you = False

    if re.search(r"\byou\b", text):
        score += 0.8

    if re.search(r"\byou (must|need to|have to)\b", text):
        score += 1.5

    if re.search(r"\bif you\b", text):
        has_if_you = True

    # =========================
    # ⚡ 3. COMMAND START
    # =========================
    if re.search(r"^(do|stop|start|remember|never|listen|watch)\b", text):
        score += 2

    # =========================
    # ❓ 4. QUESTION / HOOK
    # =========================
    if "?" in text:
        score += 1.2

    if re.search(r"\b(do you|have you|are you|why|what if)\b", text):
        score += 1.2

    # =========================
    # 🔥 5. CONTRAST (clean)
    # =========================
    contrast_words = ["but", "however", "instead", "while", "yet"]

    contrast_hit = False
    for w in contrast_words:
        if re.search(rf"\b{w}\b", text):
            score += 2
            contrast_hit = True
            break

    if contrast_hit and "you" in text:
        score += 0.8

    # =========================
    # 🧠 6. VIRAL PATTERNS (no double count)
    # =========================
    pattern_hit = False

    patterns = [
        r"if you [^.!?]{0,60} you",
        r"not [^.!?]{0,40} but [^.!?]{0,40}",
        r"the more [^.!?]{0,40} the more",
    ]

    for p in patterns:
        if re.search(p, text):
            score += 2.5
            pattern_hit = True
            break

    # fallback (faqat agar pattern bo‘lmasa)
    if not pattern_hit and has_if_you:
        score += 1.5

    # =========================
    # ✂️ 7. SENTENCE STRUCTURE
    # =========================
    sentences = re.split(r"[.!?]", text)
    short_sentences = [s for s in sentences if 2 <= len(s.split()) <= 6]

    if len(short_sentences) >= 2:
        score += 2

    # =========================
    # 🔁 8. REPETITION (cleaned)
    # =========================
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    repeated_words = [w for w, v in freq.items() if v >= 2 and len(w) > 3]

    if len(repeated_words) >= 2:
        score += 1.5

    # strong repetition pattern
    if re.search(r"\b(\w{4,})\b.*\b\1\b.*\b\1\b", text):
        score += 1.2

    # =========================
    # ⚡ 9. CAPS / EMPHASIS (fixed)
    # =========================
    if re.findall(r"\b[A-Z]{3,}\b", raw_text):
        score += 1.2

    # =========================
    # 📏 10. LENGTH OPTIMIZATION (balanced)
    # =========================
    if 4 <= len(words) <= 10:
        score += 2
    elif 11 <= len(words) <= 18:
        score += 1

    # =========================
    # 🔒 FINAL NORMALIZATION
    # =========================
    logger.info("📝 Intensity score yakunlandi")
    return min(score, 15)