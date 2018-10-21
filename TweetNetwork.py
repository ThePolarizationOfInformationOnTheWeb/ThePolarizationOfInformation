import pandas as pd
import numpy as np


class TweetNetwork:

    def __init__(self, topic: str):
        self.topic = topic
        self.tweets_df = pd.read_csv("{}_tweets.csv".format(topic), index_col='tweet_id')
        self.node_tweet_id_map = dict(enumerate(self.tweets_df.index))
        self.adj = pd.DataFrame(np.zeros((self.tweets_df.shape[0], self.tweets_df.shape[0])),
                                index=self.tweets_df.index, columns=self.tweets_df.index)

    def build_and_write_network(self) -> None:
        ##self._connect_followers_and_friends()
        self.adj.to_csv('{}_network.csv'.format(self.topic))

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
