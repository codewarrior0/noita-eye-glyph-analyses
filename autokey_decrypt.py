# Ciphertext-keyed autokey decryption
#
# Assumes that the ciphertext alphabet is in numerical order and attempts to decrypt
# the messages using the initial key size of 4. Decrypts all but the first four letters
# of each message. The output is in the form of positions or indexes in the plaintext alphabet.

from data import eye_messages
import repeats

initial_keysize = 4


def decrypt(m):
    # Numpy makes this easy.
    # P = C - K
    plain = (m[initial_keysize:] - m[:-initial_keysize]) % 83
    return plain


def print_plain(plain):
    s = ""
    for i, p in enumerate(plain):
        s += f"{p:3}"
        if i % 5 == 4:
            s += " "
        if i % 25 == 24:
            s += "\n"
    print(s)


def main():
    msgs = [decrypt(m) for m in eye_messages]

    rep = repeats.find_repeats(msgs)
    repeats.output_html(rep, msgs, "docs/repeats_decr_out.html")
    repeats.print_stats(rep)

if __name__ == '__main__':
    main()
