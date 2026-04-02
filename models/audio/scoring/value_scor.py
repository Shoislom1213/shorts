from logger import setup_logger
logger = setup_logger("Value")

def value_score(text):
    text = text.lower()
    score = 0

    # 🔥 MAIN LOOP
    for group in VALUE_DICT.values():
        for kw in group["keywords"]:
            if kw in text:
                score += group["weight"]

    # 🔁 STRUCTURE BONUS
    if "if you" in text and "you will" in text:
        score += 2

    # 🎯 LIMIT
    logger.info(f"📝 Value score yakunlandi")
    return min(score, 10)

VALUE_DICT = {
        # 🔥 STRONG PHRASES (eng kuchli signal)
        "strong_phrases": {
            "keywords": [
                "how to", "the way to", "the secret to", "the key to",
                "this is how", "here's how", "let me show you",
                "let me tell you", "what you need to do",
                "if you want to", "this is why", "the reason is"
            ],
            "weight": 2
        },

        # ⚡ ACTION / DOING
        "actions": {
            "keywords": [
                "start", "stop", "build", "create", "focus", "work",
                "train", "practice", "repeat", "improve", "develop",
                "wake", "study", "read", "write", "speak", "listen",
                "apply", "execute", "do it"
            ],
            "weight": 1
        },

        # 🎓 LEARNING / GROWTH
        "learning": {
            "keywords": [
                "learn", "skill", "knowledge", "experience",
                "growth", "improvement", "education", "ability",
                "mindset", "understand", "master"
            ],
            "weight": 1
        },

        # 🧠 DISCIPLINE / HABITS
        "discipline": {
            "keywords": [
                "discipline", "habit", "routine", "consistency",
                "focus", "effort", "hard work", "daily",
                "morning routine", "grind"
            ],
            "weight": 1
        },

        # 📈 RESULT / SUCCESS
        "results": {
            "keywords": [
                "success", "result", "future", "win", "achieve",
                "become", "change", "transform", "level up",
                "grow", "improve your life"
            ],
            "weight": 1
        },

        # 🧩 LOGIC / EXPLANATION
        "logic": {
            "keywords": [
                "because", "that is why", "this means",
                "the reason", "so that", "therefore",
                "this leads to"
            ],
            "weight": 1
        }
    }