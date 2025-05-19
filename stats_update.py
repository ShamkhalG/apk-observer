from filelock import FileLock
import json

lock = FileLock("stats.json.lock")

def update_stat(module, key, value):
    with lock:
        try:
            with open("stats.json", "r") as f:
                stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stats = {}

        stats.setdefault(module, {})
        stats[module][key] = value

        with open("stats.json", "w") as f:
            json.dump(stats, f, indent = 4)