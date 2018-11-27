import pandas as pd
import numpy as np
from TweetFeatureExtractor import TweetFeatureExtractor
from BackwardPath import back_path_clustering, transval


class Clusterer:

    def __init__(self, topic: str, network_df: pd.DataFrame = None, node_id_map: pd.Series = None,
                 feature_extractor: TweetFeatureExtractor = None):

        if network_df is None:
            network_df = pd.read_csv('{}_network.csv'.format(topic), index_col='id')

        self.topic = topic
        self.weighted_adj_matrix = network_df.values.tolist()

        if node_id_map is None:
            self.node_id_map = pd.Series(dict(zip(list(range(network_df.shape[0])), network_df.index.tolist())))
        else:
            self.node_id_map = node_id_map

        if feature_extractor is None:
            self.feature_extractor = TweetFeatureExtractor(self.topic)
        else:
            self.feature_extractor = feature_extractor

        self.clusterings = None
        self.back_path_critical_times = None

    def update_network(self, new_network_df: pd.DataFrame, node_id_map: pd.Series = None):
        self.weighted_adj_matrix = new_network_df.values.tolist()
        if node_id_map is None:
            self.node_id_map = pd.Series(dict(zip(list(range(new_network_df.shape[0])), new_network_df.index.tolist())))
        else:
            self.node_id_map = node_id_map

    def backward_path(self):
        TranList, TranCumul = transval(self.weighted_adj_matrix)
        # update so adj is unweighted, for BackwardPath alg
        adj = [[1 if self.weighted_adj_matrix[i][j] > 0 else 0 for j in range(len(self.weighted_adj_matrix))]
               for i in range(len(self.weighted_adj_matrix))]
        self.clusterings, self.back_path_critical_times = back_path_clustering(adj, TranList, TranCumul)

    def get_weighted_adj(self):
        return self.weighted_adj_matrix

    def get_node_id_map(self):
        return self.node_id_map

    def get_clustering(self, method: str ='coarsest'):
        """
        :param method:
        :return: coarsest: Coarsest clustering, that is s.t. no cluster has contrasting sentiment hashtags
        (to be refined to allow some error)
                first: return first one
        """
        if method == 'first':
            return self.clusterings[0]

        elif method == 'all':
            return self.clusterings

        elif method == 'coarsest':
            tweet_hashtag_sentiment_df = self.feature_extractor.get_tweet_hashtag_sentiment_series()

            # print(tweet_hashtag_sentiment_df)

            def contrasting_sentiment(h_tag_sentiment_list):
                """
                Helper for apply() method
                :param h_tag_list:
                :return: Boolean indicating if there are contrasting polarity hashtags in the h_tag list
                """
                # print(h_tag_sentiment_list)
                return np.diff(np.signbit(h_tag_sentiment_list)).sum() != 0

            for i in np.arange(len(self.clusterings) - 1, -1, -1):
                tweet_hashtag_sentiment_sets = pd.DataFrame(index=np.arange(len(self.clusterings[i])),
                                                            columns=['tweets'])
                for j in range(len(self.clusterings[i])):
                    # tweet_hashtag_sentiment_sets is a series holding the sets of all tweet sentiments for each group
                    # print(self.node_id_map[self.clusterings[i][j]].values)
                    tweet_hashtag_sentiment_sets.loc[j, 'tweets'] = tweet_hashtag_sentiment_df.loc[self.node_id_map[self.clusterings[i][j]].values].values

                if not np.any(tweet_hashtag_sentiment_sets['tweets'].apply(contrasting_sentiment).values):
                    return self.clusterings[i]

            print("Couldn't find a coarse clustering without contrasting sentiments within the same cluster. Returning "
                  "the first clustering")
            return self.clusterings[0]






