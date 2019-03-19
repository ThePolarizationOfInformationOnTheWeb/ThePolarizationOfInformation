import numpy as np
import pandas as pd
import warnings

from functools import reduce
from EESpring19.MySQLConn import MySQLConn


class NewsNetwork:

    def __init__(self, topics: list):
        assert(type(topics) is list)
        self.topics = topics
        self.conn = MySQLConn()
        self.adj = None
        self.articles = self.conn.retrieve_article_text(self.topics)


    def build_news_network(self):
        p, channel, q, phi = self.build_document_word_communication_system()
        informative_indices = self.keep_words(p, phi)  # add threshold
        filtered_channel = channel.iloc[:, informative_indices]

    def build_document_adjacency_matrix(self, channel):
        pass

    def min_addition(self, dist1: np.array, dist2: np.array):
        dist2 = dist2.T
        ret = np.zeros((dist1.shape[0],dist2.shape[1]))
        for i in range(dist1.shape[0]):
            for j in range(dist2.shape[1]):
                for k in range(dist2.shape[0]):
                    ret[i][j] += min(dist1[i][k], dist2[k][j])
        return ret
