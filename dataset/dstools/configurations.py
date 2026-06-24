# Thinking about reference components, types of mutations on components, and classifying sets of component mutations.

from dstools.datasets import EntryMutator   # Strange

# Again, no error handling in any of this. Will break if it breaks.

# The dataset entry mutator object.
M = None

def init(*, h_titles, h_authors, h_journals, component_set):
    global M # Stupid
    M = EntryMutator(h_titles=h_titles,
                     h_authors=h_authors,
                     h_journals=h_journals,
                     component_set=component_set)
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

def test(dataset):
    for entry in dataset:
        pass
        M.author_typo(entry)
