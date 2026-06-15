
# Functions to make a good thing go bad.

# Creating the puzzle piece collection, for swapping of authors, etc.

# Reconstructing, but with each element in a specific style?
#  - Can we have a func with precise general control over component style, order?

# Mutable Elements 
#  - Author list (List, or et al?) A special char for an et al?
#  - ["Durst F", "Doe J", "Appleseed J."] or ["Durst F", '!'] # ! means et al?
#  - What about constructing the names themselves from full RIS?

# A general constructor, with per component formatting, would allow for format metagarbling too.

import random

def typo_fatfinger(word, index):
    QWERTY = ["qwertyuiop", "asdfghjkl;", "zxcvbnmn,."]
    typo = None
    for ri, row in enumerate(QWERTY):
        if (li := row.find(word[index])) != -1:
            #row_shift = random.randint(-1*(li!=0), 1*(li!=len(QWERTY)-1))
            #row_shift = random.choice(tuple(set([-1*(ri>0), 0, 1*(ri<len(QWERTY)-1)])))
            #let_shift = random.choice(tuple(set([-1*(li>0), 0*(row_shift!=0), 1*(li<len(QWERTY)-1)])))
            #if ri > 0: r.append(-1)
            #ri.append(0)
            #if ri < len(QWERTY)-1: r.append(1)
            #if li > 0: l.append(-1)
            #if row_shift == 0: l.append(0)
            #if li < len(row)-1: l.append(1)
            row_shift = [0]
            if ri > 0: row_shift.append(-1)         # Stupid. Will break easy if row or letter counts change.
            if ri < 2: row_shift.append(1)
            row_shift = random.choice(row_shift)
            let_shift = []
            if li > 0: let_shift.append(-1)
            if row_shift != 0: let_shift.append(0)
            if li < 9: let_shift.append(1)
            let_shift = random.choice(let_shift)
            typo = word[:index]+QWERTY[ri+row_shift][li+let_shift]+word[index+1:]
            break
    return typo

def typo_swapletter(word, index): pass
def typo_autocorrect(word): pass
#def 

for i in range(8):
    print(typo_fatfinger("medicine", i))
