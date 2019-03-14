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

    def build_document_word_communication_system(self):
        channel = self._build_word_probability_matrix()
        Q = np.matrix(channel.values)
        p, q = self._blahut_arimoto(Q)
        joint_dist = (channel.values.T * p).T
        I = self._mutual_information(joint_dist, p, q)
        numerator = (channel.values.T * p).T
        phi = (numerator / q).T
        #return p, channel, q, I, phi
        doc_entropy = self._entropy(p)
        phi_entropy = np.apply_along_axis(self._entropy, 1, phi)
        conditional_mutual_information = doc_entropy - phi_entropy
        return conditional_mutual_information

    def _entropy(self, dist: np.array):
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        dist_log = np.log(dist)
        warnings.filterwarnings("default", category=RuntimeWarning)
        dist_log = np.nan_to_num(dist_log)
        return -(dist_log * dist).sum()

    def _blahut_arimoto(self, Q: np.matrix, epsilon: float=0.001, max_iter=1000) -> (np.array, np.array):
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
                D[j] = p[j] * np.exp(self._kl_divergence(np.array(Q[j])[0], np.array(q)[0]))

            d_sum = np.sum(D)

            for i in range(len(p_old)):
                p[i] = D[i]/d_sum

            q = np.matmul(p, Q)

        print(count)
        # use bayes rule to calculate phi with Q,p,q
        # phi = (p Q) / q and it isn't matrix multiplication its component wise
        return p, np.array(q)[0]

    @staticmethod
    def _kl_divergence(dist1: np.array, dist2: np.array):
        """
        This method calculates the Kullback Liebler (KL) divergence of two distributions. The KL divergence is the
        difference between the cross entropy and the entropy. It measures the similarity (or dissimilarity) between two
        probability distributions. The cross entropy is a measure of the expected number of bits per source symbol if
        one were to estimate the distribution dist_1 with dist_2. The entropy is the
        :param dist1:
        :param dist2:
        :return:
        """
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        vector = dist1 * np.log(dist2 / dist1)
        warnings.filterwarnings("default", category=RuntimeWarning)
        vector = np.nan_to_num(vector)
        return - vector.sum()

    def _mutual_information(self, joint: np.array, dist1: np.array, dist2: np.array):
        product = np.outer(dist1, dist2)
        I = self._kl_divergence(joint, product)
        return I

    def _build_word_probability_matrix(self) -> pd.DataFrame:
        """
        Method for building the conditional probability matrix between the articles and words.
        This matrix is used in the Blahut Arimoto Algorithm.
        :return: Q: The conditional probability matrix describing the probability of a word j given the document i.
        :type: Q: pd.DataFrame
        """
        articles = self.conn.retrieve_article_text(self.topics)

        print("_build_word_probability_matrix: retrieved articles")

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

        print("_build_word_probability_matrix: formatted content text")

        # unique_article_words is a list of tuples with (article id, unique values)
        unique_article_words = [(id_, np.unique(str.split(article_series[id_]))) for id_ in article_series.index]
        words = [word_list for article_id, word_list in unique_article_words]
        unique_words = reduce(np.union1d, words)

        Q = pd.DataFrame(data=0, index=article_series.index, columns=unique_words)
        Q = Q.apply(unique_frequency, axis='rows')

        print("_build_word_probability_matrix: calculated unique word frequencies for articles.")

        Q = Q.apply(total_frequency, axis='columns')

        return Q