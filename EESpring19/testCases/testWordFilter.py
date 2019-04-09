import unittest
import numpy as np
import pandas as pd
from nltk.corpus import words
from EESpring19.WordFilter import WordFilter

def gen_document_content_series(num_words: np.array=np.array([10] * 10),
                                num_unique_words=100,
                                seed=1)->pd.Series:

    document_content_dict = {}

    np.random.seed(seed=seed)
    word_list = np.random.choice(words.words(), size=num_unique_words, replace=False)

    for _id, word_count in enumerate(num_words):
        document_content_dict['a_{}'.format(_id)] = np.random.choice(word_list, size=word_count, replace=True)

    return pd.Series(document_content_dict)

class MyTest(unittest.TestCase):

    def setUp(self):
        word_filter = WordFilter

    def test(self):
        self.assertEqual(fun(3), 4)

if __name__ == '__main__':
    unittest.main()