import unittest
import numpy as np
import pandas as pd
from nltk.corpus import words
from EESpring19.WordFilter import WordFilter


def gen_document_content_series(num_words: np.array=np.array([10] * 10),
                                num_unique_words=10,
                                seed=1)->pd.Series:
    document_content_dict = {}

    np.random.seed(seed=seed)
    word_list = np.random.choice(words.words(), size=num_unique_words, replace=False)

    for _id, word_count in enumerate(num_words):
        document_content_dict['a_{}'.format(_id)] = ' '.join(np.random.choice(word_list, size=word_count, replace=True))

    return pd.Series(document_content_dict)


class MyTest(unittest.TestCase):

    def setUp(self):
        # default word filter
        self.default_doc_series = gen_document_content_series()
        print(self.default_doc_series)
        self.word_filter = WordFilter(self.default_doc_series)

    def test_get_keep_words(self):
        # default test
        keep_words = self.word_filter.get_keep_words(threshold=0.5)
        #print(keep_words)
        assert(len(keep_words) == len(np.unique(keep_words)))  # no duplicates

    def test_get_document_word_frequency_df(self):
        # default test
        document_word_frequency_df = self.word_filter.get_document_word_frequency_df()
        # print('document_word_frequency_df: ')
        # print(document_word_frequency_df)
        assert(document_word_frequency_df.sum().sum() == 100)  # all words accounted for

    def test_combine_documents(self):
        # cluster adjacent pairs
        cluster = [[self.default_doc_series.index[i], self.default_doc_series.index[i + 1]]
                   for i in range(0, self.default_doc_series.shape[0], 2)]
        self.word_filter.combine_documents(cluster)
        document_word_frequency_df = self.word_filter.get_document_word_frequency_df()
        print('document_word_frequency_df: ')
        print(document_word_frequency_df)
        # new data frame index only contains clustered topics
        assert(document_word_frequency_df.index.shape[0] == len(cluster))

if __name__ == '__main__':
    unittest.main()
