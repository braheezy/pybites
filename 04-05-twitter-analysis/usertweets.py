#! venv/bin/python
from collections import namedtuple
import csv
from pathlib import Path
from pprint import pprint

import tweepy

from config import CONSUMER_KEY, CONSUMER_SECRET
from config import ACCESS_TOKEN, ACCESS_SECRET

DEST_DIR = 'data'
EXT = 'csv'
NUM_TWEETS = 100

Tweet = namedtuple('Tweet', 'id_str created_at text')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
API = tweepy.API(auth)


class UserTweets(object):
    def __init__(self, handle, count=NUM_TWEETS, max_id=None):
        # max_id: Get tweets starting at a particular id
        # None means get most recent tweets.

        # Instance vars
        self.handle = handle
        self.tweets = self._get_tweets(count, max_id)
        self._save_tweets()

    def _get_tweets(self, count, max_id):
        tweets = [
            status
            for status in tweepy.Cursor(API.user_timeline,
                                        id=self.handle,
                                        max_id=max_id,
                                        tweet_mode='extended').items(count)
        ]
        tweets = [
            Tweet(tweet.id_str, tweet.created_at, str(tweet.full_text))
            for tweet in tweets
        ]
        print('UserTweets {}: got {} tweets'.format(self.handle, len(tweets)))

        return tweets

    def _save_tweets(self):
        # Make /data folder and write .csv inside.
        out = Path('./data')
        out.mkdir(exist_ok=True)
        self.output_file = out / (self.handle + '.csv')

        with self.output_file.open('w', newline='') as csvfile:
            fieldnames = ['id_str', 'created_at', 'text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for tweet in self.tweets:
                writer.writerow(tweet._asdict())

    # These two functions below let UserTweets support Iteration pattern
    def __len__(self):
        return len(self.tweets)

    def __getitem__(self, position):
        return self.tweets[position]


if __name__ == "__main__":
    for handle in ('pybites', 'bbelderbos'):
        print('--- {} ---'.format(handle))
        user = UserTweets(handle)
        # for tw in user[:5]:
        #     pprint(tw)
    print()
