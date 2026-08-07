import json
import os

# На Android берем приватную папку приложения, на ПК — текущую папку
BASE_DIR = os.environ.get("ANDROID_PRIVATE", ".")
SAVE_FILE = os.path.join(BASE_DIR, "save.json")


def save_progress(world_name):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"world": world_name}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")


def load_progress():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("world")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None
