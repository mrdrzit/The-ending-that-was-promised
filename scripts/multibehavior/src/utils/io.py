import json
from pathlib import Path

def load_session_groups(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)["merged"]

    for group_key in data:
        data[group_key] = [Path(p.replace("\\", "/")) for p in data[group_key]]

    session_group_map = {}

    for group_key, paths in data.items():
        phase = "treino" if group_key.startswith("tr") else "teste"
        context = "A" if group_key.endswith("a") else "B"

        for p in paths:
            session_group_map[p.stem] = {
                "group": group_key,
                "phase": phase,
                "context": context,
                "video_path": p
            }

    return session_group_map
