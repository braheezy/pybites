#!venv/bin/python
import json
import sys
import string
import re
from textblob import TextBlob
from pprint import pprint
from nltk.tokenize import casual


def read_json(input_file):
    with open(input_file) as f:
        for line in f.readlines():
            yield json.loads(line)


def get_text(tweet):
    '''Find and return appropriate text for tweet.
    Could be:
        text
        full_text
        a retweet, so the text is buried deeper
    '''
    text = tweet['text']
    if text.startswith('RT'):
        try:
            text = tweet.get('retweeted_status').get('extended_tweet').get(
                'full_text')
            # print('using extended tweet')
        except Exception as err:
            pass
            # print('using normal text')

    return text


def process(tweet):
    '''
    Get tweet text into format ready for NLP'''
    # Tokenize first to let nltk smartly handle casual talk
    # EZ stripping of handles here.
    tokens = casual.casual_tokenize(tweet, strip_handles=True)
    # Now that we have list, do some processing that's easier that way
    # Remove the literal string 'RT' and links.
    tokens = filter(lambda t: not t.startswith("https://") and t != 'RT',
                    tokens)
    # Put tweet back together, naively
    tweet = ' '.join(tokens)
    # Now that tweet is string, do processing that's easier that way.
    # Regex to remove all punctuation, unicode too, and emojis
    # print(tweet)
    tweet = re.sub('\W[\s]', '', tweet)
    return tweet


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('please provide json data file')
        sys.exit(1)
    input_file = sys.argv[1]
    tweets = read_json(input_file)
    for tw in tweets:
        tw = dict(tw)
        # pprint(tw)
        tweet_text = get_text(tw)
        # print(tweet_text)
        tweet = process(tweet_text)

        blob = TextBlob(tweet)
        sentiment = blob.sentiment.polarity
        # print(sentiment)

        print('***************\n')
        print('{}\nhas a {:.6f} sentiment.\nBroken down tweet: {}'.format(
            tweet_text, sentiment, tweet))
        print('***************')
