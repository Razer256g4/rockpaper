"""
Multi-Slot Rock Paper Scissors GUI - Casino Edition
---------------------------------------------------
A graphical representation of the predictive AI casino RPS game!
Created as a final project for COMP9001: The Python Project Challenge.

Features:
- GUI (Event-Driven Architecture): Built natively with Tkinter without popups.
- File I/O: Automatically saves and loads player state using JSON.
- AI Prediction: Tracks player input history to predict moves.
- Object-Oriented Programming: Clean encapsulation and scalable design.
"""

import tkinter as tk
from tkinter import ttk
import random
import json
import os
import winsound
import threading
from typing import List, Dict, Optional

# Global Constants
CHOICES = ['rock', 'paper', 'scissors']
WIN_MAP = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
SAVE_FILE = 'save_data.json'
STARTING_BALANCE = 1000
AI_STARTING_BALANCE = 5000 # The House always has more!

class FileManager:
    """Manages file I/O operations for saving and loading game states."""
    @staticmethod
    def load_data() -> Dict:
        if not os.path.exists(SAVE_FILE):
            return {}
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    return {}
                return data
        except Exception:
            return {}
            
    @staticmethod
    def save_data(data: Dict) -> None:
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

class Player:
    """Represents the human user in the game, managing balance and stats."""
    def __init__(self, name: str, data: Dict):
        self.name = name
        user_data = data.get(self.name, {})
        self.balance: int = user_data.get('balance', STARTING_BALANCE)
        self.total_games: int = user_data.get('total_games', 0)
        
    def to_dict(self) -> Dict:
        return {'balance': self.balance, 'total_games': self.total_games}
        
    def bet(self, amount: int) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True

    def win(self, amount: int) -> None:
        self.balance += amount
        if self.balance < 0:
            self.balance = 0

class AIPlayer:
    """A predictive AI that attempts to predict the player's next move."""
    def __init__(self, data: Dict):
        self.history: Dict[str, Dict[str, int]] = data.get('ai_history', {
            'rock': {'rock': 0, 'paper': 0, 'scissors': 0},
            'paper': {'rock': 0, 'paper': 0, 'scissors': 0},
            'scissors': {'rock': 0, 'paper': 0, 'scissors': 0}
        })
        self.balance: int = data.get('ai_balance', AI_STARTING_BALANCE)
        self.last_moves: List[str] = []

    def get_moves(self) -> List[str]:
        ai_choices = []
        if len(self.last_moves) != 3:
            return [random.choice(CHOICES) for _ in range(3)]
            
        for i in range(3):
            last_human_move = self.last_moves[i]
            predictions = self.history.get(last_human_move, {})
            
            most_likely = 'rock'
            highest_freq = -1
            for move, freq in predictions.items():
                if freq > highest_freq:
                    highest_freq = freq
                    most_likely = move
                    
            if highest_freq == 0:
                most_likely = random.choice(CHOICES)
                
            counter_move = 'paper'
            for my_move, targets in WIN_MAP.items():
                if targets == most_likely:
                    counter_move = my_move
                    break
            ai_choices.append(counter_move)
            
        return ai_choices

    def update_history(self, current_human_moves: List[str]) -> None:
        if len(self.last_moves) == 3:
            for i in range(3):
                prev = self.last_moves[i]
                curr = current_human_moves[i]
                self.history[prev][curr] += 1
        self.last_moves = current_human_moves

    def get_history_data(self) -> Dict:
        return self.history

class SoundManager:
    """Handles playing chiptune-style sounds using the system speaker."""
    @staticmethod
    def _play(melody):
        """Internal helper to play a series of (freq, duration) tuples."""
        try:
            for freq, dur in melody:
                winsound.Beep(freq, dur)
        except Exception:
            pass # Silent failure if speaker is unavailable

    def play(self, sound_type: str):
        """Plays a pre-defined jingle in a background thread."""
        melody = []
        if sound_type == "click":
            melody = [(800, 50)]
        elif sound_type == "spin":
            melody = [(400 + i*50, 40) for i in range(5)]
        elif sound_type == "win":
            melody = [(523, 100), (659, 100), (784, 100), (1046, 200)]
        elif sound_type == "loss":
            melody = [(440, 150), (349, 150), (261, 300)]
        elif sound_type == "jackpot":
            melody = [(1046, 100), (1318, 100), (1568, 100), (1046, 100)] * 2
        elif sound_type == "error":
            melody = [(200, 200)]
        elif sound_type == "coins":
            melody = [(1200, 50), (1500, 50)] * 3
        elif sound_type == "repair":
            melody = [(400, 100), (600, 100), (800, 100)]

        if melody:
            threading.Thread(target=self._play, args=(melody,), daemon=True).start()

class CasinoApp(tk.Tk):
    """The main Graphical User Interface controller."""
    def __init__(self):
        super().__init__()
        self.title("Multi-Slot RPS Casino")
        self.geometry("650x600")
        self.configure(bg="#2c3e50")
        self.resizable(False, False)
        
        # Initialize Backend
        self.data_store = FileManager.load_data()
        
        # Repair Fix: If AI balance was corrupted/negative by the 'void' bug, reset it.
        if self.data_store.get('ai_balance', 0) <= 0:
            self.data_store['ai_balance'] = AI_STARTING_BALANCE
            
        self.player: Optional[Player] = None
        self.ai = AIPlayer(self.data_store)
        self.sound = SoundManager()
        
        self.current_frame = None
        self.show_login_screen()
        
        # Handle Window Close event gracefully
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def save_game(self) -> None:
        if self.player:
            self.data_store[self.player.name] = self.player.to_dict()
            self.data_store['ai_history'] = self.ai.get_history_data()
            self.data_store['ai_balance'] = self.ai.balance
            FileManager.save_data(self.data_store)

    def on_close(self):
        """Saves game on exit."""
        self.save_game()
        self.destroy()

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        self.switch_frame(LoginFrame)
        
    def show_slot_machine(self):
        self.switch_frame(SlotMachineFrame)
        
    def show_rules_screen(self):
        self.switch_frame(RulesFrame)

    def get_profiles(self) -> List[str]:
        """Returns a list of profile names up to 4, excluding AI data keys."""
        to_exclude = ['ai_history', 'ai_balance']
        return [k for k in self.data_store.keys() if k not in to_exclude][:4]

    def create_profile(self, name: str):
        """Creates a new profile if space is available."""
        name = name.strip().lower()
        if not name:
            return
        if name == 'ai_history':
            return
        if len(self.get_profiles()) >= 4:
            return
        
        self.data_store[name] = {'balance': STARTING_BALANCE, 'total_games': 0}
        self.save_game()

    def delete_profile(self, name: str):
        """Deletes a profile from the data store."""
        if name in self.data_store:
            del self.data_store[name]
            self.save_game()
            self.show_login_screen() # Refresh screen

class LoginFrame(tk.Frame):
    def __init__(self, master: CasinoApp):
        super().__init__(master, bg="#2c3e50")
        self.master = master
        
        tk.Label(self, text="🎰 Multi-Slot RPS Casino 🎰", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        tk.Label(self, text="Select or Create a Save Slot (Max 4)", font=("Helvetica", 12), bg="#2c3e50", fg="#bdc3c7").pack(pady=5)
        
        self.slots_container = tk.Frame(self, bg="#2c3e50")
        self.slots_container.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.refresh_slots()

    def refresh_slots(self):
        for widget in self.slots_container.winfo_children():
            widget.destroy()
            
        profiles = self.master.get_profiles()
        
        for i in range(4):
            slot_frame = tk.Frame(self.slots_container, bg="#34495e", pady=10, padx=10, relief=tk.RAISED, bd=2)
            slot_frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            self.slots_container.grid_columnconfigure(i % 2, weight=1)
            
            if i < len(profiles):
                name = profiles[i]
                p_data = self.master.data_store[name]
                
                # Safety check: ensure p_data is a dictionary
                if not isinstance(p_data, dict):
                    continue
                
                tk.Label(slot_frame, text=name.upper(), font=("Helvetica", 14, "bold"), bg="#34495e", fg="#f1c40f").pack()
                tk.Label(slot_frame, text=f"Balance: {p_data['balance']} | Games: {p_data['total_games']}", font=("Helvetica", 10), bg="#34495e", fg="white").pack()
                
                btn_row = tk.Frame(slot_frame, bg="#34495e")
                btn_row.pack(pady=5)
                
                tk.Button(btn_row, text="PLAY", bg="#27ae60", fg="white", font=("Helvetica", 10, "bold"), width=8, command=lambda n=name: self.load_profile(n)).pack(side="left", padx=5)
                tk.Button(btn_row, text="DELETE", bg="#e74c3c", fg="white", font=("Helvetica", 10, "bold"), width=8, command=lambda n=name: self.delete_profile(n)).pack(side="left", padx=5)
            else:
                tk.Label(slot_frame, text="EMPTY SLOT", font=("Helvetica", 14), bg="#34495e", fg="#95a5a6").pack(pady=5)
                
                self.name_var = tk.StringVar()
                entry = tk.Entry(slot_frame, textvariable=self.name_var, font=("Helvetica", 10), width=15)
                entry.pack(pady=2)
                
                tk.Button(slot_frame, text="CREATE NEW", bg="#2980b9", fg="white", font=("Helvetica", 10, "bold"), command=lambda e=entry: self.create_profile(e.get())).pack(pady=5)

    def create_profile(self, name):
        name = name.strip().lower()
        if not name or name == 'ai_history':
            return
        if name in self.master.data_store:
            return
        self.master.create_profile(name)
        self.refresh_slots()

    def login(self):
        username = self.entry.get().strip().lower()
        if not username:
            self.lbl_error.config(text="Error: Username cannot be empty!")
            self.master.sound.play("error")
            return
            
        self.master.sound.play("win")
        self.master.player = Player(username, self.master.data_store)
        self.master.show_slot_machine()

    def load_profile(self, name):
        self.master.player = Player(name, self.master.data_store)
        self.master.show_slot_machine()

    def delete_profile(self, name):
        self.master.delete_profile(name)
        self.refresh_slots()

class RulesFrame(tk.Frame):
    def __init__(self, master: CasinoApp):
        super().__init__(master, bg="#1a252f")
        self.master = master
        
        title = tk.Label(self, text="GAME RULES & PAYOUTS", font=("Helvetica", 20, "bold"), bg="#1a252f", fg="white")
        title.pack(pady=20)
        
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
        
        lbl_rules = tk.Label(self, text=rules, font=("Helvetica", 12), bg="#1a252f", fg="white", justify="center")
        lbl_rules.pack(pady=10)
        
        btn_back = tk.Button(self, text="Back to Match", font=("Helvetica", 14, "bold"), bg="#27ae60", fg="white", command=master.show_slot_machine)
        btn_back.pack(pady=20)


class SlotMachineFrame(tk.Frame):
    def __init__(self, master: CasinoApp):
        super().__init__(master, bg="#1a252f")
        self.master = master
        
        # Top Header
        header = tk.Frame(self, bg="#2c3e50", height=50)
        header.pack(fill="x")
        
        tk.Label(header, text="🎰 AI MEGA SLOTS 🎰", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=10)
        self.lbl_ai_balance = tk.Label(header, text=f"AI Bank: {master.ai.balance}", font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="#e74c3c")
        self.lbl_ai_balance.pack(side="right", padx=10, pady=10)
        self.lbl_balance = tk.Label(header, text=f"Balance: {master.player.balance}", font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.lbl_balance.pack(side="right", padx=10, pady=10)
        
        # Selection Grid
        grid_frame = tk.Frame(self, bg="#1a252f")
        grid_frame.pack(pady=20)
        
        tk.Label(grid_frame, text="Slot 1", font=("Helvetica", 14), bg="#1a252f", fg="white").grid(row=0, column=0, padx=20, pady=5)
        tk.Label(grid_frame, text="Slot 2", font=("Helvetica", 14), bg="#1a252f", fg="white").grid(row=0, column=1, padx=20, pady=5)
        tk.Label(grid_frame, text="Slot 3", font=("Helvetica", 14), bg="#1a252f", fg="white").grid(row=0, column=2, padx=20, pady=5)
        
        self.cbox_vars = []
        self.slot_frames = []
        for i in range(3):
            # Frame to provide highlight border
            s_frame = tk.Frame(grid_frame, bg="#1a252f", padx=5, pady=5)
            s_frame.grid(row=1, column=i, padx=15)
            
            var = tk.StringVar(value="rock")
            cbox = ttk.Combobox(s_frame, textvariable=var, values=["rock", "paper", "scissors"], state="readonly", font=("Helvetica", 12), width=10)
            cbox.pack()
            
            self.cbox_vars.append(var)
            self.slot_frames.append(s_frame)
        
        self.current_slot_idx = 0
        self.update_slot_highlight()

        # Results area
        self.res_frame = tk.Frame(grid_frame, bg="#34495e", pady=10, relief=tk.SUNKEN, bd=2)
        self.res_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky="ew")
        
        self.lbl_user_res = tk.Label(self.res_frame, text="User: ? | ? | ?", font=("Helvetica", 12), bg="#34495e", fg="white")
        self.lbl_user_res.pack(pady=2)
        self.lbl_comp_res = tk.Label(self.res_frame, text="Comp: ? | ? | ?", font=("Helvetica", 12), bg="#34495e", fg="#e74c3c")
        self.lbl_comp_res.pack(pady=2)
        self.lbl_outcome = tk.Label(self.res_frame, text="RES:  ? | ? | ?", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#2ecc71")
        self.lbl_outcome.pack(pady=2)
        
        self.lbl_message = tk.Label(self.res_frame, text="Place your wager and Spin!", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#f1c40f")
        self.lbl_message.pack(pady=5)
        
        self.lbl_calc = tk.Label(self.res_frame, text="", font=("Courier", 10), bg="#34495e", fg="#bdc3c7")
        self.lbl_calc.pack(pady=2)
        
        # Wager Input
        wager_frame = tk.Frame(self, bg="#1a252f")
        wager_frame.pack()
        tk.Label(wager_frame, text="Wager:", font=("Helvetica", 14), bg="#1a252f", fg="white").pack(side="left")
        
        self.ent_wager = tk.Entry(wager_frame, font=("Helvetica", 14), width=8, justify="center")
        self.ent_wager.insert(0, "10")
        self.ent_wager.pack(side="left", padx=10)

        # Wager Presets
        presets_frame = tk.Frame(self, bg="#1a252f")
        presets_frame.pack(pady=5)
        for val in [10, 50, 100, 500]:
            btn = tk.Button(presets_frame, text=f"Bet {val}", font=("Helvetica", 9), bg="#34495e", fg="white", 
                            command=lambda v=val: self.set_wager(v))
            btn.pack(side="left", padx=5)
        
        # Action Buttons
        self.controls = tk.Frame(self, bg="#1a252f")
        self.controls.pack(pady=15)
        
        self.btn_rules = tk.Button(self.controls, text="View Rules", font=("Helvetica", 12), width=12, bg="#3498db", fg="white", command=master.show_rules_screen)
        self.btn_rules.pack(side="left", padx=10)
        
        self.btn_logout = tk.Button(self.controls, text="Logout", font=("Helvetica", 12), width=12, bg="#95a5a6", command=master.show_login_screen)
        self.btn_logout.pack(side="left", padx=10)
        
        self.btn_spin = tk.Button(self.controls, text="🎰 SPIN! 🎰", font=("Helvetica", 14, "bold"), width=15, bg="#e67e22", fg="white", command=self.play_round)
        self.btn_spin.pack(side="left", padx=10)
        
        # Check bankruptcy immediately on load
        if self.master.player.balance <= 0 or self.master.ai.balance <= 0:
            self.trigger_game_over()
        else:
            self.bind_keys()

    def bind_keys(self):
        self.master.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        key = event.char.lower()
        if key == 'r': self.fast_fill("rock")
        elif key == 'p': self.fast_fill("paper")
        elif key == 's': self.fast_fill("scissors")
        elif event.keysym == 'Return': self.play_round()

    def fast_fill(self, choice):
        self.master.sound.play("click")
        self.cbox_vars[self.current_slot_idx].set(choice)
        self.current_slot_idx = (self.current_slot_idx + 1) % 3
        self.update_slot_highlight()

    def update_slot_highlight(self):
        # Change the border color of the active slot container
        for i, frame in enumerate(self.slot_frames):
            if i == self.current_slot_idx:
                frame.config(bg="#f1c40f") # Gold Highlight
            else:
                frame.config(bg="#1a252f") # Default Background

    def set_wager(self, val):
        self.ent_wager.delete(0, tk.END)
        self.ent_wager.insert(0, str(val))

    def trigger_game_over(self):
        self.master.sound.play("loss")
        if self.master.player.balance <= 0:
            text = "💀 GAME OVER! AI WINS! 💀\nYou went bankrupt!"
        else:
            text = "🎉 VICTORY! HOUSE IS BROKE! 🎉\nYou won the Casino!"
            
        self.lbl_message.config(text=text, fg="#e74c3c" if self.master.player.balance <= 0 else "#2ecc71")
        self.btn_spin.config(state="disabled", bg="#7f8c8d")
        
        self.btn_restart = tk.Button(self.controls, text="New Game", font=("Helvetica", 14, "bold"), width=15, bg="#27ae60", fg="white", command=self.restart_game)
        self.btn_restart.pack(side="left", padx=10)

    def restart_game(self):
        self.master.sound.play("coins")
        self.master.player.balance = STARTING_BALANCE
        self.master.ai.balance = AI_STARTING_BALANCE
        self.master.player.total_games = 0
        self.btn_restart.destroy()
        self.btn_spin.config(state="normal", bg="#e67e22")
        self.lbl_balance.config(text=f"Balance: {self.master.player.balance}")
        self.lbl_ai_balance.config(text=f"AI Bank: {self.master.ai.balance}")
        self.lbl_message.config(text="Balance reset! Place your wager.", fg="#2ecc71")
        self.lbl_calc.config(text="")
        self.master.save_game()

    def evaluate_slot(self, user_move: str, comp_move: str) -> str:
        if user_move == comp_move: return 'TIE'
        elif WIN_MAP[user_move] == comp_move: return 'WIN'
        else: return 'LOSS'

    def play_round(self):
        try:
            wager = int(self.ent_wager.get())
        except ValueError:
            self.lbl_message.config(text="Error! Wager must be a number.", fg="#e74c3c")
            return
            
        if wager <= 0 or not self.master.player.bet(wager):
            self.lbl_message.config(text="Error! Invalid wager or no tokens.", fg="#e74c3c")
            return

        # ZERO-SUM FIX: The AI 'collects' the wager immediately at the start of the round
        self.master.ai.balance += wager
        self.lbl_ai_balance.config(text=f"AI Bank: {self.master.ai.balance}")

        self.btn_spin.config(state="disabled")
        self.lbl_message.config(text="🎰 SPINNING... 🎰", fg="#f1c40f")
        self.lbl_calc.config(text="")
        
        user_moves = [v.get() for v in self.cbox_vars]
        comp_moves = self.master.ai.get_moves()
        outcomes = [self.evaluate_slot(u, c) for u, c in zip(user_moves, comp_moves)]
        
        # Start Shuffle Animation
        self.shuffle_frames(20, user_moves, comp_moves, outcomes, wager)

    def shuffle_frames(self, count, user_moves, comp_moves, outcomes, wager):
        if count > 0:
            temp_comp = [random.choice(CHOICES) for _ in range(3)]
            self.lbl_comp_res.config(text="Comp: " + " | ".join(c.upper() for c in temp_comp))
            self.master.sound.play("click")
            self.master.after(50, lambda: self.shuffle_frames(count-1, user_moves, comp_moves, outcomes, wager))
        else:
            self.reveal_slot(0, user_moves, comp_moves, outcomes, wager)

    def reveal_slot(self, slot_idx, user_moves, comp_moves, outcomes, wager):
        if slot_idx < 3:
            current_revealed_comp = comp_moves[:slot_idx+1] + ["?"] * (2 - slot_idx)
            current_revealed_outcomes = outcomes[:slot_idx+1] + ["?"] * (2 - slot_idx)
            
            self.lbl_user_res.config(text="User: " + " | ".join(u.upper() for u in user_moves))
            self.lbl_comp_res.config(text="Comp: " + " | ".join(c.upper() for c in current_revealed_comp))
            self.lbl_outcome.config(text="RES:  " + " | ".join(current_revealed_outcomes))
            
            self.master.sound.play("click")
            self.master.after(400, lambda: self.reveal_slot(slot_idx+1, user_moves, comp_moves, outcomes, wager))
        else:
            self.finalize_round(user_moves, comp_moves, outcomes, wager)

    def finalize_round(self, user_moves, comp_moves, outcomes, wager):
        wins = outcomes.count('WIN')
        ties = outcomes.count('TIE')
        losses = outcomes.count('LOSS')
        unique_user = len(set(user_moves))
        unique_comp = len(set(comp_moves))
        
        payout = 0
        message = ""
        multiplier = 0
        
        if wins == 3:
            multiplier = 10 if unique_user == 1 else (7 if unique_user == 3 else 5)
            message = "🔥 MEGA JACKPOT! 🔥" if multiplier == 10 else ("🌈 RAINBOW JACKPOT! 🌈" if multiplier == 7 else "💰 JACKPOT! 💰")
            payout = wager * multiplier
        elif wins == 2:
            multiplier = 2.5 if unique_user == 1 else 2
            message = "⚡ DOUBLE STRIKE! ⚡" if multiplier == 2.5 else "👍 NICE PLAY! 👍"
            payout = int(wager * multiplier)
        elif losses == 3:
            multiplier = 10 if unique_comp == 1 else (7 if unique_comp == 3 else 5)
            message = "💀 AI MEGA JACKPOT! 💀" if multiplier == 10 else ("🤖 AI RAINBOW! 🤖" if multiplier == 7 else "💸 AI JACKPOT! 💸")
            payout = - (int(wager * multiplier) - wager)
        elif losses == 2:
            multiplier = 2.5 if unique_comp == 1 else 2
            message = "🌩️ AI DOUBLE STRIKE! 🌩️" if multiplier == 2.5 else "📉 AI NICE PLAY! 📉"
            payout = - (int(wager * multiplier) - wager)
        elif wins == 1 and ties == 2:
            multiplier = 1.5; message = "🛡️ CLOSE CALL 🛡️"; payout = int(wager * 1.5)
        elif losses == 1 and ties == 2:
            multiplier = 1.5; message = "😬 AI CLOSE CALL 😬"; payout = - (int(wager * 1.5) - wager)
        elif ties == 3:
            multiplier = 1.2; message = "🤝 STANDOFF! 🤝"; payout = int(wager * 1.2)
        elif wins == 1 and losses == 1 and ties == 1:
            multiplier = 1.0; message = "⚖️ DEAD HEAT ⚖️"; payout = wager
        else:
            multiplier = 0; message = "❌ YOU LOSE! ❌"; payout = 0
            
        # Payout Transfer
        self.master.player.win(payout)
        self.master.ai.balance -= payout
        self.master.player.total_games += 1
        
        # Audio / Visual Feedback
        self.master.ai.update_history(user_moves)
        self.master.save_game()
        
        self.lbl_balance.config(text=f"Balance: {self.master.player.balance}")
        self.lbl_ai_balance.config(text=f"AI Bank: {self.master.ai.balance}")
        self.btn_spin.config(state="normal")
        
        if payout > 0:
            self.master.sound.play("jackpot" if multiplier >= 5 else "win")
            self.lbl_message.config(text=f"{message}\nYou won {payout} Tokens!", fg="#2ecc71")
            calc_text = f"Calculation: {wager} (Bet) x {multiplier}x multiplier = {payout} gain"
        elif payout == 0:
            self.master.sound.play("loss")
            self.lbl_message.config(text=f"{message}\nYou lost your {wager} Token wager.", fg="#e74c3c")
            calc_text = f"Calculation: {wager} (Bet) x 0x multiplier = {wager} loss"
        else:
            self.master.sound.play("loss")
            total_lost = wager + abs(payout)
            self.lbl_message.config(text=f"{message}\nYou lost {total_lost} Tokens!", fg="#e74c3c")
            calc_text = f"Calculation: {wager} (Bet) + {abs(payout)} (AI Jackpot penalty) = {total_lost} total loss"
            
        self.lbl_calc.config(text=calc_text)
            
        if self.master.player.balance <= 0 or self.master.ai.balance <= 0:
            self.trigger_game_over()

if __name__ == "__main__":
    app = CasinoApp()
    app.mainloop()
