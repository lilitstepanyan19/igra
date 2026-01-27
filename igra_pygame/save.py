import json
import os

SAVE_FILE = "save.json"


def save_progress(world_name):
    with open(SAVE_FILE, "w") as f:
        json.dump({"world": world_name}, f)


def load_progress():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
        return data.get("world")
