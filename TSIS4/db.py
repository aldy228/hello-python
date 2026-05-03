"""
db.py — JSON-based data storage for the Snake game.
Originally designed for PostgreSQL, replaced with JSON to avoid
encoding errors and setup complexity while keeping the same interface.

All functions return the same types as the original database version,
so snake.py doesn't need to know whether data comes from JSON or SQL.
"""

import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  FILE PATH
# ─────────────────────────────────────────────

# Store leaderboard.json in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")


# ─────────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────────

def connect():
    """
    Placeholder that exists so any file importing 'connect' doesn't crash.
    JSON needs no connection — returns None.
    """
    return None


def create_tables():
    """
    In a real database this would run CREATE TABLE SQL.
    With JSON we just make sure the leaderboard file exists.
    Called once at startup in SnakeGame.__init__().
    """
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)  # start with an empty list


def get_or_create_player(username):
    """
    In a SQL version, this would INSERT a player row and return its ID.
    With JSON, players have no separate table — just return the username as-is.
    Kept so any callers don't need to change.
    """
    return username


# ─────────────────────────────────────────────
#  WRITE
# ─────────────────────────────────────────────

def save_result(username, score, level):
    """
    Append a game result to leaderboard.json.
    After appending, the list is sorted by score (highest first)
    and trimmed to 100 entries so the file never grows too large.

    Each entry is a dict with: username, score, level_reached, played_at.
    played_at uses the current local time formatted as "YYYY-MM-DD HH:MM".
    """
    try:
        # Load existing data (or start fresh if file is missing)
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        # Build the new entry dictionary
        new_entry = {
            "username":      username,
            "score":         score,
            "level_reached": level,
            "played_at":     datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(new_entry)

        # Keep only the top 100 scores to cap file size
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:100]

        # Write back to disk (indent=2 keeps it human-readable)
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as error:
        print("Error saving result:", error)


# ─────────────────────────────────────────────
#  READ
# ─────────────────────────────────────────────

def get_personal_best(username):
    """
    Find the highest score ever recorded for a specific username.
    Filters all entries by username, then returns the max score.
    Returns 0 if the player has no recorded games yet.
    """
    try:
        if not os.path.exists(LEADERBOARD_FILE):
            return 0

        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # List comprehension: collect scores only for this user
        user_scores = [entry["score"] for entry in data if entry["username"] == username]

        return max(user_scores) if user_scores else 0

    except Exception as error:
        print("Error getting personal best:", error)
        return 0


def get_top_10():
    """
    Return the top 10 scores from leaderboard.json.

    Returns a list of tuples in the format:
        (username, score, level_reached, played_at)

    Tuples are used (not dicts) to match the format the original PostgreSQL
    version returned — so snake.py can unpack rows the same way either way:
        username, score, level, date = row
    """
    try:
        if not os.path.exists(LEADERBOARD_FILE):
            return []

        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Sort by score descending and take the top 10
        sorted_data = sorted(data, key=lambda x: x["score"], reverse=True)
        top = sorted_data[:10]

        # Convert each dict to a tuple matching the old DB row format
        return [
            (entry["username"], entry["score"], entry["level_reached"], entry["played_at"])
            for entry in top
        ]

    except Exception as error:
        print("Database error while getting leaderboard:", error)
        return []