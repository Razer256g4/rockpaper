"""
Human player model and wallet state.
"""
from typing import Dict
from constants import STARTING_BALANCE

class Player:
    """Represents the human player."""

    def __init__(self, name: str, data: Dict):
        self.name = name
        user_data = data.get(name, {})

        self.balance: int = user_data.get("balance", STARTING_BALANCE)
        self.total_games: int = user_data.get("total_games", 0)

    def to_dict(self) -> Dict:
        """Serializes player state for saving."""
        return {
            "balance": self.balance,
            "total_games": self.total_games,
        }

    def bet(self, amount: int) -> bool:
        """
        Attempts to subtract wager from balance.
        Returns False if insufficient funds.
        """
        if amount <= 0 or amount > self.balance:
            return False

        self.balance -= amount
        return True

    def win(self, amount: int) -> None:
        """Adds to balance, preventing negative balances."""
        self.balance += amount
        if self.balance < 0:
            self.balance = 0
