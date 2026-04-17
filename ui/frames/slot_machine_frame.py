"""
Main gameplay screen and core logic controller.
"""
import tkinter as tk
from tkinter import ttk
import random
from typing import TYPE_CHECKING, List, Callable

from constants import CHOICES, WIN_MAP, STARTING_BALANCE, AI_STARTING_BALANCE

if TYPE_CHECKING:
    from ui.app import CasinoApp

class SlotMachineFrame(tk.Frame):
    """Main gameplay screen containing slot animation and payout logic."""

    SLOT_COUNT = 3
    DEFAULT_WAGER = 10
    SHUFFLE_COUNT = 20
    SHUFFLE_DELAY_MS = 50
    REVEAL_DELAY_MS = 400

    BALANCE_ANIMATION_STEPS = 8
    BALANCE_ANIMATION_DELAY_MS = 35
    BALANCE_FLASH_DELAY_MS = 90

    PLAYER_BALANCE_COLOR = "#f1c40f"
    AI_BALANCE_COLOR = "#e74c3c"
    POSITIVE_FLASH_COLOR = "#2ecc71"
    NEGATIVE_FLASH_COLOR = "#ff5c5c"

    def __init__(self, master: "CasinoApp"):
        super().__init__(master, bg="#1a252f")
        self.master = master

        self.current_slot_idx = 0
        self.cbox_vars: List[tk.StringVar] = []
        self.slot_frames: List[tk.Frame] = []

        self.displayed_player_balance = self.master.player.balance
        self.displayed_ai_balance = self.master.ai.balance

        self.player_balance_job_ids: List[str] = []
        self.ai_balance_job_ids: List[str] = []

        self._build_ui()
        self._initialize_screen_state()

    def _build_ui(self) -> None:
        self._build_header()
        self._build_selection_grid()
        self._build_result_area()
        self._build_wager_controls()
        self._build_action_buttons()
        self._build_music_button()

    def _initialize_screen_state(self) -> None:
        self.update_slot_highlight()
        self.bind_keys()

        # Make sure hotkeys work as soon as this frame opens.
        self.focus_set()
        self.after(100, self.focus_force)

        if self.master.player.balance <= 0 or self.master.ai.balance <= 0:
            self.trigger_game_over()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg="#2c3e50", height=50)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🎰 AI MEGA SLOTS 🎰",
            font=("Helvetica", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack(side="left", padx=20, pady=10)

        self.lbl_ai_balance = tk.Label(
            header,
            text=f"AI Bank: {self.displayed_ai_balance}",
            font=("Helvetica", 12, "bold"),
            bg="#2c3e50",
            fg=self.AI_BALANCE_COLOR,
        )
        self.lbl_ai_balance.pack(side="right", padx=10, pady=10)

        self.lbl_balance = tk.Label(
            header,
            text=f"Balance: {self.displayed_player_balance}",
            font=("Helvetica", 12, "bold"),
            bg="#2c3e50",
            fg=self.PLAYER_BALANCE_COLOR,
        )
        self.lbl_balance.pack(side="right", padx=10, pady=10)

    def _build_selection_grid(self) -> None:
        grid_frame = tk.Frame(self, bg="#1a252f")
        grid_frame.pack(pady=20)

        for index in range(self.SLOT_COUNT):
            tk.Label(
                grid_frame,
                text=f"Slot {index + 1}",
                font=("Helvetica", 14),
                bg="#1a252f",
                fg="white",
            ).grid(row=0, column=index, padx=20, pady=5)

        for index in range(self.SLOT_COUNT):
            slot_frame = tk.Frame(grid_frame, bg="#1a252f", padx=5, pady=5)
            slot_frame.grid(row=1, column=index, padx=15)

            value = tk.StringVar(value="rock")
            combo = ttk.Combobox(
                slot_frame,
                textvariable=value,
                values=CHOICES,
                state="readonly",
                font=("Helvetica", 12),
                width=10,
            )
            combo.pack()

            self.cbox_vars.append(value)
            self.slot_frames.append(slot_frame)

        self.res_frame = tk.Frame(grid_frame, bg="#34495e", pady=10, relief=tk.SUNKEN, bd=2)
        self.res_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky="ew")

    def _build_result_area(self) -> None:
        self.lbl_user_res = tk.Label(
            self.res_frame,
            text="User: ? | ? | ?",
            font=("Helvetica", 12),
            bg="#34495e",
            fg="white",
        )
        self.lbl_user_res.pack(pady=2)

        self.lbl_comp_res = tk.Label(
            self.res_frame,
            text="Comp: ? | ? | ?",
            font=("Helvetica", 12),
            bg="#34495e",
            fg="#e74c3c",
        )
        self.lbl_comp_res.pack(pady=2)

        self.lbl_outcome = tk.Label(
            self.res_frame,
            text="RES:  ? | ? | ?",
            font=("Helvetica", 12, "bold"),
            bg="#34495e",
            fg="#2ecc71",
        )
        self.lbl_outcome.pack(pady=2)

        self.lbl_message = tk.Label(
            self.res_frame,
            text="Place your wager and Spin!",
            font=("Helvetica", 12, "bold"),
            bg="#34495e",
            fg="#f1c40f",
        )
        self.lbl_message.pack(pady=5)

        self.lbl_calc = tk.Label(
            self.res_frame,
            text="",
            font=("Courier", 10),
            bg="#34495e",
            fg="#bdc3c7",
            justify="center",
        )
        self.lbl_calc.pack(pady=2)

    def _build_wager_controls(self) -> None:
        wager_frame = tk.Frame(self, bg="#1a252f")
        wager_frame.pack()

        tk.Label(
            wager_frame,
            text="Wager:",
            font=("Helvetica", 14),
            bg="#1a252f",
            fg="white",
        ).pack(side="left")

        self.ent_wager = tk.Entry(
            wager_frame,
            font=("Helvetica", 14),
            width=8,
            justify="center",
        )
        self.ent_wager.insert(0, str(self.DEFAULT_WAGER))
        self.ent_wager.pack(side="left", padx=10)

        presets_frame = tk.Frame(self, bg="#1a252f")
        presets_frame.pack(pady=5)

        for value in [10, 50, 100, 500]:
            tk.Button(
                presets_frame,
                text=f"Bet {value}",
                font=("Helvetica", 9),
                bg="#34495e",
                fg="white",
                command=lambda preset=value: self.set_wager(preset),
            ).pack(side="left", padx=5)

    def _build_action_buttons(self) -> None:
        self.controls = tk.Frame(self, bg="#1a252f")
        self.controls.pack(pady=15)

        self.btn_rules = tk.Button(
            self.controls,
            text="View Rules",
            font=("Helvetica", 12),
            width=12,
            bg="#3498db",
            fg="white",
            command=self.master.show_rules_screen,
        )
        self.btn_rules.pack(side="left", padx=10)

        self.btn_logout = tk.Button(
            self.controls,
            text="Logout",
            font=("Helvetica", 12),
            width=12,
            bg="#95a5a6",
            command=self.do_logout,
        )
        self.btn_logout.pack(side="left", padx=10)

        self.btn_spin = tk.Button(
            self.controls,
            text="🎰 SPIN! 🎰",
            font=("Helvetica", 14, "bold"),
            width=15,
            bg="#e67e22",
            fg="white",
            command=self.play_round,
        )
        self.btn_spin.pack(side="left", padx=10)

    def _build_music_button(self) -> None:
        self.btn_mute = tk.Button(
            self,
            text="Music: OFF",
            font=("Helvetica", 8),
            bg="#34495e",
            fg="white",
            command=self.toggle_music,
        )
        self.btn_mute.place(x=10, y=560)
        self.update_mute_btn()

    def bind_keys(self) -> None:
        self.master.bind("<Key>", self.handle_keypress)
        self.master.bind("<Return>", lambda event: self.play_round())

    def cleanup(self) -> None:
        self.master.unbind("<Key>")
        self.master.unbind("<Return>")
        self._cancel_balance_jobs()

    def handle_keypress(self, event) -> None:
        key = event.char.lower()

        if key == "r":
            self.fast_fill("rock")
        elif key == "p":
            self.fast_fill("paper")
        elif key == "s":
            self.fast_fill("scissors")

    def fast_fill(self, choice: str) -> None:
        self.master.sound.play("click")
        self.cbox_vars[self.current_slot_idx].set(choice)
        self.current_slot_idx = (self.current_slot_idx + 1) % self.SLOT_COUNT
        self.update_slot_highlight()

    def update_slot_highlight(self) -> None:
        for index, frame in enumerate(self.slot_frames):
            frame.config(bg="#f1c40f" if index == self.current_slot_idx else "#1a252f")

    def _cancel_balance_jobs(self) -> None:
        for job_id in self.player_balance_job_ids + self.ai_balance_job_ids:
            try:
                self.after_cancel(job_id)
            except Exception:
                pass

        self.player_balance_job_ids.clear()
        self.ai_balance_job_ids.clear()

    def _update_balance_labels(self) -> None:
        self.lbl_balance.config(text=f"Balance: {self.displayed_player_balance}")
        self.lbl_ai_balance.config(text=f"AI Bank: {self.displayed_ai_balance}")

    def _flash_label(self, label: tk.Label, flash_color: str, normal_color: str) -> None:
        """Pulse the balance color to mimic damage or healing."""
        sequence = [flash_color, normal_color, flash_color, normal_color]

        def apply(index: int) -> None:
            if index >= len(sequence):
                label.config(fg=normal_color)
                return

            label.config(fg=sequence[index])
            job_id = self.after(
                self.BALANCE_FLASH_DELAY_MS,
                lambda: apply(index + 1),
            )

            if label == self.lbl_balance:
                self.player_balance_job_ids.append(job_id)
            else:
                self.ai_balance_job_ids.append(job_id)

        apply(0)

    def _animate_balance_value(
        self,
        start_value: int,
        end_value: int,
        setter: Callable[[int], None],
        label: tk.Label,
        normal_color: str,
        flash_color: str,
    ) -> None:
        """Animate the number instead of snapping instantly."""
        delta = end_value - start_value

        if delta == 0:
            setter(end_value)
            self._update_balance_labels()
            label.config(fg=normal_color)
            return

        step_count = self.BALANCE_ANIMATION_STEPS

        def run(step: int) -> None:
            if step >= step_count:
                setter(end_value)
                self._update_balance_labels()
                self._flash_label(label, flash_color, normal_color)
                return

            progress = (step + 1) / step_count
            current_value = round(start_value + delta * progress)
            setter(current_value)
            self._update_balance_labels()

            job_id = self.after(
                self.BALANCE_ANIMATION_DELAY_MS,
                lambda: run(step + 1),
            )

            if label == self.lbl_balance:
                self.player_balance_job_ids.append(job_id)
            else:
                self.ai_balance_job_ids.append(job_id)

        run(0)

    def animate_balances(
        self,
        player_target: int,
        ai_target: int,
        player_delta: int,
        ai_delta: int,
    ) -> None:
        """Animate player and AI balances together."""
        self._cancel_balance_jobs()

        player_flash = self.POSITIVE_FLASH_COLOR if player_delta >= 0 else self.NEGATIVE_FLASH_COLOR
        ai_flash = self.POSITIVE_FLASH_COLOR if ai_delta >= 0 else self.NEGATIVE_FLASH_COLOR

        self._animate_balance_value(
            start_value=self.displayed_player_balance,
            end_value=player_target,
            setter=self._set_displayed_player_balance,
            label=self.lbl_balance,
            normal_color=self.PLAYER_BALANCE_COLOR,
            flash_color=player_flash,
        )

        self._animate_balance_value(
            start_value=self.displayed_ai_balance,
            end_value=ai_target,
            setter=self._set_displayed_ai_balance,
            label=self.lbl_ai_balance,
            normal_color=self.AI_BALANCE_COLOR,
            flash_color=ai_flash,
        )

    def _set_displayed_player_balance(self, value: int) -> None:
        self.displayed_player_balance = value

    def _set_displayed_ai_balance(self, value: int) -> None:
        self.displayed_ai_balance = value

    def update_mute_btn(self) -> None:
        if self.master.music_on:
            self.btn_mute.config(text="Music: ON", bg="#27ae60")
        else:
            self.btn_mute.config(text="Music: OFF", bg="#34495e")

    def toggle_music(self) -> None:
        self.master.sound.play("ui")
        self.master.music_on = not self.master.music_on

        if self.master.music_on:
            self.master.sound.start_music()
        else:
            self.master.sound.stop_music()

        self.update_mute_btn()

    def do_logout(self) -> None:
        self.master.sound.play("ui")
        self.master.sound.stop_music()
        self.master.music_on = False
        self.master.show_login_screen()

    def set_wager(self, value: int) -> None:
        self.master.sound.play("bet")
        self.ent_wager.delete(0, tk.END)
        self.ent_wager.insert(0, str(value))

    def trigger_game_over(self) -> None:
        self.master.sound.play("loss")

        if self.master.player.balance <= 0:
            text = "💀 GAME OVER! AI WINS! 💀\nYou went bankrupt!"
            color = "#e74c3c"
        else:
            text = "🎉 VICTORY! HOUSE IS BROKE! 🎉\nYou won the Casino!"
            color = "#2ecc71"

        self.lbl_message.config(text=text, fg=color)
        self.btn_spin.config(state="disabled", bg="#7f8c8d")

        if hasattr(self, "btn_restart") and self.btn_restart.winfo_exists():
            return

        self.btn_restart = tk.Button(
            self.controls,
            text="New Game",
            font=("Helvetica", 14, "bold"),
            width=15,
            bg="#27ae60",
            fg="white",
            command=self.restart_game,
        )
        self.btn_restart.pack(side="left", padx=10)

    def restart_game(self) -> None:
        self.master.sound.play("coins")

        self.master.player.balance = STARTING_BALANCE
        self.master.ai.balance = AI_STARTING_BALANCE
        self.master.player.total_games = 0

        self.animate_balances(
            player_target=self.master.player.balance,
            ai_target=self.master.ai.balance,
            player_delta=self.master.player.balance - self.displayed_player_balance,
            ai_delta=self.master.ai.balance - self.displayed_ai_balance,
        )

        if hasattr(self, "btn_restart") and self.btn_restart.winfo_exists():
            self.btn_restart.destroy()

        self.btn_spin.config(state="normal", bg="#e67e22")
        self.lbl_message.config(text="Balance reset! Place your wager.", fg="#2ecc71")
        self.lbl_calc.config(text="")
        self.master.save_game()

    def evaluate_slot(self, user_move: str, comp_move: str) -> str:
        if user_move == comp_move:
            return "TIE"
        if WIN_MAP[user_move] == comp_move:
            return "WIN"
        return "LOSS"

    def collect_wager(self, wager: int) -> bool:
        """
        Move the wager immediately:
        - player pays the stake
        - AI bank receives the stake
        """
        if wager <= 0:
            return False

        if not self.master.player.bet(wager):
            return False

        self.master.ai.balance += wager

        self.animate_balances(
            player_target=self.master.player.balance,
            ai_target=self.master.ai.balance,
            player_delta=-wager,
            ai_delta=+wager,
        )
        return True

    def play_round(self) -> None:
        try:
            wager = int(self.ent_wager.get())
        except ValueError:
            self.master.sound.play("error")
            self.lbl_message.config(text="Error! Wager must be a number.", fg="#e74c3c")
            return

        if not self.collect_wager(wager):
            self.master.sound.play("error")
            self.lbl_message.config(text="Error! Invalid wager or no tokens.", fg="#e74c3c")
            return

        self.btn_spin.config(state="disabled")
        self.lbl_message.config(
            text=f"Wager accepted: {wager} tokens.\nAI collects the stake. Spinning...",
            fg="#f1c40f",
        )
        self.lbl_calc.config(text=f"Stake moved -> Player -{wager} | AI +{wager}")

        user_moves = [value.get() for value in self.cbox_vars]
        comp_moves = self.master.ai.get_moves()
        outcomes = [self.evaluate_slot(user, comp) for user, comp in zip(user_moves, comp_moves)]

        self.shuffle_frames(self.SHUFFLE_COUNT, user_moves, comp_moves, outcomes, wager)

    def shuffle_frames(
        self,
        remaining_steps: int,
        user_moves: List[str],
        comp_moves: List[str],
        outcomes: List[str],
        wager: int,
    ) -> None:
        if remaining_steps > 0:
            temporary_comp_moves = [random.choice(CHOICES) for _ in range(self.SLOT_COUNT)]
            self.lbl_comp_res.config(
                text="Comp: " + " | ".join(move.upper() for move in temporary_comp_moves)
            )
            self.master.sound.play("click")

            self.after(
                self.SHUFFLE_DELAY_MS,
                lambda: self.shuffle_frames(
                    remaining_steps - 1,
                    user_moves,
                    comp_moves,
                    outcomes,
                    wager,
                ),
            )
            return

        self.reveal_slot(0, user_moves, comp_moves, outcomes, wager)

    def reveal_slot(
        self,
        slot_index: int,
        user_moves: List[str],
        comp_moves: List[str],
        outcomes: List[str],
        wager: int,
    ) -> None:
        if slot_index < self.SLOT_COUNT:
            revealed_comp = comp_moves[: slot_index + 1] + ["?"] * (self.SLOT_COUNT - slot_index - 1)
            revealed_outcomes = outcomes[: slot_index + 1] + ["?"] * (self.SLOT_COUNT - slot_index - 1)

            self.lbl_user_res.config(text="User: " + " | ".join(move.upper() for move in user_moves))
            self.lbl_comp_res.config(text="Comp: " + " | ".join(move.upper() for move in revealed_comp))
            self.lbl_outcome.config(text="RES:  " + " | ".join(revealed_outcomes))

            self.master.sound.play("click")

            self.after(
                self.REVEAL_DELAY_MS,
                lambda: self.reveal_slot(
                    slot_index + 1,
                    user_moves,
                    comp_moves,
                    outcomes,
                    wager,
                ),
            )
            return

        self.finalize_round(user_moves, comp_moves, outcomes, wager)

    def finalize_round(
        self,
        user_moves: List[str],
        comp_moves: List[str],
        outcomes: List[str],
        wager: int,
    ) -> None:
        wins = outcomes.count("WIN")
        ties = outcomes.count("TIE")
        losses = outcomes.count("LOSS")
        unique_user_moves = len(set(user_moves))
        unique_comp_moves = len(set(comp_moves))

        multiplier = 0
        message = ""
        player_settlement = 0

        # player_settlement is applied after the stake has already been collected
        # positive: AI pays player
        # negative: player pays extra penalty to AI
        if wins == 3:
            multiplier = 10 if unique_user_moves == 1 else 7 if unique_user_moves == 3 else 5
            message = (
                "🔥 MEGA JACKPOT! 🔥"
                if multiplier == 10
                else "🌈 RAINBOW JACKPOT! 🌈"
                if multiplier == 7
                else "💰 JACKPOT! 💰"
            )
            player_settlement = wager * multiplier

        elif wins == 2:
            multiplier = 2.5 if unique_user_moves == 1 else 2
            message = "⚡ DOUBLE STRIKE! ⚡" if multiplier == 2.5 else "👍 NICE PLAY! 👍"
            player_settlement = int(wager * multiplier)

        elif losses == 3:
            multiplier = 10 if unique_comp_moves == 1 else 7 if unique_comp_moves == 3 else 5
            message = (
                "💀 AI MEGA JACKPOT! 💀"
                if multiplier == 10
                else "🤖 AI RAINBOW! 🤖"
                if multiplier == 7
                else "💸 AI JACKPOT! 💸"
            )
            player_settlement = -(int(wager * multiplier) - wager)

        elif losses == 2:
            multiplier = 2.5 if unique_comp_moves == 1 else 2
            message = "🌩️ AI DOUBLE STRIKE! 🌩️" if multiplier == 2.5 else "📉 AI NICE PLAY! 📉"
            player_settlement = -(int(wager * multiplier) - wager)

        elif wins == 1 and ties == 2:
            multiplier = 1.5
            message = "🛡️ CLOSE CALL 🛡️"
            player_settlement = int(wager * 1.5)

        elif losses == 1 and ties == 2:
            multiplier = 1.5
            message = "😬 AI CLOSE CALL 😬"
            player_settlement = -(int(wager * 1.5) - wager)

        elif ties == 3:
            multiplier = 1.2
            message = "🤝 STANDOFF! 🤝"
            player_settlement = int(wager * 1.2)

        elif wins == 1 and losses == 1 and ties == 1:
            multiplier = 1.0
            message = "⚖️ DEAD HEAT ⚖️"
            player_settlement = wager

        else:
            multiplier = 0
            message = "❌ YOU LOSE! ❌"
            player_settlement = 0

        self.master.player.win(player_settlement)
        self.master.ai.balance -= player_settlement
        self.master.player.total_games += 1

        self.master.ai.update_history(user_moves)
        self.master.save_game()

        self.animate_balances(
            player_target=self.master.player.balance,
            ai_target=self.master.ai.balance,
            player_delta=player_settlement,
            ai_delta=-player_settlement,
        )

        self.btn_spin.config(state="normal")

        if player_settlement > 0:
            self.master.sound.play("jackpot" if multiplier >= 5 else "win")
            self.lbl_message.config(
                text=f"{message}\nYou received {player_settlement} tokens from the AI bank.",
                fg="#2ecc71",
            )
            self.lbl_calc.config(
                text=(
                    f"Stake: Player -{wager} | AI +{wager}\n"
                    f"Settlement: AI -> Player {player_settlement}\n"
                    f"Net result: Player +{player_settlement - wager} | AI {wager - player_settlement}"
                )
            )

        elif player_settlement == 0:
            self.master.sound.play("loss")
            self.lbl_message.config(
                text=f"{message}\nThe AI keeps your {wager} token wager.",
                fg="#e74c3c",
            )
            self.lbl_calc.config(
                text=(
                    f"Stake: Player -{wager} | AI +{wager}\n"
                    f"Settlement: none\n"
                    f"Net result: Player -{wager} | AI +{wager}"
                )
            )

        else:
            self.master.sound.play("loss")
            extra_penalty = abs(player_settlement)
            total_loss = wager + extra_penalty
            self.lbl_message.config(
                text=f"{message}\nYou lost {total_loss} tokens in total.",
                fg="#e74c3c",
            )
            self.lbl_calc.config(
                text=(
                    f"Stake: Player -{wager} | AI +{wager}\n"
                    f"Settlement: Player -> AI {extra_penalty}\n"
                    f"Net result: Player -{total_loss} | AI +{total_loss}"
                )
            )

        if self.master.player.balance <= 0 or self.master.ai.balance <= 0:
            self.trigger_game_over()
