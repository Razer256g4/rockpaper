"""
Predictive AI opponent model using transition probabilities.
"""
import random
from typing import List, Dict, Any
from constants import CHOICES, WIN_MAP, AI_STARTING_BALANCE, DECAY_FACTOR

class AIPlayer:
    """Predictive AI based on blended Trigram & Bigram transitions."""

    def __init__(self, data: Dict[str, Any]):
        self.bigram: Dict[str, Dict[str, float]] = data.get(
            "ai_history",
            {
                "rock": {"rock": 0.0, "paper": 0.0, "scissors": 0.0},
                "paper": {"rock": 0.0, "paper": 0.0, "scissors": 0.0},
                "scissors": {"rock": 0.0, "paper": 0.0, "scissors": 0.0},
            },
        )
        self.trigram: Dict[str, Dict[str, Dict[str, float]]] = data.get("ai_trigram", {})
        if not self.trigram:
            self.trigram = {
                c1: {c2: {"rock": 0.0, "paper": 0.0, "scissors": 0.0} for c2 in CHOICES}
                for c1 in CHOICES
            }

        self.balance: int = data.get("ai_balance", AI_STARTING_BALANCE)
        self.last_moves: List[str] = []
        self.prev_last_moves: List[str] = []

    def get_moves(self) -> List[str]:
        """Generate 3 predicted moves based on the user's historical sequences."""
        if len(self.last_moves) != 3:
            return [random.choice(CHOICES) for _ in range(3)]

        ai_choices = []
        for i, last_human_move in enumerate(self.last_moves):
            prev = last_human_move
            pprev = self.prev_last_moves[i] if len(self.prev_last_moves) == 3 else None

            bigram_counts = self.bigram.get(prev, {})
            trigram_counts = self.trigram.get(pprev, {}).get(prev, {}) if pprev else {}

            predicted_move = self._get_blended_prediction(bigram_counts, trigram_counts)
            ai_choices.append(self._get_counter_move(predicted_move))

        return ai_choices

    def _get_blended_prediction(self, bigram_counts: Dict[str, float], trigram_counts: Dict[str, float]) -> str:
        """Find the move the human is most likely to play using blended score."""
        scores = {}
        for move in CHOICES:
            b_count = bigram_counts.get(move, 0.0)
            t_count = trigram_counts.get(move, 0.0)
            scores[move] = (2.0 * t_count) + (1.0 * b_count)

        if not scores or all(score == 0.0 for score in scores.values()):
            return random.choice(CHOICES)

        return max(scores, key=scores.get)

    def _get_counter_move(self, move: str) -> str:
        """Find the move that beats the predicted move."""
        for candidate, defeated_move in WIN_MAP.items():
            if defeated_move == move:
                return candidate
        return "paper"

    def _decay_dict(self, d: Dict) -> None:
        """Recursively multiply counts by the decay factor."""
        for k, v in d.items():
            if isinstance(v, dict):
                self._decay_dict(v)
            else:
                d[k] = v * DECAY_FACTOR

    def update_history(self, current_human_moves: List[str]) -> None:
        """Apply decay and record the user's latest moves into history."""
        self._decay_dict(self.bigram)
        self._decay_dict(self.trigram)

        if len(self.last_moves) == 3:
            for prev, curr in zip(self.last_moves, current_human_moves):
                self.bigram[prev][curr] += 1.0

            if len(self.prev_last_moves) == 3:
                for pprev, prev, curr in zip(self.prev_last_moves, self.last_moves, current_human_moves):
                    self.trigram[pprev][prev][curr] += 1.0

        if len(self.last_moves) == 3:
            self.prev_last_moves = self.last_moves
        self.last_moves = current_human_moves

    def get_history_data(self) -> Dict[str, Any]:
        """Serializes AI history states for saving."""
        return {
            "ai_history": self.bigram,
            "ai_trigram": self.trigram
        }
