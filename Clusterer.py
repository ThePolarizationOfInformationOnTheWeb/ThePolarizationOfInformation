import pandas as pd
from TweetFeatureExtractor import TweetFeatureExtractor
from BackwardPath import back_path_clustering, transval


class Clusterer:
    weighted_adj_matrix = []  # adj_matrix[i][j] = directed edge weight from node i to node j

    def __init__(self, topic: str):
        network_df = pd.read_csv('{}_network.csv'.format(topic), index_col='id')
        self.topic = topic
        self.weighted_adj_matrix = network_df.values.tolist()
        self.node_id_map = dict(zip(network_df.index.tolist(), list(range(network_df.shape[0]))))
        self.feature_extractor = TweetFeatureExtractor(self.topic)
        self.clusterings = None
        self.back_path_critical_times = None

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
        :return: kmeans_update: Coarsest clustering, that is s.t. no cluster has contrasting sentiment hashtags
        (to be refined to allow some error)
                binary_and_sentiment: return first one for now, tbd.
        """
        if self.method == 'first':
            return self.clusterings[0]

        elif self.method == 'coarsest':
            for cluster in self.clusterings:
                hashtag_sets =
                hashtag_sentiments = self.hashtag_sentiments_df[]
