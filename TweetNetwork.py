import pandas as pd
import numpy as np
import math
from textblob import TextBlob
from scipy import spatial


class TweetNetwork:

    def __init__(self, topic: str):
        self.topic = topic
        self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')
        self.node_tweet_id_map = dict(enumerate(self.tweets_df.index))
        self.adj = None
        self.tweet_binary_feature_matrix = pd.DataFrame(index=self.tweets_df.index)
        self.tweet_sentiment_adj = None

    def build_and_write_network(self) -> None:
        # self._connect_followers_and_friends()
        hashtag_df = self._generate_hashtag_data_frame()
        self._generate_sentiment_data_frame()
        self.tweet_binary_feature_matrix = pd.concat([hashtag_df], axis=1)
        self._calc_similarity()
        self.adj.to_csv('{}_network.csv'.format(self.topic))

    def _calc_similarity(self) -> None:
        """
        Calculates the cosine similarity between two tweets in the matrix.
        :return: None
        """

        # Calculate the cosine similarity of the binary features of the tweets
        binary_feature_adj = pd.DataFrame(np.zeros((self.tweets_df.shape[0], self.tweets_df.shape[0])),
                                          index=self.tweets_df.index, columns=self.tweets_df.index)

        tweet_ids = self.tweets_df.index.values
        while tweet_ids.shape[0] != 0:
            tweet_id_i = tweet_ids[0]
            tweet_ids = np.delete(tweet_ids, 0)
            for tweet_id_j in tweet_ids:
                binary_feature_adj.loc[tweet_id_i, tweet_id_j] = 1 - spatial.distance.cosine(
                    self.tweet_binary_feature_matrix.loc[tweet_id_i, :],
                    self.tweet_binary_feature_matrix.loc[tweet_id_j, :])
                binary_feature_adj.loc[tweet_id_j, tweet_id_i] = binary_feature_adj.loc[tweet_id_i, tweet_id_j]

        binary_feature_adj = binary_feature_adj.fillna(0)

        # Calculate the projection of the Binary feature similarity and the sentiment similarity of two tweets onto the
        # ideal, i.e. add the two up and divide by sqrt(2)
        self.adj = (binary_feature_adj + self.tweet_sentiment_adj) / (2 ** 0.5)

    def get_node_tweet_id_map(self) -> dict:
        return self.node_tweet_id_map

    def get_adj_list(self):
        return self.adj.values.tolist()

    def _connect_followers_and_friends(self) -> None:
        for idx in self.tweets_df.index:
            followers_arr = np.fromstring(self.tweets_df.loc[idx, 'followers'], sep=',')
            friends_arr = np.fromstring(self.tweets_df.loc[idx, 'friends'], sep=',')

            followers_series = pd.Series(1, index=followers_arr).reindex(self.tweets_df.index, fill_value=0)
            friends_series = pd.Series(1, index=friends_arr).reindex(self.tweets_df.index, fill_value=0)

            self.adj.loc[:, idx] = self.adj.loc[:, idx] + followers_series
            self.adj.loc[:, idx] = self.adj.loc[:, idx] + friends_series

    def _generate_sentiment_data_frame(self) -> None:
        """
        Helper method for build_and_write_network(). Adds edges based on how similar their sentiment is
        :return:
        """
        sentiment_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], 1)), index=self.tweets_df.index,
                                           columns=['sentiment'])

        self.tweet_sentiment_adj = pd.DataFrame(np.zeros((self.tweets_df.shape[0], self.tweets_df.shape[0])),
                                                index=self.tweets_df.index, columns=self.tweets_df.index)

        def calc_sentiment(tweet_text):
            tweet_text_blob = TextBlob(tweet_text)
            return tweet_text_blob.sentiment.polarity

        sentiment_dataframe.loc[:, 'sentiment'] = self.tweets_df.loc[:, 'text'].apply(calc_sentiment)

        for tweet_id_i in self.tweets_df.index:
            for tweet_id_j in self.tweets_df.index:
                if tweet_id_i != tweet_id_j:
                    self.tweet_sentiment_adj.loc[tweet_id_i, tweet_id_j] = math.e ** (
                            (-2) * ((sentiment_dataframe.loc[tweet_id_i, 'sentiment']
                                     - sentiment_dataframe.loc[tweet_id_j, 'sentiment']) ** 2))


        # negative_sentiment_df = sentiment_dataframe[sentiment_dataframe.loc[:, 'sentiment'] < 0].reindex(
        #     sentiment_dataframe.index, fill_value=0)
        #
        # negative_sentiment_df.columns = ['negative_sentiment']
        #
        # negative_sentiment_df.loc[:, 'negative_sentiment'] = negative_sentiment_df.loc[:, 'negative_sentiment'].abs()
        #
        # positive_sentiment_df = sentiment_dataframe[sentiment_dataframe.loc[:, 'sentiment'] > 0].reindex(
        #     sentiment_dataframe.index, fill_value=0)
        #
        # positive_sentiment_df.columns = ['positive_sentiment']
        #
        # negative_sentiment_df[sentiment_dataframe.loc[:, 'sentiment'] == 0] = 0.25
        # positive_sentiment_df[sentiment_dataframe.loc[:, 'sentiment'] == 0] = 0.25
        #
        # sentiment_dataframe = pd.concat([negative_sentiment_df, positive_sentiment_df], join='outer', axis='columns')

        # return sentiment_dataframe

    def _generate_hashtag_data_frame(self) -> pd.DataFrame:
        """
        helper method for build_and_write_network(). adds edges based on the number of similar hashtags shared by two
        tweets
        :return:
        """

        # create dictionary of hashtags
        hashtags_by_user = {}
        for tweet_id in self.tweets_df.index:
            hashtags_by_user[tweet_id] = np.array([h['text']
                                                   for h in eval(self.tweets_df.loc[tweet_id, 'entities'])['hashtags']])

        hashtag_list = list(set(list(np.concatenate(list(hashtags_by_user.values())))))

        hashtag_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], len(hashtag_list))),
                                      index=self.tweets_df.index, columns=hashtag_list)

        for tweet_id in self.tweets_df.index:
            hashtag_arr = np.array(hashtags_by_user[tweet_id])
            hashtag_series = pd.Series(1, index=hashtag_arr).reindex(hashtag_list, fill_value=0)
            hashtag_dataframe.loc[tweet_id, :] = hashtag_series

        return hashtag_dataframe


