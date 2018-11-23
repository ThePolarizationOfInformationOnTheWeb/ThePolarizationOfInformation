import pandas as pd
import numpy as np
import math
import sys
from TweetFeatureExtractor import TweetFeatureExtractor
from scipy import spatial


class TweetNetwork:

    def __init__(self, topic: str):
        self.topic = topic
        self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')
        self.feature_extractor = TweetFeatureExtractor(self.topic)
        self.hashtag_sentiments_df = None
        self.node_tweet_id_map = dict(enumerate(self.tweets_df.index))
        self.adj = None
        self.tweet_binary_feature_matrix = pd.DataFrame(index=self.tweets_df.index)
        self.tweet_sentiment_adj = None

    def build_and_write_network(self, method: str = 'kmeans_update',
                                ideal_radians_from_sentiment: float = math.pi / 4) -> None:
        """
        builds and writes network of weighted edges to <topic>_network.csv file
        :param method: 'kmeans_update' for dynamic weighting of edges using the weighted kmeans update
                        'binary_and_sentiment' for considering a single pass considering only binary features and
                        sentiment
        :param ideal_radians_from_sentiment: for 'binary_and_sentiment' method
        :return:
        """
        if method == 'kmeans_update':
            try:
                self.hashtag_sentiments_df = pd.read_csv("TweetNetwork: {}_hashtag_sentiments.csv".format(self.topic),
                                                         index_col='hashtag')

            except FileNotFoundError:
                print("TweetNetwork: {}_hashtag_sentiments.csv does not exist.".format(self.topic))
                print("TweetNetwork: Use hashtag_sentiment.py script to generate empty {}_hashtag_sentiments.csv file "
                      "and then manually label hashtags using excel or whatever editor you like most, "
                      "and... good luck".format(self.topic))
                sys.exit()

            if self.hashtag_sentiments_df['sentiment'].isnull().sum() > 0:
                print("TweetNetwork: {}_hashtag_sentiments.csv exists but "
                      "is not completely filled yet".format(self.topic))
                sys.exit()

        elif method == 'binary_and_sentiment':
            hashtag_df = self.feature_extractor.get_hashtag_dataframe()
            mentions_df = self.feature_extractor.get_mentions_dataframe()
            self.feature_extractor.get_sentiment_dataframe()
            self.tweet_binary_feature_matrix = pd.concat([hashtag_df, mentions_df], axis=1)
            self._calc_similarity(ideal_radians_from_sentiment=ideal_radians_from_sentiment)
            self.adj.to_csv('{}_network.csv'.format(self.topic))

        else:
            print('TweetNetwork: Method {} not implemented'.format(method))
            sys.exit()

    def _calc_similarity(self, ideal_radians_from_sentiment: float = math.pi / 4) -> None:
        """
        Calculates the cosine similarity between two tweets in the matrix.
        :param ideal_radians_from_sentiment: between -pi / 4 to 3pi/4, pi/4 is the vector [1,1], i.e.
                                             equal weight to both binary and sentiment
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
        # ideal
        magnitude = ((math.sqrt(2) * math.cos(ideal_radians_from_sentiment) + 0.5) ** 2 +
                     (math.sqrt(2) * math.sin(ideal_radians_from_sentiment) + 0.5) ** 2) ** 1/2
        sentiment_coeff = magnitude * math.cos(ideal_radians_from_sentiment)
        binary_coeff = magnitude * math.sin(ideal_radians_from_sentiment)

        self.adj = (binary_coeff * binary_feature_adj + sentiment_coeff * self.tweet_sentiment_adj) / magnitude

    def get_node_tweet_id_map(self) -> dict:
        return self.node_tweet_id_map

    def get_adj_list(self):
        return self.adj.values.tolist()

