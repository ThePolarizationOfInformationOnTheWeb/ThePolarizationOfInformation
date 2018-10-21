import networkx as nx
from Clusterer import Clusterer

class PolarityCalculator:

    def _init_(self, topic: str):
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
            print("PolarityCalculator: Clustering Not Implemented")
            return None
        else:
            adj = clusterer.get_adj()
            clustering = clusterer.get_clustering()

        # generate networkx graph to obtain conductance values of clusterings after each critical time
        nx_graph = nx.Graph()

        for i in range(len(adj)):
            nx_graph.add_edges_from([(i, j) for j in range(i, len(adj[i])) if adj[i][j] == 1])

        node_list = nx_graph.nodes()

        conductance_values = []

        for i in clustering:
            # calculate the cutsize of the clustering to the rest of the graph
            cut_size = len(nx.edge_boundary(nx_graph, i, list(set(node_list) - set(i))))

            # calculate the volume of the community
            volume_i = 0
            for j in i:
                volume_i += nx_graph.degree(j)

            # calculate the volume of the rest of the graph
            volume_not_i = 0
            for k in i:
                volume_not_i += nx_graph.degree(k)

            conductance_values.append((float(cut_size) / float(min(volume_not_i, volume_i))))

        return sum(conductance_values) / len(conductance_values)

    # calculate the size range of clusterings
    # clustering - the list of communities found by the backward path algorithm
    def cluster_size_range(clustering):
        low = len(clustering[0])  # smallest cluster size intialization
        high = low  # greatest cluster size initialization

        for i in clustering:
            # compare low and high to size of i and update low and high appropriately
            if low > len(i):
                low = len(i)

            if high < len(i):
                high = len(i)

        return high - low

    # calculate the size median of clusterings
    # clustering - the list of communities found by the backward path algorithm
    def cluster_size_median(clustering):
        size_list = []  # list of community sizes

        for i in clustering:
            size_list.append(len(i))

        return np.median(np.array(size_list))