#!/usr/bin/env python3

from string import ascii_lowercase, punctuation
import sys

from movies import get_movie as get_word  # keep interface generic
from graphics import hang_graphics

ASCII = list(ascii_lowercase)
HANG_GRAPHICS = list(hang_graphics())
ALLOWED_GUESSES = len(HANG_GRAPHICS)
PLACEHOLDER = '_ '


def prompt():
    return input('Guess a letter: ')


class HangmanTile(object):
    '''
    A Tile knows what letter it should be and if it should show
    '''
    def __init__(self, letter="  "):
        self.letter = letter
        self.show = True if letter == "  " else False

    def __str__(self):
        return self.letter if self.show else PLACEHOLDER


class Hangman(object):
    '''
    Provide a Hangman instance, allowing clients to play the game.

    Game loop:
        Ask player for letter
        If exists, show letter(s)
        Else, show next graphic

        If word is filled, player wins.
        If last graphic is reached, player loses.
    '''
    def __init__(self, words):
        # First, remove all punctuation.
        words = words.translate(str.maketrans("", "", punctuation))

        # Based on words, create initial board, which is initially all PLACEHOLDER
        self.board = []
        for word in words.split():
            for letter in word:
                self.board.append(HangmanTile(letter))
            # Extra space between words.
            self.board.append(HangmanTile())

        # Define rest of app structures
        self.guessed_letters = set()
        self.current_graphics = 1
        # For quick reference if guess is correct
        self.secret_word = "".join(words.split()).lower()

        # Print greeting and initial board.
        print('Welcome to Hangman!\n')
        self.print_board()

    def print_board(self):
        # Print current graphic.
        print(HANG_GRAPHICS[self.current_graphics - 1])
        for tile in self.board:
            # Evaluate if we need to show this letter
            if not tile.show and tile.letter.lower() in self.guessed_letters:
                tile.show = True
            print(tile, end="")
        print()

    def run(self):
        num_guesses = 0
        win = False

        while self.current_graphics < ALLOWED_GUESSES:
            # TODO: Validate input.
            c = prompt().lower()
            # Keep prompting until input is valid.
            while not self.is_valid_input(c):
                c = prompt().lower()

            # Check if incorrect guess.
            if c not in self.secret_word:
                self.current_graphics += 1

            self.guessed_letters.add(c)

            # Print next board and end game loop if win.
            self.print_board()
            if self.check_win():
                win = True
                print('********** CONGRATS WINNER **********')
                break

        if not win:
            # Game over
            print('********** YOU ARE A LOSER **********')

    def check_win(self):
        return all([tile.show for tile in self.board])

    def is_valid_input(self, c):
        if c in self.guessed_letters or not c.isalpha():
            return False

        return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        word = get_word()
    print(word)

    # init / call program
    game = Hangman(word)
    game.run()
