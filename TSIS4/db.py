"""
db.py - JSON-based storage (replaces PostgreSQL)
No more encoding errors. Works instantly.
"""

import json
import os
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

def connect():
    """Placeholder so other files don't crash"""
    return None

def create_tables():
    """JSON doesn't need tables. Just creates the file if missing."""
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def get_or_create_player(username):
    """JSON doesn't use IDs. Just returns the username."""
    return username

def save_result(username, score, level):
    """Save game result to leaderboard.json"""
    try:
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        new_entry = {
            "username": username,
            "score": score,
            "level_reached": level,
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(new_entry)

        # Sort by score (highest first) and keep top 100
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:100]

        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as error:
        print("Error saving result:", error)

def get_personal_best(username):
    """Get best score for a user from JSON"""
    try:
        if not os.path.exists(LEADERBOARD_FILE):
            return 0
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        user_scores = [entry["score"] for entry in data if entry["username"] == username]
        return max(user_scores) if user_scores else 0
    except Exception as error:
        print("Error getting personal best:", error)
        return 0

def get_top_10():
    """Get top 10 scores from JSON (returns same format as database)"""
    try:
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sorted_data = sorted(data, key=lambda x: x["score"], reverse=True)
        top = sorted_data[:10]
        # Return as tuples to match old database format: (username, score, level, date)
        return [(entry["username"], entry["score"], entry["level_reached"], entry["played_at"]) for entry in top]
    except Exception as error:
        print("Database error while getting leaderboard:", error)
        return []