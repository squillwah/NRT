
import reftools.ref_formatters as RB
import reftools.ref_mutators as RM
import random
from copy import deepcopy

# Create a set entry from reference data
def ds_entry(rd):
    return { "id": rd["pmcid"],        # Should we use PMID, PMCID, or some internal thing (just in index?).
             "errors": 0b00000000,
             "data": deepcopy(rd),
             "format": {} }

# Create a set of set entries from a list of reference data
def make_dataset(ref_data_list, *, v=False):
    dataset = [ds_entry(ref) for ref in ref_data_list]
    return dataset

# Bake formatted references from refdata for every entry in a dataset
def bake_dataset(dataset):
    for entry in dataset:
        entry["format"] = RB.bake_formats(entry["data"])

# Class of methods to mutate dataset entries using ref_mutator functions.
class EntryMutator:
    def __init__(self, *, component_set, h_titles, h_authors, h_journals):
        # Mutation flags
        self._M_FLAGS = { "author_typo":        0b00000000000000000000000000000001,
                          "author_mismatch":    0b00000000000000000000000000000010,
                          "author_hallucinate": 0b00000000000000000000000000000100,
                          "author_mismatch":    0b00000000000000000000000000001000,

                          "title_typo":         0b00000000000000000000000000010000,
                          "title_mismatch":     0b00000000000000000000000000100000,     # Some errors are not combinable.
                          "title_hallucinate":  0b00000000000000000000000001000000 }

        # Resources for hallucination and mismatch mutations
        self._COMPONENTS = component_set            # Alternatively, if we think a hallucination sample for every component is a good idea:
        self._FAKE_TITLES = h_titles                # self._REAL_COMPONENTS
        self._FAKE_AUTHORS = h_authors              # self._FAKE_COMPONENTS
        self._FAKE_JOURNALS = h_journals            # The issue is, how fake can a date, DOI, or PMCID get? Fake enough to warrant that?

    def _flag(self, ds_entry, flag):
        ds_entry["errors"] = ds_entry["errors"] | self._M_FLAGS[flag]

    # AUTHORS
    def author_typo(self, ds_entry):
        # ! Regarding typos, the question is which kind and how many. What range of randomness do we want and why?
        # Perhaps (if we care), there is a paper. This one? https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7546536
        # As a completely arbitrary heuristic, let it be that:
        #  - There is a 1/4 chance for a typo to appear in an author's name. 
        #  - Some considerations are made for appearing in the final formats:
        #    - Typos are added to both the last and first names simultaneously.
        #    - The first three authors are guaranteed to have at least one typo.
        #  - Compounding typo's follow the natural halving of the probability (2: 1/8, 3: 1/16, so on)
        #  - Fatfingers are twice as likely as swaps.
        TYPO_CHANCE = 1/3
        FATSWAP_RATIO = 2/3
        authors = ds_entry["data"]["authors"]
        for author_i, name in enumerate(authors):
            first_three_guarantee = author_i > 2
            while random.random() <= TYPO_CHANCE or not first_three_guarantee:
                for part in name:
                    if name[part]: # Skip over empty names.
                        letter_i = random.choice([i for i, letter in enumerate(name[part]) if letter.isalpha()])
                        name[part] = RM.typo_fatfinger(name[part], letter_i) if random.random() <= FATSWAP_RATIO else RM.typo_swapletter(name[part], letter_i)
                first_three_guarantee = True
        self._flag(ds_entry, "author_typo")
        return ds_entry

    def author_shuffle(self, ds_entry): pass
    def author_mismatch(self, ds_entry): pass
    def author_hallucinate(self, ds_entry): pass

    # TITLES
    def title_typo(self, ds_entry):
        # Another arbitrary definition of typos
        #  - There is 1 typo per every 10 characters in the title.
        #  - Fatfingers are twice as likely as swaps.
        pass
    def title_mismatch(self, ds_entry):
        RM.set_title(ds_entry["data"], random.choice(self._COMPONENTS["title"]))
        self._flag(ds_entry, "title_mismatch")
        return ds_entry
    def title_hallucinate(self, ds_entry):
        RM.set_title(ds_entry["data"], random.choice(self._FAKE_TITLES))
        self._flag(ds_entry, "title_hallucinate")
        return ds_entry # Note: returns reference for convenience. It is not a copy.

    # JOURNAL NAMES
    def jname_typo(self, ds_entry): pass
    def jname_mismatch(self, ds_entry): pass
    def jname_hallucinate(self, ds_entry): pass

    # JOURNAL VOLUME / ISSUE
    def jvol_randomize(self, ds_entry): pass        # @todo: Consider: Should we bother doing mismatches / hallucinations for the numerics?
    def jiss_randomize(self, ds_entry): pass

    # JOURNAL PAGE NUMBERS
    def jpage_randomize(self, ds_entry): pass

    # JOURNAL PUBLICATION DATES
    def jpub_mismatch(self, ds_entry): pass
    def jpub_randomize(self, ds_entry): pass

    # DIGITIAL PUBLICATION DATES
    def epub_mismatch(self, ds_entry): pass
    def epub_randomize(self, ds_entry): pass

    # DOI
    def doi_typo(self, ds_entry): pass                  # @todo: Consider: If we do typo's on numerics, should they include fatfinger or only swap? The assumption is that fatfinger typos are too rare in this case (letters in a number would be seen and fixed).
    def doi_mismatch(self, ds_entry): pass
    def doi_randomize_prefix(self, ds_entry): pass
    def doi_randomize_suffix(self, ds_entry): pass

    # PMIDS / PMCIDS
    def pmid_typo(self, ds_entry): pass
    def pmid_mismatch(self, ds_entry): pass
    def pmid_randomize(self, ds_entry): pass
    def pmcid_typo(self, ds_entry): pass
    def pmcid_mismatch(self, ds_entry): pass
    def pmcid_randomize(self, ds_entry): pass

    # @todo: Consider: Should we just blanket each element with the same boilerplate mutation methods, even when it might not make complete sense? (such as mismatches on vol/iss, or hallucinating page numbers?)



