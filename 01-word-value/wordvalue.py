from data import DICTIONARY, LETTER_SCORES


def load_words():
    """Load dictionary into a list and return list"""
    words = []
    with open(DICTIONARY, 'r') as dict_file:
        for line in dict_file:
            words.append(line.strip())
    return words


def calc_word_value(word):
    """Calculate the value of the word entered into function
    using imported constant mapping LETTER_SCORES"""
    value = 0

    for char in word:
        if char.isalpha():
            value += LETTER_SCORES[char.upper()]
    return value


def max_word_value(words=None):
    """Calculate the word with the max value, can receive a list
    of words as arg, if none provided uses default DICTIONARY"""
    if words is None:
        words = load_words()
    max_value = [0, ""]
    for word in words:
        word_val = calc_word_value(word)
        if word_val > max_value[0]:
            max_value[0] = word_val
            max_value[1] = word
    return max_value[1]


if __name__ == "__main__":
    pass  # run unittests to validate
