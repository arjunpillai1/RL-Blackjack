import tkinter as tk
from PIL import Image, ImageTk
import random
import os

# Constants for suits and ranks
SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]

# Path to the directory with card images
IMAGE_DIR = "playing-cards-assets-master\playing-cards-assets-master\png"  # Update with the correct path

# Simple AI Player for demonstration purposes
class AIPlayer:
    def __init__(self, blackjack_game):
        self.blackjack_game = blackjack_game

    def make_decision(self):
        # Simple strategy: hit if score < 17, otherwise stand
        if self.blackjack_game.calculate_score(self.blackjack_game.player_hand) < 17:
            return 'hit'
        return 'stand'

class Blackjack:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.start_game()

    def create_deck(self):
        return [(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_card(self, hand):
        hand.append(self.deck.pop())

    def calculate_score(self, hand):
        score = 0
        ace_count = 0
        for rank, _ in hand:
            if rank in ["jack", "queen", "king"]:
                score += 10
            elif rank == "ace":
                ace_count += 1
                score += 11
            else:
                score += int(rank)
        while score > 21 and ace_count:
            score -= 10
            ace_count -= 1
        return score

    def start_game(self):
        self.shuffle_deck()
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)

    def reset_game(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.start_game()

    def display_hand(self, hand):
        return ' '.join(f"{rank} of {suit}," for rank, suit in hand)
    
class BlackjackGUI:
    def __init__(self, game):
        self.game = game
        self.window = tk.Tk()
        self.window.title("Blackjack")

        # Load card images
        self.card_images = self.load_card_images()

        # Initialize game
        self.game.start_game()

        # Setup GUI components
        self.setup_gui()
        self.update_gui()

    def load_card_images(self):
        card_images = {}
        for suit in SUITS:
            for rank in RANKS:
                filename = f"{rank}_of_{suit}.png"
                image_path = os.path.join(IMAGE_DIR, filename)
                try:
                    image = Image.open(image_path)
                    card_images[(rank, suit)] = ImageTk.PhotoImage(image)
                except FileNotFoundError:
                    print(f"Error: Unable to find {image_path}")
        return card_images

    def setup_gui(self):
        self.player_area = tk.Frame(self.window, bg="green")
        self.player_area.pack(side="bottom", fill="x")

        self.dealer_area = tk.Frame(self.window, bg="green")
        self.dealer_area.pack(side="top", fill="x")

        self.hit_button = tk.Button(self.window, text="Hit", command=self.hit)
        self.hit_button.pack(side="left")

        self.stand_button = tk.Button(self.window, text="Stand", command=self.stand)
        self.stand_button.pack(side="right")

        self.status_label = tk.Label(self.window, text="", font=('Helvetica', 16))
        self.status_label.pack(side="bottom")

        self.replay_button = tk.Button(self.window, text="Replay", command=self.replay)
        self.replay_button.pack(side="bottom")
        self.replay_button.config(state=tk.DISABLED)  # Disabled by default

    def update_gui(self):
        for widget in self.player_area.winfo_children():
            widget.destroy()
        for widget in self.dealer_area.winfo_children():
            widget.destroy()

        for card in self.game.player_hand:
            label = tk.Label(self.player_area, image=self.card_images[card])
            label.pack(side="left")

        for card in self.game.dealer_hand:
            label = tk.Label(self.dealer_area, image=self.card_images[card])
            label.pack(side="left")

        self.status_label.config(text=f"Player Score: {self.game.calculate_score(self.game.player_hand)}")

    def hit(self):
        self.game.deal_card(self.game.player_hand)
        self.update_gui()
        if self.game.calculate_score(self.game.player_hand) > 21:
            self.game_over()
            self.status_label.config(text="Busted!")

    def stand(self):
        while self.game.calculate_score(self.game.dealer_hand) < 17:
            self.game.deal_card(self.game.dealer_hand)
        self.game_over()

    def game_over(self):
        player_score = self.game.calculate_score(self.game.player_hand)
        dealer_score = self.game.calculate_score(self.game.dealer_hand)
        self.update_gui()

        if player_score > 21:
            result = "Player busts! Dealer wins!"
        elif dealer_score > 21 or player_score > dealer_score:
            result = "Player wins!"
        elif player_score < dealer_score:
            result = "Dealer wins!"
        else:
            result = "It's a tie!"

        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.NORMAL)
        self.status_label.config(text=result)

    def replay(self):
        self.game.reset_game()
        self.replay_button.config(state=tk.DISABLED)
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.update_gui()

    def run_ai_game(self, num_games):
        self.ai_player = AIPlayer(self.game)
        player_wins = 0
        dealer_wins = 0
        ties = 0
        
        for game_number in range(num_games):
            self.game.reset_game()
            while not self.game.game_over:
                decision = self.ai_player.make_decision()
                if decision == 'hit':
                    self.game.deal_card(self.game.player_hand)
                    if self.game.calculate_score(self.game.player_hand) > 21:
                        self.game.game_over = True
                else:
                    while self.game.calculate_score(self.game.dealer_hand) < 17:
                        self.game.deal_card(self.game.dealer_hand)
                    self.game.game_over = True
            
            # Determine the outcome of the game and update the counters
            player_score = self.game.calculate_score(self.game.player_hand)
            dealer_score = self.game.calculate_score(self.game.dealer_hand)
            player_hand = self.game.display_hand(self.game.player_hand)
            dealer_hand = self.game.display_hand(self.game.dealer_hand)

            if player_score > 21 or (dealer_score <= 21 and dealer_score > player_score):
                dealer_wins += 1
                result = "loss"
            elif dealer_score > 21 or player_score > dealer_score:
                player_wins += 1
                result = "win"
            else:
                ties += 1
                result = "tie"
            
            print(f"Game {game_number + 1}: Player {result}.")
            print(f"Player Hand: {player_hand} | Score: {player_score}")
            print(f"Dealer Hand: {dealer_hand} | Score: {dealer_score}\n")
        
        # Print the final tally
        print(f"\nAI Mode Summary:")
        print(f"Player wins: {player_wins}")
        print(f"Dealer wins: {dealer_wins}")
        print(f"Ties: {ties}")

if __name__ == "__main__":
    game = Blackjack()
    ai_mode = input("Play in AI mode? (yes/no): ").lower() == 'yes'
    if ai_mode:
        num_games = int(input("How many games should the AI play? "))
        gui = BlackjackGUI(game)
        gui.run_ai_game(num_games)
    else:
        gui = BlackjackGUI(game)
        gui.window.mainloop()
