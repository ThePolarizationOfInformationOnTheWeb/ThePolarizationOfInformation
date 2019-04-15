import numpy as np
import pandas as pd

from EESpring19.MySQLConn import MySQLConn
from EESpring19.WordFilter import WordFilter
from EESpring19.Information import mutual_information

class NewsNetwork:

    def __init__(self, topics: list, path='./EESpring19/keys/SQL_Login.yml'):
        assert(type(topics) is list)
        self.topics = topics
        self.conn = MySQLConn(path)
        self.adj = None
        self.articles = self.conn.retrieve_article_text(self.topics)
        self.WordFilter = WordFilter(pd.Series(self.articles))

    def build_news_network(self) -> pd.DataFrame:
        pass

    def build_document_adjacency_matrix(self, method='word_union') -> pd.DataFrame:
        if method is 'word_union':
            informative_words = self.WordFilter.get_keep_words()  # add threshold
            if(informative_words.shape[0] != 0):
                word_frequency_df = self.WordFilter.get_document_word_frequency_df().loc[:, informative_words]
                #TODO: Account for when a single article has no informative words
                return self._jaccard_similarity(word_frequency_df)
            else:
                print('NOTE: No Informative Words Found')
                return np.eye(len(self.articles))
        else:
            if method is 'mutual_information':
                return self._information_similarity()
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

    def _information_similarity(self):
        channel = self.WordFilter.get_channel_dataframe()
        p = self.WordFilter.get_topic_distribution()
        adj = pd.DataFrame(data=0,columns=channel.index, index=channel.index)
        for row_index in range(adj.index.shape[0]):
            for col_index in range(adj.index.shape[0]):
                t = p[row_index] + p[col_index]
                p_prime = [p[row_index]/t, p[col_index]/t]
                mi = mutual_information()#TODO Fix this line
                adj.iloc[row_index, col_index] = mi
                adj.iloc[col_index, row_index] = mi

        return adj

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
