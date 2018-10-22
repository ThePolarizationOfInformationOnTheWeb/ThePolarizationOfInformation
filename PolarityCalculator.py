import networkx as nx
import numpy as np
from Clusterer import Clusterer

class PolarityCalculator:

    def __init__(self, topic: str):
        self.topic = topic
        self.back_path_clusterer = None

    def cluster_backward_path(self):
        self.back_path_clusterer = Clusterer(self.topic)
        self.back_path_clusterer.backward_path()

    def conductance_calc(self, clustering_type: str = 'back_path'):
        """
        Method for calculating the average conductance of the clustering
        :param clustering_type: the clustering we want to use for the conductance calculation
        :return: the average conductance of the clustering
        """
        def switch_clusterer(clusterer_name):
            return {
                'back_path': self.back_path_clusterer,
            }.get(clusterer_name, None)

        clusterer = switch_clusterer(clustering_type)

        if clusterer is None:
            print("PolarityCalculator: Clustering Either Not Implemented or Fitted")
            return None
        else:
            weighted_adj = clusterer.get_weighted_adj()
            #weighted_adj = [(np.array(w) / sum(w)).tolist() for w in weighted_adj]
            clustering = clusterer.get_clustering()

        # generate networkx graph to obtain conductance values of clusterings after each critical time
        nx_graph = nx.DiGraph()

        for i in range(len(weighted_adj)):
            nx_graph.add_edges_from([(i, j, {'capacity': weighted_adj[i][j]}) for j in range(len(weighted_adj[i])) if weighted_adj[i][j] != 0])

        node_list = nx_graph.nodes()
        capacity = nx.get_edge_attributes(nx_graph, 'capacity')

        conductance_values = []

        if len(clustering) == 1:
            # only 1 clustering for the entire, define conductance to be 0
            return 0

        for i in clustering:
            # calculate the cutsize of the clustering to the rest of the graph
            edge_boundary = nx.edge_boundary(nx_graph, i)
            cut_size = sum([capacity[(a, b)] for a, b in edge_boundary])

            # calculate the volume of the community
            volume_i = 0
            for j in i:
                volume_i += sum([capacity[(j, k)] for k in nx_graph.neighbors(j)])

            # calculate the volume of the rest of the graph
            not_i = list(set(nx_graph.nodes) - set(i))
            volume_not_i = 0
            for j in not_i:
                volume_not_i += sum([capacity[(j, k)] for k in nx_graph.neighbors(j)])

            if float(min(volume_not_i, volume_i)) == 0:
                # i is a disconnected subgraph with no edges
                conductance_values.append(1)
                continue

            conductance_values.append((float(cut_size) / float(min(volume_not_i, volume_i))))

        return min(conductance_values)

    # # calculate the size range of clusterings
    # # clustering - the list of communities found by the backward path algorithm
    # def cluster_size_range(clustering):
    #     low = len(clustering[0])  # smallest cluster size intialization
    #     high = low  # greatest cluster size initialization
    #
    #     for i in clustering:
    #         # compare low and high to size of i and update low and high appropriately
    #         if low > len(i):
    #             low = len(i)
    #
    #         if high < len(i):
    #             high = len(i)
    #
    #     return high - low
    #
    # # calculate the size median of clusterings
    # # clustering - the list of communities found by the backward path algorithm
    # def cluster_size_median(clustering):
    #     size_list = []  # list of community sizes
    #
    #     for i in clustering:
    #         size_list.append(len(i))
    #
    #     return np.median(np.array(size_list))