#!/usr/bin/env python3

import words

fixed = '_AS_E'

found = [
    [ 's', 0, 3 ],
    # ['e', 1 ],
    # ['r', 2 ]
]

remaining = ''
excluded = 'rinpu'
lang = 'de'

# -----

def iter(outer=['']):
    return lambda inner=['']: [ o + i for o in outer for i in inner ]


CHARACTERS = 5
ALLLETTERS = set('abcdefghijklmnopqrstuvwxyz')

fixed += '_____'

if 0 < len(remaining) < len(ALLLETTERS):
    baseset = {r.lower() for r in remaining}
else:
    baseset = ALLLETTERS
letters = baseset - {e.lower() for e in excluded}
iterator = iter()
letter = [None] * CHARACTERS
must_contain = { f[0] for f in found }

for position in range(CHARACTERS):
    if fixed[position].lower() in ALLLETTERS:
        possible = {fixed[position].lower()}
    else:
        possible = letters - {f[0].lower() for f in found if position in f[1:]}
    print(position, ''.join(possible))
    iterator = iter(iterator(possible))

word_list = {
    'en': words.en,
    'de': words.de
}[lang]

for word in iterator():
    for char in must_contain:
        if char not in word:
            break
    else:
        if word in word_list:
            print(word, end='\t')