"""
persistence.py — Data storage for the TSIS3 Racer game.
Handles reading and writing of two JSON files:
  - settings.json  → player preferences (sound, car color, difficulty)
  - leaderboard.json → top 10 scores

All data is stored as JSON so it persists between game sessions.
If a file is missing or corrupted, it is automatically recreated with defaults.
"""

import json
import os

# ─────────────────────────────────────────────
#  FILE NAMES
# ─────────────────────────────────────────────

# Files are created in the same folder the script runs from (the project root)
SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

# ─────────────────────────────────────────────
#  DEFAULT VALUES
# ─────────────────────────────────────────────

# Used when settings.json doesn't exist yet or is missing a key
DEFAULT_SETTINGS = {
    "sound":      True,      # crash sound effect on/off
    "car_color":  "Orange",  # which player car sprite to load
    "difficulty": "Normal"   # controls traffic spawn rate and speed
}

# Used when leaderboard.json doesn't exist yet — starts as an empty list
DEFAULT_LEADERBOARD = []


# ─────────────────────────────────────────────
#  GENERIC JSON HELPERS
# ─────────────────────────────────────────────

def load_json(filename, default_data):
    """
    Load data from a JSON file and return it.
    If the file doesn't exist or is corrupted (invalid JSON / OS error),
    the file is recreated with default_data and that default is returned.

    This means the game never crashes on a missing or broken save file —
    it silently resets to defaults instead.

    Parameters:
        filename     (str): path to the JSON file
        default_data (dict or list): value to use if the file can't be read

    Returns:
        The parsed JSON content, or a copy of default_data on failure.
    """
    if not os.path.exists(filename):
        # First run — file doesn't exist yet, create it with defaults
        save_json(filename, default_data)
        # Return a copy so callers can't accidentally mutate the default
        return default_data.copy() if isinstance(default_data, dict) else list(default_data)

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)  # parse the JSON text into a Python dict/list
    except (json.JSONDecodeError, OSError):
        # File exists but is broken (empty, garbled, permission error, etc.)
        # Reset it to defaults and continue normally
        save_json(filename, default_data)
        return default_data.copy() if isinstance(default_data, dict) else list(default_data)


def save_json(filename, data):
    """
    Serialize data to JSON and write it to a file.
    indent=4 makes the file human-readable (pretty-printed).

    Parameters:
        filename (str): path to write to
        data (dict or list): the data to save
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ─────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────

def load_settings():
    """
    Load settings from settings.json.
    After loading, checks that every key from DEFAULT_SETTINGS is present.
    This handles the case where a new setting was added to the code but
    the player's old settings.json was saved before that key existed.
    Returns the complete, validated settings dictionary.
    """
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

    # Fill in any missing keys with their default values
    # (important when we add new settings in future versions)
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value

    save_settings(settings)  # persist the filled-in version
    return settings


def save_settings(settings):
    """Save the current settings dictionary to settings.json."""
    save_json(SETTINGS_FILE, settings)


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────

def load_leaderboard():
    """
    Load the leaderboard from leaderboard.json.
    Returns a list of score dictionaries, sorted best-first (maintained by add_score).
    If the file contains something other than a list (corrupted data), returns an empty list.
    """
    scores = load_json(LEADERBOARD_FILE, DEFAULT_LEADERBOARD)

    # Guard against corrupted data where JSON parsed but wasn't a list
    if not isinstance(scores, list):
        scores = []

    return scores


def add_score(name, score, distance, coins):
    """
    Add a new result to the leaderboard and keep only the top 10 entries.

    Steps:
    1. Load the current leaderboard
    2. Append the new result as a dictionary
    3. Sort all entries by score, highest first
    4. Trim to at most 10 entries
    5. Save back to leaderboard.json

    Parameters:
        name     (str): player's username
        score    (int): final score (distance + coins * 15)
        distance (int): meters traveled
        coins    (int): coins collected during the run
    """
    leaderboard = load_leaderboard()

    # Append the new score entry
    leaderboard.append({
        "name":     name,
        "score":    int(score),     # cast to int in case floats slipped in
        "distance": int(distance),
        "coins":    int(coins)
    })

    # Sort descending by score so the best result is first
    leaderboard.sort(key=lambda item: item["score"], reverse=True)

    # Keep only the top 10 — discard any entries beyond that
    leaderboard = leaderboard[:10]

    save_json(LEADERBOARD_FILE, leaderboard)