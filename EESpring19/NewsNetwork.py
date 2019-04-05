import numpy as np
import pandas as pd

from EESpring19.MySQLConn import MySQLConn
from EESpring19.WordFilter import WordFilter


class NewsNetwork:

    def __init__(self, topics: list, path='./EESpring19/keys/SQL_Login.yml'):
        assert(type(topics) is list)
        self.topics = topics
        self.conn = MySQLConn(path)
        self.adj = None
        self.articles = self.conn.retrieve_article_text(self.topics)
        self.WordFilter = WordFilter(self.articles)

    def build_news_network(self) -> pd.DataFrame:
        pass

    def build_document_adjacency_matrix(self, method='word_union') -> pd.DataFrame:
        if method is 'word_union':
            informative_words = self.WordFilter.get_keep_words()  # add threshold
            word_frequency_df = self.WordFilter.get_document_word_frequency_df().loc[:, informative_words]
            return self._jaccard_similarity(word_frequency_df)
        else:
            print('NewsNetwork:build_document_adjacency_matrix: method {} not defined'.format(method))
            return None

    def _jaccard_similarity(self, word_frequency_df) -> pd.DataFrame:
        """

        :param word_frequency_df:
        :return:
        """
        min = self._min_addition(word_frequency_df.values, word_frequency_df.values)
        jaccard_array = np.array([np.array([elem / (min[i][i] + min[j][j] - elem) for j, elem in enumerate(row)])
                                  for i, row in enumerate(min)])
        return pd.DataFrame(jaccard_array, index=word_frequency_df.index, columns=word_frequency_df.index)

    def _min_addition(self, dist1: np.array, dist2: np.array):
        """
        Calculates the sum of two arrays defined by component wise min. Ex: [1,3,4,0] + [0,2,5,6] = [0,2,4,0]
        :param dist1:
        :param dist2:
        :return:
        """
        dist2 = dist2.T
        ret = np.zeros((dist1.shape[0], dist2.shape[1]))
        for i in range(dist1.shape[0]):
            for j in range(dist2.shape[1]):
                for k in range(dist2.shape[0]):
                    ret[i][j] += min(dist1[i][k], dist2[k][j])
        return ret
