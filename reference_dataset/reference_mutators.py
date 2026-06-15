
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
    QWERTY = ["qwertyuiop",
              "asdfghjkl;",
              "zxcvbnmn,."]
    typo = None
    for ri, row in enumerate(QWERTY):
        if (li := row.find(word[index])) != -1:
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
    print(f"{i*" "}{i}\n{typo}")
    return typo

def typo_swapletter(word, index):
    right = (index == 0 or (random.random()>.5 and index < len(word)-1))
    if right:
        word = word[0:index]+word[index+1]+word[index]+word[index+2:]
    else:
        word = word[0:index-1]+word[index]+word[index-1]+word[index+1:]
    print(f"{i*" "}{i}{int(right)*"-"}\n{word}")
    return word

def typo_autocorrect(word): pass

#def 

for i in range(8):
    word = typo_fatfinger("medicine", i)
print()
for i in range(8):
    word = typo_swapletter("medicine", i)
