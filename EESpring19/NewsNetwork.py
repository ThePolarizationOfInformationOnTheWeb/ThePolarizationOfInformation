import numpy as np
import pandas as pd

from functools import reduce
from EESpring19.MySQLConn import MySQLConn


class NewsNetwork:

    def __init__(self, topics: list):
        self.topics = topics
        self.conn = MySQLConn()

    def _blahut_arimoto(self, Q: np.matrix, epsilon: float=0.01, max_iter=1000) -> (np.array, np.array):
        """
        Implementation of the Blahut Arimoto algorithm. This Algorithm maximizes the channel capacity and finds the
        corresponding input and output distributions.
        :param Q: The conditional probability matrix describing the conditional probability of the input given the
        output. In the context of news articles: the probability of a word given and article, i.e.
        Q width is number of words, and Q height is number of documents.
        :param epsilon: The acceptable convergence error
        :param max_iter: The maximum number of iterations
        :return: p,q: The input, output distributions, respectively
        """
        p = np.array([1/Q.shape[0]] * Q.shape[0])
        q = np.matmul(p, Q)
        q_old = np.array([np.inf] * Q.shape[1])
        count = 0
        while(np.linalg.norm(q_old - q) >= epsilon) and count < max_iter:
            count = count + 1
            q_old = q
            p_old = p
            D = [None] * len(p_old)
            for j in range(len(p_old)):
                D[j] = p[j] * np.exp(self._kl_divergence(np.array(Q[j])[0], q))
            d_sum = np.sum(D)
            for i in range(len(p_old)):
                p[i] = D[i]/d_sum

            q = np.matmul(p, Q)

        # use bayes rule to calculate phi with Q,p,q
        return p, q

    @staticmethod
    def _kl_divergence(dist1:np.array, dist2:np.array):
        return (dist1 * np.log(dist1 / dist2)).sum()

    def _build_word_probability_matrix(self) -> pd.DataFrame:
        """
        Method for building the conditional probability matrix between the articles and words.
        This matrix is used in the Blahut Arimoto Algorithm.
        :return: Q: The conditional probability matrix describing the probability of a word j given the document i.
        :type: Q: pd.DataFrame
        """
        articles = self.conn.retrieve_article_text(self.topics)

        def unique_frequency(col):
            return article_series.str.count('\\b{}\\b'.format(col.name))

        def total_frequency(row):
            return row / len(article_series[row.name].split())

        # remove non letters and ensure all are lowercase letters
        # default replace with space
        # certain chars replace with nothing: comma, period, single hyphen, quotes
        article_series = pd.Series(articles)
        article_series = article_series.str.lower()
        article_series = article_series.str.replace("[-,.\"\']", "")
        article_series = article_series.str.replace("[^\w\s]", " ")

        # unique_article_words is a list of tuples with (article id, unique values)
        unique_article_words = [(id_, np.unique(str.split(article_series[id_]))) for id_ in article_series.index]
        words = [word_list for article_id, word_list in unique_article_words]
        unique_words = reduce(np.union1d, words)

        Q = pd.DataFrame(data=0, index=article_series.index, columns=unique_words)
        Q = Q.apply(unique_frequency, axis='rows')
        Q = Q.apply(total_frequency, axis='columns')

        return Q