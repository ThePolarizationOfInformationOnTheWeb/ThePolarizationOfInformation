import pandas as pd
import numpy as np
import math
import sys
from Clusterer import Clusterer
from TweetFeatureExtractor import TweetFeatureExtractor
from scipy import spatial


class TweetNetwork:

    def __init__(self, topic: str):
        self.topic = topic
        self.tweets_df = pd.read_csv("{}_tweets.csv".format(self.topic), index_col='id')
        self.feature_extractor = TweetFeatureExtractor(self.topic)
        self.node_id_map = pd.Series(dict(zip(list(range(self.tweets_df.shape[0])), self.tweets_df.index.tolist())))
        self.clusterer = None
        self.hashtag_sentiments_df = None
        self.adj = pd.DataFrame(index=self.tweets_df.index, columns=self.tweets_df.index)
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

            iteration_count = 1

            tweet_cluster_assignment_df = pd.DataFrame(index=self.tweets_df.index)
            tweet_cluster_assignment_df['cluster_0'] = list(range(self.tweets_df.shape[0]))

            # initially every node is in its own cluster
            clustering = [[i] for i in range(self.tweets_df.index.size)]
            tweet_cluster_vector_df = self._calc_tweet_cluster_vector_df(clustering)

            self.adj = self._calc_cosine_similarity_matrix(tweet_cluster_vector_df)

            # initialize clusterer class with network
            self.clusterer = Clusterer(self.topic, network_df=self.adj)
            self.clusterer.backward_path()

            while iteration_count < 100:
                clustering = self.clusterer.get_clustering(method='coarsest')

                tweet_cluster_assignment_df['cluster_{}'.format(iteration_count)] = 0

                for i in range(len(clustering)):
                    tweet_cluster_assignment_df.loc[self.node_id_map[clustering[i]].values,
                                                    'cluster_{}'.format(iteration_count)] = i

                if ((tweet_cluster_assignment_df['cluster_{}'.format(iteration_count - 1)].values ==
                        tweet_cluster_assignment_df['cluster_{}'.format(iteration_count)].values).all()):
                    break

                tweet_cluster_vector_df = self._calc_tweet_cluster_vector_df(clustering)
                self.adj = self._calc_cosine_similarity_matrix(tweet_cluster_vector_df)

                # update clusterer
                self.clusterer.update_network(self.adj)
                self.clusterer.backward_path()

                iteration_count = iteration_count + 1

            print(iteration_count)

            # write network to .csv file
            self.adj.to_csv('{}_network.csv'.format(self.topic))

            # write cluster evolution to .csv file
            tweet_cluster_assignment_df.to_csv('{}_cluster_evolution.csv'.format(self.topic))

        elif method == 'binary_and_sentiment':
            hashtag_df = self.feature_extractor.get_hashtag_dataframe()
            mentions_df = self.feature_extractor.get_mentions_dataframe()
            self.tweet_sentiment_adj = self.feature_extractor.get_sentiment_dataframe()
            self.tweet_binary_feature_matrix = pd.concat([hashtag_df, mentions_df], axis=1)
            self._calc_similarity(ideal_radians_from_sentiment=ideal_radians_from_sentiment)
            self.adj.to_csv('{}_network.csv'.format(self.topic))

        else:
            print('TweetNetwork: Method {} not implemented'.format(method))
            sys.exit()

    @staticmethod
    def _calc_cosine_similarity_matrix(cluster_vector_df):

        def normalize_vector(vector):
            magnitude = np.dot(vector, vector) ** (1 / 2)
            if magnitude == 0:
                return vector
            else:
                return vector / magnitude

        # normalize each vector in the cluster_vector_df
        vector_df = cluster_vector_df.apply(normalize_vector)
        return (pd.DataFrame(np.matmul(np.stack(vector_df.values), np.stack(vector_df.values).T),
                             index=vector_df.index, columns=vector_df.index))

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

    def _calc_tweet_cluster_vector_df(self, clustering) -> pd.DataFrame:
        hashtag_df = self.feature_extractor.get_hashtag_dataframe()
        hashtag_frequency_series = self.feature_extractor.get_hashtag_frequency_series()
        tweet_vector_df = pd.DataFrame(index=hashtag_df.index, columns=['vector'])
        tweet_vector_df['vector'] = hashtag_df.index

        hashtag_df['cluster'] = 0

        for i in range(len(clustering)):
            hashtag_df.loc[self.node_id_map[clustering[i]].values, 'cluster'] = i

        cluster_hashtag_frequency_df = hashtag_df.groupby('cluster').agg('sum') / hashtag_frequency_series

        def vector_calc(tweet_id):
            hashtag_set = hashtag_df.drop('cluster', axis='columns').loc[tweet_id, :]
            hashtag_set = hashtag_set.loc[:, (hashtag_set != 0).any(axis='rows')].columns.values
            if len(hashtag_set) == 0:
                return np.zeros(len(clustering))
            vector = cluster_hashtag_frequency_df.loc[:, hashtag_set].dot(1 / hashtag_frequency_series[
                hashtag_set]).values
            return vector / (1 / hashtag_frequency_series[hashtag_set]).sum()

        return tweet_vector_df.apply(vector_calc, axis='columns')

    def get_adj_list(self):
        return self.adj.values.tolist()

