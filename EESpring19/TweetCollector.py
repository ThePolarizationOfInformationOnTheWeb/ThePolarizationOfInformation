import pandas as pd
import datetime
from searchtweets import gen_rule_payload, load_credentials, collect_results


class TweetCollector:

    def __init__(self, topic: str, path_to_keys: str = './keys/twitter_keys.yaml'):
        # set up access to API
        self.premium_search_args = load_credentials(path_to_keys, yaml_key="search_tweets_premium", env_overwrite=False)
        self.topic = topic

        # open topic_tweets.csv file that we will be modifying
        self.topic = topic
        try:
            self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')

        except FileNotFoundError:
            self.tweets_df = pd.DataFrame()

    def collect_and_write_tweets(self, query: str, results_per_call: int = 100, num_tweets: int = 100,
                                 from_date: datetime.date = None, to_date: datetime.date = None):
        """
        :param query:
        :param results_per_call
        :param num_tweets:
        :param from_date:
        :param to_date:
        :return:
        """

        if results_per_call > 100:
            print("Sandbox API limited to 100 results per request, cannot retrieve {} results".format(results_per_call))

        rule = gen_rule_payload(query, results_per_call=results_per_call, from_date=from_date.isoformat(),
                                to_date=to_date.isoformat())

        tweets = collect_results(rule, max_results=num_tweets, result_stream_args=self.premium_search_args)

        # cast tweet objects to dict and create pandas data frame
        tweets_dict_list = [dict(tweet) for tweet in tweets]
        tweets_df = pd.DataFrame(tweets_dict_list)
        tweets_df.index = tweets_df.id

        try:
            # write new data set to .csv file without duplicates
            self.tweets_df = pd.concat([self.tweets_df, tweets_df], axis=0, join='outer')
            self.tweets_df = self.tweets_df[~self.tweets_df.index.duplicated()]
            self.tweets_df.to_csv("{}_tweets.csv".format(self.topic))
        except:
            # save backup of collected tweets
            tweets_df.to_csv("{}_{}_{}_backup_tweets.csv".format(self.topic, datetime.datetime.now().date(),
                                                                 datetime.datetime.now().time()))
