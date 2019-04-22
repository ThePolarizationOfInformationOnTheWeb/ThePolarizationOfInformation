import pandas as pd
import numpy as np
import igraph
from EESpring19.BackwardPath import back_path_clustering, transval


class Clusterer:

    def __init__(self, network_df: pd.DataFrame):
        """
        Initialize clusterer instance
        :param network_df: The DataFrame that holds the adjacency matrix
        """
        self.adj = network_df.values
        self.node_id_map = pd.Series(dict(zip(list(range(network_df.shape[0])), network_df.index.tolist())))
        self.clusterings = None
        self.back_path_critical_times = None

    def update_network(self, new_network_df) -> None:
        """
        Reinitialize the clusterer instance with new adjacency matrix
        :param new_network_df: The new adjacency matrix
        """
        self.adj = new_network_df.values
        self.node_id_map = pd.Series(dict(zip(list(range(new_network_df.shape[0])), new_network_df.index.tolist())))
        self.clusterings = None
        self.back_path_critical_times = None

    def get_clustering(self, clusterMethod: str='backward_path', selectionMethod: str='first')->np.array:
        """
        :param method: Clustering method to be used. Default is the backward path algorithm
        :return: An np.array of the clusterings. An array of arrays containing ids
        """
        if self.clusterings is None:
            if clusterMethod is 'backward_path':
                TranList, TranCumul = transval(self.adj)
                # update so adj is unweighted, for BackwardPath alg
                adj = [[1 if self.adj[i][j] > 0 else 0 for j in range(len(self.adj))]
                       for i in range(len(self.adj))]
                self.clusterings, self.back_path_critical_times = back_path_clustering(adj, TranList, TranCumul)

            if clusterMethod is 'label_propagation':
                g = igraph.Graph.Weighted_Adjacency(self.adj.tolist(), mode='UNDIRECTED')
                self.clusterings = np.array([np.array(c) for c in g.community_label_propagation(weights='weight')])

        if (clusterMethod is 'backward_path') and (selectionMethod is 'first'):
            return self.clusterings[0]

        if (clusterMethod is 'backward_path') and (selectionMethod is 'all'):
            return self.clusterings

        elif clusterMethod is 'label_propagation':
            return self.clusterings


