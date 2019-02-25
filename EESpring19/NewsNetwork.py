import numpy as np
import pandas as pd
from EESpring19.MySQLConn import MySQLConn

class NewsNetwork:

    def __init__(self, topics: list):
        self.topics = topics
        self.conn = MySQLConn()

    def _blahut_arimoto(self, Q, epsilon, max_iter=1000):
        # Q width is number of words
        # Q height is number of documents
        # p length = Q height docs
        # q length = Q width words
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
                D[j] =  p[j] * np.exp(self._kl_divergence(Q[j], q))
            d_sum = np.sum(D)
            for i in range(len(p_old)):
                p[i] = D[i]/d_sum

            q = np.matmul(p, Q)
        return p,q #use bayes rule to calculate phi

    @staticmethod
    def _kl_divergence(dist1:np.matrix, dist2:np.matrix):
        dist1 = np.array(dist1)[0]
        dist2 = np.array(dist2)[0]
        assert len(dist1) == len(dist2)
        return (dist1 * np.log(dist1 / dist2)).sum()

    def _build_word_probability_matrix(self):
        articles = self.conn.retrieve_article_text(self.topics)
        #remove non letters and ensure all are lowercase letters