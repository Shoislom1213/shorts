from models.audio.selection.top_windows import top_top
import json
with open("scored_windows.json", "r", encoding="utf-8") as f:
    result = json.load(f)

result = top_top(result)
print(result) 