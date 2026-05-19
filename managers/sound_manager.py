"""
Cross-platform audio manager using pygame.mixer.

SFX are loaded from the MP3 files under assets/sounds/ (Boolean SFX Pack).
Background music is a synthesized chiptune loop generated as raw PCM
buffers so it works the same on Windows, macOS and Linux without any
extra audio assets.

If pygame is not installed (or the mixer fails to open an audio device),
every method silently no-ops so the game still runs.
"""
import math
import os
import threading
import time
from array import array
from typing import Dict, List, Optional, Tuple

# Audio is best-effort: missing pygame or no output device must not crash the game.
try:
    import pygame
    # pre_init must run before init(); small buffer keeps SFX latency low.
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
    pygame.mixer.init()
    _MIXER_OK = pygame.mixer.get_init() is not None
except Exception:
    pygame = None  # type: ignore[assignment]
    _MIXER_OK = False


_SOUND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "sounds",
)
_SAMPLE_RATE = 22050


class SoundManager:
    """Plays MP3 SFX and a synthesized chiptune background loop."""

    SFX_FILES = {
        "click":   "UI_Menu_Click_001.mp3",
        "ui":      "UI_Menu_Confirm_001.mp3",
        "bet":     "UI_Menu_Hover_001.mp3",
        "spin":    "Transitions_WhooshIn_001.mp3",
        "win":     "Feedback_LevelUp_001.mp3",
        "loss":    "UI_Menu_Error_001.mp3",
        "jackpot": "Feedback_Victory_001.mp3",
        "error":   "UI_Menu_Error_001.mp3",
        "coins":   "Pickups_Items_Coin_001.mp3",
        "delete":  "Transitions_WhooshOut_001.mp3",
    }

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
        self._sounds: Dict[str, "pygame.mixer.Sound"] = {}
        self._tone_cache: Dict[Tuple[int, int], "pygame.mixer.Sound"] = {}
        self._music_channel: Optional["pygame.mixer.Channel"] = None

        if _MIXER_OK:
            self._load_sfx()
            try:
                # Dedicated channel for music so SFX never preempt the melody.
                self._music_channel = pygame.mixer.Channel(0)
                self._music_channel.set_volume(0.35)  # sit under SFX
            except Exception:
                self._music_channel = None

    def _load_sfx(self) -> None:
        # Preload once at startup so .play() never blocks on disk I/O.
        for key, filename in self.SFX_FILES.items():
            path = os.path.join(_SOUND_DIR, filename)
            try:
                self._sounds[key] = pygame.mixer.Sound(path)
            except Exception:
                pass  # missing file is non-fatal; that SFX just goes silent

    def play(self, sound_type: str) -> None:
        """Play a one-shot SFX. Safe to call when audio is unavailable."""
        sound = self._sounds.get(sound_type)
        if sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass

    def start_music(self) -> None:
        if self.music_running or not _MIXER_OK or self._music_channel is None:
            return
        self.music_running = True
        self.music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self.music_thread.start()

    def stop_music(self) -> None:
        self.music_running = False
        if self._music_channel is not None:
            try:
                self._music_channel.stop()
            except Exception:
                pass

    def _tone(self, frequency: int, duration_ms: int) -> "pygame.mixer.Sound":
        """Synthesize (and cache) a short sine-wave tone."""
        # Cache by (freq, duration): the loop reuses the same notes every cycle,
        # so we pay the synthesis cost once per unique tone.
        key = (frequency, duration_ms)
        cached = self._tone_cache.get(key)
        if cached is not None:
            return cached

        n_samples = max(1, int(_SAMPLE_RATE * duration_ms / 1000))
        amplitude = 12000  # ~37% of int16 range — leaves headroom for SFX mix
        fade = max(1, int(_SAMPLE_RATE * 0.005))  # 5ms ramp kills boundary clicks
        samples = array("h", [0] * n_samples)
        two_pi_f = 2 * math.pi * frequency / _SAMPLE_RATE

        for i in range(n_samples):
            value = amplitude * math.sin(two_pi_f * i)
            if i < fade:
                value *= i / fade
            elif i > n_samples - fade:
                value *= (n_samples - i) / fade
            samples[i] = int(value)

        sound = pygame.mixer.Sound(buffer=samples.tobytes())
        self._tone_cache[key] = sound
        return sound

    def _play_note(self, frequency: int, duration_ms: int) -> None:
        # freq <= 0 is the rest convention used by the score below.
        if frequency <= 0 or self._music_channel is None:
            time.sleep(duration_ms / 1000)
            return
        try:
            self._music_channel.play(self._tone(frequency, duration_ms))
        except Exception:
            pass
        # Sleep paces the score; channel.play() is non-blocking.
        time.sleep(duration_ms / 1000)

    def _play_channel(self, notes: List[Tuple[int, int]]) -> None:
        for frequency, duration in notes:
            if not self.music_running:
                return
            self._play_note(frequency, duration)

    def _music_loop(self) -> None:
        """Retro casino-style loop: a single monophonic line cycling sections."""
        # Sections are reused across iterations so the tone cache stays hot.
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
