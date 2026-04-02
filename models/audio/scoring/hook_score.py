import re
from logger import setup_logger
logger = setup_logger("hook score")

HOOK_PHRASES = {

    # 🔥 ULTRA VIRAL (max power)
    "this will change your life": 6,
    "you will not believe": 6,
    "this is what nobody tells you": 6,
    "this is what no one tells you": 6,
    "this changes everything": 6,

    # 💥 STRONG ATTACK (psychological)
    "you are wasting your time": 5.5,
    "you are doing this wrong": 5,
    "you are missing this": 5,
    "you are not ready for this": 5.5,
    "you are sabotaging yourself": 5.5,

    # 🧠 CURIOSITY / HOOK
    "what if": 4,
    "have you ever": 4,
    "do you know": 4,
    "did you know": 4,
    "guess what": 4,
    "want to know": 4,
    "what happens if": 4.5,

    # 🔥 CONTRAST / YOU VS OTHERS
    "while others": 5,
    "most people": 5,
    "everyone else": 4.5,
    "people think": 4,
    "you think": 4,
    "they think": 3.5,

    # 🎯 PROMISE / RESULT
    "this is why": 4,
    "this is how": 4,
    "this is the reason": 4,
    "the truth is": 4,
    "here is the truth": 4,
    "this is the secret": 4.5,
    "the secret is": 4.5,

    # 🚀 MOTIVATION (ENG MUHIM SENGA)
    "you can do this": 4,
    "you got this": 4,
    "this is your moment": 4.5,
    "this is your chance": 4.5,
    "your future depends on this": 5,
    "this will make you unstoppable": 5.5,
    "this will make you better": 4.5,
    "this will change your mindset": 5,

    # ⚡ COMMAND (clean)
    "listen carefully": 3.5,
    "pay attention": 3.5,
    "remember this": 3.5,
    "watch this": 3.5,
    "look at this": 3.5,

    # 😮 SHOCK / REACTION
    "this is insane": 4,
    "this is crazy": 4,
    "this is wild": 4,
    "this is unbelievable": 5,

    # 🗣️ STORYTELLING
    "let me tell you": 3.5,
    "i will tell you this": 3.5,
    "let me show you": 3.5,
    "i want to tell you something": 3.5,
    "you need to hear this": 5,
    "this will shock you": 5,
    "listen to this carefully": 4.5
}

SLANG_HOOKS = {
    # 🔥 strong attention grab
    "bro listen": 3,
    "listen bro": 3,
    "look bro": 3,
    "look man": 3,

    # 🧠 persuasion / trust
    "trust me bro": 3.5,
    "i am telling you": 3.5,
    "real talk": 3,
    "dead serious": 3,
    "no joke": 3,

    # 💬 conversational
    "you know what": 2.5,
    "you know what i am saying": 2.5,
    "honestly": 2.2,
    "for real": 2.2,
    "straight up": 2.2,

    # ⚡ modern slang
    "lowkey": 2,
    "highkey": 2,

    # 🎯 command-ish slang
    "you gotta": 2.8,
    "you gotta understand": 3.2
}

COMMANDS = {
    "strong": {
        "words": ["listen", "look", "watch"],
        "phrases": ["listen carefully", "look at this", "watch this"],
        "weight": 3
    },

    "mental": {
        "words": ["imagine", "think", "remember"],
        "phrases": ["imagine this", "think about it", "remember this"],
        "weight": 2.5
    },

    "action": {
        "words": ["stop", "start", "focus"],
        "phrases": ["stop doing this", "start doing this", "focus on this"],
        "weight": 3
    }
}

QUESTION_TRIGGERS = {
    "strong": {
        "phrases": [
            "do you know", "have you ever", "did you know",
            "are you aware", "can you imagine"
        ],
        "weight": 3
    },

    "medium": {
        "phrases": [
            "what if", "why do", "how do",
            "why is", "how is"
        ],
        "weight": 2.5
    },

    "basic": {
        "words": ["why", "what", "how"],
        "weight": 1.5
    }
}

PATTERNS = {
    "command": {
        "patterns": [
            ("you", "must"),
            ("you", "should"),
            ("you", "need")
        ],
        "weight": 3
    },

    "promise": {
        "patterns": [
            ("this", "will"),
            ("change", "life")
        ],
        "weight": 3.5
    },

    "instruction": {
        "patterns": [
            ("how", "to"),
            ("best", "way")
        ],
        "weight": 2.5
    },

    "curiosity": {
        "patterns": [
            ("why", "you"),
            ("what", "happens")
        ],
        "weight": 2.5
    },

    "negative": {
        "patterns": [
            ("you", "wrong"),
            ("you", "mistake")
        ],
        "weight": 3
    },

    "social": {
        "patterns": [
            ("no", "one"),
            ("people", "do")
        ],
        "weight": 2
    },

    "action": {
        "patterns": [
            ("start", "now"),
            ("stop", "doing")
        ],
        "weight": 3
    }
}

NEGATIVE_WORDS = ["wrong", "mistake", "wasting", "fail", "problem", "bad"]

# 🔥 HOOK TRIGGER PHRASES LUG'ATI
triggers = {

    # 🔥 NEGATION (eng kuchli hook)
    "negation": {t: {"weight": 2.0, "max_position": 1.0} for t in [
        "it was not", "this is not", "this was not", "it is not",
        "not about", "never about", "it was never",
        "you do not need", "you do not have to", "you are not",
        "nothing will", "no one can", "never say", "don't ever",
        "it's not true", "you cannot", "cannot be"
    ]},

    # 🔥 CONTRAST (viral pattern)
    "contrast": {t: {"weight": 1.5, "max_position": 1.0} for t in [
        "while others", "most people", "everyone else", "other people",
        "others are", "people are", "they are", "while they", "while most",
        "unlike them", "different from others", "you are unlike", "they don't",
        "everyone thinks", "they all"
    ]},

    # 🧠 CONDITIONAL / IF PATTERN (faqat segment boshida)
    "conditional": {t: {"weight": 2.0, "max_position": 0.3} for t in [
        "if you", "if you want", "if you are", "if you think",
        "if you really", "if you ever", "if you do not", "if you cannot",
        "in case you", "should you", "when you", "whenever you", "once you"
    ]},

    # 🎯 IMAGINATION / ATTENTION
    "imagination": {t: {"weight": 1.2, "max_position": 1.0} for t in [
        "imagine", "imagine this", "just imagine", "think about",
        "picture this", "visualize this", "can you picture", "consider this",
        "envision", "what if", "try to imagine", "let's picture"
    ]},

    # 💬 STORY / DIRECT TALK
    "story": {t: {"weight": 1.0, "max_position": 1.0} for t in [
        "let me tell you", "let me tell you something", "i will tell you",
        "i am telling you", "trust me", "believe me", "you won't believe",
        "listen closely", "hear this", "pay attention", "i have to tell you"
    ]},

    # ⚡ TRUTH / REVEAL
    "truth": {t: {"weight": 1.5, "max_position": 1.0} for t in [
        "the truth is", "here is the truth", "this is the truth",
        "the reality is", "this is why", "this is how",
        "what actually happens", "what you need to know",
        "truth be told", "let's be honest", "fact is"
    ]},

    # 🚀 RESULT / PROMISE
    "result": {t: {"weight": 1.3, "max_position": 1.0} for t in [
        "this will", "this can", "this will make you", "this will change",
        "this will help you", "you will", "you can", "you are going to",
        "it will", "it can", "expect this", "results will", "guaranteed to"
    ]}
}
all_hook_triggers = [phrase for group in triggers.values() for phrase in group]

BAD_ENDING_GROUPS = {

    # 🔥 STORY SHIFT (eng xavfli)
    "story_shift": {
        "phrases": [
            "let me tell you",
            "i will tell you",
            "i want to tell you",
            "i'm going to tell you",
            "let me share",
            "i will share",
            "i want to share",
        ]
    },

    # 🔥 LIST / STRUCTURE (cut qilish kerak)
    "list_start": {
        "phrases": [
            "first",
            "second",
            "third",
            "next",
            "another",
            "one more thing",
            "finally",
        ]
    },

    # 🔥 TRANSITION (yangi fikr boshlanishi)
    "transition": {
        "phrases": [
            "and now",
            "but now",
            "so now",
            "now let",
            "moving on",
            "after that",
        ]
    },

    # 🔥 EXPLANATION CONTINUE
    "continuation": {
        "phrases": [
            "this is why",
            "this is how",
            "because",
            "so that",
            "in order to",
        ]
    },

    # 🔥 TEACHING MODE
    "teaching": {
        "phrases": [
            "you should",
            "you need to",
            "you have to",
            "try to",
            "make sure",
        ]
    },

    # 🔥 WEAK CONNECTORS
    "connectors": {
        "phrases": [
            "and",
            "but",
            "so",
            "also",
        ]
    }
}
def normalize(text):
    text = text.lower()

    repl = {
        # basic
        "you're": "you are",
        "i'm": "i am",
        "it's": "it is",
        "don't": "do not",
        "won't": "will not",
        "can't": "cannot",
        "didn't": "did not",
        "doesn't": "does not",
        "isn't": "is not",
        "ain't": "is not",
        "lemme": "let me",
        "gimme": "give me",

        # slang
        "gonna": "going to",
        "wanna": "want to",
        "gotta": "got to",
        "kinda": "kind of",
        "sorta": "sort of",

        # short forms
        r"\bu\b": "you",
        r"\bur\b": "your"
    }

    for k, v in repl.items():
        if k.startswith(r"\b"):  # regex (masalan: \bu\b)
            text = re.sub(k, v, text)
        else:  # oddiy string (masalan: "you're")
            text = text.replace(k, v)

    # fillers (tozalash)
    fillers = ["you know", "i mean", "like", "you know what i mean", "basically"]
    for f in fillers:
        text = re.sub(rf"\b{re.escape(f)}\b", " ", text)

    # ortiqcha space larni tozalash
    text = re.sub(r"\s+", " ", text).strip()

    return text

def contains_word(text, word):
    return re.search(rf"\b{re.escape(word)}\b", text) is not None

def contains_phrase(text, phrase):
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None

def flexible_match(text, phrase):
    return all(contains_word(text, w) for w in phrase.split())

def contains_word(text, word):
    return re.search(rf"\b{re.escape(word)}\b", text) is not None

def soft_phrase_match(text, phrase):
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None

def flexible_phrase_match(text, phrase, max_gap=2):
    words = phrase.split()
    text_words = text.split()
    idx = 0
    for w in words:
        while idx < len(text_words) and text_words[idx] != w:
            idx += 1
        if idx >= len(text_words):
            return False
        idx += 1
    return True

def pattern_score(text):
    scores = []

    if re.search(r"if you .* you .*", text[:100]):
        scores.append(3)

    if re.search(r"not .* but .*", text):
        scores.append(3)

    if re.search(r"the more .* the more", text):
        scores.append(3)

    if "you will" in text:
        scores.append(2)

    if "you can" in text:
        scores.append(1.5)

    return min(max(scores) if scores else 0, 6)

def slang_score(text):
    score = 0

    for phrase, weight in SLANG_HOOKS.items():
        if soft_phrase_match(text, phrase):
            score += weight

    return min(score, 5)

def command_score(text):
    score = 0

    for group in COMMANDS.values():
        if any(re.search(rf"\b{re.escape(p)}\b", text) for p in group.get("phrases", [])):
            score += group["weight"]
        elif any(re.search(rf"\b{w}\b", text) for w in group["words"]):
            score += group["weight"]

    return min(score, 5)

def question_score(text):
    max_weight = 0

    for group in QUESTION_TRIGGERS.values():
        triggered = False

        if any(re.search(rf"\b{re.escape(p)}\b", text) for p in group.get("phrases", [])):
            triggered = True
        elif any(contains_word(text, w) for w in group.get("words", [])):
            triggered = True

        if triggered:
            max_weight = max(max_weight, group["weight"])

    score = max_weight

    # ❓ punctuation (soft boost)
    if "?" in text:
        score += 1

    return min(score, 5)

def phrase_score(text):
    max_score = 0
    text_words = text.split()
    for phrase, weight in HOOK_PHRASES.items():
        if flexible_phrase_match(text, phrase):
            # position penaltiyasi
            idx = text.find(phrase)
            pos = len(text[:idx].split()) / len(text_words)
            score = weight * (1 - pos)
            max_score = max(max_score, score)
    return min(max_score, 6)

def negative_score(text):
    if any(contains_word(text, w) for w in NEGATIVE_WORDS):
        return 1.5
    return 0

def get_trigger_weight(t):
    if t in ["it was not", "this is not", "never about"]:
        return 3
    elif t in ["while others", "most people"]:
        return 3
    elif t.startswith("if you"):
        return 1.5
    elif "tell" in t:
        return 1
    else:
        return 2
    
def hook_position_score(text):
    text_lower = text.lower()
    words = text_lower.split()
    best = 0

    for t in all_hook_triggers:
        match = re.search(re.escape(t), text_lower)
        if not match:
            continue

        idx = match.start()
        word_idx = len(text_lower[:idx].split())
        pos = word_idx / len(words)

        # dictionary'dan weight va max_position olish
        w = 2
        max_pos = 1.0
        for cat, group in triggers.items():
            if t in group:
                w = group[t]["weight"]
                max_pos = group[t]["max_position"]
                break

        # position penaltiya (conditional trigger boshida bo‘lsa yuqori score)
        score = w * (1 - min(pos, max_pos))
        best = max(best, score)

    return best

def trim_bad_ending(text):
    sentences = text.split(".")
    clean = []

    for s in sentences:
        s_clean = normalize(s.strip())
        stop = False
        for group in BAD_ENDING_GROUPS.values():
            for phrase in group["phrases"]:
                if re.search(rf"\b{re.escape(phrase)}\b", s_clean, re.I):
                    stop = True
                    break
            if stop:
                break
        if stop:
            break
        clean.append(s.strip())

    if not clean:
        return text.strip()

    result = ". ".join(clean).strip()
    if not result.endswith("."):
        result += "."
    return result

def hook_score(window):
    text = normalize(window["text"])
    first = text[:220]

    score = 0

    # 🔥 order + weight redistrib
    main_signal = (
        pattern_score(first) * 0.3 +   # oldin 0.4
        phrase_score(first) * 0.4 +    # oldin 0.3
        command_score(first) * 0.2 +
        question_score(first) * 0.1
    )

    score = main_signal

    # support
    score += slang_score(first) * 0.7   # oldin 0.5
    score += negative_score(first)
    score += hook_position_score(first)

    # bonus first 20 words
    if len(first.split()) <= 20:
        score += 0.2
    logger.info("📝 Hook score yakunlandi")
    return min(score, 10)