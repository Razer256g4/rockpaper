"""
AI Multi-Slot Rock Paper Scissors Casino - COMP9001 submission.

HOW TO RUN
----------
From the project root:

    python main.py

The project root must be the working directory because save_data.json
is loaded/written via a relative path.

REQUIREMENTS
------------
- Python 3.x
- pygame (see requirements.txt) for cross-platform audio.
  Install with:  pip install -r requirements.txt

PLATFORM
--------
- Runs on Windows, macOS and Linux.
- If pygame isn't installed (or no audio device is available) the game
  still runs - audio just silently no-ops.

FEATURES TO DECLARE (per submission form)
-----------------------------------------
- GUI:               yes (tkinter)
- Audio:             yes (pygame.mixer, cross-platform)
- Networking:        none
- External libraries: pygame

CONTROLS
--------
R / P / S : choose Rock / Paper / Scissors for the active slot
Enter     : spin
"""
from ui.app import CasinoApp

if __name__ == "__main__":
    app = CasinoApp()
    app.mainloop()
