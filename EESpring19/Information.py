import warnings
import numpy as np


def entropy(dist: np.array)->float:
    """
    This method calculates the entropy of a distribution. The entropy is a lower bound on the expected number of bits
    (depending on the base of the log) per source symbol to encode a message from a source with the given distribution.
    :param dist: the distribution of the source
    :return: the entropy of the source
    """
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    dist_log = np.log2(dist)
    warnings.filterwarnings("default", category=RuntimeWarning)
    dist_log = np.nan_to_num(dist_log)
    return -(dist_log * dist).sum()


def kl_divergence(dist1: np.array, dist2: np.array)->float:
    """
    This method calculates the Kullback Liebler (KL) divergence of two distributions. The KL divergence is the
    difference between the cross entropy and the entropy. It measures the similarity (or dissimilarity) between two
    probability distributions. The cross entropy is a measure of the expected number of bits per source symbol if
    one were to estimate the distribution dist_1 with dist_2.
    :param dist1:
    :param dist2:
    :return: The KL divergence of the two distributions
    """
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    vector = dist1 * np.log2(dist2 / dist1)
    warnings.filterwarnings("default", category=RuntimeWarning)
    vector = np.nan_to_num(vector)
    return - vector.sum()


def mutual_information(joint: np.array, dist1: np.array, dist2: np.array)->float:
    """

    :param joint:
    :param dist1:
    :param dist2:
    :return:
    """
    product = np.outer(dist1, dist2)
    mutual_inf = kl_divergence(joint, product)
    return mutual_inf
