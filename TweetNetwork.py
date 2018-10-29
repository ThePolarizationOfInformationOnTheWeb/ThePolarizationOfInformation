import pandas as pd
import numpy as np
import textblob
from scipy import spatial


class TweetNetwork:

    def __init__(self, topic: str):
        self.topic = topic
        self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')
        self.node_tweet_id_map = dict(enumerate(self.tweets_df.index))
        self.adj = pd.DataFrame(np.zeros((self.tweets_df.shape[0], self.tweets_df.shape[0])),
                                index=self.tweets_df.index, columns=self.tweets_df.index)
        self.tweet_feature_matrix = pd.DataFrame(index=self.tweets_df.index)

    def build_and_write_network(self) -> None:
        # self._connect_followers_and_friends()
        hashtag_data_frame = self._generate_hashtag_data_frame()
        self.tweet_feature_matrix = pd.concat([hashtag_data_frame], axis=1)
        self._calc_cosine_similarity()
        self.adj.to_csv('{}_network.csv'.format(self.topic))

    def _calc_cosine_similarity(self) -> None:
        """
        Calculates the cosine similarity between two tweets in the matrix
        :return: None
        """

        tweet_ids = self.adj.index.values

        while tweet_ids.shape[0] != 0:
            tweet_id_i = tweet_ids[0]
            tweet_ids = np.delete(tweet_ids, 0)
            for tweet_id_j in tweet_ids:
                self.adj.loc[tweet_id_i, tweet_id_j] = 1 - spatial.distance.cosine(
                    self.tweet_feature_matrix.loc[tweet_id_i, :], self.tweet_feature_matrix.loc[tweet_id_j, :])
                self.adj.loc[tweet_id_j, tweet_id_i] = self.adj.loc[tweet_id_i, tweet_id_j]

        self.adj = self.adj.fillna(0)

    def get_node_tweet_id_map(self) -> dict:
        return self.node_tweet_id_map

    def get_adj_list(self):
        return self.adj.values.tolist()

    def _connect_followers_and_friends(self) -> None:
        for idx in self.adj.index:
            followers_arr = np.fromstring(self.tweets_df.loc[idx, 'followers'], sep=',')
            friends_arr = np.fromstring(self.tweets_df.loc[idx, 'friends'], sep=',')

            followers_series = pd.Series(1, index=followers_arr).reindex(self.adj.index, fill_value=0)
            friends_series = pd.Series(1, index=friends_arr).reindex(self.adj.index, fill_value=0)

            self.adj.loc[:, idx] = self.adj.loc[:, idx] + followers_series
            self.adj.loc[:, idx] = self.adj.loc[:, idx] + friends_series

    def _connect_sentiment(self) -> None:
        """
        Helper method for build_and_write_network(). Adds edges based on how similar their sentiment is
        :return:
        """

    def _generate_hashtag_data_frame(self) -> pd.DataFrame:
        """
        helper method for build_and_write_network(). adds edges based on the number of similar hashtags shared by two
        tweets
        :return:
        """

        # 1st pass to create dictionary of hashtags
        hashtags_by_user = {}
        for tweet_id in self.adj.index:
            hashtags_by_user[tweet_id] = np.array([h['text']
                                                   for h in eval(self.tweets_df.loc[tweet_id, 'entities'])['hashtags']])

        hashtag_list = list(set(list(np.concatenate(list(hashtags_by_user.values())))))

        hashtag_dataframe = pd.DataFrame(np.zeros((self.tweets_df.shape[0], len(hashtag_list))),
                                      index=self.tweets_df.index, columns=hashtag_list)

        for tweet_id in self.adj.index:
            hashtag_arr = np.array(hashtags_by_user[tweet_id])
            hashtag_series = pd.Series(1, index=hashtag_arr).reindex(hashtag_list, fill_value=0)
            hashtag_dataframe.loc[tweet_id, :] = hashtag_series

        return hashtag_dataframe


