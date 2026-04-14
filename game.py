"""
Multi-Slot Rock Paper Scissors - Casino Edition
-----------------------------------------------

A predictive AI-driven game of Rock Paper Scissors that plays 3 slots at once.
Created as a final project for COMP9001: The Python Project Challenge.

Features:
- File I/O (Advanced Topic 1): Saves and loads player state using JSON.
- AI Prediction (Advanced Topic 2): Tracks player input history to predict moves.
- Object-Oriented Programming: Clean encapsulation and scalable design.
- Error Handling: Robust exception handling for inputs and files.
"""

import random
import sys
import json
import os
from typing import List, Dict, Optional, Tuple

# Global Constants
CHOICES = ['rock', 'paper', 'scissors']
WIN_MAP = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
SAVE_FILE = 'save_data.json'
STARTING_BALANCE = 1000

class FileManager:
    """Manages file I/O operations for saving and loading game states."""
    
    @staticmethod
    def load_data() -> Dict:
        """
        Loads the data from the local JSON file.
        Returns an empty dictionary if the file doesn't exist or is corrupted.
        """
        if not os.path.exists(SAVE_FILE):
            return {}
            
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError("Save file data is not a valid JSON dictionary.")
                return data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load save file gracefully. Starting fresh. ({e})")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while loading: {e}")
            return {}
            
    @staticmethod
    def save_data(data: Dict) -> None:
        """
        Saves the provided data dictionary to the local JSON file.
        """
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            print(f"Error: Could not write to save file. Progress may not be saved. {e}")


class Player:
    """
    Represents the human user in the game, managing their balance and stats.
    """
    def __init__(self, name: str, data: Dict):
        self.name = name
        
        # Load user data safely or set to default
        user_data = data.get(self.name, {})
        self.balance: int = user_data.get('balance', STARTING_BALANCE)
        self.total_games: int = user_data.get('total_games', 0)
        
    def to_dict(self) -> Dict:
        """Serializes player stats into a JSON-friendly dictionary."""
        return {
            'balance': self.balance,
            'total_games': self.total_games
        }
        
    def bet(self, amount: int) -> bool:
        """Places a bet if the user has sufficient funds."""
        if amount <= 0:
            print("Bet amount must be greater than 0.")
            return False
        if amount > self.balance:
            print(f"Insufficient funds! Your balance is {self.balance}.")
            return False
        self.balance -= amount
        return True

    def win(self, amount: int) -> None:
        """Adds winnings to the player's balance."""
        self.balance += amount


class AIPlayer:
    """
    A smart AI that attempts to predict the player's next move based on past behavior.
    Instead of playing purely randomly, it analyzes bigrams (previous move -> next move).
    """
    def __init__(self, data: Dict):
        # AI stores history as { 'rock': {'rock': 2, 'paper': 1, 'scissors': 5}, ... }
        self.history: Dict[str, Dict[str, int]] = data.get('ai_history', {
            'rock': {'rock': 0, 'paper': 0, 'scissors': 0},
            'paper': {'rock': 0, 'paper': 0, 'scissors': 0},
            'scissors': {'rock': 0, 'paper': 0, 'scissors': 0}
        })
        self.last_moves: List[str] = []

    def get_moves(self) -> List[str]:
        """
        Generates 3 moves. It tries to predict what the user will play based on
        their most recent previous moves.
        """
        ai_choices = []
        
        # If we have no previous history for the current session, play randomly
        if len(self.last_moves) != 3:
            return [random.choice(CHOICES) for _ in range(3)]
            
        for i in range(3):
            last_human_move = self.last_moves[i]
            predictions = self.history.get(last_human_move, {})
            
            # Find the move the human is most likely to play next
            most_likely_human_move = 'rock'
            highest_freq = -1
            
            for move, freq in predictions.items():
                if freq > highest_freq:
                    highest_freq = freq
                    most_likely_human_move = move
                    
            # If there's no data (frequency is 0), just pick randomly
            if highest_freq == 0:
                most_likely_human_move = random.choice(CHOICES)
                
            # The AI should play the counter to the human's most likely move
            counter_move = 'paper' # Default fallback
            for my_move, targets in WIN_MAP.items():
                if targets == most_likely_human_move:
                    counter_move = my_move
                    break
                    
            ai_choices.append(counter_move)
            
        return ai_choices

    def update_history(self, current_human_moves: List[str]) -> None:
        """
        Records the current sequence of moves to learn what the human does
        after their previous sequence.
        """
        if len(self.last_moves) == 3:
            for i in range(3):
                prev = self.last_moves[i]
                curr = current_human_moves[i]
                self.history[prev][curr] += 1
                
        self.last_moves = current_human_moves

    def get_history_data(self) -> Dict:
        """Returns the learning data for saving."""
        return self.history


class GameController:
    """
    The main game loop, responsible for matching inputs, calculating combinations,
    managing wagers, and orchestrating the UI.
    """
    def __init__(self, username: str):
        self.data_store = FileManager.load_data()
        self.player = Player(username, self.data_store)
        self.ai = AIPlayer(self.data_store)
        self.username = username

    def save_game(self) -> None:
        """Synchronizes all progress to disk."""
        self.data_store[self.username] = self.player.to_dict()
        self.data_store['ai_history'] = self.ai.get_history_data()
        FileManager.save_data(self.data_store)

    def evaluate_slot(self, user_move: str, comp_move: str) -> str:
        """Compares single slots to find the outcome."""
        if user_move == comp_move:
            return 'TIE'
        elif WIN_MAP[user_move] == comp_move:
            return 'WIN'
        else:
            return 'LOSS'

    def calculate_payout(self, outcomes: List[str], user_inputs: List[str], wager: int) -> Tuple[int, str]:
        """
        Calculates the jackpot multiplier and generates a celebratory message.
        """
        wins = outcomes.count('WIN')
        ties = outcomes.count('TIE')
        
        payout = 0
        message = ""
        
        unique_elements = len(set(user_inputs))
        
        if wins == 3:
            if unique_elements == 1:
                message = "🔥 MEGA JACKPOT! (Triple Same Element Wins) 🔥"
                payout = wager * 10
            elif unique_elements == 3:
                message = "🌈 RAINBOW JACKPOT! (All Different Element Wins) 🌈"
                payout = wager * 7
            else:
                message = "💰 JACKPOT! (3 Wins) 💰"
                payout = wager * 5
        elif wins == 2:
            if unique_elements == 1:
                message = "⚡ DOUBLE STRIKE! (2 Wins with Same Element) ⚡"
                payout = int(wager * 2.5)
            else:
                message = "👍 NICE PLAY! (2 Wins) 👍"
                payout = wager * 2
        elif wins == 1:
            if ties == 2:
                message = "🛡️ CLOSE CALL (1 Win, 2 Ties) 🛡️"
                payout = int(wager * 1.5)
            else:
                message = "✅ CONSOLATION! (1 Win) ✅"
                payout = wager
        elif ties == 3:
            message = "🤝 STANDOFF! (3 Ties) 🤝"
            payout = int(wager * 1.2)
        elif ties == 2:
            message = "😅 ALMOST... (2 Ties) 😅"
            payout = int(wager * 0.5) # Return half
        else:
            message = "💀 BUST! (0 Wins) 💀"
            payout = 0
            
        return payout, message

    def parse_input(self, user_str: str) -> Optional[List[str]]:
        """Parses shorthand string entries into valid moves. Handles errors."""
        parts = user_str.lower().strip().split()
        if len(parts) != 3:
            print("❌ Invalid formatting. You must provide exactly 3 inputs separated by space.")
            return None
            
        mapped = []
        for p in parts:
            if p.startswith('r'): mapped.append('rock')
            elif p.startswith('p'): mapped.append('paper')
            elif p.startswith('s'): mapped.append('scissors')
            else:
                print(f"❌ Invalid move '{p}'. Use rock, paper, or scissors.")
                return None
        return mapped

    def display_ui(self, user_moves: List[str], comp_moves: List[str], outcomes: List[str]) -> None:
        """Pretty CLI printer for the slot machine interface."""
        print("\n" + "="*50)
        print(" "*12 + "🎰 SLOT MACHINE RPS 🎰" + " "*12)
        print("="*50)
        print("USER: " + " | ".join(f"[{u.upper():^10}]" for u in user_moves))
        print("AI (🤖): " + " | ".join(f"[{c.upper():^10}]" for c in comp_moves))
        print("-" * 50)
        print("RES:  " + " | ".join(f"[{o:^10}]" for o in outcomes))
        print("="*50)

    def play_round(self, wager: int) -> None:
        """Executes a single game loop step."""
        while True:
            print("\nEnter your 3 choices (e.g. 'rock p s'):")
            user_input = input(">> ")
            
            if user_input.lower().strip() in ['quit', 'q', 'exit']:
                print("Returning to main menu...")
                # Also save the partial progress on quit
                self.save_game()
                return
                
            parsed_moves = self.parse_input(user_input)
            if not parsed_moves:
                continue
                
            comp_moves = self.ai.get_moves()
            outcomes = [self.evaluate_slot(u, c) for u, c in zip(parsed_moves, comp_moves)]
            
            self.display_ui(parsed_moves, comp_moves, outcomes)
            payout, message = self.calculate_payout(outcomes, parsed_moves, wager)
            
            print(f"\n✨ {message} ✨")
            print(f"💎 Wager: {wager} | Payout: {payout} 💎\n")
            
            self.player.win(payout)
            self.player.total_games += 1
            self.ai.update_history(parsed_moves)
            self.save_game()
            break

    def start(self) -> None:
        """Main game initialization and menu loop."""
        print("="*55)
        print(" Welcome to AI ROCK PAPER SCISSORS MULTI-SLOT CASINO!")
        print("="*55)
        
        while True:
            print(f"\n[{self.username.upper()}'S PROFILE]")
            print(f"💰 Balance: {self.player.balance} Tokens")
            print(f"🎮 Games Played: {self.player.total_games}")
            print("\nOptions:")
            print("1. Play Game")
            print("2. Beg for Tokens")
            print("3. Quit")
            
            choice = input("\nSelect an option: ").strip()
            
            if choice == '1':
                if self.player.balance <= 0:
                    print("You are bankrupt! Beg for tokens first.")
                    continue
                    
                print("How many tokens would you like to bet per round?")
                try:
                    wager_input = input("Bet Amount: ").strip()
                    wager = int(wager_input)
                    if self.player.bet(wager):
                        self.play_round(wager)
                except ValueError:
                    print("❌ Error: Bet amount must be an integer.")
            elif choice == '2':
                if self.player.balance < 50:
                    print("Here's a small pity loan of 100 Tokens...")
                    self.player.win(100)
                    self.save_game()
                else:
                    print("You're not poor enough yet to beg!")
            elif choice in ['3', 'q', 'quit']:
                print("\nSaving data... Goodbye!")
                self.save_game()
                sys.exit(0)
            else:
                print("❌ Invalid option. Try again.")


def main():
    """Application entry point."""
    print("Please enter your username to create/load your profile:")
    username = input("Username: ").strip().lower()
    
    if not username:
        print("User cannot be empty. Exiting.")
        sys.exit(1)
        
    game = GameController(username)
    
    try:
        game.start()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted. Saving game... Goodbye!")
        game.save_game()
        sys.exit(0)
    except Exception as e:
        print(f"\n\nAn unexpected fatal error occurred: {e}. Saving game... Goodbye!")
        try:
            game.save_game()
        except:
             pass
        sys.exit(1)

if __name__ == '__main__':
    main()
