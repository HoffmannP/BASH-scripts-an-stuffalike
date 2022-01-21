#/usr/bin/env python3

fixed = '_R'

found = [
    ['c', 0 ]
    # [ Letter, Places … ]
]

remaining = ''
excluded = ''


# -----

def iter(outer=['']):
    return lambda inner=['']: [ o + i for o in outer for i in inner ]


CHARACTERS = 5
ALLLETTERS = set('abcdefghijklmnopqrstuvwxyz')
MUST_CONTAIN = set('aeiou')

fixed += '_____'

if 0 < len(remaining) < len(ALLLETTERS):
    baseset = {r.lower() for r in remaining}
else:
    baseset = ALLLETTERS
letters = baseset - {e.lower() for e in excluded}
iterator = iter()
letter = [None] * CHARACTERS

for position in range(CHARACTERS):
    if fixed[position].lower() in ALLLETTERS:
        possible = {fixed[position].lower()}
    else:
        possible = letters - {f[0].lower() for f in found if position in f[1:]}
    print(position, possible)
    iterator = iter(iterator(possible))

for word in iterator():
    if MUST_CONTAIN & set(word) == set():
        continue

    print(word, end='\t')
