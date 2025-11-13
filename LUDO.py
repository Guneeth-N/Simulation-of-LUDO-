import random
import os

# Define constants for the game
PLAYERS = ['Red', 'Green', 'Yellow', 'Blue']
START_POSITIONS = {'Red': 1, 'Green': 14, 'Yellow': 27, 'Blue': 40}
HOME_ENTRANCE = {'Red': 51, 'Green': 12, 'Yellow': 25, 'Blue': 38}
SAFE_SPOTS = [1, 9, 14, 22, 27, 35, 40, 48]
PATH_LENGTH = 52
HOME_PATH_LENGTH = 6

class LudoGame:
    """
    Manages the state and logic of a 4-player Ludo game.
    """
    def __init__(self):
        """Initializes the game with 4 players and sets up the initial state."""
        self.players = {color: self.initialize_player_tokens() for color in PLAYERS}
        self.current_player_index = 0
        self.turn_history = []
        self.game_winner = None
        print("Ludo Game Initialized!")

    def initialize_player_tokens(self):
        """Returns the initial state for a player's four tokens."""
        # Position 0: In the yard
        # Position 1-52: On the main board path
        # Position 53-58: On the home path
        # Position 99: Reached home
        return {i: 0 for i in range(1, 5)}

    def roll_dice(self):
        """Simulates rolling a 6-sided die."""
        return random.randint(1, 6)

    def display_board(self):
        """Displays the current positions of all tokens on the board."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- Ludo Game Board ---")
        for color, tokens in self.players.items():
            print(f"\nPlayer: {color}")
            for token_id, position in tokens.items():
                status = ""
                if position == 0:
                    status = "In Yard"
                elif position == 99:
                    status = "Home"
                elif position > 52:
                    status = f"On Home Path (Step {position - 52})"
                else:
                    status = f"On Board (Square {position})"
                print(f"  Token {token_id}: {status}")
        print("\n-----------------------")

    def get_player_turn(self):
        """Gets the color of the current player."""
        return PLAYERS[self.current_player_index]

    def get_movable_tokens(self, player_color, dice_roll):
        """
        Determines which of the player's tokens can be moved based on the dice roll.
        """
        movable_tokens = []
        player_tokens = self.players[player_color]

        for token_id, position in player_tokens.items():
            if position == 0 and dice_roll == 6:
                movable_tokens.append(token_id)
            elif position > 0 and position != 99:
                # Check for moves on the home path
                if position > 52:
                    if (position + dice_roll) <= 58:
                         movable_tokens.append(token_id)
                else: # On main board
                    movable_tokens.append(token_id)

        return movable_tokens

    def move_token(self, player_color, token_id, dice_roll):
        """Moves a selected token and handles all related game logic."""
        current_position = self.players[player_color][token_id]
        start_pos = START_POSITIONS[player_color]

        # --- Move token from YARD to START ---
        if current_position == 0 and dice_roll == 6:
            self.players[player_color][token_id] = start_pos
            self.check_for_capture(player_color, start_pos)
            return

        # --- Calculate new position ---
        new_position = current_position + dice_roll
        home_entrance = HOME_ENTRANCE[player_color]

        # --- Handle Home Path Entry ---
        # This logic checks if the token passes its home entrance
        if current_position <= home_entrance and new_position > home_entrance:
             # Move onto home path
            home_path_pos = 52 + (new_position - home_entrance)
            if home_path_pos > 58: # Overshot the home square
                 return # Invalid move, do nothing
            self.players[player_color][token_id] = home_path_pos
            if home_path_pos == 58: # Reached home
                self.players[player_color][token_id] = 99
        # --- Handle movement on the home path ---
        elif current_position > 52:
            if new_position <= 58:
                self.players[player_color][token_id] = new_position
                if new_position == 58: # Reached home
                    self.players[player_color][token_id] = 99
            # else: overshot, do nothing (handled in get_movable_tokens)
        # --- Handle Normal Board Movement ---
        else:
            # Wrap around the board if necessary
            final_position = new_position % PATH_LENGTH
            if final_position == 0:
                final_position = PATH_LENGTH
            self.players[player_color][token_id] = final_position
            self.check_for_capture(player_color, final_position)

    def check_for_capture(self, attacker_color, position):
        """Checks if a move results in capturing an opponent's token."""
        if position in SAFE_SPOTS:
            return # Cannot capture on safe spots

        for player_color, tokens in self.players.items():
            if player_color != attacker_color:
                for token_id, token_pos in tokens.items():
                    if token_pos == position:
                        self.players[player_color][token_id] = 0 # Send back to yard
                        print(f"!!! {attacker_color} captured {player_color}'s token at position {position}!")


    def check_win_condition(self, player_color):
        """Checks if a player has all four tokens at home."""
        return all(pos == 99 for pos in self.players[player_color].values())

    def play_turn(self):
        """Executes a single turn for the current player."""
        player = self.get_player_turn()
        print(f"\n--- It's {player}'s turn! ---")
        input("Press Enter to roll the dice...")

        dice_roll = self.roll_dice()
        print(f"{player} rolled a {dice_roll}!")

        movable_tokens = self.get_movable_tokens(player, dice_roll)

        if not movable_tokens:
            print("No movable tokens. Turn skipped.")
        else:
            print(f"You can move these tokens: {movable_tokens}")
            choice = 0
            while choice not in movable_tokens:
                try:
                    choice = int(input("Which token do you want to move? (Enter ID): "))
                    if choice not in movable_tokens:
                        print("Invalid choice. Please pick a token from the list.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            self.move_token(player, choice, dice_roll)

        # Check for winner
        if self.check_win_condition(player):
            self.game_winner = player
            return # End the turn early

        # Next player's turn, unless a 6 was rolled
        if dice_roll != 6:
            self.current_player_index = (self.current_player_index + 1) % len(PLAYERS)
        else:
            print("You rolled a 6! You get to roll again.")

    def start_game(self):
        """The main game loop."""
        while not self.game_winner:
            self.display_board()
            self.play_turn()

        self.display_board()
        print(f"\n🎉 CONGRATULATIONS! {self.game_winner} has won the game! 🎉")


if __name__ == "__main__":
    game = LudoGame()
    game.start_game()
