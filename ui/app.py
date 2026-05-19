"""
Main application window and frame coordinator.
"""
import tkinter as tk
from typing import Optional, List

from constants import AI_STARTING_BALANCE, STARTING_BALANCE
from managers.file_manager import FileManager
from managers.sound_manager import SoundManager
from models.player import Player
from models.ai_player import AIPlayer
from ui.frames.login_frame import LoginFrame
from ui.frames.rules_frame import RulesFrame
from ui.frames.slot_machine_frame import SlotMachineFrame

class CasinoApp(tk.Tk):
    """Main application window and state manager."""

    RESERVED_KEYS = {"ai_history", "ai_trigram", "ai_balance"}

    def __init__(self):
        super().__init__()

        self.title("Multi-Slot RPS Casino")
        self.geometry("650x600")
        self.configure(bg="#2c3e50")
        self.resizable(False, False)

        self.data_store = FileManager.load_data()

        # Repair corrupted or missing AI bank values.
        if self.data_store.get("ai_balance", 0) <= 0:
            self.data_store["ai_balance"] = AI_STARTING_BALANCE

        self.player: Optional[Player] = None
        self.ai = AIPlayer(self.data_store)
        self.sound = SoundManager()
        self.music_on = False
        self.current_frame = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login_screen()

    def save_game(self) -> None:
        """Persist current state of player and AI to disk."""
        if self.player:
            self.data_store[self.player.name] = self.player.to_dict()

        history_state = self.ai.get_history_data()
        self.data_store["ai_history"] = history_state["ai_history"]
        self.data_store["ai_trigram"] = history_state["ai_trigram"]
        self.data_store["ai_balance"] = self.ai.balance
        FileManager.save_data(self.data_store)

    def on_close(self) -> None:
        self.save_game()
        self.destroy()

    def switch_frame(self, frame_class) -> None:
        """Destroys current frame and replaces it with a new one."""
        if self.current_frame is not None:
            if hasattr(self.current_frame, "cleanup"):
                self.current_frame.cleanup()
            self.current_frame.destroy()

        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_screen(self) -> None:
        self.switch_frame(LoginFrame)

    def show_slot_machine(self) -> None:
        self.switch_frame(SlotMachineFrame)

    def show_rules_screen(self) -> None:
        self.sound.play("ui")
        self.switch_frame(RulesFrame)

    def get_profiles(self) -> List[str]:
        return [key for key in self.data_store.keys() if key not in self.RESERVED_KEYS][:4]

    def create_profile(self, name: str) -> bool:
        cleaned_name = name.strip().lower()

        if not cleaned_name:
            return False
        if cleaned_name in self.RESERVED_KEYS:
            return False
        if cleaned_name in self.data_store:
            return False
        if len(self.get_profiles()) >= 4:
            return False

        self.sound.play("win")
        self.data_store[cleaned_name] = {
            "balance": STARTING_BALANCE,
            "total_games": 0,
        }
        self.save_game()
        return True

    def delete_profile(self, name: str) -> None:
        if name in self.data_store:
            self.sound.play("delete")
            del self.data_store[name]
            self.save_game()
            self.show_login_screen()
