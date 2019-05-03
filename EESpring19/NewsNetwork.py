import numpy as np
import pandas as pd

from EESpring19.MySQLConn import MySQLConn
from EESpring19.WordFilter import WordFilter
from EESpring19.Information import mutual_information
from EESpring19.Clusterer import Clusterer

class NewsNetwork:

    def __init__(self, topics: list, path='./EESpring19/keys/SQL_Login.yml', similarity_metric='mutual_information'):
        assert(type(topics) is list)
        self.topics = topics
        self.conn = MySQLConn(path)
        self.adj = None
        self.Clusterer = None
        self.articles = self.conn.retrieve_article_text(self.topics)
        self.WordFilter = WordFilter(pd.Series(self.articles))
        self.similarity_metric = similarity_metric

    def build_news_network(self) -> pd.DataFrame:
        curr_clustering = [[key] for key in self.articles]
        clusterings = [curr_clustering]
        dams = []
        Topic_article_map = {T: [T] for T in self.articles}
        for i in range(100):
            dam = self.build_document_adjacency_matrix()
            dams.append(dam)
            self.Clusterer = Clusterer(dam)
            curr_clustering = self.Clusterer.get_clustering('backward_path')

            if (len(clusterings[-1]) == len(curr_clustering)) or (len(curr_clustering) == 1):
                # no new clusters, or single cluster => equilibrium
                print("Topic_article_map")
                print(Topic_article_map)
                print("curr_clustering")
                print(curr_clustering)
                print("range(len(curr_clustering))")
                print(range(len(curr_clustering)))
                print("urr_clustering[T_1]]")
                print(curr_clustering[0])
                print('Topic_article_map[T_0]')
                print(Topic_article_map[curr_clustering[0][0]])
                Topic_article_map = {T_1: [Topic_article_map[T_0] for
                                           T_0 in curr_clustering[T_1]] for T_1 in range(len(curr_clustering))}
                Topic_article_map = {idx: [i for l in Topic_article_map[idx] for i in l] for idx in Topic_article_map}
                self.WordFilter.combine_documents(curr_clustering)
                clusterings.append(list(Topic_article_map.values()))
                dams.append(dam)
                break

            print("Topic_article_map")
            print(Topic_article_map)
            print("curr_clustering")
            print(curr_clustering)
            print("range(len(curr_clustering))")
            print(range(len(curr_clustering)))
            print("urr_clustering[T_1]]")
            print(curr_clustering[0])
            print('Topic_article_map[T_0]')
            print(Topic_article_map[curr_clustering[0][0]])
            # join articles into topics
            Topic_article_map = {T_1: [Topic_article_map[T_0] for
                                       T_0 in curr_clustering[T_1]] for
                                       T_1 in range(len(curr_clustering))}
            print("Topic_article_map !!!!!!!!!")
            print(Topic_article_map)
            Topic_article_map = {idx: [i for l in Topic_article_map[idx] for i in l] for idx in Topic_article_map}
            self.WordFilter.combine_documents(curr_clustering)
            clusterings.append(list(Topic_article_map.values()))


        return clusterings, dams

    def build_document_adjacency_matrix(self) -> pd.DataFrame:
        if self.similarity_metric is 'word_union':
            informative_words = self.WordFilter.get_keep_words()  # add threshold
            informative_topics = self.WordFilter.get_keep_topics()
            if(informative_words.shape[0] != 0):
                word_frequency_df = self.WordFilter.get_document_word_frequency_df().loc[informative_topics, informative_words]
                return self._jaccard_similarity(word_frequency_df)
            else:
                print('NOTE: No Informative Words Found')
                return np.eye(len(self.articles))
        elif self.similarity_metric is 'mutual_information':
            return self._information_similarity()
        else:
            print('NewsNetwork:build_document_adjacency_matrix: method {} not defined'.format(self.similarity_metric))
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

        # subset on informative words
        informative_words = self.WordFilter.get_keep_words()  # add threshold
        informative_topics = self.WordFilter.get_keep_topics()
        #print(informative_words.shape)
        #print(informative_topics.shape)
        channel_prime = channel.loc[informative_topics, informative_words]
        channel_prime = channel_prime.divide(channel_prime.sum(axis=1), axis=0)  # re-normalize conditional pmfs

        adj = pd.DataFrame(data=0, columns=informative_topics, index=informative_topics)
        for row_index in informative_topics:
            for col_index in informative_topics:
                t = p[row_index] + p[col_index]
                p_prime = [p[row_index]/t, p[col_index]/t]
                joint = [channel_prime.loc[row_index, :].values * p_prime[0],
                         channel_prime.loc[col_index, :].values * p_prime[1]]
                mi = mutual_information(joint)
                adj.loc[row_index, col_index] = (1-mi)**90
                adj.loc[col_index, row_index] = (1-mi)**90
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
