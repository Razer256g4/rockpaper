"""
Core game configuration constants.
"""

CHOICES = ["rock", "paper", "scissors"]
WIN_MAP = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

SAVE_FILE = "save_data.json"
STARTING_BALANCE = 1000
AI_STARTING_BALANCE = 5000
DECAY_FACTOR = 0.95
