#! /usr/bin/python3
# Code Challenge 02 - Word Values Part II - a simple game
# http://pybit.es/codechallenge02.html

# TODO: Make Scrabble GUI?
from data import DICTIONARY, LETTER_SCORES, POUCH
import random, itertools, sys, shelve, getpass

NUM_LETTERS = 7
VOWELS = {'A', 'E', 'I', 'O', 'U'}


# re-use from challenge 01
def calc_word_value(word):
    """Calc a given word value based on Scrabble LETTER_SCORES mapping"""
    return sum(LETTER_SCORES.get(char.upper(), 0) for char in word)


# re-use from challenge 01
def max_word_value(words):
    """Calc the max value of a collection of words"""
    return max(words, key=calc_word_value)


def draw_letters(amount=NUM_LETTERS, vowel_check=True):
    # Pick amount of letters from POUCH and return as list.
    letters = [random.choice(POUCH) for i in range(amount)]

    # Make sure got vowel, otherwise pick amount again
    if not vowel_check and not has_vowels(letters):
        print(f'no vowels in {letters}, trying again')
        letters = draw_letters(amount)
    return letters


def find_optimal_word(curr_letters):
    possible_words = []
    for r in range(1, len(curr_letters)):
        for possible_word in itertools.permutations(curr_letters, r=r):
            # tuple to lowercase string
            possible_word = ''.join(str(char)
                                    for char in possible_word).lower()
            if possible_word in DICTIONARY:
                possible_words.append(possible_word)

    return max_word_value(possible_words)


def is_valid(_letters, word=None):
    letters = _letters.copy()
    # Must be in dictionary
    if word.lower() not in DICTIONARY:
        print(f'{word} is not a dictionary word... Try Again!\n')
        return False
    # Must be made from current letters, and only once
    for char in word.upper():
        if char in letters:
            letters.remove(char)
        else:
            print('Use the letters given... Try Again!\n')
            return False
    return True


def has_vowels(letters):
    return set(letters) & VOWELS


def calculate_score(word, best_word_val):
    total = calc_word_value(word)
    # Keep this check first.
    if total == best_word_val:
        print('Just as good as optimal!')
        total += 3
    if len(word) == NUM_LETTERS:
        print('Used all letters!')
        total += 5
    return total


def save(word, score):
    with shelve.open('app') as db:
        user = getpass.getuser()
        print(f'saving new best... {word} for {score} pts!!')
        db[user] = {'score': score, 'word': word}


def app_exit():
    print("Thanks for playing!!")
    sys.exit()


def main():
    '''
    Game Loop
        Draw letters from POUCH (first time is 7)
        Ask player for word
        Show player word score
        Show player the optimal word and its score
        Grade player: player_score / optimal_score
        Replace letters used from POUCH, repeat
    '''
    draw_amt = NUM_LETTERS
    curr_letters = []
    user_max_score = 0

    with shelve.open('app') as db:
        user = getpass.getuser()
        res = db.setdefault(user, {'word': None, 'score': 0})
        user_max_score = db[user]['score']

        print(f"{user}'s current best is {user_max_score}")

    while True:
        # Draw new letters
        vowel_status = has_vowels(curr_letters)
        curr_letters.extend(draw_letters(draw_amt, vowel_check=vowel_status))

        # Get user input
        user_word = None
        while not user_word or not is_valid(curr_letters, user_word):
            user_word = input(
                f'Here are your letters. Craft a word! \n{curr_letters}\n '
            ).lower()

        # Calculate word values vs optimal
        best_word = find_optimal_word(curr_letters)
        best_word_val = calc_word_value(best_word)
        user_score = calculate_score(user_word, best_word_val)
        grade = user_score / best_word_val
        print(f'You scored: {user_score} with {user_word}')
        print(f'The best word was {best_word} and scored {best_word_val}')
        print(f'Your grade: %.02f ' % grade)

        if user_score > user_max_score:
            save(user_word, user_score)
            user_max_score = user_score
        print(f'****************\n\n')

        # Set up for next loop
        draw_amt = len(user_word)
        for char in user_word:
            curr_letters.remove(char.upper())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        app_exit()