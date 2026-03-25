import numpy as np
import librosa
from utils import get_audio_path


# 🔥 LOAD AUDIO (1 marta)
def load_audio():
    path = get_audio_path()
    audio, sr = librosa.load(path, sr=None)
    return audio, sr


# 🔥 GLOBAL STATS (dynamic threshold)
def get_global_audio_stats(audio):
    rms = librosa.feature.rms(y=audio)[0]

    return {
        "rms_mean": float(np.mean(rms)),
        "rms_std": float(np.std(rms))
    }


# 🔥 WINDOW CUT
def get_window_audio(audio, sr, start, end):
    start_sample = max(0, int(start * sr))
    end_sample = min(len(audio), int(end * sr))

    if start_sample >= end_sample:
        return np.array([])

    return audio[start_sample:end_sample]


# 🔥 FEATURE EXTRACTION (PATCHED RMS 🔥)
def extract_audio_features(audio_slice, sr):
    if len(audio_slice) < sr * 0.2:
        return {
            "volume": 0,
            "energy": 0,
            "variation": 0,
            "rms": np.array([])
        }

    # ✅ PATCH: better RMS params
    rms = librosa.feature.rms(
        y=audio_slice,
        frame_length=2048,
        hop_length=512
    )[0]

    return {
        "volume": float(np.max(rms)),
        "energy": float(np.mean(rms)),
        "variation": float(np.std(rms)),
        "rms": rms
    }


# 🔥 SPIKE DETECTION (PATCHED 🔥)
def spike_score(rms):
    if len(rms) < 2:
        return 0

    diff = np.diff(rms)

    # ✅ PATCH: dynamic threshold
    threshold = np.mean(diff) + np.std(diff)

    spikes = np.sum(diff > threshold)

    return min(int(spikes), 3)


# 🔥 SILENCE DETECTION (PATCHED 🔥)
def silence_score(energy, stats):
    if energy < stats["rms_mean"] * 0.3:
        return 1
    return 0


# 🔥 AUDIO EMOTION SCORE
def audio_emotion_score(features, stats):
    score = 0

    volume = features["volume"]
    energy = features["energy"]
    variation = features["variation"]
    rms = features["rms"]

    mean = stats["rms_mean"]
    std = stats["rms_std"]

    # 🔊 volume (relative)
    if volume > mean + 2 * std:
        score += 3
    elif volume > mean + std:
        score += 2
    elif volume > mean:
        score += 1

    # ⚡ energy
    if energy > mean + std:
        score += 2

    # 🔥 variation
    if variation > std:
        score += 2

    # ⚡ spike
    score += spike_score(rms)

    # 😈 silence (PATCHED)
    score += silence_score(energy, stats)

    return score


# 🔥 MAIN FUNCTION
def process_window_audio(window, audio, sr, stats):
    audio_slice = get_window_audio(
        audio,
        sr,
        window["start"],
        window["end"]
    )

    features = extract_audio_features(audio_slice, sr)

    score = audio_emotion_score(features, stats)

    # ✅ PATCH: normalization qo‘shildi
    norm_score = min(score / 10, 1.0)

    window.update({
        "audio_emotion": score,
        "audio_emotion_norm": norm_score,
        "volume": features["volume"],
        "energy": features["energy"],
        "variation": features["variation"]
    })

    return window


# 🔥 MAIN PIPELINE (nom saqlandi)
def emotion_audio_score(windows):
    audio, sr = load_audio()
    stats = get_global_audio_stats(audio)

    results = []

    for w in windows:
        w = process_window_audio(w, audio, sr, stats)
        results.append(w)

    return results