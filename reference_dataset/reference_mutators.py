
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
import copy

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
    typo = None
    if right:
        typo = word[0:index]+word[index+1]+word[index]+word[index+2:]
    else:
        typo = word[0:index-1]+word[index]+word[index-1]+word[index+1:]
    #print(f"{index*" "}{index}{int(right)*"-"}\n{typo}")
    return typo

def typo_autocorrect(word): pass

# Gabe code :D
# do keep in mind that this is only hypothetical, and once we have the go-ahead, we can then begin to actually implement
# this.
def mutate_authors_refinement(authors_list: list) -> tuple: # do note that this is merely temporary and will be
    # adjusted as we implement it back into a more centralized code

    # sets mutated_authors equal to a deep copy of the authors_list
    mutated_authors = copy.deepcopy(authors_list)
    actions_logged = []
    if not mutated_authors:
        return mutated_authors, actions_logged

    # portion of code that swaps any two authors by X amount of indexes, and not just first two
    if len(mutated_authors) >= 2:
        # authors are within an array, so this will examine said positions across the list array.
        idx1, idx2 = random.sample(range(len(mutated_authors)), k=2)
        mutated_authors[idx1], mutated_authors[idx2] = mutated_authors[idx2], mutated_authors[idx1]
        actions_logged.append(f"author_position_swap_(idx{idx1}_with_idx{idx2})")

        # Calls back to Ravi's functions regarding either swapping a random letter or a typo.
        # first part picks a random author index from the live array pool to sabotage
        target_author_idx = random.randint(0, len(mutated_authors) - 1)
        target_name_string = mutated_authors[target_author_idx]

        if len(target_name_string) >= 2:
            # picks an index inside the chosen author's name string
            random_char_index = random.randint(0, len(target_name_string) - 1)

            # randomly picks which of Ravi's functions to push the string through
            chosen_typo_tool = random.choice(["fatfinger", "swapletter"])

            if chosen_typo_tool == "fatfinger":
                mutated_name = typo_fatfinger(target_name_string, random_char_index)
                actions_logged.append(
                    f"called_typo_fatfinger_(author_idx_{target_author_idx}_char_idx_{random_char_index})")

            else:
                mutated_name = typo_swapletter(target_name_string, random_char_index)
                actions_logged.append(
                    f"called_typo_swapletter_(author_idx_{target_author_idx}_char_idx_{random_char_index})")
            # rewrites the mutated_authors name back into the array
            mutated_authors[target_author_idx] = mutated_name
        return mutated_authors, actions_logged



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
