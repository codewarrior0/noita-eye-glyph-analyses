import numpy as np
from matplotlib import pyplot as plt

from data import eye_messages

# Superimposition test
#
# Superimposes each message against each other message, shifted by amounts ranging from 4 to 90, and
# displays a graph showing the number of coincidences for each shift amount.

def kappa_test(msg1, msg2, width):
    """
    Test the two ciphertexts and return an (N, D) tuple, where:
        N is the number of coincidences
        D is the number of tests performed
    """
    m1 = msg1[width:]
    m2 = msg2[:m1.shape[0]]
    m1 = m1[:m2.shape[0]]
    return np.sum(m1 == m2), m1.shape[0]


def main():
    x = list(range(4, 90))
    results_y = []
    for w in x:
        matches = 0
        checks = 0
        for i in range(9):
            for j in range(9):
                match, check = kappa_test(eye_messages[i], eye_messages[j], w)
                matches += match
                checks += check

        results_y.append(1000 * matches / checks)

    plt.bar(x, results_y, 0.8, label="Coincidences per 1000")
    plt.plot((4, 90), (66, 66), 'g', label="Expected (English)")
    plt.plot((4, 90), (12, 12), 'r', label="Expected (Random)")
    plt.xlabel("Period Length")
    plt.ylabel("Count")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()