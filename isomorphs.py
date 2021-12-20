import itertools
import random
from collections import defaultdict
from pprint import pprint
from typing import List

import colorhash as colorhash


NEARBY = 3
MAX_DISTANCE = 6

LETTER_SIZE = 2


class Break:
    WORD = '-'
    CLAUSE = '.'
    PARAGRAPH = '&'
    SEGMENT = '$'
    CHAPTER = '§'
    LINE = '/'
    PAGE = '%'
    SEPARATORS = '-.&/'


class Runic:
    _table_orig = [
        ['ᚠ', 2, ['F']],
        ['ᚢ', 3, ['U', 'V']],
        ['ᚦ', 5, ['TH']],
        ['ᚩ', 7, ['O']],
        ['ᚱ', 11, ['R']],
        ['ᚳ', 13, ['C', 'K']],
        ['ᚷ', 17, ['G']],
        ['ᚹ', 19, ['W']],
        ['ᚻ', 23, ['H']],
        ['ᚾ', 29, ['N']],
        ['ᛁ', 31, ['I']],
        ['ᛄ', 37, ['J']],
        ['ᛇ', 41, ['EO']],
        ['ᛈ', 43, ['P']],
        ['ᛉ', 47, ['X']],
        ['ᛋ', 53, ['S', 'Z']],
        ['ᛏ', 59, ['T']],
        ['ᛒ', 61, ['B']],
        ['ᛖ', 67, ['E']],
        ['ᛗ', 71, ['M']],
        ['ᛚ', 73, ['L']],
        ['ᛝ', 79, ['(I)NG', 'ING', 'NG']],
        ['ᛟ', 83, ['OE']],
        ['ᛞ', 89, ['D']],
        ['ᚪ', 97, ['A']],
        ['ᚫ', 101, ['AE']],
        ['ᚣ', 103, ['Y']],
        ['ᛡ', 107, ['I(A/O)', 'IA', 'IO']],
        ['ᛠ', 109, ['EA']]
    ]
    _table = [
        ['ᚠ', 2, ['F']],
        ['ᚢ', 3, ['U']],
        ['ᚦ', 5, ['TH']],
        ['ᚩ', 7, ['O']],
        ['ᚱ', 11, ['R']],
        ['ᚳ', 13, ['C']],
        ['ᚷ', 17, ['G']],
        ['ᚹ', 19, ['W']],
        ['ᚻ', 23, ['H']],
        ['ᚾ', 29, ['N']],
        ['ᛁ', 31, ['I']],
        ['ᛄ', 37, ['J']],
        ['ᛇ', 41, ['EO']],
        ['ᛈ', 43, ['P']],
        ['ᛉ', 47, ['X']],
        ['ᛋ', 53, ['S']],
        ['ᛏ', 59, ['T']],
        ['ᛒ', 61, ['B']],
        ['ᛖ', 67, ['E']],
        ['ᛗ', 71, ['M']],
        ['ᛚ', 73, ['L']],
        ['ᛝ', 79, ['NG']],
        ['ᛟ', 83, ['OE']],
        ['ᛞ', 89, ['D']],
        ['ᚪ', 97, ['A']],
        ['ᚫ', 101, ['AE']],
        ['ᚣ', 103, ['Y']],
        ['ᛡ', 107, ['IA']],
        ['ᛠ', 109, ['EA']]
    ]
    rune_alphabet = [a[0] for a in _table]
    latin_alphabet = [a[2][0] for a in _table]
    runes_to_latin = {r: l for r, l in zip(rune_alphabet, latin_alphabet)}


skips = "-.&$§/%\n "


class IsomorphGroup:
    """
    Immutable.

    A group of isomorphs containing the same pattern of repeated letters.
    The initial isomorph groups each contain every pair of repeated letters at a given distance.
    Further groups are created by intersecting pairs of groups.

    An isomorph group is identified by:
    - The list of positions where the isomorph appears
    - The specific pattern of repeated letters at each position
        The pattern is represented as a list of (offset, size) pairs. The initial groups contain
        only a single pair.


    """

    def __init__(self, positions, pattern):
        """

        :param positions: [pos, ...]
        :param pattern: [(offset, size), ...]
        """
        self.positions = tuple(sorted(set(positions)))
        self.pattern = tuple(sorted(set(pattern)))
        max_offset = 0
        for offset, size in pattern:
            max_offset = max(offset + size, max_offset)
        self.max_offset = max_offset
        self.order = len(pattern)
        self.size = len(positions)

    def __hash__(self):
        return hash((self.positions, self.pattern))

    def __eq__(self, other):
        return (self.positions, self.pattern) == (other.positions, other.pattern)

    def __str__(self):
        return f"IsomorphGroup(size={self.size}, order={self.order},\n\tpositions={self.positions}, \n\tpattern=\"{self.pattern_string()}\")"

    def contains(self, other: 'IsomorphGroup'):
        return self.positions == other.positions and set(self.pattern).intersection(set(other.pattern)) == set(
            other.pattern)

    def pattern_string(self):
        s = ["_"] * (self.max_offset + 1)
        for char, (offset, size) in zip("ABCDEFGHIJLKMNOPQRSTUVWXYZ", list(self.pattern)[:26]):
            if s[offset] != '_':
                char = s[offset]
            elif s[offset + size] != '_':
                char = s[offset + size]
            s[offset] = char
            s[offset + size] = char
        return ''.join(s)

    def msg_string(self, msg):
        return ", ".join(f"[{''.join(msg[position:position + self.max_offset])}]" for position in self.positions)

    def intersect(self, other: 'IsomorphGroup') -> List['IsomorphGroup']:
        """
        Given the set of positions in self and the set of positions in other, find each subset of the cartesian product
        of the two where the distance between elements of each pair in the subset is equal, and where that distance
        satisfies the NEARBY relation, and where the subset has at least two elements.

        Using each subset, create a new pattern derived from self and other, then create a list of positions with
        one element for each pair in the subset. Use the pattern and position list to return a new IsomorphGroup.
        Return one such group for each subset.

        The NEARBY relation:
        Given group1, group2, pos1, pos2:
            pos1 is NEARBY pos2 if  pos1 + group1.max_offset >= pos2 - NEARBY
                                and pos2 + group2.max_offset >= pos1 - NEARBY
            pos1
            v

            A___A
                  B____B
                  ^
                  pos2

            [ dist]
            A___A B____B


        :param other:
        :return:
        """
        pairs_by_distance = defaultdict(list)
        for pos1, pos2 in itertools.product(self.positions, other.positions):
            dist = pos2 - pos1
            if pos1 + self.max_offset >= pos2 - NEARBY and pos2 + other.max_offset >= pos1 - NEARBY:
                pairs_by_distance[dist].append((pos1, pos2))

        subsets = [(dist, pairs) for dist, pairs in pairs_by_distance.items() if len(pairs) > 1]

        results = []

        for dist, pairs in subsets:
            if dist >= 0:
                # if dist > 0, then we are adding other on to the end of self. self's min_offset stays the same.
                # each offset in other's pattern needs to be increased by dist.
                # positions are the first element of each pair, since those are self's positions.
                pattern = set(self.pattern)
                for offset, size in other.pattern:
                    pattern.add((offset + dist, size))
                positions = [p1 for p1, p2 in pairs]
                pattern = tuple(sorted(pattern))
                if pattern == self.pattern:
                    continue
            else:
                # if dist < 0, then we are adding self on to the end of other. each offset in self's pattern
                # needs to be decreased by dist (which is negative, increasing the offset...)
                # positions are the second element of each pair, other's positions.
                pattern = set(other.pattern)
                for offset, size in self.pattern:
                    pattern.add((offset - dist, size))
                positions = [p2 for p1, p2 in pairs]
                pattern = tuple(sorted(pattern))
                if pattern == other.pattern:
                    continue

            results.append(IsomorphGroup(positions, pattern))

        return results

    def split_enclosing(self, msg):
        """
        Check each position in this group for repeated letters within the group. Return one or more new IsomorphGroups
        using the updated pattern.
        :param msg:
        :return:
        """
        # print(f"Splitting {self.msg_string(msg)}")
        position_patterns = defaultdict(list)
        for position in self.positions:
            pattern = set(self.pattern)
            letter_offsets = {}
            for offset, letter in enumerate(msg[position:position + self.max_offset]):
                if letter in letter_offsets:
                    prev_offset = letter_offsets[letter]
                    pattern.add((prev_offset, offset - prev_offset))
                    del letter_offsets[letter]
                else:
                    letter_offsets[letter] = offset
            position_patterns[tuple(sorted(pattern))].append(position)

        result = [IsomorphGroup(position_patterns[pattern], pattern)
                  for pattern in position_patterns]
        # print(f"Split {self.pattern_string()} into {[r.pattern_string() for r in result]}")
        return [a for a in result if len(a.positions) > 1]


def get_initial_groups(msg):
    """
    For each letter in the alphabet, find its positions, and then find the distance between
    each pair of positions. Group the gaps by distance. Return an IsomorphGroup for each distance.
    :param msg:
    :return:
    """
    positions = defaultdict(list)
    for i, letter in enumerate(msg):
        positions[letter].append(i)

    groups_by_size = defaultdict(list)

    for pos in positions.values():
        if len(pos) == 1:
            continue
        for i, p1 in enumerate(pos[:-1]):
            p2 = pos[i + 1]
            size = p2 - p1
            if size > MAX_DISTANCE:
                continue

            groups_by_size[size].append(p1)

    gbs = list(groups_by_size.items())
    gbs.sort(key=lambda a: a[0])
    return [IsomorphGroup(positions, [(0, size)]) for size, positions in gbs]


def find_isomorphs(msg) -> List[IsomorphGroup]:
    initial_groups = get_initial_groups(msg)

    result = []
    # Get the intersections of each pair of groups.
    isects = set([c for a, b in itertools.combinations(initial_groups, 2) for c in a.intersect(b)])
    isects = [c for a in isects for c in a.split_enclosing(msg)]
    while len(isects):
        next_isects = set([c for a, b in itertools.product(isects, initial_groups) for c in a.intersect(b)])
        next_isects = [c for a in next_isects for c in a.split_enclosing(msg)]
        result.extend(isects)
        isects = next_isects

    # Only non-accidental isomorphs, please
    result = set([g for g in result if g.order > 2 or g.size > 2])
    rejects = []
    for group1, group2 in itertools.combinations(result, 2):
        if group1.contains(group2):
            rejects.append(group2)
        if group2.contains(group1):
            rejects.append(group1)

    return [g for g in result if g not in rejects]


def get_color(obj):
    r, g, b = colorhash.ColorHash(obj, lightness=(0.6, 0.7, 0.8)).rgb
    return f"rgb({r}, {g}, {b})"


def colored_letter(colors, letter):
    letter = Runic.runes_to_latin[letter]
    if colors and len(colors):
        return f"<span style=\"" \
               f"background-color:{colors[0]}; " \
               f"background-image:linear-gradient(to bottom, " \
               f"{', '.join(str(c) for c in colors)})\">" \
               f"{letter:{LETTER_SIZE}}" \
               f"</span>"
    else:
        return f"{letter:{LETTER_SIZE}}"


def format_isomorphs(isomorphs: List[IsomorphGroup], msg):
    def expected_rate(order, size):
        rates = monte_carlo_results.get(len(msg_cleaned))
        if rates is None:
            return "Unknown"
        rate = rates.get((order, size))
        if rate is None:
            return "Unknown"
        return rate

    msg_cleaned = [m for m in msg if m in Runic.rune_alphabet]

    colors_by_position = defaultdict(list)
    underlines = {}
    output_chunks = [f"Number of letters: <b>{len(msg_cleaned)}</b>\n\n"]

    morph_header = f"Isomorphs by (order) and [group size]:\n"

    order_size_key = lambda a: (a.order, a.size)
    for (order, size), morphs in itertools.groupby(
            sorted(isomorphs, key=order_size_key), key=order_size_key):
        morph_header += f"    ({order:2})[{size:2}]: {len(list(morphs)):3} ({expected_rate(order, size)} expected)\n"

    morph_chunk = [morph_header]

    for morphnum, morph in enumerate(isomorphs):
        pattern = morph.pattern_string()
        for p in morph.positions:
            morph_line = ""
            for off, ch in enumerate(pattern):
                color = get_color((morphnum, ch))
                morph_line += colored_letter([color] if ch != '_' else [], msg_cleaned[p + off])
                if ch != '_':
                    colors_by_position[p + off].append(color)

            underlines[p] = p + morph.max_offset
            morph_chunk.append(morph_line)

    output_chunks.append('\n'.join(morph_chunk))

    output_letters = []

    def flush_letters():
        groups = []
        for i in range(0, len(output_letters), 5):
            groups.append(''.join(output_letters[i:i + 5]))

        lines = []
        for i in range(0, len(groups), 6):
            lines.append('  '.join(groups[i:i + 6]))

        chunk = '\n\n'.join(lines)
        output_letters[:] = []
        output_chunks.append(chunk)

    ul_end = None
    letter_idx = 0
    put_separator = False
    for letter in msg:
        if letter not in Runic.rune_alphabet:
            if letter == Break.PAGE:
                flush_letters()
            if letter in Break.SEPARATORS:
                put_separator = True
            continue

        frag = " "
        if put_separator:
            frag = "•"
            put_separator = False

        if underlines.get(letter_idx) is not None and ul_end is None:
            ul_end = underlines[letter_idx]
            frag += "<u>"

        colors = colors_by_position.get(letter_idx)
        frag += colored_letter(colors, letter)

        if letter_idx == ul_end:
            ul_end = None
            frag += "</u>"
        output_letters.append(frag)
        letter_idx += 1

    flush_letters()
    return '\n\n'.join(output_chunks)


def monte_carlo_main():
    with open("liber-primus__transcription--master.txt", encoding='utf8') as f:
        liber_raw = ''.join(f.readlines()[9:])
    liber_segments = liber_raw.split(Break.SEGMENT)[7:-3]
    print(len(liber_segments))
    seg_lengths = [len([a for a in seg if a in Runic.rune_alphabet]) for seg in liber_segments]
    order_size_key = lambda a: (a.order, a.size)

    trial_count = 1000
    trial_results = {}

    for length in seg_lengths:
        trials = defaultdict(list)

        for _ in range(trial_count):
            msg = random.choices(Runic.rune_alphabet, k=length)
            isomorphs = find_isomorphs(msg)

            for (order, size), morphs in itertools.groupby(
                    sorted(isomorphs, key=order_size_key), key=order_size_key):
                trials[order, size].append(len(list(morphs)))

        trial_results[length] = {(order, size): sum(trials[order, size]) / trial_count
                                 for order, size in sorted(trials.keys())}

    pprint(trial_results)


monte_carlo_results = {
    9: {},
    308: {(2, 3): 0.222,
          (2, 4): 0.022,
          (3, 2): 0.083,
          (3, 3): 0.001,
          (4, 2): 0.001},
    729: {(2, 3): 2.518,
          (2, 4): 0.376,
          (2, 5): 0.045,
          (2, 6): 0.005,
          (2, 7): 0.001,
          (3, 2): 0.492,
          (3, 3): 0.005,
          (4, 2): 0.012},
    1021: {(2, 3): 5.143,
           (2, 4): 1.115,
           (2, 5): 0.187,
           (2, 6): 0.028,
           (2, 7): 0.002,
           (3, 2): 0.949,
           (3, 3): 0.012,
           (4, 2): 0.018,
           (5, 2): 0.002},
    1145: {(2, 3): 6.756,
           (2, 4): 1.628,
           (2, 5): 0.346,
           (2, 6): 0.059,
           (2, 7): 0.011,
           (2, 8): 0.002,
           (3, 2): 1.261,
           (3, 3): 0.013,
           (4, 2): 0.023},
    1524: {(2, 3): 11.59,
           (2, 4): 3.742,
           (2, 5): 1.002,
           (2, 6): 0.23,
           (2, 7): 0.056,
           (2, 8): 0.009,
           (2, 9): 0.001,
           (3, 2): 2.184,
           (3, 3): 0.031,
           (4, 2): 0.036,
           (5, 2): 0.001},
    1589: {(2, 3): 12.457,
           (2, 4): 4.137,
           (2, 5): 1.146,
           (2, 6): 0.259,
           (2, 7): 0.067,
           (2, 8): 0.011,
           (2, 9): 0.001,
           (3, 2): 2.399,
           (3, 3): 0.033,
           (4, 2): 0.037},
    1729: {(2, 3): 14.323,
           (2, 4): 5.085,
           (2, 5): 1.487,
           (2, 6): 0.402,
           (2, 7): 0.093,
           (2, 8): 0.021,
           (2, 9): 0.004,
           (2, 10): 0.001,
           (3, 2): 2.701,
           (3, 3): 0.044,
           (4, 2): 0.056},
    1894: {(2, 3): 16.654,
           (2, 4): 6.395,
           (2, 5): 2.105,
           (2, 6): 0.62,
           (2, 7): 0.15,
           (2, 8): 0.034,
           (2, 9): 0.003,
           (2, 10): 0.001,
           (3, 2): 3.434,
           (3, 3): 0.05,
           (4, 2): 0.059,
           (5, 2): 0.001},
    3008: {(2, 3): 27.47,
           (2, 4): 15.957,
           (2, 5): 7.946,
           (2, 6): 3.355,
           (2, 7): 1.304,
           (2, 8): 0.417,
           (2, 9): 0.146,
           (2, 10): 0.043,
           (2, 11): 0.016,
           (2, 12): 0.006,
           (3, 2): 8.072,
           (3, 3): 0.182,
           (3, 4): 0.006,
           (4, 2): 0.17,
           (5, 2): 0.001}
}


def main():
    with open("liber-primus__transcription--master.txt", encoding='utf8') as f:
        liber_raw = ''.join(f.readlines()[9:])
    liber_segments = liber_raw.split(Break.SEGMENT)[7:-3]
    print(len(liber_segments))
    print(f"Corpus: {len([a for seg in liber_segments for a in seg if a in Runic.rune_alphabet])} letters")

    with open("docs/isomorphs_out.html", "w", encoding='utf8') as f:
        f.write("<html><body><pre>\n")

        for secno, liber_section in enumerate(liber_segments):
            f.write(f"\n<h3>Section {secno}</h3>\n")
            msg_cleaned = [m for m in liber_section if m in Runic.rune_alphabet]
            isomorphs = find_isomorphs(msg_cleaned)
            # for iso in isomorphs:
            #     print(iso)
            s = format_isomorphs(isomorphs, liber_section)
            f.write(s)
        f.write("</pre></body></html>")


if __name__ == '__main__':
    main()
