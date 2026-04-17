"""
Handles persistence for player and AI state.
"""
import os
import json
from typing import Dict
from constants import SAVE_FILE

class FileManager:
    """Handles loading and saving of the game data to disk."""

    @staticmethod
    def load_data() -> Dict:
        """
        Loads the game data from the save file.
        Returns empty dictionary if file missing or corrupted.
        """
        if not os.path.exists(SAVE_FILE):
            return {}

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def save_data(data: Dict) -> None:
        """
        Saves the game data dict to the save file safely.
        """
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except IOError as error:
            print(f"Error saving data: {error}")
