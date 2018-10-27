import tweepy
import pandas as pd
import datetime
from searchtweets import ResultStream, gen_rule_payload, load_credentials

# write these in a config file: TODO
features = ['user_id', 'username', 'text', 'friends']

class tweet_collector:

    def __init__(self, topic: str, path_to_keys: str = './keys.csv'):
        # # set up access to API

        self.premium_search_args = load_credentials("./twitter_keys.yaml",
                                               yaml_key="search_tweets_premium",
                                               env_overwrite=False)

        # keys = pd.read_csv(path_to_keys)
        # consumer_key = keys['consumer_key'][0]
        # consumer_secret = keys['consumer_secret'][0]
        # access_token = keys['access_token'][0]
        # access_token_secret = keys['access_token_secret'][0]
        # self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # self.auth.set_access_token(access_token, access_token_secret)
        # self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        #
        # # open topic_tweets.csv file that we will be modifying
        # self.topic = topic
        # try:
        #     self.tweets_df = pd.read_csv("{}_tweets.csv".format(topic), index_col='tweet_id')
        #
        # except FileNotFoundError:
        #     self.tweets_df = pd.DataFrame(columns=features)
        #     self.tweets_df.index.name = 'tweet_id'

    def collect_tweets(self, query: str, results_per_call: int = 100, num_tweets: int = 100,
                       from_date: datetime.date = None, to_date: datetime.date = None, has_hashtags: bool = False):
        """
        :param queries:
        :param num_tweets:
        :param from_date:
        :param to_date:
        :return:
        """

        if has_hashtags:
            query = "{} has:hashtags".format(query)

        rule = gen_rule_payload(query, results_per_call=results_per_call, from_date=from_date.isoformat(), to_date=to_date.isoformat())

        return None



