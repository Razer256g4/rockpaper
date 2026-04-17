"""
Predictive AI opponent model using transition probabilities.
"""
import random
from typing import List, Dict
from constants import CHOICES, WIN_MAP, AI_STARTING_BALANCE

class AIPlayer:
    """Simple predictive AI based on previous move transitions."""

    def __init__(self, data: Dict):
        self.history: Dict[str, Dict[str, int]] = data.get(
            "ai_history",
            {
                "rock": {"rock": 0, "paper": 0, "scissors": 0},
                "paper": {"rock": 0, "paper": 0, "scissors": 0},
                "scissors": {"rock": 0, "paper": 0, "scissors": 0},
            },
        )
        self.balance: int = data.get("ai_balance", AI_STARTING_BALANCE)
        self.last_moves: List[str] = []

    def get_moves(self) -> List[str]:
        """Generate 3 predicted moves based on the user's last turn."""
        # Until enough history exists in session, use random moves.
        if len(self.last_moves) != 3:
            return [random.choice(CHOICES) for _ in range(3)]

        ai_choices = []
        for last_human_move in self.last_moves:
            predictions = self.history.get(last_human_move, {})
            predicted_move = self._get_most_likely_move(predictions)
            ai_choices.append(self._get_counter_move(predicted_move))

        return ai_choices

    def _get_most_likely_move(self, predictions: Dict[str, int]) -> str:
        """Find the move the human is most likely to play."""
        if not predictions or all(freq == 0 for freq in predictions.values()):
            return random.choice(CHOICES)

        return max(predictions, key=predictions.get)

    def _get_counter_move(self, move: str) -> str:
        """Find the move that beats the predicted move."""
        for candidate, defeated_move in WIN_MAP.items():
            if defeated_move == move:
                return candidate
        return "paper"

    def update_history(self, current_human_moves: List[str]) -> None:
        """Record the user's latest moves into the history Bigram."""
        if len(self.last_moves) == 3:
            for previous_move, current_move in zip(self.last_moves, current_human_moves):
                self.history[previous_move][current_move] += 1

        self.last_moves = current_human_moves

    def get_history_data(self) -> Dict:
        """Serializes AI history state for saving."""
        return self.history
