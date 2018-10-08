import pandas as pd

from BackwardPath import back_path_clustering, transval


class Clusterer:
    adj_matrix = []  # adj_matrix[i][j] = directed edge weight from node i to node j

    def __init__(self, topic_file: str):
        network_df = pd.read_csv(topic_file, index_col='Tweet_id')
        self.adj_matrix = network_df.values.tolist()
        self.node_id_map = dict(zip(network_df.index.tolist(), list(range(network_df.shape[0]))))
        self.back_path_clusterings = None
        self.back_path_critical_times = None

    def backward_path(self):
        TranList, TranCumul = transval(self.adj_matrix)
        # update so adj is unweighted, for BackwardPath alg
        adj = [[1 if self.adj_matrix[i][j] > 0 else 0 for j in range(len(self.adj_matrix))]
               for i in range(len(self.adj_matrix))]
        self.back_path_clusterings, self.back_path_critical_times = back_path_clustering(adj, TranList, TranCumul)