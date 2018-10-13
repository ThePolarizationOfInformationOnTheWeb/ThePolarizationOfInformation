import tweepy
import pandas as pd

# write these in a config file: TODO
features = ['user_id', 'username', 'text', 'friends']

class tweet_collector:

    def __index__(self, topic: str, path_to_keys: str = './keys.csv'):
        # set up access to API
        keys = pd.read_csv(path_to_keys)
        consumer_key = keys['consumer_key'][0]
        consumer_secret = keys['consumer_secret'][0]
        access_token = keys['access_token'][0]
        access_token_secret = keys['access_token_secret'][0]
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # open topic_tweets.csv file that we will be modifying
        self.topic = topic
        try:
            self.tweets_df = pd.read_csv("{}_tweets.csv".format(topic), index_col='tweet_id')

        except FileNotFoundError:
            self.tweets_df = pd.DataFrame(columns=features)
            self.tweets_df.index.name = 'tweet_id'

    def collect_tweets(self, queries: list, options: list = None):
        # TODO
        return None