from logger import setup_logger
logger = setup_logger("windows")

def create_windows(
    segments,
    min_duration=25,
    max_duration=59,
    min_words=5,
    step=1
):
    windows = []
    n = len(segments)

    for i in range(0, n, step):
        start = segments[i]["start"]
        text_parts = []

        for j in range(i, n):
            seg = segments[j]

            t = seg["text"].strip()

            if not t or t == ".":
                continue

            text_parts.append(t)

            end = seg["end"]
            duration = end - start

            text = " ".join(text_parts)

            if duration > max_duration:
                break

            if duration < min_duration:
                continue
            
            if not text or text.strip() == ".":
                continue

            if len(text.split()) < min_words:
                continue

            window ={
                "start": start,
                "end": end,
                "duration": duration,
                "text": text,
                "segment_count": j - i + 1
            }

            windows.append(window)
            logger.info(f"🪟 Window yaratildi: start={start}, end={end}, duration={duration:.1f}s, segments={window['segment_count']}")
            break
    logger.info(f"✅ Umumiy windows soni: {len(windows)}")
    return windows