# Superimposition test for periodic ciphers
#
# Superimposes each message against each other message, shifted by amounts ranging from 4 to 90, and
# displays a graph showing the number of coincidences for each shift amount.

from matplotlib import pyplot as plt

from tests import kappa_test
from data import eye_messages

bounds = (4, 90)


def main():
    x = list(range(*bounds))
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
    plt.plot(bounds, (66, 66), 'g', label="Expected (English)")
    plt.plot(bounds, (12, 12), 'r', label="Expected (Random)")
    plt.xlabel("Period Length")
    plt.ylabel("Count")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()