"""
Audio synthesis manager using the native Windows system speaker.
"""
import winsound
import threading
import time
from typing import List, Optional

class SoundManager:
    """Plays sound effects and a more musical retro background loop."""

    # Note frequency constants
    NOTE_F3 = 175
    NOTE_G3 = 196
    NOTE_A3 = 220
    NOTE_C4 = 262
    NOTE_D4 = 294
    NOTE_E4 = 330
    NOTE_F4 = 349
    NOTE_G4 = 392
    NOTE_A4 = 440
    NOTE_B4 = 494
    NOTE_C5 = 523
    NOTE_D5 = 587
    NOTE_E5 = 659
    NOTE_G5 = 784

    def __init__(self) -> None:
        self.music_running = False
        self.music_thread: Optional[threading.Thread] = None

    @staticmethod
    def _safe_beep(frequency: int, duration: int) -> None:
        """Play a note or a short rest."""
        try:
            if frequency <= 0:
                time.sleep(duration / 1000)
            else:
                winsound.Beep(frequency, duration)
        except Exception:
            # Fallback if winsound fails to ensure timing remains consistent
            time.sleep(duration / 1000)

    def _play(self, melody: List[tuple[int, int]]) -> None:
        """Play a one-shot sound effect sequentially over a thread."""
        try:
            for frequency, duration in melody:
                self._safe_beep(frequency, duration)
        except Exception:
            pass

    def play(self, sound_type: str) -> None:
        """Play one-shot UI and game sounds asynchronously."""
        sound_map = {
            "click": [(900, 35)],
            "ui": [(740, 50), (988, 60)],
            "bet": [(330, 50), (494, 55), (659, 60)],
            "spin": [(420, 35), (520, 35), (620, 35), (720, 35), (840, 50)],
            "win": [(523, 70), (659, 70), (784, 100), (1046, 140)],
            "loss": [(440, 100), (349, 100), (262, 180)],
            "jackpot": [
                (523, 70), (659, 70), (784, 70), (1046, 140),
                (784, 70), (1046, 70), (1318, 160),
            ],
            "error": [(220, 180)],
            "coins": [(1200, 40), (1500, 40), (1800, 50), (1500, 40)],
            "delete": [(300, 90), (220, 100), (180, 140)],
        }

        melody = sound_map.get(sound_type, [])
        if melody:
            threading.Thread(target=self._play, args=(melody,), daemon=True).start()

    def start_music(self) -> None:
        """Start background music once."""
        if self.music_running:
            return

        self.music_running = True
        self.music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self.music_thread.start()

    def stop_music(self) -> None:
        """Stop the music loop."""
        self.music_running = False

    def _play_channel(self, notes: List[tuple[int, int]]) -> None:
        """Play one music phrase."""
        for frequency, duration in notes:
            if not self.music_running:
                return
            self._safe_beep(frequency, duration)

    def _music_loop(self) -> None:
        """
        Retro casino-style loop.
        winsound is monophonic, so this simulates multiple layers
        by alternating bass and lead phrases quickly.
        """
        intro = [
            (self.NOTE_C4, 90), (0, 25), (self.NOTE_E4, 90), (0, 25),
            (self.NOTE_G4, 110), (0, 40), (self.NOTE_C5, 160), (0, 60),
        ]

        groove_a = [
            (self.NOTE_C4, 120), (0, 30), (self.NOTE_C4, 90), (0, 30),
            (self.NOTE_G3, 120), (0, 30), (self.NOTE_C4, 90), (0, 30),
            (self.NOTE_E4, 70), (self.NOTE_G4, 70), (self.NOTE_C5, 110), (0, 30),
            (self.NOTE_G4, 70), (self.NOTE_E4, 70), (self.NOTE_D4, 110), (0, 40),
        ]

        groove_b = [
            (self.NOTE_A3, 120), (0, 25), (self.NOTE_A3, 90), (0, 25),
            (self.NOTE_E4, 120), (0, 25), (self.NOTE_A3, 90), (0, 25),
            (self.NOTE_C5, 70), (self.NOTE_E5, 70), (self.NOTE_D5, 100), (0, 25),
            (self.NOTE_C5, 70), (self.NOTE_A4, 70), (self.NOTE_G4, 120), (0, 40),
        ]

        groove_c = [
            (self.NOTE_F3, 120), (0, 25), (self.NOTE_F3, 90), (0, 25),
            (self.NOTE_C4, 120), (0, 25), (self.NOTE_F3, 90), (0, 25),
            (self.NOTE_A4, 70), (self.NOTE_C5, 70), (self.NOTE_A4, 90), (0, 25),
            (self.NOTE_G4, 70), (self.NOTE_E4, 70), (self.NOTE_F4, 120), (0, 40),
        ]

        groove_d = [
            (self.NOTE_G3, 120), (0, 25), (self.NOTE_G3, 90), (0, 25),
            (self.NOTE_D4, 120), (0, 25), (self.NOTE_G3, 90), (0, 25),
            (self.NOTE_B4, 70), (self.NOTE_D5, 70), (self.NOTE_G5, 110), (0, 30),
            (self.NOTE_D5, 70), (self.NOTE_B4, 70), (self.NOTE_G4, 120), (0, 45),
        ]

        ending_fill = [
            (self.NOTE_E4, 60), (self.NOTE_G4, 60), (self.NOTE_A4, 60), (self.NOTE_C5, 90),
            (self.NOTE_G4, 60), (self.NOTE_E4, 60), (self.NOTE_C4, 120), (0, 60),
        ]

        while self.music_running:
            for section in (intro, groove_a, groove_b, groove_c, groove_d, ending_fill):
                if not self.music_running:
                    break
                self._play_channel(section)
