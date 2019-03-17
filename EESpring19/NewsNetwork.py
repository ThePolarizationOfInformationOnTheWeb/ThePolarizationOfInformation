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

    def build_news_network(self):
        p, channel, q, phi = self.build_document_word_communication_system()
        informative_indices = self.keep_words(p, phi)  # add threshold
        filtered_channel = channel.iloc[:, informative_indices]

    def build_document_word_communication_system(self):
        """
        This method will build the document to word communications system where the channel is the conditional
        probability of a word given the document, the input distribution, p, is the distribution of the words, and the
        output distribution is the distribution of unique words. The channel of the system is fixed and is the data and
        the input and output distributions are constructed using the Blahut-Arimoto algorithm.
        :return: The parameters of the system p, channel, q, and phi. phi is the conditional probability
        """
        channel = self._build_channel()
        Q = np.matrix(channel.values)
        p, q = self._blahut_arimoto(Q)
        # joint_dist = (channel.values.T * p).T
        # I = self._mutual_information(joint_dist, p, q)
        numerator = (channel.values.T * p).T
        phi = (numerator / q).T
        return p, channel, q, phi

    def keep_words(self, p, phi, threshold=2):
        """
        takes in processed variables about the data. Calculates the conditional mutual information in order to determine which
        words are informative. This is done by looking for words that exceed the threshold. Informative in this case means a word
        helps identify the document it is in.
        :param p: probability of articles
        :param phi: probability of document given word
        :param threshold: conditional mutual information threshold to be considered informative
        :return: indices for informative words
        """
        doc_entropy = self._entropy(p)
        phi_entropy = np.apply_along_axis(self._entropy, 1, phi)
        conditional_mutual_information = doc_entropy - phi_entropy
        cmi_series = pd.Series(conditional_mutual_information)
        return cmi_series[(cmi_series > threshold)].index.values

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

    def _entropy(self, dist: np.array):
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        dist_log = np.log(dist)
        warnings.filterwarnings("default", category=RuntimeWarning)
        dist_log = np.nan_to_num(dist_log)
        return -(dist_log * dist).sum()

    def _blahut_arimoto(self, Q: np.matrix, epsilon: float=0.001, max_iter=1000) -> (np.array, np.array):
        """
        Implementation of the Blahut Arimoto algorithm. This algorithm finds the input and output distributions which
        maximizes the channel capacity of the communication system, which is the mutual information between the input
        and output.
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
        one were to estimate the distribution dist_1 with dist_2.
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

    def _build_channel(self) -> pd.DataFrame:
        """
        Method for building the conditional probability matrix between the articles and words.
        This matrix is used in the Blahut Arimoto Algorithm.
        :return: channel_df: The conditional probability matrix describing the probability of a word j given the document i.
        :type: channel_df: pd.DataFrame
        """
        articles = self.conn.retrieve_article_text(self.topics)

        print("_build_channel: retrieved articles")

        # remove non letters and ensure all are lowercase letters
        # default replace with space
        # certain chars replace with nothing: comma, period, single hyphen, quotes
        article_series = pd.Series(articles)
        article_series = article_series.str.lower()
        article_series = article_series.str.replace("[-,.\"\']", "")
        article_series = article_series.str.replace("[^\w\s]", " ")

        print("_build_channel: formatted content text")

        # unique_article_words is a list of tuples with (article id, unique values)
        unique_article_words = [(id_, np.unique(str.split(article_series[id_]))) for id_ in article_series.index]
        words = [word_list for article_id, word_list in unique_article_words]
        unique_words = reduce(np.union1d, words)
        
        print("_build_channel: found unique words")
        
        def unique_frequency(col):
            return article_series.str.count('\\b{}\\b'.format(col.name))

        def total_frequency(row):
            return row / len(article_series[row.name].split())

        channel_df = pd.DataFrame(data=0, index=article_series.index, columns=unique_words)
        channel_df = channel_df.apply(unique_frequency, axis='rows')
        channel_df = channel_df.apply(total_frequency, axis='columns')
        
        print("_build_channel: calculated unique word frequencies for articles.")

        return channel_df
