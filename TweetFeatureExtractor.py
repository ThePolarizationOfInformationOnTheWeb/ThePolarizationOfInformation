import pandas as pd
import numpy as np
import math
import re
import sys
from textblob import TextBlob


class TweetFeatureExtractor:

    def __init__(self, topic: str, tweets_df: pd.DataFrame = None):
        self.topic = topic
        if tweets_df is None:
            try:
                self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')
            except FileNotFoundError:
                print("File: {}_tweets.csv was not found. Use TweetCollector to generate this file".format(self.topic))
                sys.exit(0)
        else:
            self.tweets_df = tweets_df
        self.mentions_dataframe = None
        self.sentiment_dataframe = None
        self.hashtag_dataframe = None
        self.tweet_sentiment_adj = None
        self.hashtag_sentiment_dataframe = None
        self.hashtag_frequency_series = None
        self.tweets_with_hashtags_dataframe = None

    def _generate_mentions_dataframe(self):
        """
        helper method for get_mentions_dataframe.
        """

        # create dictionary of mentions
        mentions_by_user = {}
        for tweet_id in self.tweets_df.index:
            mentions_by_user[tweet_id] = np.array([h['screen_name']
                                                   for h in eval(self.tweets_df.loc[tweet_id, 'entities'])
                                                   ['user_mentions']])

        mentions_list = list(set(list(np.concatenate(list(mentions_by_user.values())))))

        self.mentions_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], len(mentions_list))),
                                               index=self.tweets_df.index, columns=mentions_list)

        for tweet_id in self.tweets_df.index:
            mentions_arr = np.array(mentions_by_user[tweet_id])
            mentions_series = pd.Series(1, index=mentions_arr).reindex(mentions_list, fill_value=0)
            self.mentions_dataframe.loc[tweet_id, :] = mentions_series

    def get_mentions_dataframe(self) -> pd.DataFrame:
        if self.mentions_dataframe is None:
            self._generate_mentions_dataframe()

        return self.mentions_dataframe

    def _generate_sentiment_dataframe(self) -> None:
        """
        Helper method for get_sentiment_data_frame. Adds edges based on how similar their sentiment is
        :return:
        """
        self.sentiment_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], 1)), index=self.tweets_df.index,
                                                columns=['sentiment'])

        self.tweet_sentiment_adj = pd.DataFrame(np.zeros((self.tweets_df.shape[0], self.tweets_df.shape[0])),
                                                index=self.tweets_df.index, columns=self.tweets_df.index)

        def calc_sentiment(tweet_text):
            tweet_text_blob = TextBlob(tweet_text)
            return tweet_text_blob.sentiment.polarity

        self.sentiment_dataframe.loc[:, 'sentiment'] = self.tweets_df.loc[:, 'text'].apply(calc_sentiment)

        for tweet_id_i in self.tweets_df.index:
            for tweet_id_j in self.tweets_df.index:
                if tweet_id_i != tweet_id_j:
                    self.tweet_sentiment_adj.loc[tweet_id_i, tweet_id_j] = math.e ** (
                            (-2) * ((self.sentiment_dataframe.loc[tweet_id_i, 'sentiment']
                                     - self.sentiment_dataframe.loc[tweet_id_j, 'sentiment']) ** 2))

    def get_sentiment_dataframe(self) -> pd.DataFrame:
        if self.sentiment_dataframe is None:
            self._generate_sentiment_dataframe()

        return self.sentiment_dataframe

    def _generate_hashtag_dataframe(self) -> None:
        """
        helper method for build_and_write_network().
        :return: hashtag_dataframe: pandas DataFrame where entry h_ij = 1 if tweet_i contains hashtag_j
        """

        no_hashtag = 0

        # create dictionary of hashtags
        hashtags_by_tweet = {}
        for tweet_id in self.tweets_df.index:
            # hastags from tweet text
            hashtags_by_tweet[tweet_id] = [h_tag.lower() for h_tag in np.array([h['text'] for h in eval(
                self.tweets_df.loc[tweet_id, 'entities'])['hashtags']])]

            # # hashtags from user descriptions
            # description = eval(self.tweets_df.loc[tweet_id, 'user'])['description']
            # if description is not None:
            #     hashtags_by_tweet[tweet_id] = np.append(
            #         hashtags_by_tweet[tweet_id], [h_tag.lower() for h_tag in re.findall(r"#(\w+)", description)])

            # ensure no duplicates for each tweet
            hashtags_by_tweet[tweet_id] = list(set(hashtags_by_tweet[tweet_id]))
            if len(hashtags_by_tweet[tweet_id]) == 0:
                no_hashtag = no_hashtag + 1

        print("Number of tweets without hashtags: {}".format(no_hashtag))
        print("Number of tweets: {}".format(len(hashtags_by_tweet)))

        hashtag_list = list(set(list(np.concatenate(list(hashtags_by_tweet.values())))))

        self.hashtag_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], len(hashtag_list))),
                                              index=self.tweets_df.index, columns=hashtag_list)

        for tweet_id in self.tweets_df.index:
            hashtag_arr = np.array(hashtags_by_tweet[tweet_id])
            hashtag_series = pd.Series(1, index=hashtag_arr).reindex(hashtag_list, fill_value=0)
            self.hashtag_dataframe.loc[tweet_id, :] = hashtag_series

        return self.hashtag_dataframe

    def get_hashtag_dataframe(self) -> pd.DataFrame:
        if self.hashtag_dataframe is None:
            self._generate_hashtag_dataframe()

        return self.hashtag_dataframe

    def get_hashtag_sentiment_dataframe(self) -> pd.DataFrame:
        if self.hashtag_sentiment_dataframe is None:
            try:
                self.hashtag_sentiment_dataframe = pd.read_csv("{}_hashtag_sentiments.csv".format(self.topic),
                                                               index_col='hashtag')

            except FileNotFoundError:
                print("TweetNetwork: {}_hashtag_sentiments.csv does not exist.".format(self.topic))
                print("TweetNetwork: Use hashtag_sentiment.py script to generate empty {}_hashtag_sentiments.csv file "
                      "and then manually label hashtags using excel or whatever editor you like most, "
                      "and... good luck".format(self.topic))
                sys.exit()

            if (self.hashtag_sentiment_dataframe['left'].isnull().sum() > 0 or
                    self.hashtag_sentiment_dataframe['right'].isnull().sum() > 0):
                print("TweetNetwork: {}_hashtag_sentiments.csv exists but "
                      "is not completely filled yet".format(self.topic))
                sys.exit()

            self.hashtag_sentiment_dataframe['polarity'] = (self.hashtag_sentiment_dataframe['right']
                                                            - self.hashtag_sentiment_dataframe['left'])
        return self.hashtag_sentiment_dataframe[['polarity']]

    def get_hashtag_frequency_series(self) -> pd.DataFrame:
        if self.hashtag_frequency_series is None:
            if self.hashtag_dataframe is None:
                self._generate_hashtag_dataframe()

            self.hashtag_frequency_series = self.hashtag_dataframe.sum(axis='rows')


        return self.hashtag_frequency_series

    def get_tweets_with_hashtags(self) -> pd.DataFrame:
        if self.hashtag_dataframe is None:
            self._generate_hashtag_dataframe()

        if self.tweets_with_hashtags_dataframe is None:
            hashtagged_tweets = self.hashtag_dataframe[(self.hashtag_dataframe.T != 0).any()].index

            self.tweets_with_hashtags_dataframe = self.tweets_df.loc[hashtagged_tweets, :]

        return self.tweets_with_hashtags_dataframe