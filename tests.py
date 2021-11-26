import numpy as np


def chi_test(dist1, dist2):
    """
    Chi test for correlation between distributions. Statisticians recommend against using
    this to test a distribution against itself.
    """
    return sum(dist1 * dist2) / ((sum(dist1) * sum(dist2)) or 1)


def phi_test(dist1):
    """
    Phi test for auto-correlation of a distribution.
    Test the distribution against itself and an (N, D) tuple, where:
      N is the number of auto-correlations
      D is the product N(N-1) where N is the number of samples in dist1

    Their ratio is the rate of auto-correlation for the given distribution.
    When this ratio divided by the expected auto-correlation for random text, the
    result is Friedman's Index of Coincidence.
    """
    dist2 = np.maximum(dist1 - 1, 0)
    return sum(dist1 * dist2), (sum(dist1) * (sum(dist1) - 1))


def kappa_test(msg1, msg2, width):
    """
    Kappa test for rate of coincidence between distinct ciphertexts.

    Test the two ciphertexts and return an (N, D) tuple, where:
        N is the number of coincidences
        D is the number of tests performed
    """
    m1 = msg1[width:]
    m2 = msg2[:m1.shape[0]]
    m1 = m1[:m2.shape[0]]
    return np.sum(m1 == m2), m1.shape[0]
