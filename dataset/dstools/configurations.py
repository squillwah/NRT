# Thinking about reference components, types of mutations on components, and classifying sets of component mutations.

from dstools.datasets import EntryMutator   # Strange
import random

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

def testugh(dataset):
    for entry in dataset:
        #M.elocator_mismatch(entry)
        #M.elocator_randomize(entry)
        #M.doi_typo(entry)
        #M.doi_mismatch_prefix(entry)
        #M.doi_mismatch_suffix(entry)
        #M.doi_hallucinate_prefix(entry)
        #M.doi_hallucinate_suffix(entry)
        M.pmid_hallucinate(entry)
        M.pmcid_hallucinate(entry)

# Protoyping categories/labels.
# Definitions are going by Dr. Pan's doc, and should be refined later.
# As in, NOT FINAL. Translating the precise language of component typos, mutations, mismatches, and hallucinations to the four broad category definitions will be tricky.
def l1_metadata_error(dataset):
    # "Article exists, but one or more fields are wrong, incomplete, abbrieviated, or formatted differently." (any formatting funnies will need to be handled in the baking step, apart from EntryMutator @todo)

    # Right now, it just adds typos to the authors, title, and journal. More could be added with removing data and screwing up formatting in the final bake. @todo
    for entry in dataset:
        M.author_typo(entry)  # Note: if the typos come on too strong, they can be tweaked in Typofier and EntryMutator
        M.title_typo(entry)
        M.jname_typo(entry)

    # Here is where we might want some methods like:
    # - M.abreviate_title 
    # - M.abreviate_authors or M.abreviate_journal
    # - M.force_et_al
    # - etc, stuff like that
    # They would probably just set a flag on the dsentry (no logic performed in EntryMutator). 
    # It's the formatters that would need to handle the flag.

    # @todo: There is potential also for methods like:
    # - Delete author
    # - Delete title
    # - Delete whatever

def l2_serious_metadata_error(dataset):
    # The title and other major fields are wrong, but the DOI or PMID still correctly points to a real article."

    # Right now, it just mismatches everything. Some variation should be added to mix that up (only mismatching some components, random ratios). 
    for entry in dataset:
        if random.random() <= .5: M.author_mismatch(entry) # 50/50 chance between mismatching auths and shuffling.
        else: M.author_shuffle(entry)
        M.title_mismatch(entry)
        M.jname_mismatch(entry)

    # The IDs, DOIs, elocators, and everything else is left untouched.
    # In the future, considerations can be made if all IDs should remaine pristine like that, or if it should get muddier.

def l3_plausible_fabricated(dataset):
    # Fake title, other real parts, but not enough info.
    for entry in dataset:
        M.title_hallucinate(entry)  # @Consider: will the chance of randomly picking the same hallucinated title be large enough to warrant some shuffled queue thing?
        # @todo: This is were we'd really need something like 'remove_doi' or 'omit_doi_from_bake'.
        #        - Mutation could delete the data in place or just flag the formatter to omit the data.
        #        - That all is if we even pursue this route of classification. !!! There is always the alternative: just bake out a big random distributed set of many mutations and their combinations, and gather data.

        #M.jpage_hallucinate(entry)
        #M.elocator_hallucinate(entry)

def l4_needs_human_review(dataset):
    # Just a bunch of random mangling.
    for entry in dataset:
        M.author_mismatch(entry)
        M.author_shuffle(entry)     # Also author_hallucinate(entry), but we don't have the file for that yet :( @todo!
        M.title_mismatch(entry)
        M.jvol_hallucinate(entry)
        M.jiss_hallucinate(entry)
        M.jname_mismatch(entry)
        M.pubs_hallucinate(entry)
        M.elocator_mismatch(entry)
        M.pmcid_typo(entry)
        M.pmid_hallucinate(entry)
        M.doi_mismatch_suffix(entry)

# The big takeaway: 1. we need to have a good think about how to group/classify these variations of reference errors.
#                      - Orthogonality? The bounds between them are blurry, it is difficult to decide which mutations go where.
#                        - EntryMutator follows a pattern of typo/mismatch/hallucinate, could that be a model?
#                   2. how can we best express those groups with the tools we've developed? 
#                      - Ideally the code should support the classifications, though we should remain wary not to let it define them in our thoughts. 
