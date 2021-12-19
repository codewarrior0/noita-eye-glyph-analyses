# Superimposition test for positional polyalphabetic ciphers
#
# Superimposes each message against each other message with no shift. A message is
# not tested against itself, and reciprocal tests are skipped. The rate of coincidence
# is written to standard output.

from matplotlib import pyplot as plt

from tests import kappa_test
from data import eye_messages


def do_test(start=0):
    matches = 0
    checks = 0
    for i in range(9):
        for j in range(i+1, 9):
            match, check = kappa_test(eye_messages[i][start:], eye_messages[j][start:], 0)
            matches += match
            checks += check
    return checks, matches

def main():
    checks, matches = do_test()
    print(f"== Full messages ==\n"
          f"Tests:           {checks:>5}\n"
          f"Matches:         {matches:>5}\n"
          f"Coincidence rate: {(matches * 1000 // checks):>4} per thousand")
    checks, matches = do_test(25)
    print(f"== Messages[25:] ==\n"
          f"Tests:           {checks:>5}\n"
          f"Matches:         {matches:>5}\n"
          f"Coincidence rate: {(matches * 1000 // checks):>4} per thousand")
    checks, matches = do_test(50)
    print(f"== Messages[50:] ==\n"
          f"Tests:           {checks:>5}\n"
          f"Matches:         {matches:>5}\n"
          f"Coincidence rate: {(matches * 1000 // checks):>4} per thousand")


if __name__ == '__main__':
    main()