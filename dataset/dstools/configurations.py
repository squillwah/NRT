# Thinking about reference components, types of mutations on components, and classifying sets of component mutations.

from dstools.datasets import EntryMutator   # Strange

# Again, no error handling in any of this. Will break if it breaks.

# The dataset entry mutator object.
M = None

def init(*, h_titles, h_authors, h_journals, component_set, rand_year_range):
    global M # Stupid
    M = EntryMutator(h_titles=h_titles,
                     h_authors=h_authors,
                     h_journals=h_journals,
                     component_set=component_set,
                     rand_year_range=rand_year_range)
    print("we inited")

# Create sets of ds_entries for source references, hallucinated title references, and mismatched title references. @todo: more

#    # Creating DS entry mutator
#    cs, ft = None, None
#    with open("./data2/component_set.json", "r") as f:
#        cs = json.load(f)
#    with open("./data/fake_titles.txt", "r") as f:
#        ft = [line.strip() for line in f if line.strip()]
#    M = EntryMutator(component_set = cs, fake_titles = ft, fake_authors = [], fake_journals = [])
#
#
#
#
#    # Applying mutations to references (entries in dataset) 
#    for entry in title_hallucinate_ds:
#        M.title_hallucinate(entry)
#    for entry in title_mismatch_ds:
#        M.title_mismatch(entry)

def test_typos(dataset):
    for entry in dataset:
        M.author_shuffle(entry) # and shuffle
        M.author_typo(entry)
        M.title_typo(entry)
        M.jname_typo(entry)

def test_mismatch(dataset):
    for entry in dataset:
        M.author_mismatch(entry)
        M.title_mismatch(entry)
        M.jname_mismatch(entry)

def test_hallucinate(dataset):
    for entry in dataset:
        M.author_hallucinate(entry)
        M.title_hallucinate(entry)
        M.jname_hallucinate(entry)


def test_voliss(dataset):
    for entry in dataset:
        M.jvol_randomize(entry)
        M.jiss_randomize(entry)

def test_pagepub(dataset):
    for entry in dataset:
        M.jpage_randomize(entry)
        M.pub_randomize(entry)
        #M.epub_randomize(entry) # Moved into pub randomize
