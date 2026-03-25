import re


CONTRAST_TRIGGERS = {
    "strong": {
        "phrases": [
            "not only", "not just", "not this but",
            "the truth is", "the reality is",
            "what people don't realize is",
            "what you don't understand is",
            "but actually", "but in reality",
            "but the truth is",
            "but the reality is",
            "you think", "everyone thinks", "most people think"
        ],
        "words": [
            "but", "however", "yet"
        ],
        "weight": 3
    },

    "medium": {
        "phrases": [
            "on the other hand",
            "in contrast",
            "by contrast",
            "rather than",
            "instead of",
            "while others",           # 🔥 qo‘shildi
            "most people",            # 🔥 qo‘shildi
            "some people"             # 🔥 qo‘shildi
        ],
        "words": [
            "while", "whereas", "instead", "rather", "unlike"
        ],
        "weight": 2
    },

    "weak": {
        "phrases": [
            "this is why",
            "the reason is",
            "that's why",
            "believe it or not",
            "it turns out",          # 🔥 qo‘shildi
            "you might think"        # 🔥 qo‘shildi
        ],
        "words": [
            "actually", "in fact"
        ],
        "weight": 1.2
    },

    "negation": {
        "phrases": [
            "you don't need",
            "you don't have to",
            "no longer",
            "you are not",
            "you are never",         # 🔥 qo‘shildi
            "you can't",             # 🔥 qo‘shildi
            "you will not"           # 🔥 qo‘shildi
        ],
        "words": [
            "not", "never", "no"
        ],
        "weight": 1.5
    }
}


def contrast_score(text: str) -> float:
    text = text.lower()
    score = 0

    strong_hit = False
    medium_hit = False
    weak_hit = False

    # =========================
    # 🔥 1. TRIGGER SYSTEM (MAIN)
    # =========================
    for name, group in CONTRAST_TRIGGERS.items():
        triggered = False

        # phrases
        for p in group.get("phrases", []):
            if p in text:
                score += group["weight"]
                triggered = True
                break

        # words (agar phrase topilmasa)
        if not triggered:
            for w in group.get("words", []):
                if re.search(rf"\b{w}\b", text):
                    score += group["weight"]
                    triggered = True
                    break

        # flaglar
        if triggered:
            if name == "strong":
                strong_hit = True
            elif name == "medium":
                medium_hit = True
            elif name == "weak":
                weak_hit = True

    # =========================
    # 🎯 2. PATTERNS (MAIN BOOST)
    # =========================
    pattern_score = 0

    patterns = [
        r"not [^.!?]{0,40} but [^.!?]{0,40}",
        r"while [^.!?]{0,40} you [^.!?]{0,40}",
        r"most people [^.!?]{0,40} you [^.!?]{0,40}",
        r"you think [^.!?]{0,40} but [^.!?]{0,40}",
    ]

    for p in patterns:
        if re.search(p, text):
            pattern_score = 3.5
            break

    score += pattern_score

    # =========================
    # ⚡ 3. YOU BOOST
    # =========================
    if (strong_hit or medium_hit or pattern_score > 0) and re.search(r"\byou\b", text):
        score += 1.5

    # =========================
    # 🔁 4. MULTI CONTRAST
    # =========================
    contrast_count = len(re.findall(r"\b(but|however|yet|while)\b", text))
    if contrast_count >= 2:
        score += 2

    # =========================
    # ✂️ 5. SHORT SENTENCE BONUS
    # =========================
    sentences = re.split(r"[.!?]", text)
    short_sentences = [s for s in sentences if 2 <= len(s.split()) <= 6]

    if short_sentences and (strong_hit or pattern_score > 0):
        score += 1

    # =========================
    # 🧠 6. BALANCE CONTROL
    # =========================
    if weak_hit and not (strong_hit or medium_hit or pattern_score):
        score -= 0.5

    # =========================
    # 🔒 FINAL
    # =========================
    return max(0, min(score, 10))