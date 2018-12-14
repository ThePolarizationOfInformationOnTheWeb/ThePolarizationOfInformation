from sklearn.decomposition import PCA
import networkx as nx
import matplotlib.pyplot as plt
from TweetFeatureExtractor import TweetFeatureExtractor
import pandas as pd
import numpy as np
import math


class ClusterVisualizer:

    def __init__(self, topic):
        self.topic = topic
        self.network_df = pd.read_csv('{}_network.csv'.format(topic), index_col='id')
        self.node_id_map = pd.Series(dict(enumerate(self.network_df.index)))
        self.nx_graph = nx.Graph()
        feature_extractor = TweetFeatureExtractor(topic)
        tweets_with_hashtags = feature_extractor.get_tweets_with_hashtags()
        self.feature_extractor = TweetFeatureExtractor(topic=self.topic, tweets_df=tweets_with_hashtags)
        self.tweet_cluster_vector_df = pd.read_csv('{}_tweet_cluster_vectors.csv'.format(topic), header=None,
                                                   index_col=0)

        clustering = pd.read_csv('{}_cluster_evolution.csv'.format(topic), index_col='id')
        clustering = clustering.iloc[:, -1]
        cluster_dict = {}
        for group in clustering.unique():
            cluster_dict[group] = []
        id_node_map = pd.Series({t_id: node for node, t_id in dict(self.node_id_map).items()})
        for tweet_id in clustering.index:
            cluster_dict[clustering[tweet_id]].append(id_node_map[tweet_id])

        self.clustering = list(cluster_dict.values())

    def visualize_network(self):
        # build nx Graph
        # add nodes and attributes to nx_graph
        for i, cluster in enumerate(self.clustering):
            self.nx_graph.add_nodes_from(cluster, group=i)

        # create hashtag labels dictionary
        hashtag_df = self.feature_extractor.get_hashtag_dataframe()
        hashtag_labels = {}
        for node in self.node_id_map.index:
            hashtag_set = hashtag_df.columns[np.nonzero(hashtag_df.loc[self.node_id_map[node], :].values)].values
            hashtag_labels[node] = hashtag_set[0]

        id_node_map = pd.Series({t_id: node for node, t_id in dict(self.node_id_map).items()})

        # add edges
        # calc avg edge weight
        total_edge_weight = 0
        for tweet_id_i in self.network_df.index.values:
            for tweet_id_j in self.network_df.index.values:
                total_edge_weight = total_edge_weight + self.network_df['{}'.format(tweet_id_i)][tweet_id_j]

        avg_edge_weight = total_edge_weight / (2 * math.pow(len(self.network_df.index.values), 2))


        for tweet_id_i in self.network_df.index.values:
            for tweet_id_j in self.network_df.index.values:
                if self.network_df['{}'.format(tweet_id_i)][tweet_id_j] > 0.5*(avg_edge_weight):
                    self.nx_graph.add_edge(id_node_map[tweet_id_i], id_node_map[tweet_id_j])
                    self.nx_graph[id_node_map[tweet_id_i]][id_node_map[tweet_id_j]][
                        'weight'] = self.network_df['{}'.format(tweet_id_i)][tweet_id_j]

        # calculate position dictionary for vis using PCA to project down to 2 dimensions
        # X = [s.strip('[').strip(']').split() for s in self.tweet_cluster_vector_df.iloc[:, 0].values]
        # X = [[float(s) for s in l] for l in X]
        # pca = PCA(n_components=2)
        # proj_X = pca.fit_transform(X)
        # position_dict = dict(enumerate(proj_X))

        # generate color map for clusters
        color_map = dict(enumerate(np.random.rand(len(self.clustering), 3)))

        # don't plot tweets that are isolated
        tweet_node_subset = [id_node_map[tweet_id] if len(self.network_df['{}'.format(tweet_id)].nonzero()[0]) > 2 else
                             None for tweet_id in self.network_df.index]
        tweet_node_subset = np.array(tweet_node_subset)[np.array(tweet_node_subset) != None]
        new_hashtag_labels = {}
        for node in tweet_node_subset.tolist():
            new_hashtag_labels[node] = hashtag_labels[node]
        hashtag_labels = new_hashtag_labels

        # plot
        plt.figure(figsize=(25, 25))
        options = {
            'edge_color': '#FFDEA2',
            'width': 1,
            'with_labels': True,
            'font_weight': 'regular',
        }
        colors = [color_map[self.nx_graph.node[node]['group']] for node in self.nx_graph]
        nx.draw(self.nx_graph, nodelist=tweet_node_subset.tolist(), node_color=colors,
                pos=nx.spring_layout(self.nx_graph, k=50, iterations=500), labels=hashtag_labels, **options)
        ax = plt.gca()
        ax.collections[0].set_edgecolor("#555555")
        plt.show()
