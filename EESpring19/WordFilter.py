import pandas as pd
import numpy as np
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

        self.keep_words = None

        # Blahut Arimoto attributes
        self.channel_df = None  # Conditional probability of word given document
        self.word_frequency_df = None  # Conditional probability of word given document
        self.phi = None  # Conditional probability of document given word
        self.p = None  # Probability of document
        self.q = None  # Probability of word

    def get_keep_words(self, method: str='Blahut Arimito', threshold: float=2)->np.array:
        """
        Returns the array of words to keep
        :param method: method to use for the word filter. Defaults to Blahut Arimito.
        :param threshold: conditional mutual information threshold to be considered informative
        :return: np.array of informative words
        """

        if not self.keep_words:
            if method == 'Blahut Arimito':
                self._build_document_word_communication_system()
                doc_entropy = entropy(self.p)
                phi_entropy = np.apply_along_axis(entropy, 1, self.phi)
                conditional_mutual_information = doc_entropy - phi_entropy
                cmi_series = pd.Series(conditional_mutual_information)
                self.keep_words = self.channel_df.columns[cmi_series[(cmi_series > threshold)].index.values]
            else:
                print('WordFilter.WordFilter.get_keep_words: method: {} is not implemented.'.format(method))
                return self.keep_words

        return self.keep_words

    def get_document_word_frequency_df(self):
        return self.word_frequency_df

    def _build_document_word_communication_system(self):
        """
        This method will build the document to word communications system where the channel is the conditional
        probability of a word given the document, the input distribution, p, is the distribution of the words, and the
        output distribution is the distribution of unique words. The channel of the system is fixed and is the data and
        the input and output distributions are constructed using the Blahut-Arimoto algorithm.
        :return: The parameters of the system p, channel, q, and phi. phi is the conditional probability
        """
        # build channel and calculate p and q using Blahut Arimoto
        self._build_channel()
        self._blahut_arimoto()
        # joint_dist = (channel.values.T * p).T
        # I = self._mutual_information(joint_dist, p, q)

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

    def combine_documents(self):
        pass

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

        print("_build_channel: calculated unique word frequencies for articles.")

        self.word_frequency_df = word_frequency_df
        self.channel_df = channel_df
