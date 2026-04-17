# AI Multi-Slot Rock Paper Scissors Casino

Welcome to the **AI Multi-Slot RPS Casino**, a high-stakes, predictive AI-driven Rock Paper Scissors game developed for the COMP9001 Python Project Challenge. This application combines traditional gameplay with casino-style jackpot mechanics and a machine-learning opponent.

## 🚀 Features

- **Predictive AI Strategy**: The AI doesn't pick randomly. It uses Bigram frequency analysis to learn your move patterns and counter them in real-time.
- **Save Slot Management**: Manage up to 4 unique player profiles with persistent balances and statistics saved to disk.
- **Symmetrical Betting Mechanics**: Win big with 10x Jackpots—but be careful! The AI can hit those same jackpots, forcing you to pay out from your own balance.
- **Chiptune Audio System**: Built-in background audio jingles using the Windows system speaker for immersive feedback.
- **Speed-Input GUI**: Play the entire game using only your keyboard via hotkeys (`R`, `P`, `S`, `Enter`).
- **Zero Dependencies**: Native Python implementation using `tkinter` and `winsound`—no external libraries to install.

---

## 🛠️ Advanced Programming Concepts

### 1. Object-Oriented Programming (OOP)
The application is built using a decoupled, modular class-based architecture:
- `CasinoApp(tk.Tk)`: The core event-driven engine and window manager.
- `Player`: Encapsulates user state, including balance tracking and data serialization.
- `AIPlayer`: The "Brain" of the game. It manages the Markov-like history state and prediction logic.
- `SoundManager`: Handles asynchronous chiptune generation using system threading.
- `FileManager`: High-level static interface for robust JSON data persistence.

### 2. Predictive AI (Bigram Analysis)
The AI opponent implements a learning algorithm that tracks your transitions. It stores data in a nested dictionary:
`{ 'rock': {'rock': 5, 'paper': 2, 'scissors': 0} }`
When you play a 'Rock', the AI looks at what you historically play *next*. If it predicts you will play 'Rock' again (based on its frequency counter), it will play 'Paper' to counter you.

### 3. Asynchronous Threading
To prevent the GUI from freezing while playing musical beeps, the `SoundManager` spawns a background `daemon` thread for every jingle. This ensures the animation and input remain 100% responsive.

### 4. Robust File I/O & Exception Handling
Data is saved in a JSON format (`save_data.json`). The program includes multiple `try...except` blocks to handle:
- Corrupted or missing save files.
- Invalid wager inputs (non-numeric or negative).
- System-level speaker unavailability.
- Profile name validation.

---

## 🎮 How to Play

### Installation
Ensure you are on a Windows machine (for `winsound` support) and have Python 3.x installed.
```bash
# Clone the repository and navigate to the folder
cd rockpaper
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
├── models/            # Logical state representations
│   ├── player.py
│   └── ai_player.py
├── managers/          # Helper utilities
│   ├── file_manager.py
│   └── sound_manager.py
├── ui/                # UI presentation
│   ├── app.py
│   └── frames/
├── save_data.json     # Auto-generated save file
└── README.md          # This documentation
```

Created by **Antigravity** (AI Assistant) in collaboration with the **USER** for COMP9001.
