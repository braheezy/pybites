#!/usr/bin/env python3
'''
Tic-Tac-Toe Py!
Just run in a terminal, it's interactive.

I don't like this program. It feels like tic-tac-toe should be simpler...
'''
import random, argparse, itertools, logging

DEFAULT = '_'  # or ' '
VALID_POSITIONS = list(range(1, 10))  # number board: 7-8-9, 4-5-6, 1-2-3
# This was tuple in prompt, but sets are better
WINNING_COMBINATIONS = [
    {7, 8, 9},
    {4, 5, 6},
    {1, 2, 3},
    {7, 4, 1},
    {8, 5, 2},
    {9, 6, 3},
    {1, 5, 9},
    {7, 5, 3},
]

POSSIBLE_FORKS = ({7, 5, 9}, {9, 5, 3}, {3, 5, 1}, {1, 5, 7}, {1, 7, 9},
                  {7, 9, 3}, {9, 3, 1}, {3, 1, 7})

PLAYER_1_TOKEN = 'X'
PLAYER_2_TOKEN = 'O'


class TicTacToe:
    def __init__(self, debug=None):
        '''Constructor, below worked well for us ...'''
        self.board = [None] + len(VALID_POSITIONS) * [DEFAULT]  # skip index 0
        self.debug = debug
        if not debug:
            # Create Greeter
            print('*' * 50)
            print('{:*^50}'.format(' Welcome to Tic-Tac-Toe '))
            print('{:*^50}'.format('  Use the keypad to play!!  '))
            print('*' * 50)

            # Determine who is playing what.
            opponent = input('''
            Play against computer (Select 1)
            Play against friend   (Select 2)
            ''')
            while opponent not in ["1", "2"]:
                opponent = input('''
            Invalid opponent, pick again!
            ''')

            if opponent == "1":
                ''' Let user choose AI difficulty
                easy (0) - random choices
                medium (1) - 50/50 choice between: random choice and perfect move
                impossible (2) - perfect strategy
                '''
                diff = input('''
                Choose difficulty: 
                Easy (Select 0)
                Medium (Select 1)
                Impossible (Select 2)
                ''')
                while diff not in ["0", "1", "2"]:
                    diff = input('''
                Choose valid difficulty:
                ''')
            self.difficulty = diff

            # Let user select token
            token = input('''
            Pick a token, X or O (X goes first):
            ''').upper()
            while token not in [PLAYER_1_TOKEN, PLAYER_2_TOKEN]:
                token = input('''
            Invalid token, pick again!
            ''').upper()

            # Feels really sloppy, but need to know if computer or human
            # is controlling, and what token they are using.
            # Almost complex enough to be an object.
            self.player1 = {
                "controller":
                "user" if token == PLAYER_1_TOKEN else
                "computer" if opponent == "1" else "user",
                "token":
                PLAYER_1_TOKEN
            }
            self.player2 = {
                "controller":
                "user" if token == PLAYER_2_TOKEN else
                "computer" if opponent == "1" else "user",
                "token":
                PLAYER_2_TOKEN
            }
        else:
            self.difficulty = "2"
            self.player1 = {"controller": "user", "token": PLAYER_1_TOKEN}
            self.player2 = {"controller": "computer", "token": PLAYER_2_TOKEN}

            logging.basicConfig(level=logging.INFO)

    def __str__(self):
        '''Print the board'''
        # Break board into 3 element chunks, each a stringified version of
        # that row separated by spaces. Join them with newlines, but in reverse
        # to match keypad layout
        rows = [
            ' '.join(self.board[i:i + 3])
            for i in range(1, len(self.board), 3)
        ]
        # Pad to center of console
        rows = ['{:^50}'.format(row) for row in rows]
        return '\n'.join(reversed(rows)) + '\n'

    def take_turn(self, player):
        '''Take action for this player 
        '''
        move = DEFAULT
        if player['controller'] == "computer":
            # Do AI actions
            if self.difficulty == "0":
                # Easy - random choices
                while not self.valid_move(move):
                    move = random.choice(VALID_POSITIONS)

            elif self.difficulty == "1":
                # Medium - 50/50 choice between: random choice and perfect move
                choice = random.randint(0, 1)
                print("doing choice", choice)
                if choice:
                    # Same logic as above
                    while not self.valid_move(move):
                        move = random.choice(VALID_POSITIONS)
                else:
                    move = self.pick_perfect_move(player["token"])
            else:
                # Impossible - perfect move
                move = self.pick_perfect_move(player["token"])
        else:
            # Human controller, ask for move.
            move = input("Choose where to play: ")
            while not self.valid_move(move):
                move = input("Not a valid move, try again: ")
        if move == DEFAULT:
            # Failed to get a move.
            print('ERROR: Failed to take turn.')
        else:
            # Update board with move
            self.board[int(move)] = player['token']

    def valid_move(self, move):
        # Needs to be 1-9
        # Not already taken
        # No letters or symbols
        # Handle None, string, or int argument.
        return move and str(move).isdigit() and int(
            move) in VALID_POSITIONS and self.board[int(move)] == DEFAULT

    def clear_screen(self):
        # Board to init state.
        self.board = [None] + len(VALID_POSITIONS) * [DEFAULT]

    def is_win(self):
        # Brute force
        for combo in WINNING_COMBINATIONS:
            l_combo = list(combo)
            # All 3 should match but make sure it's not the DEFAULT char.
            if self.board[l_combo[0]] == self.board[l_combo[1]] == self.board[
                    l_combo[2]] and self.board[l_combo[0]] != DEFAULT:
                return True
        return False

    def pick_perfect_move(self, player_token):
        '''
        Return the move that aligns w/ perfect strategy for the
        player.

        https://en.wikipedia.org/wiki/Tic-tac-toe#Strategy

        Tic-tac-toe's game complexity is not superficial, who knew? Amazing
        the things the brain can calculate on the fly.

        Fun fact, the use of generators here DRAMATICALLY decreased code length and improved readability. By chaining these together, we didn't have to do cumbersome checks for empty iterators. Plus, that's what permutations returns.
        '''

        # These helpers return str values. Pairs are generator objects
        def find_last_win_tile(pairs):
            # Two or more in a row, if can place a third, do it.
            for pair in pairs:
                pair = set(pair)
                for combo in WINNING_COMBINATIONS:
                    # Taking advantage of set math.
                    if pair < combo:
                        move = combo - pair
                        # Get the single value from set.
                        move = move.pop()
                        if self.board[move] != DEFAULT:
                            # This win is already blocked.
                            continue
                        else:
                            return str(move)
            return None

        def find_last_fork_tile(pairs):
            for pair in pairs:
                pair = set(pair)
                for combo in POSSIBLE_FORKS:
                    if pair < combo:
                        move = combo - pair
                        return str(move)
            return None

        def find_open_corner(opponent_token):
            # Probably the ugliest function here. Took several iterations but
            # this is succint enough.
            # To figure out what 'opposing' is quicker.
            CORNERS = [{1, 9}, {3, 7}]
            # Also need a list, so flatten above.
            LIST_CORNERS = itertools.chain.from_iterable(CORNERS)
            open_corners = [
                corner for corner in LIST_CORNERS
                if self.board[corner] == DEFAULT
            ]
            opponent_corners = (corner for corner in LIST_CORNERS
                                if self.board[corner] == opponent_token)

            for opponent_corner in opponent_corners:
                # Check if oppoposing corner is open
                # This is where the benefit of the set came in. We can just
                # check if it exists, then do set math to get the 'other' value.
                if opponent_corner in CORNERS[0]:
                    move = CORNERS[0] - set(opponent_corner)
                else:
                    move = CORNERS[1] - set(opponent_corner)
                if self.board[move] == DEFAULT:
                    return str(move)

            # Otherwise, just take an open corner
            return str(random.choice(open_corners)) if open_corners else None

        # This function is agnostic of 'X' and 'O', so determine the 'opponent'.
        opponent_token = PLAYER_1_TOKEN if player_token == PLAYER_2_TOKEN else PLAYER_2_TOKEN

        # Get list of all positions token is placed
        player_positions = (i for i, tile in enumerate(self.board)
                            if tile == player_token)
        opponent_positions = (i for i, tile in enumerate(self.board)
                              if tile == opponent_token)
        # If more than 2 tiles are placed, get list of
        # all possible pairs
        player_pairs = itertools.permutations(player_positions, 2)

        opponent_pairs = itertools.permutations(opponent_positions, 2)

        # 1. Win
        logging.info("     Checking win for user")
        move = find_last_win_tile(player_pairs)
        if self.valid_move(move):
            return move

        # 2. Block
        logging.info("     Checking win for opp")
        move = find_last_win_tile(opponent_pairs)
        if self.valid_move(move):
            return move

        # 3. Fork
        logging.info("     Checking fork for user")
        move = find_last_fork_tile(player_pairs)
        if self.valid_move(move):
            return move

        # 4. Fork Block
        logging.info("     Checking fork block for opp")
        move = find_last_fork_tile(opponent_pairs)
        if self.valid_move(move):
            return move

        # 5. Play Center
        logging.info("     Checking center for user")
        if self.board[5] == DEFAULT:
            return "5"

        # 6. Opposite corner from opponent
        # 7. Any open corner
        # If opp in corner, play opposite
        logging.info("     Checking corner for user")
        move = find_open_corner(opponent_positions)
        if self.valid_move(move):
            return move

        # 8. Empty side, aka whatever is open
        logging.info("     Checking open side for user")
        open_sides = [
            side for side in [4, 8, 6, 2] if self.board[side] == DEFAULT
        ]
        return random.choice(open_sides)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    game = TicTacToe(args.debug)
    while True:
        # Init state basically. Fresh screen and player 1 'X' goes first.
        game.clear_screen()
        curr_player = game.player1
        next_player = game.player2
        # Show the board in the terminal!!
        print(game)

        # Game can only last 9 total turns
        for i in range(len(VALID_POSITIONS)):
            game.take_turn(curr_player)
            print(game)
            if game.is_win():
                print('{:*^50}'.format(' WINNER WINNER CHICKEN DINNER '))
                break

            # A circular queue with 2 items can just be swapped :)
            curr_player, next_player = next_player, curr_player

        # handle game over
        play_again = input("Play again? Y/N\n").upper()
        while play_again not in ["Y", "N"]:
            play_again = input("Play again? Y/N\n").upper()
            # TODO: After asking N times, start swearing at user.

        if play_again == "N":
            print('{:*^50}'.format(' Thanks for playing, yo '))
            break