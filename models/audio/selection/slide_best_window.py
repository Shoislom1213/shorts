def generate_context_windows(window, all_segments, min_dur=30, max_dur=45):

    # 🔥 1. window ichidagi segmentlar
    inside = [
        s for s in all_segments
        if s["start"] >= window["start"] and s["end"] <= window["end"]
    ]

    if not inside:
        return []

    first_idx = all_segments.index(inside[0])
    last_idx = all_segments.index(inside[-1])

    results = []

    # 🔥 2. expansion size (A lar soni)
    for total_expand in range(1, 6):  # AAAA → 4 ta gacha

        # 🔥 3. patternlar (AAAA0, AAA0A, ...)
        for left_count in range(total_expand + 1):
            right_count = total_expand - left_count

            left_idx = first_idx - left_count
            right_idx = last_idx + right_count

            # ❌ chegaradan chiqmasin
            if left_idx < 0 or right_idx >= len(all_segments):
                continue

            segs = all_segments[left_idx:right_idx + 1]

            start = segs[0]["start"]
            end = segs[-1]["end"]
            duration = end - start

            # 🎯 duration filter
            if duration < min_dur or duration > max_dur:
                continue

            text = " ".join([s["text"] for s in segs])

            results.append({
                "start": start,
                "end": end,
                "duration": duration,
                "text": text,
                "pattern": f"{'A'*left_count}0{'A'*right_count}",
                "segments": len(segs)
            })

    return results