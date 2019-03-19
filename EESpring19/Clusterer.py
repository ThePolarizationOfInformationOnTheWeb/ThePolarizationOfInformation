import pandas as pd
import numpy as np


class Clusterer:

    def __init__(self, network_df: pd.DataFrame):
        """
        Initialize clusterer instance
        :param network_df: The DataFrame that holds the adjacency matrix
        """
        self.adj = network_df.values
        self.node_id_map = pd.Series(dict(zip(list(range(network_df.shape[0])), network_df.index.tolist())))
        self.clusterings = None

    def update_network(self, new_network_df) -> None:
        """
        Reinitialize the clusterer instance with new adjacency matrix
        :param new_network_df: The new adjacency matrix
        """
        self.adj = new_network_df.values
        self.node_id_map = pd.Series(dict(zip(list(range(new_network_df.shape[0])), new_network_df.index.tolist())))
        self.clusterings = None

    def get_clustering(self, method: str='backward_path')->np.array:
        """

        :param method: Clustering method to be used. Default is the backward path algorithm
        :return: An np.array of the clusterings. An array of arrays containing ids
        """
        # ToDo
        pass
