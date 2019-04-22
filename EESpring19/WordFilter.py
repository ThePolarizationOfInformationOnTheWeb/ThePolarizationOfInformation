import pandas as pd
import numpy as np
import copy
from functools import reduce
from EESpring19.Information import entropy, mutual_information, kl_divergence


class WordFilter:

    def __init__(self, documents: pd.Series):
        """
        :param documents: The document series indexed by the document ids and containing the document text
        Initialize word filter instance
        """
        # remove non letters and ensure all are lowercase letters
        # default replace with space
        # certain characters replace with nothing: comma, period, single hyphen, quotes
        self.documents = documents.str.lower()
        self.documents = self.documents.str.replace("[-,.\"\']", "")
        self.documents = self.documents.str.replace("[^\w\s]", " ")
        print("WordFilter.__init__: formatted document text")

        self.keep_words = np.array([])
        self.keep_topics = np.array([])
        self.topic_document_map = {'t_{}'.format(i): ['a_{}'.format(i)] for i in range(self.documents.shape[0])}

        # Blahut Arimoto attributes
        self.channel_df = pd.DataFrame()  # Conditional probability of word given document
        self.word_frequency_df = pd.DataFrame()  # Conditional probability of word given document
        self.phi = np.array([])  # Conditional probability of document given word
        self.p = np.array([])  # Probability of document
        self.q = np.array([])  # Probability of word

    def get_word_distribution(self) -> pd.Series:
        if self.q.shape[0] != 0:
            self._build_document_word_communication_system()
        data = copy.copy(self.q)
        return pd.Series(data=data, index=self.channel_df.columns)

    def get_topic_distribution(self) -> pd.Series:
        if self.p.shape[0] != 0:
            self._build_document_word_communication_system()
        data = copy.copy(self.p)
        return pd.Series(data=data, index=self.channel_df.index)

    def get_channel_dataframe(self):
        if self.channel_df.empty:
            self._build_document_word_communication_system()
        return copy.deepcopy(self.channel_df)

    def get_keep_topics(self, method: str='Blahut Arimito', threshold: float=0.25)->np.array:
        if (self.keep_topics.size == 0) or (self.keep_words.size == 0):
            if method == 'Blahut Arimito':
                self._calc_keep_topics_and_words(method=method, threshold=threshold)

            else:
                print('WordFilter.WordFilter.get_keep_topics: method: {} is not implemented.'.format(method))
                return self.keep_topics

        return self.keep_topics

    def get_keep_words(self, method: str='Blahut Arimito', threshold: float=0.25)->np.array:
        """
        Returns the array of words to keep
        :param method: method to use for the word filter. Defaults to Blahut Arimito.
        :param threshold: conditional mutual information threshold to be considered informative
        :return: np.array of informative words
        """

        if (self.keep_topics.size == 0) or (self.keep_words.size == 0):
            if method == 'Blahut Arimito':
                self._calc_keep_topics_and_words(method=method, threshold=threshold)
            else:
                print('WordFilter.WordFilter.get_keep_words: method: {} is not implemented.'.format(method))
                return self.keep_words
        return self.keep_words

    def get_document_word_frequency_df(self):
        """
        Returns
        :return:
        """
        if self.word_frequency_df.empty:
            self._build_channel()
        return self.word_frequency_df

    def _calc_keep_topics_and_words(self, method: str='Blahut Arimito', threshold: float=0.1):
        if method == 'Blahut Arimito':
            self._build_document_word_communication_system()

            # conditional mutual information is used to filter uninformative words
            doc_entropy = entropy(self.p)
            phi_entropy = np.apply_along_axis(entropy, 1, self.phi)
            conditional_mutual_information = doc_entropy - phi_entropy
            cmi_series = pd.Series(conditional_mutual_information)
            condition = cmi_series >= (np.log2(threshold * len(self.topic_document_map)))
            print(cmi_series)

            # words used in analysis must be present in at least log_10(number of documents)
            condition = condition & ((self.word_frequency_df > 1).sum() > np.log10(self.channel_df.shape[0])).values

            self.keep_words = self.channel_df.columns[cmi_series[condition].index.values].values
            print(self.keep_words)
            keep_word_freq_df = self.word_frequency_df[self.keep_words]
            self.keep_topics = self.channel_df[keep_word_freq_df.sum(axis=1) > 0].index.values
            print(self.keep_topics)

    def _build_document_word_communication_system(self):
        """
        This method will build the document to word communications system where
        - the channel is the conditional probability of a word given the document,
        - the input distribution, p, is the distribution of the articles,
        - and the output distribution is the distribution over the unique words.
        - phi is the conditional probability of a document given a word.
        The channel of the system is fixed and is the data and the input and output distributions are constructed using
        the Blahut-Arimoto algorithm. The parameters of the system are update p, channel, q, and phi.
        :return: None
        """
        # check if channel and word_frequency_df are valid
        if self.channel_df.empty or self.word_frequency_df.empty:
            self._build_channel()

        # build channel and calculate p and q using Blahut Arimoto
        if np.any(np.array([self.p.shape[0] == 0, self.q.shape[0] == 0, self.phi.shape[0] == 0])):
            self._blahut_arimoto()

        # Calculate phi using bayes rule
        numerator = (self.channel_df.values.T * self.p).T
        phi = (numerator / self.q).T
        self.phi = phi

    def _blahut_arimoto(self, epsilon: float=0.001, max_iter=1000)->None:
        """
        Implementation of the Blahut Arimoto algorithm. This algorithm finds the input and output distributions which
        maximizes the channel capacity of the communication system, which is the mutual information between the input
        and output.
        :param epsilon: The acceptable convergence error
        :param max_iter: The maximum number of iterations
        :return: p,q: The input, output distributions, respectively
        """
        Q = np.matrix(self.channel_df.values)

        p = np.array([1/Q.shape[0]] * Q.shape[0])
        q = np.matmul(p, Q)
        q_old = np.array([np.inf] * Q.shape[1])
        count = 0

        while(np.linalg.norm(q_old - q) >= epsilon) and count < max_iter:
            count = count + 1
            q_old = q
            p_old = p
            d = [None] * len(p_old)

            for j in range(len(p_old)):
                d[j] = p[j] * np.exp(kl_divergence(np.array(Q[j])[0], np.array(q)[0]))

            d_sum = np.sum(d)

            for i in range(len(p_old)):
                p[i] = d[i]/d_sum

            q = np.matmul(p, Q)

        print("WordFilter.WordFilter._blahut_arimoto: {} Iterations for Blahut Arimoto".format(count))
        self.p, self.q = p, np.array(q)[0]

    def combine_documents(self, clustering: np.array):
        """
        given a clustering of documents, combine documents and update communication system.
        :param clustering: array of arrays of documents
        :return:
        """
        if self.word_frequency_df.empty or self.channel_df.empty:
            self._build_channel()

        def normalize(row):
            return row / self.word_frequency_df.loc[row.name, :].sum()

        new_topic_document_map = {'t_{}'.format(i): cluster for i, cluster in enumerate(clustering)}
        new_word_frequency_df = pd.DataFrame(columns=self.word_frequency_df.columns)
        for topic in new_topic_document_map:
            temp_series = self.word_frequency_df.loc[new_topic_document_map[topic], :].sum()
            temp_series.name = topic
            new_word_frequency_df = new_word_frequency_df.append(temp_series)
        # update word_frequency_df and channel_df
        # sum words frequency
        self.topic_document_map = new_topic_document_map
        self.word_frequency_df = new_word_frequency_df
        self.channel_df = new_word_frequency_df.apply(normalize, axis='columns')
        (self.phi, self.q, self.p) = (np.array([]), np.array([]), np.array([]))
        self._build_document_word_communication_system()

    def _build_channel(self)->None:
        """
        Method for building the conditional probability matrix between the articles and words.
        This matrix is used in the Blahut Arimoto Algorithm.
        :return: channel_df: The conditional probability matrix describing the probability of a word j given the
        document i.
        :type: channel_df: pd.DataFrame
        """
        print("_build_channel: formatted content text")

        # unique_article_words is a list of tuples with (article id, unique values)
        unique_article_words = [(id_, np.unique(str.split(self.documents[id_]))) for id_ in self.documents.index]
        words = [word_list for article_id, word_list in unique_article_words]
        unique_words = reduce(np.union1d, words)

        print("_build_channel: found unique words")

        def unique_frequency(col):
            return self.documents.str.count('\\b{}\\b'.format(col.name))

        def normalize(row):
            return row / len(self.documents[row.name].split())

        channel_df = pd.DataFrame(data=0, index=self.documents.index, columns=unique_words)
        word_frequency_df = channel_df.apply(unique_frequency, axis='rows')
        channel_df = word_frequency_df.apply(normalize, axis='columns')

        print("_build_channel: found words frequencies")

        self.word_frequency_df = word_frequency_df
        self.channel_df = channel_df