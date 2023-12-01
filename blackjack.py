import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import numpy as np
# Constants for suits and ranks
SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]

# Path to the directory with card images
IMAGE_DIR = "png" 

# Simple AI Player for demonstration purposes
class AIPlayer:
    def __init__(self, blackjack_game, training = True, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.blackjack_game = blackjack_game
        self.training = training
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # exploration rate
        self.q_table = np.zeros((32, 12, 2))  # 22 for player's hand value (1-21, and >21), 11 for dealer's card (1-10), 2 for actions
        # Adjusted to 31 to accomodate all possible player hand values

    def make_decision(self):
        exploration_chance = np.random.rand()
        if exploration_chance < self.epsilon:
            # Exploration: choose a random action
            action =  np.random.choice(['hit', 'stand'])

        else:
            # Exploitation: choose the best action based on Q-table
            player_value = self.blackjack_game.calculate_score(self.blackjack_game.player_hand)
            dealer_card = self.blackjack_game.calculate_score(self.blackjack_game.dealer_hand[0])
            if self.q_table[player_value, dealer_card, 0] > self.q_table[player_value, dealer_card, 1]:
                action = 'hit'
            else:
                action = 'stand'
        return action

    def update_q_table(self, state, action, reward, new_state):
        action_index = 0 if action == 'hit' else 1
        current_q_value = self.q_table[state[0], state[1], action_index]
        # Map all bust values to 22
        player_score = max(new_state[0],22)
        # Find the best Q value for the new state
        new_max_q = np.max(self.q_table[player_score, new_state[1]])

        # Update the Q-table using the Q-learning formula
        self.q_table[state[0], state[1], action_index] = current_q_value + \
                                                        self.alpha * (reward + self.gamma * new_max_q - current_q_value)

    def get_final_reward(self):
        player_score = self.blackjack_game.calculate_score(self.blackjack_game.player_hand)
        dealer_score = self.blackjack_game.calculate_score(self.blackjack_game.dealer_hand)
        
        # Basic win/lose/tie rewards
        if player_score > 21:
            return -1.5  # Lose with additional penalty for busting
        elif dealer_score > 21 or player_score > dealer_score:
            reward = 1   # Win
        elif player_score < dealer_score:
            return -1  # Lose
        else:
            return 0   # Tie

        # Additional rewards for scores close to 21
        if player_score >= 20:
            reward += 0.5
        elif player_score >= 18:
            reward += 0.2

        return reward

    def get_immediate_reward(self, old_state,new_state):
        if new_state[0] > 21:
            return -1  # Penalty for busting
        elif new_state[0] > old_state[0]:
            return 0.1  # Small reward for improvement
        else:
            return 0  # Neutral for no significant change


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

        if isinstance(hand, tuple): # Unelegant solution to handling score for upcard
            hand = [hand]
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
    
    def get_game_state(self):
        return (self.calculate_score(self.player_hand),self.calculate_score(self.dealer_hand))

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
        player_score_frequency = {}
        dealer_score_frequency = {}
        
        for game_number in range(num_games):
            self.game.reset_game()
            while not self.game.game_over:
                 # Current state before making a decision
                current_state = (self.game.calculate_score(self.game.player_hand), self.game.calculate_score([self.game.dealer_hand[0]]))
                # AI makes a decision
                decision = self.ai_player.make_decision()

                # Apply decision and get new state
                if decision == 'hit':
                    # print("pre hit hand:",self.game.player_hand)
                    self.game.deal_card(self.game.player_hand)
                    # print("after hit hand:",self.game.player_hand)
                new_state = (self.game.calculate_score(self.game.player_hand), self.game.calculate_score([self.game.dealer_hand[0]]))

                # Immediate reward to incentivize hitting without busting
                immediate_reward = self.ai_player.get_immediate_reward(current_state,new_state)
                self.ai_player.update_q_table(current_state, decision, immediate_reward, new_state)
                
                # Check if game is over
                if new_state[0] > 21 or decision =='stand':
                    self.game.game_over = True
            while self.game.calculate_score(self.game.dealer_hand) < 17:
                self.game.deal_card(self.game.dealer_hand)
            # Final reward calculation and Q-table update for game end
            final_reward = self.ai_player.get_final_reward()
            self.ai_player.update_q_table(current_state, decision, final_reward, new_state)
        
            
            
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
            
            # Update score frequencies
            player_score_frequency[player_score] = player_score_frequency.get(player_score, 0) + 1
            dealer_score_frequency[dealer_score] = dealer_score_frequency.get(dealer_score, 0) + 1

            
            print(f"Game {game_number + 1}: Player {result}.")
            print(f"Player Hand: {player_hand} | Score: {player_score}")
            print(f"Dealer Hand: {dealer_hand} | Score: {dealer_score}\n")
        
        # Print the final tally
        print(f"\nAI Mode Summary:")
        print(f"Player wins: {player_wins}")
        print(f"Dealer wins: {dealer_wins}")
        print(f"Ties: {ties}")

        print("\nPlayer Score Frequencies:")
        for score, frequency in sorted(player_score_frequency.items()):
            print(f"Score {score}: {frequency} times")

        print("\nDealer Score Frequencies:")
        for score, frequency in sorted(dealer_score_frequency.items()):
            print(f"Score {score}: {frequency} times")

        #Visualizing the q table
        import matplotlib.pyplot as plt
        np.savez(f"qtable-{num_games}steps.npz",self.ai_player.q_table)
        # Set up the matplotlib figure with subplots
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        # Loop through each slice and create a heatmap
        for i in range(2):
            ax = axes[i]
            heatmap = ax.imshow(self.ai_player.q_table[:, :, i])
            ax.set_title(f'Index {i + 1}')
            fig.colorbar(heatmap, ax=ax)

        plt.tight_layout()
        plt.show()

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
