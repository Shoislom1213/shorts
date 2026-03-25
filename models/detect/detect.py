import whisper
import librosa
import numpy as np
import random

model = whisper.load_model("small")


def detect_speech(audio_path, num_samples=15, chunk_duration=8, threshold=0.3):
    y, sr = librosa.load(audio_path, sr=16000)

    chunk_size = int(sr * chunk_duration)
    total_length = len(y)

    speech_count = 0
    checked = 0

    for _ in range(num_samples):
        start = random.randint(0, max(0, total_length - chunk_size))
        end = start + chunk_size

        y_sample = y[start:end]

        energy = np.mean(librosa.feature.rms(y=y_sample))
        if energy < 0.01:
            continue  # skip jim joy

        checked += 1

        result = model.transcribe(
            y_sample,
            language="uz",
            fp16=False,  
            verbose=False
        )

        text = result["text"].strip()

        if len(text.split()) >= 3:
            speech_count += 1

    if checked == 0:
        return False

    ratio = speech_count / checked

    return ratio >= threshold