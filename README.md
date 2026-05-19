# AI Multi-Slot Rock Paper Scissors Casino

Welcome to the **AI Multi-Slot RPS Casino**, a high-stakes, predictive AI-driven Rock Paper Scissors game developed for the COMP9001 Python Project Challenge. This application combines traditional gameplay with casino-style jackpot mechanics and a machine-learning opponent.

## 🚀 Features

- **Predictive AI Strategy**: The AI doesn't pick randomly. It uses Bigram frequency analysis to learn your move patterns and counter them in real-time.
- **Save Slot Management**: Manage up to 4 unique player profiles with persistent balances and statistics saved to disk.
- **Symmetrical Betting Mechanics**: Win big with 10x Jackpots—but be careful! The AI can hit those same jackpots, forcing you to pay out from your own balance.
- **Cross-Platform Audio**: MP3 sound effects (Boolean SFX Pack) plus a synthesized chiptune music loop, powered by `pygame.mixer`. Works on Windows, macOS and Linux.
- **Speed-Input GUI**: Play the entire game using only your keyboard via hotkeys (`R`, `P`, `S`, `Enter`).
- **Minimal Dependencies**: Standard library + `pygame` only (see `requirements.txt`).

---

## 🛠️ Advanced Programming Concepts

### 1. Object-Oriented Programming (OOP)
The application is built using a decoupled, modular class-based architecture:
- `CasinoApp(tk.Tk)`: The core event-driven engine and window manager.
- `Player`: Encapsulates user state, including balance tracking and data serialization.
- `AIPlayer`: The "Brain" of the game. It manages the Markov-like history state and prediction logic.
- `SoundManager`: Loads MP3 SFX via `pygame.mixer` and runs a synthesized chiptune music loop on a background thread.
- `FileManager`: High-level static interface for robust JSON data persistence.

### 2. Predictive AI (Blended Trigram + Decay)
The AI opponent implements a learning algorithm that tracks your move transitions independently for each of the 3 slots using both **Trigram** (2 layers deep) and **Bigram** (1 layer deep) models.
- **Blended Score**: Predictions weigh Trigrams at 2.0x and Bigrams at 1.0x to gracefully fall back on broader patterns when precise historical sequences are sparse.
- **Memory Decay**: A `DECAY_FACTOR` of `0.95` is applied to historical probabilities every turn, ensuring older strategies fade so the AI dynamically reacts if you change your patterns!

### 3. Asynchronous Threading
SFX playback is non-blocking via `pygame.mixer` channels. The chiptune music loop runs in a daemon thread that synthesizes sine-wave tones into raw PCM buffers, keeping the GUI 100% responsive on every platform.

### 4. Robust File I/O & Exception Handling
Data is saved in a JSON format (`save_data.json`). The program includes multiple `try...except` blocks to handle:
- Corrupted or missing save files.
- Invalid wager inputs (non-numeric or negative).
- System-level speaker unavailability.
- Profile name validation.

---

## 🎮 How to Play

### Installation
Requires Python 3.x. Works on Windows, macOS and Linux.
```bash
cd rockpaper
pip install -r requirements.txt
python main.py
```

### Controls
1. **Startup**: Create a new profile or select an existing save slot.
2. **Betting**: Click a preset button (Bet 10, 50, etc.) or type manually.
3. **Choosing Moves**: Tap **`R`**, **`P`**, or **`S`** on your keyboard. A **Gold Border** will show you which slot you are filling.
4. **Spin**: Hit **`Enter`** to start the round.
5. **Jackpots**:
   - **MEGA JACKPOT**: 3 wins with the same element (e.g., 3 Rocks).
   - **RAINBOW JACKPOT**: 3 wins using one of each element.
   - **JACKPOT**: 3 simple wins.

---

## 🏗️ Project Structure

```text
├── constants.py       # Constants and configuration
├── main.py            # Entry point for the Application
├── requirements.txt   # External dependencies (pygame)
├── assets/sounds/     # MP3 SFX (Boolean SFX Pack)
├── models/            # Logical state representations
│   ├── player.py
│   └── ai_player.py
├── managers/          # Helper utilities
│   ├── file_manager.py
│   └── sound_manager.py
├── ui/                # UI presentation
│   ├── app.py
│   └── frames/
│       ├── login_frame.py
│       ├── rules_frame.py
│       └── slot_machine_frame.py
├── save_data.json     # Auto-generated save file
└── README.md          # This documentation
```

Created by **Antigravity** (AI Assistant) in collaboration with the **USER** for COMP9001.
