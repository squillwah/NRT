
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

# -----
# Typos
# -----

# Swap char at index with adjacent key (on the keyboard).
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

# Swap char at index with adjacent char in string.
def typo_swapletter(word, index):
    right = (index == 0 or (random.random()>.5 and index < len(word)-1))
    typo = None
    if right:
        typo = word[0:index]+word[index+1]+word[index]+word[index+2:]
    else:
        typo = word[0:index-1]+word[index]+word[index-1]+word[index+1:]
    #print(f"{index*" "}{index}{int(right)*"-"}\n{typo}")
    return typo

def typo_autocorrect(word): pass


# -------
# Authors
# -------


# Thinking about the types of errors

# Authors
# - Author list rearrange
# - Mismatching (group and individual level)

# Title
# - Bogus title (hallucinated)
# - Mismatching

# Journal

# Vol/Issue

# Page numbers
# - Completely random? Is that a type of hallucination, where the last could be before the start?


# ---------------------------

# Mutators targetting the six bibliographic parameters of the RHS (reference hallucination score) system.
# https://medinform.jmir.org/2024/1/e54345/

# @todo: make RIS parser extract all elements, not just the ones we think we need.

# DATES

# Messing up / randomizing
#  set_date(reference["pub"], m=3, d=24, y=2023)
#  set_date(reference["epub"], y=3017, d=random.randint(1, 28))
def set_date(datedict, *, m=None, d=None, y=None):
    if m: datedict["m"] = m
    if d: datedict["d"] = m
    if y: datedict["y"] = m

# Swaping / mismatching
#  copy_date(reference1["pub"], reference2["pub"])
#  copy_date(reference1["epub"], random.choice(component_set["pub"]))
def copy_date(datedict1, datedict2):
    #set_date(datedict1, m=datedict2["m"], d=datedict2["d"], y=datedict2["y"])
    datedict1["m"] = datedict2["m"]
    datedict1["d"] = datedict2["d"]
    datedict1["y"] = datedict2["y"]

# TITLES
#  set_title(reference, random.choice(ai_titles))               # Hallucinated title swap
#  set_title(reference, random.choice(component_set["title"]))  # Real title mismatch
def set_title(refdict, title):
    refdict["title"] = title

# DOI
def set_doi(refdict, doi):
    refdict["doi"] = doi
def set_doi_suffix(refdict, suffix):
    set_doi(refdict, refdict["doi"].split("/")[0] + "/" + suffix)
def set_doi_prefix(refdict, prefix):
    set_doi(refdict, prefix + "/" + refdict["doi"].split("/")[1])

# AUTHORS
def 


# @Note: Make sure to use DEEPCOPY when copying refdicts for mutation.


from parse_refs import parse_ris
import json



if __name__ == "__main__":
    for i in range(8):
        word = typo_fatfinger("medicine", i)
    print()
    for i in range(8):
        word = typo_swapletter("medicine", i)
    print()

    typer = "bartender"
    print(typer)
    for i in range(10):
        for i in range(len(typer)):
            typer = typo_swapletter(typer, i)
        print(typer)

    FILE = "./references.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    refdata = [parse_ris(ref["ris"]) for ref in refs]

    print(json.dumps(refdata, indent=2))
