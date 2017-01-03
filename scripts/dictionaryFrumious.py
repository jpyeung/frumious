
# http://tools.qhex.org/
#
# A function for dictionary searches. Returns an integer score, zero
# if the input was not found.
#
# I just threw it all into a dictionary because we have memory to spare.
# Someone please fix my comprehension btw, I don't know why it doesn't work.

import os
here = os.path.dirname(__file__)
fname = os.path.join(here, '../dict/scoredwords.txt')
d = {}
with open(fname) as f:
    lines = f.readlines()
    for line in lines:
        parts = line.split(' ')
        if len(parts) != 2:
            continue
        d[parts[0]] = int(parts[1])
    #d = {{word : score for word, score in line.split(' ') if len(line.split(' ')) == 2} for line in lines}

def score(word):
    if len(word) > 34:
        return 0
    word = word.lower();
    if any([c not in 'abcdefghijklmnopqrstuvwxyz' for c in word]):
        return 0
    if word not in d:
        return 0
    return d[word]
