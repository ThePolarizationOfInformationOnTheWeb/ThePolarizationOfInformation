import pandas as pd
import numpy as np
from TweetFeatureExtractor import TweetFeatureExtractor
from BackwardPath import back_path_clustering, transval


class Clusterer:

    def __init__(self, topic: str, network_df: pd.DataFrame = None):

        if network_df is None:
            network_df = pd.read_csv('{}_network.csv'.format(topic), index_col='id')

        self.topic = topic
        self.weighted_adj_matrix = network_df.values.tolist()
        self.node_id_map = pd.Series(dict(zip(list(range(network_df.shape[0])), network_df.index.tolist())))
        self.feature_extractor = TweetFeatureExtractor(self.topic)
        self.clusterings = None
        self.back_path_critical_times = None

    def update_network(self, new_network_df: pd.DataFrame):
        self.weighted_adj_matrix = new_network_df.values.tolist()
        self.node_id_map = pd.Series(dict(zip(list(range(new_network_df.shape[0])), new_network_df.index.tolist())))

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
            hashtag_df = self.feature_extractor.get_hashtag_dataframe()
            hashtag_sentiment_df = self.feature_extractor.get_hashtag_sentiment_dataframe()

            def contrasting_sentiment(h_tag_list):
                """
                Helper for apply() method
                :param h_tag_list:
                :return: Boolean indicating if there are contrasting polarity hashtags in the h_tag list
                """
                return np.diff(np.signbit(hashtag_sentiment_df.loc[h_tag_list, 'polarity'].values[
                                              hashtag_sentiment_df.loc[h_tag_list, 'polarity'].values.nonzero()])
                               ).sum() != 0

            for i in np.arange(len(self.clusterings) - 1, -1, -1):
                hashtag_sets = pd.Series(name='hashtags', data=np.NaN, index=np.arange(len(self.clusterings[i])))
                for j in range(len(self.clusterings[i])):
                    # hashtag_sets is a series holding the sets of all hashtags for each group
                    hashtag_sets[j] = hashtag_df.columns[
                        hashtag_df.loc[self.node_id_map[self.clusterings[i][j]].values, :].any(axis='rows')].values

                if not np.any(hashtag_sets.apply(contrasting_sentiment).values):
                    return self.clusterings[i]

            print("Couldn't find a coarse clustering without contrasting sentiments within the same cluster. Returning "
                  "the first clustering")
            return self.clusterings[0]






