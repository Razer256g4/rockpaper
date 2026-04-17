"""
Static instructions and rules screen.
"""
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.app import CasinoApp

class RulesFrame(tk.Frame):
    """Static rules screen displaying payout multipliers."""

    def __init__(self, master: "CasinoApp"):
        super().__init__(master, bg="#1a252f")
        self.master = master

        tk.Label(
            self,
            text="GAME RULES & PAYOUTS",
            font=("Helvetica", 20, "bold"),
            bg="#1a252f",
            fg="white",
        ).pack(pady=20)

        rules = (
            "Play 3 hands of RPS against an adaptive AI!\n"
            "The AI tracks your sequences and tries to predict your next moves.\n"
            "If your balance drops to 0, The AI WINS and it's GAME OVER.\n\n"
            "💰 PAYOUT & PENALTY MULTIPLIERS:\n"
            "(If the AI scores these, you LOSE the multiplied wager!)\n\n"
            "🔥 MEGA JACKPOT (3 Wins, Same Element): 10x\n"
            "🌈 RAINBOW JACKPOT (3 Wins, All Different Elements): 7x\n"
            "💎 JACKPOT (3 Wins): 5x\n"
            "⚡ DOUBLE STRIKE (2 Wins, Same Element): 2.5x\n"
            "👍 NICE PLAY (2 Wins): 2x\n"
            "🛡️ CLOSE CALL (1 Win, 2 Ties): 1.5x\n"
            "🤝 STANDOFF (3 Ties): 1.2x\n"
            "⚖️ DEAD HEAT (1 Win, 1 Loss, 1 Tie): 1x\n"
            "💀 BUST! (fallback): 0x\n"
        )

        tk.Label(
            self,
            text=rules,
            font=("Helvetica", 12),
            bg="#1a252f",
            fg="white",
            justify="center",
        ).pack(pady=10)

        tk.Button(
            self,
            text="Back to Match",
            font=("Helvetica", 14, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.go_back,
        ).pack(pady=20)

    def go_back(self) -> None:
        self.master.sound.play("ui")
        self.master.show_slot_machine()
