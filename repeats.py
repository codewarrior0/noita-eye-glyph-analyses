from collections import Counter, defaultdict

from data import eye_messages

max_size = 25


# Kasiski Analysis, kind of.
#
# Writes the ciphertexts with repeats underlined to out/repeats_out.html
# Writes some statistics to stdout
#
# I am not too happy with how this one turned out. I had to hand-adjust the HTML
# after pasting it into Google Docs, and the method I chose to find the longest repeats
# kind of smells bad.
# Rewrites or refactors are welcome.


def find_repeats(msgs=eye_messages):
    # Keys in repeats are bytestrings, so we can use 'in' to check for substrings
    # Values in repeats are sets of positions, so we can easily discard repeats at the same position.
    repeats = defaultdict(set)
    for m in msgs:
        for pos in range(len(m) - 1):
            for size in reversed(range(2, max_size)):
                key = bytes(tuple(m[pos:pos + size]))
                repeats[key].add(pos)

    counts = {c: repeats[c] for c in repeats if len(repeats[c]) > 1}
    ret = {}

    def find_superstrings(needle):
        for k in counts:
            if len(k) > len(needle) and needle in k:
                yield k

    for c, n in counts.items():
        # Only return the longest repeats:
        # If a repeat which is a substring of another repeat also has the same positions as the other repeat, drop it
        subs = find_superstrings(c)
        if any(counts[sub] == counts[c] for sub in subs):
            continue
        ret[tuple(c)] = n

    return ret


def output_html(repeats, msgs=eye_messages, output_filename="out/repeats_out.html"):
    class _output:
        x = 0
        s = ""

        def __call__(self, letters, underline=False):
            if underline:
                self.s += "<u>"
            for i, c in enumerate(letters):
                self.s += f"{c:02}"
                if underline and i == len(letters) - 1:
                    self.s += "</u>"
                self.s += " "
                self.x += 1
                if self.x == 25:
                    self.s += "\n"
                    self.x = 0
                else:
                    if self.x % 5 == 0:
                        self.s += " "

    output = _output()
    for msgnum, m in enumerate(msgs):
        i = 0
        output.s += " " * 39 + f"{msgnum}\n"
        while i < len(m):
            for j in reversed(range(0, 8)):
                if tuple(m[i:i + j]) in repeats:
                    output(m[i:i + j], True)
                    i += j
                    break
            else:
                output(m[i:i + 1])
                i += 1
        output.s += "\n\n"
        output.x = 0
    with open(output_filename, "w") as f:
        f.write("<html><body><pre>" + output.s + "</pre></body></html>")


def print_stats(repeats):
    sorted_repeats = sorted([(s, p) for s, p in repeats.items()], key=lambda a: -len(a[1]))
    repeat_counts = Counter()
    for string, positions in sorted_repeats:
        print(f"{string}: {sorted(positions)}")
        repeat_counts[len(positions)] += 1
    for n, c in repeat_counts.items():
        print(f"{c} strings occur {n} times")


def main():
    repeats = find_repeats()

    output_html(repeats)

    print_stats(repeats)


if __name__ == '__main__':
    main()
