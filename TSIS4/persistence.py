"""
Persistence Module - JSON-based storage
Simple alternative to PostgreSQL for practice projects
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "sound_enabled": True,
    "car_color": "red",
    "difficulty": "normal"
}


def load_json(filepath, default):
    """Load JSON file or return default"""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Warning: Could not load {filepath}: {e}")
    return default


def save_json(filepath, data):
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"❌ Error saving {filepath}: {e}")
        return False


def load_settings():
    """Load game settings"""
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    return {**DEFAULT_SETTINGS, **settings}


def save_settings(settings):
    """Save game settings"""
    return save_json(SETTINGS_FILE, settings)


def get_top_10(limit=10):
    """Get top scores from leaderboard"""
    leaderboard = load_json(LEADERBOARD_FILE, [])
    # Sort by score descending
    sorted_lb = sorted(leaderboard, key=lambda x: x.get("score", 0), reverse=True)
    return sorted_lb[:limit]


def save_result(username, score, level):
    """Save game result to leaderboard"""
    leaderboard = load_json(LEADERBOARD_FILE, [])
    
    new_entry = {
        "username": username,
        "score": score,
        "level_reached": level,
        "played_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    leaderboard.append(new_entry)
    
    # Keep only top 100 to avoid huge file
    sorted_lb = sorted(leaderboard, key=lambda x: x.get("score", 0), reverse=True)[:100]
    
    return save_json(LEADERBOARD_FILE, sorted_lb)


def get_personal_best(username):
    """Get player's best score"""
    leaderboard = load_json(LEADERBOARD_FILE, [])
    
    # Find all entries for this user
    user_scores = [entry for entry in leaderboard if entry.get("username") == username]
    
    if not user_scores:
        return 0
    
    # Return highest score
    return max(entry.get("score", 0) for entry in user_scores)