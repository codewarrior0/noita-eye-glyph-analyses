import numpy as np


# Chi test for correlation between distributions. Statisticians recommend against using
# this to test a distribution against itself.
def chi_test(dist1, dist2):
    return sum(dist1 * dist2) / ((sum(dist1) * sum(dist2)) or 1)


# Kappa test for auto-correlation.
# When multiplied by N(N-1) where N is the number of samples in dist1, the result is the Phi test.
# When divided by the expected auto-correlation for random text, the result is Friedman's Index of Coincidence.
def kappa_test(dist1):
    dist2 = np.maximum(dist1 - 1, 0)
    return sum(dist1 * dist2) / ((sum(dist1) * (sum(dist1)-1)) or 1)
