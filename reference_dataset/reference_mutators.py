
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


# second function by Gabe. basically takes the doi_str parameter (defined from the ripping of the RIS) and
# corrupts it through these means: the duplication or deletion of slash "/", prefix swapping, or protocol
# deletion, such as changing https to http, or outright deleting the doi
def mutate_doi_refinement(doi_str: str) -> tuple:
    # fallback if citation has no doi whatsoever
    if not doi_str:
        return "", ["doi_skipped_due_to_missing_field"]

    mutated_doi = doi_str
    actions_logged = []

    # allows for random choice of the vector that will affect the doi. this is done through the import of
    # random to allow for the selection of either one of these three mutations.
    corruption_options = ["slash_error", "prefix_swap", "protocol_or_delete"]
    chosen_vector = random.choice(corruption_options)

    # portion of code that defines the slash error.
    # NOTE: for next tuesday (or friday), I intend to add more randomness to it instead of just set parameters.
    if chosen_vector == "slash_error":
        slash_sub_type = random.choice(["remove", "duplicate"])

        if slash_sub_type == "remove":
            # strips out the divider entirely.
            mutated_doi = doi_str.replace("/", "")  # might add random clause here later
            actions_logged.append("doi_slash_divider_removed")
        else:
            # finds first single slash and duplicates the separator
            mutated_doi = doi_str.replace("/", "//", 1)
            actions_logged.append("doi_slash_divider_duplicated")

    # portion of code that defines the prefix swap mutation.
    # NOTE: for next tuesday (or friday), I intend to add more randomness to it instead of just set parameters.
    elif chosen_vector == "prefix_swap":
        # portion that ensures if it contains standard directory layout
        if "/" in doi_str:
            prefix, suffix = doi_str.split("/", 1)
            # lists common prefixes that can be swapped to:
            # Elsevier, Wiley, NEJM Group respectively
            alternative_prefixes = ["10.1016", "10.1002", "10.1056"]
            # filter out already existing prefix
            clean_prefix = prefix.replace("https://doi.org/", "").replace("http://doi.org/", "")
            filtered_alternatives = [p for p in alternative_prefixes if p not in clean_prefix]
            new_prefix = random.choice(filtered_alternatives)
            # reconstructs the doi with the fake publisher prefix.
            # keeps genuine suffix
            if doi_str.startswith("https://"):
                mutated_doi = f"https://doi.org/{new_prefix}/{suffix}"
            elif doi_str.startswith("http://"):
                mutated_doi = f"http://doi.org/{new_prefix}/{suffix}"
            else:
                mutated_doi = f"{new_prefix}/{suffix}"
            actions_logged.append(f"doi_prefix_swapped_with_{new_prefix}")
        else:
            # fallback to suffix corruption if string contains no slash to split on
            mutated_doi = doi_str[:-3] + "999"
            actions_logged.append("doi_prefix_swap_failed_fallback_to_suffix_corruption")

    # portion of code that tampers with protocol and deletes the protocol or doi entirely.
    # no randomness needed here (i think)
    elif chosen_vector == "protocol_or_delete":
        protocol_sub_type = random.choice(["drop_s", "strip_protocol", "delete_all"])
        if protocol_sub_type == "drop_s":
            # downgrades https to http, security vulnerability (https:// -> http://)
            if doi_str.startswith("https://"):
                mutated_doi = doi_str.replace("https://", "http://", 1)
                actions_logged.append("doi_protocol_downgraded_to_http")
            else:
                actions_logged.append("doi_drop_s_skipped_no_https_found")
        elif protocol_sub_type == "strip_protocol":
            # yeets the prefix
            mutated_doi = doi_str.replace("https://", "").replace("http://", "")
            actions_logged.append("doi_protocol_stripped_completely")
        elif protocol_sub_type == "delete_all":
            # just nukes the damn thing
            mutated_doi = ""
            actions_logged.append("doi_field_deleted_completely")

    return mutated_doi, actions_logged

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
