import itertools
from collections import Counter

from prac_crib import word_score

raw_lore = """
Devoted seeker after true wisdom
know this  we are watching you.

   Why? Why did you look here? What
answers are you trying to find in here?

  We know what you are after.
But it is not here, Knower to Be.

Why are you doing this? Why are you reading this?
   What do you think you will find in here?
     The answer to the treasure?

 Why must you go destroying everything? Why?
   For glory? For your precious god of gods.
Is it really worth all this? Is it? Is it really?

What do you worship? You don't even know it.
You think you know the answer, but you don't.
You think the treasure will satisfy you, but
it won't. You don't even know what your seeking.
    You think you do, but you don't.

You gave your free will to the true god. Why else would be here?
  Why else would be reading this? We wanted you to come here.
   We wanted you to read this! You think you have free will?
          We made you come here. We made you read this.

Who do you worship? Who is your god? Your real god? you don't
even know it. You don't even understand it. You understand so
 little that we pity you... poor little thing. You've come so
 far, yet you have so far to go. Or maybe you understand more
than we think? You are reading this? Do you even know who your
 god is? Your true god? The god of gods, the one true god! You
think we're the false god, but we created your god and your god
of gods. Now who is the real god? If we've created your god and
 your god of gods and you and your free will and this world and
all the worlds. All of it. We allowed you to have free will. You
 think you have free will. You poor thing. You don't. You think
   we are the monsters. We're not. Who is the real monster?
    Your god is, your god of gods is the real monster.
           Your true god is the real monster.

     You come here seeking answers?
   You think we have all the answers?
We don't not. You think we are so different
We are the same. We both serve the same god.
The god of many gods. The god we've created.
You think you're destroying us. You are not.
         You are helping us.

You think you can destroy us?
You will not destroy us.
We gave you your free will.
We made this place.
And not just this place,
all the places, all the dimensions,
all the free wills. You think
you've come to steal from us?
No, we stole from you.
We stole your time and your
money and your sanity.

This is very clever of you. Very clever.
We're impressed with you, Knower to Be.

While we're impressed, we must ask you this
 is it really worth transcribing these? Do
you really expect us the reveal the real secret?
   We can tell you this  it is possible but
          even we don't know how.
""".upper()

# In the writing originally used for the secret messages above, the letter E is represented by a square large enough
# to fully overlap any other glyph. If this square is treated as one of the holes in an overlaid grille, a message can
# be overlaid against another message and the holes in the grille will reveal only a handful of letters in the second
# message... possibly spelling out another secret message.
#
# This program superimposes each message against each other (larger) message, reads out the letters through the holes
# in the grille (by looking for the letter "E" in the smaller message), and repeats the process for each possible
# alignment allowed by the differing rectangular sizes of each pair of messages. The results are collected,
# filtered by MINIMUM_LENGTH, the rate of coincidence is computed for each, and then they are ranked by deviation
# from the expected rate of coincidence for written English. The top 100 are written to standard output.

MINIMUM_LENGTH = 10

lore_messages = raw_lore.split("\n\n")

lore_lines = [s.split('\n') for s in lore_messages]

# (y, x)
lore_sizes = [(len(msg), max(len(line) for line in msg)) for msg in lore_lines]


def coincidence_rate(msg):
    count = Counter(msg)
    coincidences = sum(c * (c - 1) for c in count.values())
    tests = len(msg) * (len(msg) - 1)
    if tests == 0:
        return 0.
    return coincidences / tests


def superimpose(lore1, lore2, x=0, y=0, w=0):
    s = [None]*w
    for line1, line2 in zip(lore1[y:], lore2):
        for x, (c1, c2) in enumerate(zip(line1[x:], line2)):
            if c1 == 'E':
                # s += c2
                s[x] = c2
    return ''.join([a for a in s if a is not None])


def main():
    scorer = word_score()

    sizes_lines = list(zip(lore_sizes, lore_lines))
    results = []
    for (sz1, ln1), (sz2, ln2) in itertools.product(sizes_lines, sizes_lines):
        if ln1 is ln2:
            continue
        dy = sz2[0] - sz1[0]
        dx = sz2[1] - sz1[1]
        if dy < 0 or dx < 0:
            continue
        for x in range(dx):
            for y in range(dy):
                msg = superimpose(ln1, ln2, x, y, sz2[1])
                if len(msg) > MINIMUM_LENGTH:
                    results.append((scorer.score(msg), msg))
                    msg = msg[::-1]
                    results.append((scorer.score(msg), msg))

    #results.sort(key=lambda a: abs(0.066 - a[0]))
    results.sort(key=lambda a:a[0])
    for rating, msg in results[-100:]:
        # print(f"{rating:<8.3} {msg}")
        print(f"{rating} {msg}")


if __name__ == '__main__':
    main()