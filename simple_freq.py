import numpy as np
from matplotlib import pyplot as plt

from data import eye_messages

# Simple frequency analysis.
#
# Writes some statistics to stdout
# Displays a plot in a matplotlib window

def main():
    bins = np.sum([np.bincount(i, minlength=83) for i in eye_messages], 0)
    binsort = np.argsort(bins)
    print(f"5 most common letters: {binsort[-5:]}")
    print(f"5 least common letters: {binsort[:5]}")
    print(f"Median frequency: {np.median(bins)}")
    print(f"Mean frequency: {np.mean(bins)}")

    x = bins.nonzero()[0]
    plt.bar(x, bins[x])
    plt.xlabel("Cipher Letter")
    plt.ylabel("Count")
    plt.show()


if __name__ == '__main__':
    main()