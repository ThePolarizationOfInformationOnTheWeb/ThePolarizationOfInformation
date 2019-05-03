import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


class plotter:
    def __init__(self, graph: pd.DataFrame, clustering: list):
        # generate networkx graph to obtain conductance values of clusterings after each critical time
        nx_graph = nx.DiGraph()

        weight_thresh = graph[0].median().median()  # adjust to remove edges below certain threshold

        for i in range(graph.shape[0]):
            nx_graph.add_edges_from(
                [(i, j, {'weight': 1 / graph.iloc[i, j]}
                  ) for j in range(graph.shape[0]) if graph.iloc[i, j] > weight_thresh])

        self.graph = nx_graph
        self.clustering = clustering

    def plot(self):
        coloring = [[i] * len(self.clustering[i]) for i in range(len(self.clustering))]
        coloring = [j[i] for j in coloring for i in range(len(j))]

        plt.figure()
        nx.draw_networkx(self.graph, node_color=coloring)
        plt.show()