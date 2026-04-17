"""
Profile select and creation screen.
"""
import tkinter as tk
from typing import TYPE_CHECKING
from constants import STARTING_BALANCE
from models.player import Player

if TYPE_CHECKING:
    from ui.app import CasinoApp

class LoginFrame(tk.Frame):
    """Profile select / create screen."""

    MAX_PROFILES = 4

    def __init__(self, master: "CasinoApp"):
        super().__init__(master, bg="#2c3e50")
        self.master = master

        tk.Label(
            self,
            text="🎰 Multi-Slot RPS Casino 🎰",
            font=("Helvetica", 24, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack(pady=20)

        tk.Label(
            self,
            text="Select or Create a Save Slot (Max 4)",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="#bdc3c7",
        ).pack(pady=5)

        self.slots_container = tk.Frame(self, bg="#2c3e50")
        self.slots_container.pack(pady=10, padx=20, fill="both", expand=True)

        self.refresh_slots()

    def refresh_slots(self) -> None:
        """Clears and redraws the available profile slots."""
        for widget in self.slots_container.winfo_children():
            widget.destroy()

        profiles = self.master.get_profiles()

        for index in range(self.MAX_PROFILES):
            slot_frame = tk.Frame(
                self.slots_container,
                bg="#34495e",
                pady=10,
                padx=10,
                relief=tk.RAISED,
                bd=2,
            )
            slot_frame.grid(
                row=index // 2,
                column=index % 2,
                padx=10,
                pady=10,
                sticky="nsew",
            )
            self.slots_container.grid_columnconfigure(index % 2, weight=1)

            if index < len(profiles):
                self._build_existing_profile_slot(slot_frame, profiles[index])
            else:
                self._build_empty_slot(slot_frame)

    def _build_existing_profile_slot(self, parent: tk.Frame, name: str) -> None:
        """Build UI elements for a populated slot."""
        player_data = self.master.data_store.get(name, {})
        if not isinstance(player_data, dict):
            return

        tk.Label(
            parent,
            text=name.upper(),
            font=("Helvetica", 14, "bold"),
            bg="#34495e",
            fg="#f1c40f",
        ).pack()

        tk.Label(
            parent,
            text=f"Balance: {player_data.get('balance', STARTING_BALANCE)} | Games: {player_data.get('total_games', 0)}",
            font=("Helvetica", 10),
            bg="#34495e",
            fg="white",
        ).pack()

        button_row = tk.Frame(parent, bg="#34495e")
        button_row.pack(pady=5)

        tk.Button(
            button_row,
            text="PLAY",
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=8,
            command=lambda profile_name=name: self.load_profile(profile_name),
        ).pack(side="left", padx=5)

    def _build_empty_slot(self, parent: tk.Frame) -> None:
        """Build UI elements for an unpopulated slot."""
        tk.Label(
            parent,
            text="EMPTY SLOT",
            font=("Helvetica", 14),
            bg="#34495e",
            fg="#95a5a6",
        ).pack(pady=5)

        entry_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=entry_var, font=("Helvetica", 10), width=15)
        entry.pack(pady=2)

        tk.Button(
            parent,
            text="CREATE NEW",
            bg="#2980b9",
            fg="white",
            font=("Helvetica", 10, "bold"),
            command=lambda: self.create_profile(entry.get()),
        ).pack(pady=5)

    def create_profile(self, name: str) -> None:
        """Attempts to create a new profile through the main app."""
        created = self.master.create_profile(name)
        if created:
            self.refresh_slots()

    def load_profile(self, name: str) -> None:
        """Loads selected profile and navigates to the game screen."""
        self.master.sound.play("ui")
        self.master.player = Player(name, self.master.data_store)
        self.master.show_slot_machine()
