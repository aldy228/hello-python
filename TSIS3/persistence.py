import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "Orange",
    "difficulty": "Normal"
}

DEFAULT_LEADERBOARD = []


def load_json(filename, default_data):
    """Load data from json file. If file is missing/broken, create default data."""
    if not os.path.exists(filename):
        save_json(filename, default_data)
        return default_data.copy() if isinstance(default_data, dict) else list(default_data)

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        save_json(filename, default_data)
        return default_data.copy() if isinstance(default_data, dict) else list(default_data)


def save_json(filename, data):
    """Save data to json file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_settings():
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

    # Make sure all required keys exist.
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value

    save_settings(settings)
    return settings


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


def load_leaderboard():
    scores = load_json(LEADERBOARD_FILE, DEFAULT_LEADERBOARD)
    if not isinstance(scores, list):
        scores = []
    return scores


def add_score(name, score, distance, coins):
    """Add new result and keep only top 10 scores."""
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })

    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    leaderboard = leaderboard[:10]
    save_json(LEADERBOARD_FILE, leaderboard)