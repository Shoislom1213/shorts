import re
from logger import setup_logger
logger = setup_logger("text_emotion") 

# 🔥 NORMALIZATION
def normalize_text(text):
    text = text.lower()

    # remove repeated letters: noooo → no
    text = re.sub(r"(.)\1{2,}", r"\1", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text


# 🔥 WORD BOUNDARY MATCH (no substring bugs)
def match_phrase(text, phrase):
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


# 🔥 NEGATION HANDLING
NEGATIONS = ["not", "never", "no"]

def is_negated(text, phrase):
    pattern = rf"\b(not|never|no)\b(?:\W+\w+){{0,2}}\W+{re.escape(phrase)}"
    return re.search(pattern, text) is not None


# 🔥 MAIN FUNCTION
def emotion_text_score(text):
    text_norm = normalize_text(text)
    score = 0
    matched = set()

    for phrase, weight in SORTED_PHRASES:
        if match_phrase(text_norm, phrase):
            if phrase not in matched:

                if not is_negated(text_norm, phrase):
                    count = len(re.findall(rf"\b{re.escape(phrase)}\b", text_norm))
                    boost = min(count, 2)
                    score += weight * boost
                matched.add(phrase)

    # 🔥 punctuation (capped)
    score += min(text.count("!"), 3) * 0.5
    score += min(text.count("?"), 3) * 0.5

    logger.info(f"📝 Text emotion yakunlandi")

    return score


EMOTION_WORDS = {
    # 🔥 SHOCK / SURPRISE
    "unbelievable": 3, "no way": 3, "nooo way": 3,
    "wtf": 4, "what the hell": 3, "what the fuck": 4,
    "insane": 3, "crazy": 2, "wild": 2, "shocking": 3,
    "mind blowing": 4, "blown away": 3,
    "are you serious": 3, "you gotta be kidding": 3,

    # ⚡ EXCITEMENT / HYPE
    "amazing": 2, "incredible": 3, "wow": 2, "woah": 2,
    "awesome": 2, "lets go": 3, "let's go": 3,
    "yess": 2, "yesss": 2, "omg": 3, "omfg": 4,
    "fire": 3, "lit": 3, "so good": 2,
    "goat": 3, "legendary": 3, "next level": 3,
    "this is insane": 3, "this is crazy": 3,

    # 🧠 CURIOSITY / HOOK
    "you won't believe": 4, "you wouldnt believe": 4,
    "guess what": 3, "did you know": 3,
    "wait for it": 3, "watch this": 2,
    "what happens next": 3, "this is why": 2,
    "here's the thing": 2, "listen to this": 2,
    "pay attention": 2,

    "you": 0.5,

    # 🚀 MOTIVATION / SELF IMPROVEMENT (🔥 ENG MUHIM)
    "unstoppable": 3,
    "discipline": 2,
    "focus": 2,
    "success": 2,
    "winning": 2,
    "winner": 2,
    "grind": 2,
    "hard work": 2,
    "no excuses": 3,
    "stay focused": 2,
    "keep going": 2,
    "never give up": 3,
    "don’t quit": 3,
    "push yourself": 3,
    "level up": 3,
    "improve yourself": 2,
    "be better": 2,
    "be stronger": 2,
    "grow": 2,
    "growth": 2,
    "progress": 2,
    "future": 1,
    "your future": 2,
    "change your life": 4,
    "this will change your life": 4,
    "your life will change": 4,
    "you can do this": 2,
    "you got this": 2,

    # 🧠 REAL TALK / TRUTH
    "this is the truth": 3,
    "the truth is": 3,
    "let me tell you": 2,
    "listen carefully": 2,
    "remember this": 2,
    "don't forget": 2,
    "mark my words": 3,
    "i promise you": 3,

    # 😢 SADNESS / NEGATIVE
    "sad": 2, "so sad": 2, "terrible": 3,
    "worst": 3, "pain": 2, "it hurts": 3,
    "cry": 3, "crying": 3, "i cried": 3,
    "heartbreaking": 4, "devastating": 4,
    "depressing": 3, "so bad": 2,

    # 😡 ANGER
    "angry": 2, "mad": 2, "furious": 3,
    "pissed": 3, "so mad": 3,
    "this is stupid": 3, "this is dumb": 3,
    "i hate this": 4, "hate this": 3,

    # 🤯 SLANG / INTERNET LANGUAGE
    "bruh": 2, "nah": 1, "yo": 1, "bro": 1,
    "dude": 1, "man": 1,
    "lmao": 3, "lmfao": 4, "rofl": 3,
    "dead": 2, "i'm dead": 3, "im dead": 3,
    "no cap": 2, "cap": 1,
    "fr": 2, "for real": 2,
    "lowkey": 1, "highkey": 2,

    # 💥 STRONG STATEMENTS
    "this changed everything": 4,
    "this is insane": 3,
    "this is crazy": 3,
    "this is huge": 3,
    "this is big": 2,
    "game changer": 4,
    "life changing": 4,

    # 😱 FEAR / TENSION
    "scary": 2, "terrifying": 4,
    "creepy": 3, "fear": 2,
    "i was scared": 3,

    # 😂 HUMOR / REACTION
    "funny": 2, "hilarious": 3,
    "i can't stop laughing": 4,
    "this is funny": 2,
    "laughing": 2,

    # 🤔 CONFUSION / REACTION
    "what": 1, 
    "why": 1,
    "how": 1,
}


# 🔥 SORT (longest first)
SORTED_PHRASES = sorted(
    EMOTION_WORDS.items(),
    key=lambda x: len(x[0]),
    reverse=True
)
