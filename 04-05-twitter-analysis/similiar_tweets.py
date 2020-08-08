#! venv/bin/python
from pprint import pprint
from usertweets import UserTweets
import string

import numpy as np

from collections import Counter

from nltk.tokenize import casual
from nltk.corpus import stopwords
from nltk import PorterStemmer


def main(handle1, handle2, n_tweets):
    tweets1 = fetch_tweets(handle1, n_tweets)
    tweets2 = fetch_tweets(handle2, n_tweets)

    tweets1 = process_tweets(tweets1)
    tweets2 = process_tweets(tweets2)

    return similarity_score(tweets1, tweets2)


def similarity_score(dict1, dict2):
    '''
    dict#: A Counter dict of word freq calculated from a document
    '''
    # Create vocab of all words
    vocab = list(dict1.keys()) + list(dict2.keys())
    vocab_size = len(vocab)
    print(f'vocab size: {vocab_size}')

    vec1 = np.zeros(vocab_size, dtype=np.int)
    vec2 = np.zeros(vocab_size, dtype=np.int)

    for i, word in enumerate(vocab):
        vec1[i] = dict1.get(word, 0)
        vec2[i] = dict2.get(word, 0)
    return cos_sim(vec1, vec2)


def cos_sim(a, b):
    # Compute cosine of angle between 2 vectors
    # Also, inner (dot) product of vectors normalized to length 1
    dot_prod = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_prod / (norm_a * norm_b)


def fetch_tweets(handle, n):
    tweets = UserTweets(handle, n).tweets

    tweets = [tweet.text for tweet in tweets]
    return tweets


def process_tweets(tweets):
    token_tweets = tokenize_tweets(tweets)

    # Stemming
    porter = PorterStemmer()
    stemmed_tokens = (porter.stem(w) for tw in token_tweets for w in tw)

    # Remove tokens that are links
    stemmed_tokens = filter(lambda t: not t.startswith("https://"),
                            stemmed_tokens)
    # Stop words and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_tokens = (
        tok for tok in stemmed_tokens
        if tok not in stop_words and tok not in string.punctuation)

    return Counter(filtered_tokens)


def tokenize_tweets(tweets):
    '''
    tweets: List of strings, each a tweet. Each contains noise,
    like newlines, symbols, etc.
    Some are retweets and comments.
    '''
    def only_tweets(tw):
        # No retweets or comments
        if tw.startswith('RT') or tw.startswith('@'):
            return False
        return True

    tweets = filter(only_tweets, tweets)

    # lambda in map so we can pass False to preserve_case arg
    tweets = list(
        map(
            lambda tw: casual.casual_tokenize(
                tw, preserve_case=True, reduce_len=True), tweets))

    return tweets


if __name__ == "__main__":

    queries = (('dbader_org', 0.985021), ('gvanrossum', 0.985021),
               ('importpython', 0.985021), ('jsonmez', 0.985021),
               ('pybites', 0.985021), ('tferriss', 0.985021),
               ('newsafaribooks', 0.149423), ('paugasol', 0.149423),
               ('Schwarzenegger', 0.149423), ('raymondh', 0.142598),
               ('github', 0.064402), ('lifehacker', 0.057078))
    n_tweets = 200
    score = main('bbelderbos', 'bbelderbos', n_tweets)

    print(f"sim score between {n_tweets} tweets: {score}")
